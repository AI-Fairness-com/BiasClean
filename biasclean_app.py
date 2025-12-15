# -*- coding: utf-8 -*-
"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com with CORS Support
ENHANCED: Captures full pipeline console output for comprehensive reporting
"""

import os
import json
import tempfile
import traceback
import io
import sys
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from contextlib import redirect_stdout, redirect_stderr

# ============================================================================
# CRITICAL FIX: Configure matplotlib for headless server BEFORE any imports
# ============================================================================
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# ============================================================================
# MONKEY PATCH: Disable file saving in biasclean_7 pipeline
# ============================================================================
original_makedirs = os.makedirs
def safe_makedirs(path, *args, **kwargs):
    if 'biasclean_results' in str(path):
        return
    return original_makedirs(path, *args, **kwargs)
os.makedirs = safe_makedirs

from biasclean_7 import UniversalBiasClean, DOMAIN_CONFIGS

# ============================================================================
# OUTPUT PARSER - Extracts rich data from pipeline console output
# ============================================================================
class PipelineOutputParser:
    """Parses the console output from UniversalBiasClean to extract detailed metrics"""
    
    def __init__(self, raw_output: str):
        self.raw_output = raw_output
        self.lines = raw_output.split('\n')
        self.parsed_data = {
            'feature_weights': {},
            'statistical_tests': {},
            'mitigation_details': {},
            'improvements': {},
            'executive_summary': {},
            'phase_outputs': {}
        }
        self._parse_all()
    
    def _parse_all(self):
        """Parse all sections of the pipeline output"""
        self._parse_feature_weights()
        self._parse_statistical_tests()
        self._parse_mitigation_details()
        self._parse_improvements()
        self._parse_executive_summary()
    
    def _parse_feature_weights(self):
        """Extract feature weights from 'Features for analysis' section"""
        weight_pattern = r'•\s+(\w+)\s+←\s+\S+\s+\(weight:\s*([0-9.]+)\)'
        for line in self.lines:
            if 'weight:' in line.lower():
                match = re.search(weight_pattern, line, re.IGNORECASE)
                if match:
                    feature, weight = match.groups()
                    self.parsed_data['feature_weights'][feature.strip()] = float(weight)
    
    def _parse_statistical_tests(self):
        """Extract statistical test results"""
        test_pattern = r'•\s+(\w+)\s+p=([0-9.]+)\s+(\w+)\s+\(weight:\s*([0-9.]+)'
        for line in self.lines:
            if 'p=' in line and 'weight:' in line:
                match = re.search(test_pattern, line)
                if match:
                    feature, p_value, status, weight = match.groups()
                    self.parsed_data['statistical_tests'][feature.strip()] = {
                        'p_value': float(p_value),
                        'significant': 'SIGNIFICANT' in status.upper(),
                        'weight': float(weight)
                    }
    
    def _parse_mitigation_details(self):
        """Extract mitigation/rebalancing details"""
        rebalance_pattern = r"Rebalancing\s+['\"]?(\w+)['\"]?\s+\(weight:\s*([0-9.]+)"
        for i, line in enumerate(self.lines):
            if 'Rebalancing' in line and 'weight:' in line:
                match = re.search(rebalance_pattern, line)
                if match:
                    feature, weight = match.groups()
                    details = {'weight': float(weight)}
                    # Look for next few lines for more details
                    for j in range(i+1, min(i+6, len(self.lines))):
                        next_line = self.lines[j]
                        if 'Samples removed:' in next_line:
                            details['samples_removed'] = int(re.search(r'(\d+)', next_line).group(1))
                        if 'Samples added:' in next_line:
                            details['samples_added'] = int(re.search(r'(\d+)', next_line).group(1))
                        if 'Disparity threshold:' in next_line:
                            details['disparity_threshold'] = float(re.search(r'([0-9.]+)', next_line).group(1))
                    self.parsed_data['mitigation_details'][feature.strip()] = details
    
    def _parse_improvements(self):
        """Extract improvement percentages"""
        imp_pattern = r'✅\s+(\w+)\s+([+-]?[0-9.]+)%'
        for line in self.lines:
            if '✅' in line and '%' in line:
                match = re.search(imp_pattern, line)
                if match:
                    feature, improvement = match.groups()
                    self.parsed_data['improvements'][feature.strip()] = float(improvement)
    
    def _parse_executive_summary(self):
        """Extract key metrics from executive summary"""
        patterns = {
            'initial_bias': r'Initial Bias Score:\s*([0-9.]+)',
            'final_bias': r'Final Bias Score:\s*([0-9.]+)',
            'improvement': r'Overall Improvement:\s*([+-]?[0-9.]+)%',
            'significant_biases': r'Significant Biases:\s*(\d+)',
            'records_before': r'Records Before:\s*([0-9,]+)',
            'records_after': r'Records After:\s*([0-9,]+)',
            'retention': r'Retention Rate:\s*([0-9.]+)%'
        }
        
        for key, pattern in patterns.items():
            for line in self.lines:
                match = re.search(pattern, line)
                if match:
                    value = match.group(1).replace(',', '')
                    if '%' in line or 'improvement' in key.lower():
                        self.parsed_data['executive_summary'][key] = float(value)
                    else:
                        try:
                            self.parsed_data['executive_summary'][key] = float(value)
                        except:
                            self.parsed_data['executive_summary'][key] = int(value)
                    break
    
    def get_feature_weight(self, feature_name: str) -> float:
        """Get weight for a specific feature"""
        return self.parsed_data['feature_weights'].get(feature_name, 0.0)
    
    def get_statistical_test(self, feature_name: str) -> Dict:
        """Get statistical test results for a feature"""
        return self.parsed_data['statistical_tests'].get(feature_name, {})
    
    def get_all_improvements(self) -> Dict[str, float]:
        """Get all improvement percentages"""
        return self.parsed_data['improvements']
    
    def get_mitigation_details(self) -> Dict:
        """Get all mitigation details"""
        return self.parsed_data['mitigation_details']
    
    def get_executive_summary(self) -> Dict:
        """Get executive summary metrics"""
        return self.parsed_data['executive_summary']

# ============================================================================
# NUMPY TYPE CONVERTER
# ============================================================================
def convert_numpy_types(obj):
    """Recursively convert NumPy types to native Python types"""
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
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/*": {"origins": ["https://ai-fairness.com", "*"]}})
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

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
    return render_template('upload_biasclean.html')

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://ai-fairness.com')
        return response, 200
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV file required'}), 400
        
        domain = request.form.get('domain', 'justice')
        
        # Save uploaded file
        temp_path = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
        file.save(temp_path)
        
        try:
            df = pd.read_csv(temp_path)
            app.logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Invalid CSV: {str(e)[:100]}'}), 400
        
        # RUN PIPELINE WITH OUTPUT CAPTURE
        app.logger.info(f"Starting pipeline for domain: {domain}")
        pipeline = UniversalBiasClean(domain=domain)
        
        # Disable visualization and file saving
        pipeline._save_results = lambda: None
        if hasattr(pipeline, 'viz'):
            pipeline.viz.plot_disparity_comparison = lambda *args, **kwargs: None
            pipeline.viz.plot_feature_improvements = lambda *args, **kwargs: None
            pipeline.viz.plot_data_integrity = lambda *args, **kwargs: None
        if hasattr(pipeline, 'reporter'):
            pipeline.reporter.generate_html_report = lambda *args, **kwargs: None
        
        # CAPTURE ALL CONSOLE OUTPUT
        output_capture = io.StringIO()
        with redirect_stdout(output_capture), redirect_stderr(output_capture):
            results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
        
        pipeline_output = output_capture.getvalue()
        app.logger.info("Pipeline completed successfully")
        app.logger.info(f"Captured {len(pipeline_output)} characters of console output")
        
        # PARSE THE CAPTURED OUTPUT
        parser = PipelineOutputParser(pipeline_output)
        
        # Extract metrics
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        mappings = results.get('mappings', {})
        feature_map = results.get('feature_map', {})
        
        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0
        
        sig_biases = diagnostics.get('significant_bias_count', 0)
        executive_summary = parser.get_executive_summary()
        
        # Use parsed data where available
        if executive_summary.get('initial_bias'):
            initial_bias = executive_summary['initial_bias']
        if executive_summary.get('final_bias'):
            final_bias = executive_summary['final_bias']
        if executive_summary.get('improvement'):
            improvement = executive_summary['improvement']
        if executive_summary.get('significant_biases'):
            sig_biases = executive_summary['significant_biases']
        
        # Save corrected file
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        corrected_df = results.get('corrected_df', df)
        
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        
        try:
            corrected_df.to_csv(corrected_path, index=False)
            app.logger.info(f"Saved corrected file: {corrected_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save corrected file: {str(e)}")
        
        # CREATE COMPREHENSIVE REPORT WITH PARSED DATA
        report_filename = f"report_{session_id}.txt"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        try:
            with open(report_path, 'w') as f:
                # =============== HEADER ===============
                f.write("=" * 80 + "\n")
                f.write("BIASCLEAN ANALYSIS REPORT - COMPREHENSIVE EDITION\n")
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
                
                records_before = executive_summary.get('records_before', len(df))
                records_after = executive_summary.get('records_after', len(corrected_df))
                f.write(f"Records Before: {records_before:,}\n")
                f.write(f"Records After: {records_after:,}\n")
                
                retention_rate = executive_summary.get('retention', 
                    validation.get('data_integrity', {}).get('retention_rate', 100))
                f.write(f"Data Retention: {retention_rate:.1f}%\n\n")
                
                # =============== FEATURE WEIGHTS & MAPPING ===============
                f.write("FEATURE WEIGHTS & PRIORITIZATION\n")
                f.write("-" * 80 + "\n")
                
                feature_weights = parser.parsed_data['feature_weights']
                if feature_weights:
                    f.write("Features Analyzed (by domain weight priority):\n")
                    for feature, weight in sorted(feature_weights.items(), 
                                                 key=lambda x: x[1], reverse=True):
                        f.write(f"  #{list(feature_weights.keys()).index(feature)+1}: ")
                        f.write(f"{feature} (Weight: {weight:.2f})\n")
                else:
                    # Fallback to results data
                    f.write("Mapped Features:\n")
                    for feature_name, source_col in feature_map.items():
                        if source_col in mappings:
                            weight = mappings[source_col].get('domain_weight', 0.0)
                            f.write(f"  • {feature_name} ← {source_col} (Weight: {weight:.2f})\n")
                f.write("\n")
                
                # =============== STATISTICAL TEST RESULTS ===============
                f.write("STATISTICAL DIAGNOSIS DETAILS\n")
                f.write("-" * 80 + "\n")
                
                statistical_tests = parser.parsed_data['statistical_tests']
                if statistical_tests:
                    for feature, test_data in statistical_tests.items():
                        p_value = test_data.get('p_value', 1.0)
                        weight = test_data.get('weight', 0.0)
                        significant = test_data.get('significant', False)
                        
                        status = "SIGNIFICANT" if significant else "OK"
                        marker = "⚠️" if significant else "✅"
                        
                        f.write(f"{marker} {feature}:\n")
                        f.write(f"  p-value: {p_value:.6f}\n")
                        f.write(f"  Domain Weight: {weight:.2f}\n")
                        f.write(f"  Status: {status}\n\n")
                else:
                    # Fallback to diagnostics
                    feature_tests = diagnostics.get('feature_tests', {})
                    for feature_name, test_data in feature_tests.items():
                        p_value = test_data.get('p_value', 1.0)
                        chi2 = test_data.get('chi2', 0)
                        significant = test_data.get('significant_bias', False)
                        
                        status = "SIGNIFICANT" if significant else "OK"
                        marker = "⚠️" if significant else "✅"
                        
                        f.write(f"{marker} {feature_name}: {status}\n")
                        f.write(f"  p-value: {p_value:.6f}\n")
                        if chi2:
                            f.write(f"  χ² statistic: {chi2:.4f}\n")
                        f.write("\n")
                
                # =============== MITIGATION DETAILS ===============
                f.write("BIAS MITIGATION PROCESS\n")
                f.write("-" * 80 + "\n")
                
                mitigation_details = parser.get_mitigation_details()
                if mitigation_details:
                    f.write("Weight-Prioritized Mitigation Order:\n")
                    for i, (feature, details) in enumerate(mitigation_details.items(), 1):
                        weight = details.get('weight', 0.0)
                        removed = details.get('samples_removed', 0)
                        added = details.get('samples_added', 0)
                        f.write(f"  #{i}: {feature} (Weight: {weight:.2f})\n")
                        if removed or added:
                            f.write(f"    Samples removed: {removed}, added: {added}\n")
                    f.write("\n")
                else:
                    f.write("Mitigation: Not required or details not captured.\n\n")
                
                # =============== FAIRNESS IMPROVEMENTS ===============
                f.write("FAIRNESS IMPROVEMENTS\n")
                f.write("-" * 80 + "\n")
                
                improvements = parser.get_all_improvements()
                if improvements:
                    for feature, imp in improvements.items():
                        f.write(f"✅ {feature}: {imp:+.1f}%\n")
                else:
                    # Try validation data
                    fairness = validation.get('fairness_improvement', {})
                    if isinstance(fairness, dict):
                        for key, value in fairness.items():
                            if isinstance(value, (int, float)):
                                f.write(f"✅ {key}: {value:+.1f}%\n")
                f.write("\n")
                
                # =============== RAW PIPELINE OUTPUT (For Reference) ===============
                f.write("PIPELINE EXECUTION LOG\n")
                f.write("-" * 80 + "\n")
                f.write("[Full console output for technical reference]\n")
                f.write("-" * 40 + "\n")
                
                # Include key sections of pipeline output
                output_lines = pipeline_output.split('\n')
                key_sections = ['PHASE', 'BIASCLEAN', 'EXECUTIVE SUMMARY', 'STATISTICAL', 'REBALANCING']
                for line in output_lines:
                    if any(section in line for section in key_sections):
                        if len(line.strip()) > 0:
                            f.write(f"{line}\n")
                
                f.write("-" * 40 + "\n\n")
                
                # =============== DOWNLOAD INFORMATION ===============
                f.write("DOWNLOAD INFORMATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Corrected Dataset: {corrected_filename}\n")
                f.write(f"Analysis Report: {report_filename}\n")
                f.write(f"Session Files will be available for 24 hours.\n\n")
                
                # =============== FOOTER ===============
                f.write("=" * 80 + "\n")
                f.write("BIASCLEAN v2.3 - 7-DOMAIN EDITION\n")
                f.write("Evidence-Based Bias Mitigation • Industry-Grade SMOTE\n")
                f.write("=" * 80 + "\n")
            
            app.logger.info(f"Saved comprehensive report file: {report_filename}")
            
        except Exception as e:
            app.logger.error(f"Failed to save comprehensive report: {str(e)}")
            # Fallback to simple report
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
        
        # Return response
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
                'report': report_filename
            },
            'session_id': session_id,
            'report_content': f'Analysis complete. Bias reduced by {improvement:.1f}%.'
        }
        
        response = convert_numpy_types(response)
        os.unlink(temp_path)
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Server error', 'details': str(e)[:100]}), 500

@app.route('/download/<filename>', methods=['GET', 'OPTIONS'])
def download(filename):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename,
                        mimetype='text/csv' if filename.endswith('.csv') else 'text/plain')
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'BiasClean', 'version': '2.3'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)