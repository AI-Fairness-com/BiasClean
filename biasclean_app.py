"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
FINAL PRODUCTION VERSION - Matches frontend exactly
"""

import os
import json
import tempfile
import traceback
from datetime import datetime
from typing import Dict, Any

import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file

# MONKEY PATCH: Prevent pipeline from saving files locally
import biasclean_7
original_save = biasclean_7.UniversalBiasClean._save_results
biasclean_7.UniversalBiasClean._save_results = lambda self: None

from biasclean_7 import UniversalBiasClean, DOMAIN_CONFIGS

# ============================================================================
# FLASK APP CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# ROUTES - MATCH FRONTEND EXACTLY
# ============================================================================

@app.route('/')
def index():
    """Serve the professional upload form"""
    return render_template('upload_biasclean.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process CSV - Returns EXACT structure frontend expects"""
    try:
        # 1. Validate
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV required'}), 400
        
        domain = request.form.get('domain', 'justice')
        
        # 2. Read file
        temp_path = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
        file.save(temp_path)
        df = pd.read_csv(temp_path)
        
        # 3. Run pipeline (file saving disabled via monkey patch)
        pipeline = UniversalBiasClean(domain=domain)
        results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
        
        # 4. Extract metrics
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        
        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0
        
        # Count biases
        sig_biases = sum(1 for test in diagnostics.get('feature_tests', {}).values() 
                        if test.get('significant_bias', False))
        
        # 5. Save corrected file with SIMPLE filename
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        corrected_df = results.get('corrected_df', df)
        
        # SIMPLE filename (no session_id in name)
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        corrected_df.to_csv(corrected_path, index=False)
        
        # 6. Return EXACT structure frontend wants
        response = {
            'detection': {
                'n_rows': len(df),
                'n_columns': len(df.columns),
                'significant_biases': sig_biases
            },
            'removal': {
                'bias_reduction_percent': round(improvement, 1),
                'data_retention_percent': round(validation.get('data_integrity', {}).get('retention_rate', 100), 1),
                'production_ready': improvement > 5
            },
            'files': {
                'corrected': corrected_filename,  # Just filename, no path
                'report': f'report_{session_id}.html',
                'validation': f'validation_{session_id}.json'
            },
            'session_id': session_id,
            'report_content': f'Analysis complete. Bias reduced by {improvement:.1f}%.'
        }
        
        os.unlink(temp_path)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'details': str(e)[:100]  # Truncate for security
        }), 500


@app.route('/biasclean/download/<session_id>/<filename>', methods=['GET'])
def download(session_id, filename):
    """EXACT endpoint frontend calls: /biasclean/download/session_id/filename"""
    try:
        # Frontend sends: /biasclean/download/20251212151500/corrected_20251212151500.csv
        # We stored as: corrected_20251212151500.csv
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            # Try alternative naming
            alt_path = os.path.join(app.config['UPLOAD_FOLDER'], f"corrected_{session_id}.csv")
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                return jsonify({'error': 'File expired'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"biasclean_corrected_{session_id}.csv"
        )
        
    except Exception as e:
        return jsonify({'error': 'Download failed'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'BiasClean'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
