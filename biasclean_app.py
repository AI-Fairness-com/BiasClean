# -*- coding: utf-8 -*-
"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com
Author: CS Principal Engineer with 28 years Python experience
FIXED: Added NumPy type conversion for JSON serialization
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

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('upload_biasclean.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process CSV - Returns EXACT structure frontend expects"""
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
        
        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0
        
        # Count biases
        sig_biases = sum(1 for test in diagnostics.get('feature_tests', {}).values() 
                        if test.get('significant_bias', False))
        
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
        
        # 6. Create report file
        report_filename = f"report_{session_id}.txt"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        try:
            with open(report_path, 'w') as f:
                f.write(f"BiasClean Analysis Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Domain: {domain}\n")
                f.write(f"Original rows: {len(df)}\n")
                f.write(f"Cleaned rows: {len(corrected_df)}\n")
                f.write(f"Bias reduction: {improvement:.1f}%\n")
                f.write(f"Data retention: {validation.get('data_integrity', {}).get('retention_rate', 100):.1f}%\n")
                f.write(f"Significant biases found: {sig_biases}\n")
            app.logger.info(f"Saved report file: {report_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save report: {str(e)}")
        
        # 7. Return response with NUMPY TYPE CONVERSION
        response = {
            'detection': {
                'n_rows': int(len(df)),
                'n_columns': int(len(df.columns)),
                'significant_biases': int(sig_biases)
            },
            'removal': {
                'bias_reduction_percent': float(round(improvement, 1)),
                'data_retention_percent': float(round(validation.get('data_integrity', {}).get('retention_rate', 100), 1)),
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


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    """Simple download - filename only (no session_id in URL)"""
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
    return jsonify({'status': 'healthy', 'service': 'BiasClean'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
