# -*- coding: utf-8 -*-
"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com with CORS Support
FIXED VERSION: Enhanced HTML report with full pipeline details
PART 1 OF 2 - Copy this entire part first
"""

import os
import json
import tempfile
import traceback
import io
import sys
import re
import base64
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from contextlib import redirect_stdout, redirect_stderr

# ============================================================================
# CRITICAL FIX: Configure matplotlib for headless server BEFORE any imports
# ============================================================================
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, current_app
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
            if 'weight:' in line.lower() and '←' in line:
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
                    for j in range(i+1, min(i+10, len(self.lines))):
                        next_line = self.lines[j]
                        if 'Samples removed:' in next_line:
                            nums = re.findall(r'(\d+)', next_line)
                            if nums:
                                details['samples_removed'] = int(nums[0])
                        if 'Samples added:' in next_line:
                            nums = re.findall(r'(\d+)', next_line)
                            if nums:
                                details['samples_added'] = int(nums[0])
                        if 'Disparity threshold:' in next_line:
                            nums = re.findall(r'([0-9.]+)', next_line)
                            if nums:
                                details['disparity_threshold'] = float(nums[0])
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
        return self.parsed_data['feature_weights'].get(feature_name, 0.0)
    
    def get_statistical_test(self, feature_name: str) -> Dict:
        return self.parsed_data['statistical_tests'].get(feature_name, {})
    
    def get_all_improvements(self) -> Dict[str, float]:
        return self.parsed_data['improvements']
    
    def get_mitigation_details(self) -> Dict:
        return self.parsed_data['mitigation_details']
    
    def get_executive_summary(self) -> Dict:
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
# VISUALIZATION HANDLER
# ============================================================================
def capture_visualizations(temp_dir: str) -> Dict[str, str]:
    """Capture PNG files and convert to base64"""
    viz_base64 = {}
    if os.path.exists(temp_dir):
        viz_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            viz_files.extend(Path(temp_dir).glob(ext))
        for viz_path in viz_files[:5]:
            try:
                with open(viz_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    viz_base64[viz_path.name] = f'data:image/png;base64,{img_data}'
            except Exception as e:
                current_app.logger.warning(f"Failed to encode {viz_path.name}: {e}")
    return viz_base64

def cleanup_temp_dir(dir_path: str):
    """Cleanup function with 1 hour delay"""
    def cleanup():
        time.sleep(3600)
        try:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    try:
                        os.unlink(os.path.join(dir_path, file))
                    except:
                        pass
                try:
                    os.rmdir(dir_path)
                except:
                    pass
        except:
            pass
    cleanup_thread = threading.Thread(target=cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

# ============================================================================
# END OF PART 1
# CONTINUE WITH PART 2 (generate_html_report function and Flask routes)
# ============================================================================
# ============================================================================
# PART 2 OF 2 - Append this to Part 1
# ============================================================================

# ENHANCED HTML REPORT GENERATOR
def generate_html_report(parser, viz_base64, domain, session_id, pipeline_output, 
                       df, corrected_df, executive_summary, base_url) -> str:
    """Generate comprehensive HTML report matching local pipeline output"""
    
    initial_bias = executive_summary.get('initial_bias', 0)
    final_bias = executive_summary.get('final_bias', initial_bias)
    improvement = executive_summary.get('improvement', 0)
    sig_biases = executive_summary.get('significant_biases', 0)
    records_before = executive_summary.get('records_before', len(df))
    records_after = executive_summary.get('records_after', len(corrected_df))
    retention = executive_summary.get('retention', 100)
    mitigation_details = parser.get_mitigation_details()
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BiasClean Analysis Report - Full Pipeline Results</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1400px; margin: 0 auto; padding: 20px; background: #f5f7fa; }}
        .report-container {{ background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); padding: 30px; margin: 20px auto; }}
        .report-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin: -30px -30px 30px -30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .report-header h1 {{ font-size: 2.2em; margin: 0; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 4px; }}
        .section h2 {{ margin-top: 0; color: #667eea; font-size: 1.5em; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 30px 0; }}
        .metric-card {{ background: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .viz-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin: 30px 0; }}
        .viz-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 3px 10px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
        .viz-card h3 {{ background: #f7fafc; margin: 0; padding: 15px; font-size: 1em; border-bottom: 1px solid #e2e8f0; }}
        .viz-card img {{ width: 100%; height: 300px; object-fit: contain; padding: 15px; background: white; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; border-bottom: 2px solid #5568d3; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
        tr:hover {{ background: #f8f9fa; }}
        .feature-list {{ list-style: none; padding: 0; }}
        .feature-list li {{ padding: 10px; margin: 5px 0; background: white; border-left: 3px solid #667eea; border-radius: 4px; }}
        .improvement-positive {{ color: #27ae60; font-weight: bold; }}
        .improvement-negative {{ color: #e74c3c; font-weight: bold; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }}
        .badge-success {{ background: #c6f6d5; color: #276749; }}
        .badge-danger {{ background: #fed7d7; color: #c53030; }}
        .badge-info {{ background: #bee3f8; color: #2c5282; }}
        pre {{ background: #1a202c; color: #e2e8f0; padding: 20px; border-radius: 6px; overflow-x: auto; font-size: 0.85em; max-height: 500px; overflow-y: auto; line-height: 1.5; }}
        details {{ margin: 20px 0; padding: 15px; background: #f7fafc; border-radius: 6px; border: 1px solid #e2e8f0; }}
        summary {{ cursor: pointer; font-weight: bold; padding: 10px; user-select: none; }}
        summary:hover {{ color: #667eea; }}
        .phase-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #48bb78; }}
        .stat-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .stat-label {{ font-weight: 600; color: #555; }}
        .stat-value {{ color: #667eea; font-weight: bold; }}
        @media print {{ body {{ background: white; }} .report-container {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>🎯 BiasClean Analysis Report</h1>
            <h2>Complete Pipeline Results</h2>
            <p>Domain: {domain.upper()} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card"><div class="metric-value" style="color:#27ae60;">{improvement:.1f}%</div><div>Bias Reduction</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#3498db;">{sig_biases}</div><div>Significant Biases Found</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#9b59b6;">{records_before:,}</div><div>Initial Records</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#e74c3c;">{records_after:,}</div><div>Final Records</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#f39c12;">{retention:.1f}%</div><div>Data Retention</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#e67e22;">{initial_bias:.4f}</div><div>Initial Bias Score</div></div>
                <div class="metric-card"><div class="metric-value" style="color:#27ae60;">{final_bias:.4f}</div><div>Final Bias Score</div></div>
            </div>
        </div>
'''
    
    if viz_base64:
        html += f'<div class="section"><h2>📈 Visual Analysis</h2><p>Generated {len(viz_base64)} visualization(s)</p><div class="viz-grid">'
        for img_name, img_data in viz_base64.items():
            display_name = img_name.replace('.png', '').replace('_', ' ').title()
            html += f'<div class="viz-card"><h3>{display_name}</h3><img src="{img_data}" alt="{display_name}"></div>'
        html += '</div></div>'
    
    html += '<div class="section"><h2>🔬 Statistical Analysis Results</h2><p>Detailed breakdown of bias detection</p><table><thead><tr><th>Feature</th><th>Domain Weight</th><th>p-value</th><th>Statistical Significance</th><th>Improvement</th></tr></thead><tbody>'
    
    feature_weights = parser.parsed_data['feature_weights']
    for feature in sorted(feature_weights.keys(), key=lambda x: feature_weights[x], reverse=True):
        test_data = parser.get_statistical_test(feature)
        imp = parser.get_all_improvements().get(feature, 0)
        p_value = test_data.get('p_value', 1.0) if test_data else 1.0
        significant = test_data.get('significant', False) if test_data else False
        html += f'<tr><td><strong>{feature}</strong></td><td>{feature_weights[feature]:.2f}</td><td>{p_value:.6f}</td><td><span class="badge badge-{"danger" if significant else "success"}">{"⚠️ SIGNIFICANT BIAS" if significant else "✅ NO SIGNIFICANT BIAS"}</span></td><td class="{"improvement-positive" if imp > 0 else "improvement-negative"}">{imp:+.1f}%</td></tr>'
    
    html += '</tbody></table></div>'
    
    if mitigation_details:
        html += '<div class="section"><h2>⚙️ Bias Mitigation Actions Taken</h2><p>Weight-prioritized rebalancing performed:</p>'
        for feature, details in sorted(mitigation_details.items(), key=lambda x: x[1].get('weight', 0), reverse=True):
            samples_removed = details.get('samples_removed', 0)
            samples_added = details.get('samples_added', 0)
            disparity_threshold = details.get('disparity_threshold', 0)
            weight = details.get('weight', 0)
            html += f'<div class="phase-box"><h3>🎯 {feature} (Weight: {weight:.2f})</h3><div class="stat-row"><span class="stat-label">Disparity Threshold:</span><span class="stat-value">{disparity_threshold:.3f}</span></div><div class="stat-row"><span class="stat-label">Samples Removed:</span><span class="stat-value">{samples_removed:,}</span></div><div class="stat-row"><span class="stat-label">Samples Added (SMOTE):</span><span class="stat-value">{samples_added:,}</span></div><div class="stat-row"><span class="stat-label">Net Change:</span><span class="stat-value">{samples_added - samples_removed:+,}</span></div></div>'
        html += '</div>'
    
    html += '<div class="section"><h2>🔍 Features Analyzed (Weight-Prioritized)</h2><ul class="feature-list">'
    for feature in sorted(feature_weights.keys(), key=lambda x: feature_weights[x], reverse=True):
        weight = feature_weights[feature]
        html += f'<li><strong>{feature}</strong> <span class="badge badge-info">Weight: {weight:.2f}</span></li>'
    html += '</ul></div>'
    
    html += f'<div class="section"><h2>📋 Complete Pipeline Execution Log</h2><details open><summary>Click to expand/collapse full console output ({len(pipeline_output.split(chr(10)))} lines)</summary><pre>{pipeline_output}</pre></details></div>'
    
    html += f'''<div style="text-align: center; margin: 40px 0; padding: 30px; background: #f8f9fa; border-radius: 8px;">
            <h3 style="color: #667eea;">📥 Download Options</h3>
            <p style="color: #666; margin-bottom: 20px;">Save this report for your records</p>
            <a href="javascript:window.print()" style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin: 5px;">🖨️ Print Report</a>
            <p style="margin-top: 20px; color: #999; font-size: 0.9em;"><em>This is the complete analysis report. Use your browser's Save or Print functions to keep a copy.</em></p>
        </div>
        <div style="text-align: center; padding: 20px; color: #999; border-top: 2px solid #e2e8f0; margin-top: 40px;">
            <p><strong>BiasClean v2.4</strong> - Universal Bias Detection & Mitigation Pipeline</p>
            <p>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Session ID: {session_id}</p>
        </div>
    </div>
</body>
</html>'''
    return html

# ============================================================================
# FLASK APP CONFIGURATION
# ============================================================================
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/*": {"origins": ["https://ai-fairness.com", "*"]}})
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
BASE_URL = os.environ.get('BASE_URL', 'https://biasclean.onrender.com')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
    return response

@app.route('/')
def index():
    return render_template('upload_biasclean.html')

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV file required'}), 400
        domain = request.form.get('domain', 'justice')
        temp_path = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
        file.save(temp_path)
        try:
            df = pd.read_csv(temp_path)
            app.logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Invalid CSV: {str(e)[:100]}'}), 400
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        viz_temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"viz_{session_id}")
        os.makedirs(viz_temp_dir, exist_ok=True)
        biasclean_results_dir = os.path.join(viz_temp_dir, "biasclean_results")
        app.logger.info(f"Starting pipeline for domain: {domain}")
        os.makedirs = original_makedirs
        try:
            pipeline = UniversalBiasClean(domain=domain)
            original_cwd = os.getcwd()
            os.chdir(viz_temp_dir)
            output_capture = io.StringIO()
            with redirect_stdout(output_capture), redirect_stderr(output_capture):
                results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
            os.chdir(original_cwd)
        finally:
            os.makedirs = safe_makedirs
        pipeline_output = output_capture.getvalue()
        app.logger.info("Pipeline completed successfully")
        parser = PipelineOutputParser(pipeline_output)
        viz_base64 = capture_visualizations(biasclean_results_dir)
        app.logger.info(f"Found {len(viz_base64)} visualizations")
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        executive_summary = parser.get_executive_summary()
        initial_bias = executive_summary.get('initial_bias', diagnostics.get('initial_bias_score', 0))
        final_bias = executive_summary.get('final_bias', diagnostics.get('final_bias_score', initial_bias))
        improvement = executive_summary.get('improvement', ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0)
        sig_biases = executive_summary.get('significant_biases', diagnostics.get('significant_bias_count', 0))
        retention = executive_summary.get('retention', validation.get('data_integrity', {}).get('retention_rate', 100))
        corrected_df = results.get('corrected_df', df)
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        try:
            corrected_df.to_csv(corrected_path, index=False)
            app.logger.info(f"Saved corrected file: {corrected_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save corrected file: {str(e)}")
        report_filename = f"report_{session_id}.html"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        try:
            html_content = generate_html_report(parser, viz_base64, domain, session_id, pipeline_output, df, corrected_df, executive_summary, BASE_URL)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            app.logger.info(f"HTML report saved: {report_path}")
        except Exception as e:
            app.logger.error(f"Failed to save HTML report: {str(e)}")
            traceback.print_exc()
        cleanup_temp_dir(viz_temp_dir)
        response = {
            'detection': {'n_rows': int(len(df)), 'n_columns': int(len(df.columns)), 'significant_biases': int(sig_biases)},
            'removal': {'bias_reduction_percent': float(round(improvement, 1)), 'data_retention_percent': float(round(retention, 1)), 'production_ready': bool(improvement > 5)},
            'files': {'corrected': corrected_filename, 'report': report_filename, 'visualizations': list(viz_base64.keys()), 'report_view_url': f'{BASE_URL}/view/{report_filename}', 'report_download_url': f'{BASE_URL}/download/{report_filename}', 'data_download_url': f'{BASE_URL}/download/{corrected_filename}'},
            'session_id': session_id,
            'report_content': f'Analysis complete. Generated comprehensive HTML report with {len(viz_base64)} visualizations.'
        }
        response = convert_numpy_types(response)
        os.unlink(temp_path)
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Server error', 'details': str(e)[:100]}), 500

@app.route('/view/<filename>', methods=['GET'])
def view_report(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        if filename.endswith('.html'):
            return send_file(file_path, mimetype='text/html', as_attachment=False)
        else:
            return jsonify({'error': 'Only HTML files can be viewed'}), 400
    except Exception as e:
        app.logger.error(f"View error: {str(e)}")
        return jsonify({'error': 'View failed'}), 500

@app.route('/download/<filename>', methods=['GET', 'OPTIONS'])
def download(filename):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        if filename.endswith('.csv'):
            mimetype = 'text/csv'
        elif filename.endswith('.html'):
            mimetype = 'text/html'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        else:
            mimetype = 'application/octet-stream'
        app.logger.info(f"Serving file: {filename}")
        response = send_file(file_path, as_attachment=True, download_name=filename, mimetype=mimetype)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Download failed', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'BiasClean', 'version': '2.4'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)