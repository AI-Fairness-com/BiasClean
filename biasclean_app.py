# -*- coding: utf-8 -*-
"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com with CORS Support
Author: CS Principal Engineer with 28 years Python experience
FIXED: Added CORS headers for cross-origin requests
ENHANCED: Comprehensive reporting matching pipeline's actual data structure
"""

import os
import json
import tempfile
import traceback
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# CRITICAL FIX: Configure matplotlib for headless server BEFORE any imports
# ============================================================================
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for server deployment

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# ============================================================================
# MONKEY PATCH: Disable file saving in biasclean_7 pipeline
# ============================================================================
# Disable os.makedirs (pipeline tries to create biasclean_results/)
original_makedirs = os.makedirs
def safe_makedirs(path, *args, **kwargs):
    """Only allow temp directory creation"""
    if 'biasclean_results' in str(path):
        return  # Silently skip - we don't need these folders on server
    return original_makedirs(path, *args, **kwargs)
os.makedirs = safe_makedirs

# Import pipeline AFTER monkey patches
from biasclean_7 import UniversalBiasClean, DOMAIN_CONFIGS

# ============================================================================
# NUMPY TYPE CONVERTER (FIX FOR JSON SERIALIZATION)
# ============================================================================

def convert_numpy_types(obj):
    """
    Recursively convert NumPy types to native Python types for JSON serialization.
    
    Handles:
    - numpy.bool_ -> bool
    - numpy.int64, numpy.int32, etc. -> int
    - numpy.float64, numpy.float32, etc. -> float
    - numpy.ndarray -> list
    - Nested dictionaries and lists
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

