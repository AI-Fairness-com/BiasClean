"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com
Fixed: Disables local file saving to work on Render's filesystem
"""

import os
import json
import tempfile
import traceback
from datetime import datetime
from typing import Dict, Any

import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file

# Import your pipeline
from biasclean_7 import UniversalBiasClean, DOMAIN_CONFIGS

# ============================================================================
# FLASK APP CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
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
    """Process CSV file and run bias analysis"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded',
                'details': 'Please select a CSV file'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'details': 'Please select a CSV file'
            }), 400

        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'error': 'Invalid file type',
                'details': 'Please upload a CSV file'
            }), 400

        # Get parameters
        domain = request.form.get('domain', 'justice')
        target_column = request.form.get('target_column', None)
        if target_column == '':
            target_column = None

        threshold = request.form.get('threshold', '0.80')
        try:
            threshold = float(threshold)
            threshold = max(0.0, min(1.0, threshold))
        except ValueError:
            threshold = 0.80

        # Save uploaded file
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.csv',
            delete=False,
            dir=app.config['UPLOAD_FOLDER']
        )
        file.save(temp_file.name)
        temp_file.close()

        # Read CSV
        try:
            df = pd.read_csv(temp_file.name)
        except Exception as e:
            os.unlink(temp_file.name)
            return jsonify({
                'error': 'Failed to read CSV file',
                'details': str(e)
            }), 400

        # Initialize pipeline - WITH FIX
        pipeline = UniversalBiasClean(domain=domain)
        
        # CRITICAL FIX: Disable local file saving on Render
        os.environ['BIASCLEAN_DISABLE_SAVE'] = '1'

        # Process dataset
        results = pipeline.process_dataset(
            df=df,
            target_column=target_column,
            auto_approve_threshold=threshold
        )

        # Generate corrected dataset file
        corrected_df = results.get('corrected_df')
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if corrected_df is not None:
            # Save corrected dataset to temp location
            corrected_filename = f"biasclean_corrected_{session_id}.csv"
            corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
            corrected_df.to_csv(corrected_path, index=False)
            download_url = f"/download/{corrected_filename}"
        else:
            download_url = None
            corrected_filename = None

        # Extract key metrics
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        feature_tests = diagnostics.get('feature_tests', {})

        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0

        # Get biased features
        biased_features = []
        for feature, test in feature_tests.items():
            if test.get('significant_bias', False):
                biased_features.append(feature)

        # Clean up uploaded file
        os.unlink(temp_file.name)

        # Return results
        return jsonify({
            'success': True,
            'domain': domain,
            'records_processed': len(df),
            'columns_analyzed': len(df.columns),
            'initial_bias': round(initial_bias, 4),
            'final_bias': round(final_bias, 4),
            'improvement': round(improvement, 1),
            'significant_biases': len(biased_features),
            'biased_features': biased_features,
            'data_retention': round(validation.get('data_integrity', {}).get('retention_rate', 100), 1),
            'download_url': download_url,
            'session_id': session_id,
            'files': {
                'corrected': corrected_filename if corrected_filename else 'biasclean_corrected.csv'
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        # Clean up temp files
        if 'temp_file' in locals() and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            
        return jsonify({
            'error': 'Pipeline execution failed',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    """Serve corrected dataset for download"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'File not found',
                'details': 'The requested file has expired or was deleted'
            }), 404

        # Security check
        if not filename.lower().endswith('.csv'):
            return jsonify({
                'error': 'Invalid file type'
            }), 400

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"biasclean_corrected_{datetime.now().strftime('%Y%m%d')}.csv",
            mimetype='text/csv'
        )

    except Exception as e:
        return jsonify({
            'error': 'Download failed',
            'details': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Universal BiasClean v2.1',
        'domains_available': list(DOMAIN_CONFIGS.keys())
    })


def cleanup_old_files(max_age_hours=1):
    """Remove old uploaded files"""
    try:
        now = datetime.now().timestamp()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith('biasclean_'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_age = now - os.path.getmtime(filepath)
                if file_age > (max_age_hours * 3600):
                    os.unlink(filepath)
    except Exception:
        pass


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    cleanup_old_files()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
