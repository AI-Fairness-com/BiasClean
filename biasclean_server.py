#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiasClean v3.0 Web Server
=========================
Minimal Flask server to serve the HTML interface and process BiasClean pipeline.

Usage:
    python biasclean_server.py

Then open: http://localhost:5010
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
import json
from datetime import datetime
import traceback

# Import the BiasClean pipeline.
# NOTE: this must match the actual pipeline filename sitting alongside
# this server file. As of v3.10.1 that file is
# biasclean_v3_5_1_terminal.py (the name is a historical artifact from
# early versioning, not a "3.5.1" release) -- this import previously
# pointed at 'biasclean_v3_terminal', a name that does not match any
# pipeline file this project has actually shipped, meaning this server
# (last touched when the pipeline was v3 -> v3.5.1) may never have been
# runnable against the real pipeline in its current form. If the
# pipeline file is ever renamed, this import must be updated to match --
# a silent ModuleNotFoundError here means requests will fail at import
# time before this server even starts.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from biasclean_v3_5_1_terminal import UniversalBiasClean, smart_read_csv
import pandas as pd

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'biasclean_results'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Store HTML template path
HTML_TEMPLATE_PATH = 'biasclean_v3_render.html'

@app.route('/')
def index():
    """Serve the main HTML interface"""
    try:
        with open(HTML_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Error: HTML template not found</h1>
        <p>Please ensure 'biasclean_v3_render.html' is in the same directory as this server.</p>
        """, 404

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle the BiasClean analysis request"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate CSV file
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Get form parameters
        domain = request.form.get('domain', 'justice')
        target_column = request.form.get('target_column', '').strip()
        mode = request.form.get('mode', 'audit_first')
        enable_svm = request.form.get('enable_svm', 'false').lower() == 'true'

        # Required as of pipeline v3.10.1 -- BiasClean does not
        # auto-detect the target/outcome column (see that version's
        # changelog for why: no column-name pattern or statistic can
        # substitute for knowing what a dataset actually measures). The
        # HTML form already enforces this client-side, but /analyze can
        # be called directly, so it's enforced here too rather than
        # relying solely on the pipeline's own ValueError (which would
        # otherwise be caught below and returned as a generic 500).
        if not target_column:
            return jsonify({
                'error': 'Target column is required',
                'details': (
                    "BiasClean does not auto-detect the outcome/target "
                    "column. Only you know what this dataset measures "
                    "(e.g. which column records whether an applicant "
                    "received a callback, a loan was approved, or a "
                    "defendant reoffended). Please specify target_column."
                )
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(upload_path)
        
        print(f"\n{'='*80}")
        print(f"Processing: {filename}")
        print(f"Domain: {domain}")
        print(f"Mode: {mode}")
        print(f"Target: {target_column}")
        print(f"SVM: {enable_svm}")
        print(f"{'='*80}\n")
        
        # Load CSV -- delimiter-auto-detecting (see smart_read_csv in the
        # pipeline module for why: a plain pd.read_csv would silently
        # collapse a semicolon-delimited file like the real UCI
        # bank-full.csv into one garbage column instead of erroring).
        try:
            df = smart_read_csv(upload_path)
        except ValueError as e:
            return jsonify({
                'error': 'Could not parse this CSV',
                'details': str(e)
            }), 400
        
        # Initialize pipeline
        pipeline = UniversalBiasClean(
            domain=domain,
            mode=mode,
            enable_svm=enable_svm
        )
        
        # Process dataset
        results = pipeline.process_dataset(
            df=df,
            target_column=target_column,
            auto_approve_threshold=0.80
        )
        
        # Extract key metrics for JSON response
        response_data = {
            'success': True,
            'mode': mode,
            'svm_enabled': enable_svm,
            'timestamp': timestamp
        }
        
        # Extract audit results if available. The pipeline returns
        # 'audit' only when mode == audit_only, or when audit_first was
        # BLOCKED (RED) -- in both cases no mitigation ran. Otherwise
        # (audit_first that passed, which still runs an audit) it's
        # under 'v3_audit' instead. Legacy mode has no audit step at
        # all, so neither key will be present for it.
        audit = results.get('audit') or results.get('v3_audit')
        if audit:
            recommendation = audit.get('recommendation', {})

            # Determine audit status from traffic light
            traffic_light = recommendation.get('traffic_light', '🟡 YELLOW')
            if '🟢' in traffic_light or 'GREEN' in traffic_light.upper():
                audit_status = 'GREEN'
            elif '🔴' in traffic_light or 'RED' in traffic_light.upper():
                audit_status = 'RED'
            else:
                audit_status = 'YELLOW'

            response_data.update({
                'audit_status': audit_status,
                'audit_score': audit.get('baseline_fairness', {}).get('aggregate_bias', 0),
                'vulnerable_groups': audit.get('vulnerable_subgroups', {}).get('count', 0),
                'recommendation': recommendation.get('action', 'Review required'),
                'bias_score': audit.get('baseline_fairness', {}).get('aggregate_bias', 0)
            })

        # Extract mitigation results if available. There is no
        # top-level 'mitigation' key anywhere in the pipeline's output
        # -- the real before/after numbers live under 'diagnostics'
        # and 'validation' at the top level of results. This previously
        # meant bias_reduction/data_retention/significant_biases always
        # silently fell back to their defaults (0.0%, 100%, 0) for
        # every run that actually performed mitigation.
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})

        if diagnostics:
            initial_score = diagnostics.get('initial_bias_score', 0)
            final_score = diagnostics.get('final_bias_score', initial_score)

            if initial_score > 0:
                bias_reduction = ((initial_score - final_score) / initial_score) * 100
            else:
                bias_reduction = 0

            response_data['bias_reduction'] = f"{bias_reduction:.1f}"
            response_data['significant_biases'] = str(diagnostics.get('significant_bias_count', 0))

        if validation:
            integrity = validation.get('data_integrity', {})
            if integrity:
                response_data['data_retention'] = f"{integrity.get('retention_rate', 100):.1f}"
        
        # Default values if not present
        response_data.setdefault('bias_reduction', '0.0')
        response_data.setdefault('data_retention', '100.0')
        response_data.setdefault('significant_biases', '0')
        response_data.setdefault('vulnerable_groups', '0')
        
        # Find generated files. v3.1 consolidation: the pipeline now
        # writes exactly 3 files instead of the previous 11+ spread
        # across biasclean_results/ and biasclean_results/v27_exports/
        # (biasclean_report.html, GOVERNANCE_REPORT.txt, 3 chart PNGs,
        # pipeline_summary.json, feature_mappings.json, and 6 more JSON
        # files) -- see UniversalBiasClean._save_results and
        # ReportGenerator.generate_report in biasclean_v3_terminal.py.
        results_dir = app.config['RESULTS_FOLDER']
        files = {}

        for file_type, pattern in [
            ('report', 'report.pdf'),
            ('corrected', 'corrected_dataset.csv'),
            ('audit_trail', 'audit_trail.json'),
        ]:
            file_path = os.path.join(results_dir, pattern)
            if os.path.exists(file_path):
                files[file_type] = pattern

        response_data['files'] = files
        
        print(f"\n✅ Analysis complete!")
        print(f"Audit Status: {response_data.get('audit_status', 'N/A')}")
        print(f"Bias Reduction: {response_data.get('bias_reduction', 'N/A')}%")
        print(f"{'='*80}\n")
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve generated result files for download"""
    try:
        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("BiasClean v3.0 Web Server")
    print("="*80)
    print(f"\n🌐 Starting server on http://localhost:5010")
    print(f"\n📂 Upload folder: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    print(f"📂 Results folder: {os.path.abspath(app.config['RESULTS_FOLDER'])}")
    print(f"\n✨ Open your browser and navigate to: http://localhost:5010")
    print(f"\n⚠️  Press CTRL+C to stop the server")
    print("="*80 + "\n")
    
    app.run(host='127.0.0.1', port=5010, debug=True)