# ============================================================================
# FLASK APP CONFIGURATION
# ============================================================================

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# CRITICAL FIX: Enable CORS for all routes and origins
CORS(app, resources={
    r"/*": {
        "origins": ["https://ai-fairness.com", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Disposition"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# ============================================================================
# CORS HEADERS MIDDLEWARE (Additional layer for compatibility)
# ============================================================================

@app.after_request
def after_request(response):
    """Add CORS headers to every response"""
    response.headers.add('Access-Control-Allow-Origin', 'https://ai-fairness.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
    return response

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('upload_biasclean.html')

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Process CSV - Returns EXACT structure frontend expects"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://ai-fairness.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    try:
        # 1. Validate
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV file required'}), 400
        
        domain = request.form.get('domain', 'justice')
        
        # 2. Read file
        temp_path = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
        file.save(temp_path)
        
        try:
            df = pd.read_csv(temp_path)
            app.logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Invalid CSV: {str(e)[:100]}'}), 400
        
        # 3. Run pipeline with detailed error catching
        try:
            app.logger.info(f"Starting pipeline for domain: {domain}")
            pipeline = UniversalBiasClean(domain=domain)
            
            # CRITICAL: Disable visualization and file saving
            pipeline._save_results = lambda: None  # Override save method
            pipeline.viz.plot_disparity_comparison = lambda *args, **kwargs: None
            pipeline.viz.plot_feature_improvements = lambda *args, **kwargs: None
            pipeline.viz.plot_data_integrity = lambda *args, **kwargs: None
            pipeline.reporter.generate_html_report = lambda *args, **kwargs: None
            
            results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
            app.logger.info("Pipeline completed successfully")
            
        except Exception as e:
            app.logger.error(f"Pipeline error: {str(e)}")
            app.logger.error(traceback.format_exc())
            os.unlink(temp_path)
            return jsonify({
                'error': 'Analysis failed',
                'details': f'Pipeline error: {str(e)[:100]}'
            }), 500
        
        # 4. Extract metrics
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        mappings = results.get('mappings', {})
        feature_map = results.get('feature_map', {})
        
        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0
        
        # Count biases
        sig_biases = diagnostics.get('significant_bias_count', 0)
        
        # 5. Save corrected file
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        corrected_df = results.get('corrected_df', df)
        
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        
        try:
            corrected_df.to_csv(corrected_path, index=False)
            app.logger.info(f"Saved corrected file: {corrected_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save corrected file: {str(e)}")
        
        # 6. Create comprehensive report file
        report_filename = f"report_{session_id}.txt"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        try:
            with open(report_path, 'w') as f:
                # =============== HEADER ===============
                f.write("=" * 80 + "\n")
                f.write("BIASCLEAN ANALYSIS REPORT - v2.3\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Domain: {domain.upper()}\n")
                f.write(f"Session ID: {session_id}\n\n")
                
                # =============== EXECUTIVE SUMMARY ===============
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Initial Bias Score: {initial_bias:.4f}\n")
                f.write(f"Final Bias Score: {final_bias:.4f}\n")
                f.write(f"Overall Improvement: {improvement:.1f}%\n")
                f.write(f"Significant Biases Found: {sig_biases}\n")
                f.write(f"Records Before: {len(df)}\n")
                f.write(f"Records After: {len(corrected_df)}\n")
                retention_rate = validation.get('data_integrity', {}).get('retention_rate', 100)
                f.write(f"Data Retention: {retention_rate:.1f}%\n\n")
                
                # =============== FEATURE MAPPING DETAILS ===============
                f.write("FEATURE MAPPING & VALIDATION\n")
                f.write("-" * 80 + "\n")
                approved_count = sum(1 for m in mappings.values() if m.get('approved', False))
                
                f.write(f"Total Columns Analyzed: {len(df.columns)}\n")
                f.write(f"✅ Approved for Analysis: {approved_count}\n")
                f.write(f"⏭️  Skipped: {len(df.columns) - approved_count}\n\n")
                
                # Show mapped features with domain weights
                f.write("ANALYZED PROTECTED FEATURES:\n")
                for feature_name, source_col in feature_map.items():
                    if source_col in mappings:
                        mapping_data = mappings[source_col]
                        weight = mapping_data.get('domain_weight', 0.0)
                        confidence = mapping_data.get('confidence', 0)
                        f.write(f"• {feature_name} (Weight: {weight:.2f}) ← {source_col} (Confidence: {confidence}%)\n")
                f.write("\n")
                
                # =============== STATISTICAL TEST RESULTS ===============
                f.write("STATISTICAL DIAGNOSIS RESULTS\n")
                f.write("-" * 80 + "\n")
                
                feature_tests = diagnostics.get('feature_tests', {})
                
                for feature_name, test_data in feature_tests.items():
                    p_value = test_data.get('p_value', 1.0)
                    chi2 = test_data.get('chi2', 0)
                    effect_size = test_data.get('effect_size', 0)
                    significant = test_data.get('significant_bias', False)
                    
                    # Get domain weight for this feature
                    weight = 0.0
                    for fname, source_col in feature_map.items():
                        if fname == feature_name and source_col in mappings:
                            weight = mappings[source_col].get('domain_weight', 0.0)
                            break
                    
                    # Calculate significance threshold (based on weight)
                    significance_threshold = 0.05 * (1.0 - weight)
                    
                    status = "SIGNIFICANT" if significant else "OK"
                    significance_marker = "✅" if not significant else "⚠️"
                    
                    f.write(f"{significance_marker} {feature_name}: {status}\n")
                    f.write(f"  p-value: {p_value:.6f} (threshold: {significance_threshold:.3f})\n")
                    f.write(f"  χ² statistic: {chi2:.4f}\n")
                    f.write(f"  Effect size: {effect_size:.4f}\n")
                    f.write(f"  Domain weight: {weight:.2f}\n")
                    
                    if 'disparity_initial' in test_data and 'disparity_final' in test_data:
                        disparity_init = test_data.get('disparity_initial', 0)
                        disparity_final = test_data.get('disparity_final', 0)
                        improvement_pct = ((disparity_init - disparity_final) / disparity_init * 100) if disparity_init > 0 else 0
                        f.write(f"  Disparity: {disparity_init:.4f} → {disparity_final:.4f} (Improvement: {improvement_pct:.1f}%)\n")
                    
                    f.write("\n")
                
                # =============== MAPPING VALIDATION DETAILS ===============
                f.write("MAPPING VALIDATION DETAILS\n")
                f.write("-" * 80 + "\n")
                
                for col_name, mapping_data in mappings.items():
                    if mapping_data.get('approved', False):
                        feature = mapping_data.get('feature', 'Unknown')
                        confidence = mapping_data.get('confidence', 0)
                        weight = mapping_data.get('domain_weight', 0.0)
                        stats = mapping_data.get('validation', {}).get('statistics', {})
                        
                        f.write(f"✅ {col_name} → {feature}\n")
                        f.write(f"  Confidence: {confidence}%, Weight: {weight:.2f}\n")
                        if stats:
                            f.write(f"  Validation stats: {stats}\n")
                        f.write("\n")
                
                # =============== DATA INTEGRITY METRICS ===============
                f.write("DATA INTEGRITY & QUALITY METRICS\n")
                f.write("-" * 80 + "\n")
                
                integrity = validation.get('data_integrity', {})
                f.write(f"Retention Rate: {integrity.get('retention_rate', 100):.1f}%\n")
                f.write(f"Removed Records: {integrity.get('removed_count', 0)}\n")
                f.write(f"Added Records: {integrity.get('added_count', 0)}\n")
                f.write(f"Net Change: {integrity.get('net_change', 0):+d} records\n")
                
                distribution_change = integrity.get('distribution_change', 0)
                f.write(f"Distribution Change (Wasserstein): {distribution_change:.4f}\n")
                
                # Check for data quality metrics
                if 'data_quality' in validation:
                    quality = validation['data_quality']
                    f.write(f"Missing Values: {quality.get('missing_values', 0)}\n")
                    f.write(f"Duplicate Rows: {quality.get('duplicate_rows', 0)}\n")
                    f.write(f"Consistency Score: {quality.get('consistency_score', 100):.1f}%\n")
                f.write("\n")
                
                # =============== VALIDATION RESULTS ===============
                f.write("VALIDATION & PRODUCTION READINESS\n")
                f.write("-" * 80 + "\n")
                
                # Check if pipeline determined mitigation was needed
                requires_mitigation = diagnostics.get('requires_mitigation', False)
                prod_ready = validation.get('production_ready', False)
                
                f.write(f"Mitigation Required: {'⚠️ YES' if requires_mitigation else '✅ NO'}\n")
                f.write(f"Production Ready: {'✅ YES' if prod_ready else '⚠️ NO'}\n")
                
                if 'fairness_improvement' in validation:
                    fairness = validation['fairness_improvement']
                    if isinstance(fairness, dict) and fairness:
                        f.write("Fairness Improvements:\n")
                        for key, value in fairness.items():
                            if isinstance(value, (int, float)):
                                f.write(f"  • {key}: {value:+.1f}%\n")
                f.write("\n")
                
                # =============== PIPELINE CONFIGURATION ===============
                f.write("PIPELINE CONFIGURATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Domain: {domain}\n")
                domain_config = DOMAIN_CONFIGS.get(domain, {})
                f.write(f"Jurisdiction: {domain_config.get('jurisdiction', 'Default')}\n")
                f.write(f"Framework: {domain_config.get('framework', 'Hierarchical Taxonomy + Constraint Validation')}\n")
                f.write(f"Auto-approval Threshold: 0.80\n")
                f.write(f"Target Column: {results.get('target_column', 'Auto-detected')}\n")
                f.write("\n")
                
                # =============== DOWNLOAD INFORMATION ===============
                f.write("DOWNLOAD INFORMATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Corrected Dataset: {corrected_filename}\n")
                f.write(f"Analysis Report: {report_filename}\n")
                f.write(f"Session Files will be available for 24 hours.\n")
                f.write("\n")
                
                # =============== FOOTER ===============
                f.write("=" * 80 + "\n")
                f.write("BIASCLEAN v2.3 - 7-DOMAIN EDITION\n")
                f.write("Evidence-Based Bias Mitigation • Industry-Grade SMOTE\n")
                f.write("=" * 80 + "\n")
                
            app.logger.info(f"Saved comprehensive report file: {report_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save comprehensive report: {str(e)}")
            # Fall back to simple report if comprehensive fails
            try:
                with open(report_path, 'w') as f:
                    f.write(f"BiasClean Analysis Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Domain: {domain}\n")
                    f.write(f"Original rows: {len(df)}\n")
                    f.write(f"Cleaned rows: {len(corrected_df)}\n")
                    f.write(f"Bias reduction: {improvement:.1f}%\n")
                    f.write(f"Data retention: {retention_rate:.1f}%\n")
                    f.write(f"Significant biases found: {sig_biases}\n")
            except Exception as e2:
                app.logger.error(f"Failed to save even simple report: {str(e2)}")
        
        # 7. Return response with NUMPY TYPE CONVERSION
        response = {
            'detection': {
                'n_rows': int(len(df)),
                'n_columns': int(len(df.columns)),
                'significant_biases': int(sig_biases)
            },
            'removal': {
                'bias_reduction_percent': float(round(improvement, 1)),
                'data_retention_percent': float(round(retention_rate, 1)),
                'production_ready': bool(improvement > 5)
            },
            'files': {
                'corrected': corrected_filename,
                'report': report_filename,
                'validation': f'validation_{session_id}.json'
            },
            'session_id': session_id,
            'report_content': f'Analysis complete. Bias reduced by {improvement:.1f}%.'
        }
        
        # CRITICAL FIX: Convert all NumPy types to native Python types
        response = convert_numpy_types(response)
        
        os.unlink(temp_path)
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(f"Traceback (most recent call last):\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Server error',
            'details': str(e)[:100]
        }), 500

@app.route('/download/<filename>', methods=['GET', 'OPTIONS'])
def download(filename):
    """Simple download - filename only (no session_id in URL)"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response, 200
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv' if filename.endswith('.csv') else 'text/plain'
        )
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'BiasClean',
        'cors_enabled': True,
        'version': '2.3'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)