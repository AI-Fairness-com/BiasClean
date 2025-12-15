# -*- coding: utf-8 -*-
"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com with CORS Support
ENHANCED: Captures full pipeline console output for comprehensive reporting
ENHANCED: HTML report with embedded visualizations (FIXED VERSION)
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
import shutil
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
# VISUALIZATION MANAGER
# ============================================================================
class VisualizationManager:
    """Manages visualization capture, embedding, and cleanup"""
    
    @staticmethod
    def capture_pipeline_visualizations(pipeline, temp_dir: str):
        """Redirect pipeline to save visualizations to temp directory"""
        original_results_dir = None
        if hasattr(pipeline, 'results_dir'):
            original_results_dir = pipeline.results_dir
            pipeline.results_dir = temp_dir
        
        # Enable visualization methods if they exist
        if hasattr(pipeline, 'viz'):
            # Re-enable visualization methods
            if hasattr(pipeline.viz, '_save_figure'):
                original_viz_save = pipeline.viz._save_figure
                pipeline.viz._save_figure = lambda fig, filename: VisualizationManager._save_viz_to_temp(fig, filename, temp_dir)
        
        return original_results_dir
    
    @staticmethod
    def _save_viz_to_temp(fig, filename, temp_dir):
        """Save figure to temp directory"""
        import matplotlib.pyplot as plt
        filepath = os.path.join(temp_dir, filename)
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    @staticmethod
    def collect_visualizations(temp_dir: str) -> Dict[str, str]:
        """Collect and encode visualizations from temp directory"""
        viz_base64 = {}
        
        if os.path.exists(temp_dir):
            viz_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.svg']:
                viz_files.extend(Path(temp_dir).glob(ext))
            
            # Look for expected visualization filenames from biasclean_7
            expected_files = [
                'disparity_comparison.png',
                'fairness_improvements.png', 
                'data_integrity.png',
                'bias_score_comparison.png',
                'feature_weights.png'
            ]
            
            # First try expected files
            for filename in expected_files:
                filepath = os.path.join(temp_dir, filename)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'rb') as f:
                            img_data = base64.b64encode(f.read()).decode('utf-8')
                            viz_base64[filename] = f'data:image/png;base64,{img_data}'
                    except Exception as e:
                        print(f"Warning: Failed to encode {filename}: {e}")
            
            # Fallback: encode any PNG files found
            if not viz_base64:
                for viz_path in viz_files[:3]:  # Limit to 3 graphs
                    try:
                        with open(viz_path, 'rb') as f:
                            img_data = base64.b64encode(f.read()).decode('utf-8')
                            viz_base64[viz_path.name] = f'data:image/png;base64,{img_data}'
                    except Exception as e:
                        print(f"Warning: Failed to encode {viz_path.name}: {e}")
        
        return viz_base64
    
    @staticmethod
    def generate_html_report(parser, viz_base64, domain, session_id, corrected_filename, 
                           pipeline_output, df, corrected_df, executive_summary) -> str:
        """Generate comprehensive HTML report"""
        
        # Extract metrics
        initial_bias = executive_summary.get('initial_bias', 0)
        final_bias = executive_summary.get('final_bias', initial_bias)
        improvement = executive_summary.get('improvement', 0)
        sig_biases = executive_summary.get('significant_biases', 0)
        records_before = executive_summary.get('records_before', len(df))
        records_after = executive_summary.get('records_after', len(corrected_df))
        retention = executive_summary.get('retention', 100)
        
        # Generate HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BiasClean Analysis Report</title>
    <style>
        /* Professional Styling */
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .report-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            margin: 30px auto;
            padding: 40px;
        }}
        
        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            margin: -40px -40px 40px -40px;
            border-bottom: 5px solid #4a5568;
            text-align: center;
        }}
        
        .report-header h1 {{
            font-size: 2.8em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .report-header p {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid #e2e8f0;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #4a5568;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .visualization-section {{
            margin: 50px 0;
        }}
        
        .visualization-section h2 {{
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        .viz-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }}
        
        .viz-card {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .viz-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }}
        
        .viz-card h3 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 15px;
            font-size: 1.1em;
        }}
        
        .viz-card img {{
            width: 100%;
            height: 250px;
            object-fit: contain;
            padding: 15px;
            background: #f7fafc;
        }}
        
        .data-section {{
            margin: 50px 0;
        }}
        
        .data-section h2 {{
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        .feature-table {{
            width: 100%;
            border-collapse: collapse;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .feature-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .feature-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .feature-table tbody tr {{
            border-bottom: 1px solid #e2e8f0;
            transition: background 0.3s ease;
        }}
        
        .feature-table tbody tr:hover {{
            background: #f7fafc;
        }}
        
        .feature-table td {{
            padding: 15px;
        }}
        
        .significance-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .significant {{
            background: #fed7d7;
            color: #c53030;
            border: 2px solid #fc8181;
        }}
        
        .not-significant {{
            background: #c6f6d5;
            color: #276749;
            border: 2px solid #68d391;
        }}
        
        .improvement-positive {{
            color: #276749;
            font-weight: bold;
        }}
        
        .improvement-negative {{
            color: #c53030;
            font-weight: bold;
        }}
        
        .download-section {{
            background: #f7fafc;
            border-radius: 10px;
            padding: 30px;
            margin: 50px 0;
            text-align: center;
            border: 2px dashed #cbd5e0;
        }}
        
        .download-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            margin: 10px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .download-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
        }}
        
        .pipeline-log {{
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-top: 50px;
            border: 1px solid #e2e8f0;
        }}
        
        .pipeline-log summary {{
            cursor: pointer;
            font-weight: bold;
            color: #4a5568;
            padding: 10px;
            background: #edf2f7;
            border-radius: 5px;
        }}
        
        .pipeline-log pre {{
            background: #1a202c;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .no-visualizations {{
            text-align: center;
            padding: 40px;
            background: #f7fafc;
            border-radius: 10px;
            border: 2px dashed #cbd5e0;
            color: #4a5568;
        }}
        
        @media (max-width: 768px) {{
            .report-container {{
                padding: 20px;
            }}
            
            .report-header {{
                padding: 20px;
                margin: -20px -20px 20px -20px;
            }}
            
            .report-header h1 {{
                font-size: 2em;
            }}
            
            .viz-grid {{
                grid-template-columns: 1fr;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>BiasClean Analysis Report</h1>
            <p>Domain: {domain.upper()} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <!-- Executive Summary -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" style="color:#27ae60;">{improvement:.1f}%</div>
                <div class="metric-label">Bias Reduction</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#3498db;">{sig_biases}</div>
                <div class="metric-label">Significant Biases</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#9b59b6;">{records_before:,}</div>
                <div class="metric-label">Initial Records</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#e74c3c;">{records_after:,}</div>
                <div class="metric-label">Final Records</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#f39c12;">{retention:.1f}%</div>
                <div class="metric-label">Data Retention</div>
            </div>
        </div>
'''
        
        # Add visualizations section
        if viz_base64:
            html += f'''
        <!-- Visualizations -->
        <div class="visualization-section">
            <h2>Visual Analysis ({len(viz_base64)} graphs generated)</h2>
            <div class="viz-grid">
'''
            
            for img_name, img_data in viz_base64.items():
                display_name = img_name.replace('.png', '').replace('_', ' ').title()
                html += f'''
                <div class="viz-card">
                    <h3>{display_name}</h3>
                    <img src="{img_data}" alt="{display_name}">
                </div>
'''
            
            html += '''
            </div>
        </div>
'''
        else:
            html += '''
        <!-- No Visualizations Message -->
        <div class="visualization-section">
            <h2>Visual Analysis</h2>
            <div class="no-visualizations">
                <p>⚠️ No visualizations were generated by the pipeline.</p>
                <p>The pipeline console output is available below for debugging.</p>
            </div>
        </div>
'''
        
        # Add statistical data
        html += f'''
        <!-- Statistical Analysis -->
        <div class="data-section">
            <h2>Statistical Analysis</h2>
            <table class="feature-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Weight</th>
                        <th>p-value</th>
                        <th>Status</th>
                        <th>Improvement</th>
                    </tr>
                </thead>
                <tbody>
'''
        
        # Populate table from parser
        feature_weights = parser.parsed_data['feature_weights']
        for feature in feature_weights:
            test_data = parser.get_statistical_test(feature)
            imp = parser.get_all_improvements().get(feature, 0)
            p_value = test_data.get('p_value', 1.0) if test_data else 1.0
            significant = test_data.get('significant', False) if test_data else False
            
            html += f'''
                    <tr>
                        <td><strong>{feature}</strong></td>
                        <td>{feature_weights[feature]:.2f}</td>
                        <td>{p_value:.6f}</td>
                        <td><span class="significance-badge {'significant' if significant else 'not-significant'}">
                            {'SIGNIFICANT' if significant else 'OK'}
                        </span></td>
                        <td class="{'improvement-positive' if imp > 0 else 'improvement-negative'}">
                            {imp:+.1f}%
                        </td>
                    </tr>
'''
        
        # Close table and add download section
        html += f'''
                </tbody>
            </table>
        </div>
        
        <!-- Download Section (ONLY HTML REPORT) -->
        <div class="download-section">
            <h3>Download Full Analysis Report</h3>
            <a href="/download/report_{session_id}.html" class="download-btn">📈 Download Full Analysis Report (HTML)</a>
            <p style="margin-top: 15px; color: #4a5568; font-size: 0.9em;">
                <em>Note: Download the cleaned dataset from the main results page using the CSV button.</em>
            </p>
        </div>
        
        <!-- Include pipeline output for reference -->
        <details class="pipeline-log">
            <summary>View Full Pipeline Execution Log</summary>
            <pre>{pipeline_output[:10000]}</pre>
        </details>
    </div>
</body>
</html>'''
        
        return html
    
    @staticmethod
    def cleanup_temp_dir(dir_path: str, delay_seconds: int = 3600):
        """Clean up temporary directory after specified delay"""
        def cleanup():
            time.sleep(delay_seconds)
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
                    print(f"Cleaned up temp directory: {dir_path}")
            except Exception as e:
                print(f"Warning: Failed to cleanup {dir_path}: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()

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
        
        # RUN PIPELINE WITH VISUALIZATION CAPTURE
        app.logger.info(f"Starting pipeline for domain: {domain}")
        
        # Create temp directory for visualizations
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        viz_temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"viz_{session_id}")
        os.makedirs(viz_temp_dir, exist_ok=True)
        app.logger.info(f"Created visualization temp directory: {viz_temp_dir}")
        
        # Initialize pipeline
        pipeline = UniversalBiasClean(domain=domain)
        
        # Capture pipeline visualizations
        original_results_dir = VisualizationManager.capture_pipeline_visualizations(pipeline, viz_temp_dir)
        
        # CAPTURE ALL CONSOLE OUTPUT
        output_capture = io.StringIO()
        with redirect_stdout(output_capture), redirect_stderr(output_capture):
            results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
        
        pipeline_output = output_capture.getvalue()
        app.logger.info("Pipeline completed successfully")
        app.logger.info(f"Captured {len(pipeline_output)} characters of console output")
        
        # Restore original directory if needed
        if original_results_dir and hasattr(pipeline, 'results_dir'):
            pipeline.results_dir = original_results_dir
        
        # PARSE THE CAPTURED OUTPUT
        parser = PipelineOutputParser(pipeline_output)
        
        # COLLECT GENERATED VISUALIZATIONS
        viz_base64 = VisualizationManager.collect_visualizations(viz_temp_dir)
        app.logger.info(f"Collected {len(viz_base64)} visualizations")
        
        # Extract metrics
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        executive_summary = parser.get_executive_summary()
        
        # Use parsed data where available
        initial_bias = executive_summary.get('initial_bias', diagnostics.get('initial_bias_score', 0))
        final_bias = executive_summary.get('final_bias', diagnostics.get('final_bias_score', initial_bias))
        improvement = executive_summary.get('improvement', 
            ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0)
        sig_biases = executive_summary.get('significant_biases', diagnostics.get('significant_bias_count', 0))
        retention = executive_summary.get('retention', 
            validation.get('data_integrity', {}).get('retention_rate', 100))
        
        # Save corrected file
        corrected_df = results.get('corrected_df', df)
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        
        try:
            corrected_df.to_csv(corrected_path, index=False)
            app.logger.info(f"Saved corrected file: {corrected_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save corrected file: {str(e)}")
        
        # GENERATE HTML REPORT
        report_filename = f"report_{session_id}.html"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        try:
            html_report = VisualizationManager.generate_html_report(
                parser=parser,
                viz_base64=viz_base64,
                domain=domain,
                session_id=session_id,
                corrected_filename=corrected_filename,
                pipeline_output=pipeline_output,
                df=df,
                corrected_df=corrected_df,
                executive_summary=executive_summary
            )
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            app.logger.info(f"Saved HTML report file: {report_filename}")
            
        except Exception as e:
            app.logger.error(f"Failed to save HTML report: {str(e)}")
            traceback.print_exc()
            # Fallback to simple report
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
                    f.write(f"Significant biases found: {sig_biases}\n")
                    f.write(f"Visualizations generated: {len(viz_base64)}\n")
            except Exception as e2:
                app.logger.error(f"Failed to save even simple report: {str(e2)}")
        
        # CLEANUP TEMP DIRECTORY
        VisualizationManager.cleanup_temp_dir(viz_temp_dir)
        
        # Return response
        response = {
            'detection': {
                'n_rows': int(len(df)),
                'n_columns': int(len(df.columns)),
                'significant_biases': int(sig_biases)
            },
            'removal': {
                'bias_reduction_percent': float(round(improvement, 1)),
                'data_retention_percent': float(round(retention, 1)),
                'production_ready': bool(improvement > 5)
            },
            'files': {
                'corrected': corrected_filename,
                'report': report_filename,
                'visualizations': list(viz_base64.keys())
            },
            'session_id': session_id,
            'report_content': f'Analysis complete. Generated HTML report with {len(viz_base64)} visualizations.'
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
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        # Determine MIME type
        if filename.endswith('.csv'):
            mimetype = 'text/csv'
        elif filename.endswith('.html'):
            mimetype = 'text/html'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        else:
            mimetype = 'text/plain'
        
        app.logger.info(f"Serving file: {filename} ({mimetype})")
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'BiasClean', 'version': '2.3'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)