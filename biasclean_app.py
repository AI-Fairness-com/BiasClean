"""
Flask Web Wrapper for Universal BiasClean Pipeline - biasclean_app.py
Production Deployment for Render.com
Fixed: Returns complete pipeline results for frontend display
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
app.config['RESULTS_FOLDER'] = 'biasclean_results'

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('upload_biasclean.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process CSV file and run bias analysis - RETURNS COMPLETE RESULTS"""
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

        # Initialize pipeline
        pipeline = UniversalBiasClean(domain=domain)

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
            # Create results directory
            results_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
            os.makedirs(results_dir, exist_ok=True)
            
            # Save corrected dataset
            corrected_filename = f"biasclean_corrected_{session_id}.csv"
            corrected_path = os.path.join(results_dir, corrected_filename)
            corrected_df.to_csv(corrected_path, index=False)
            download_url = f"/download/{session_id}/{corrected_filename}"
            
            # Save pipeline results
            results_filename = f"pipeline_results_{session_id}.json"
            results_path = os.path.join(results_dir, results_filename)
            with open(results_path, 'w') as f:
                json.dump({
                    'diagnostics': results.get('diagnostics', {}),
                    'validation': results.get('validation', {}),
                    'mappings': results.get('mappings', {})
                }, f, default=str)
        else:
            download_url = None
            corrected_filename = None

        # Extract ALL metrics for response
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        feature_tests = diagnostics.get('feature_tests', {})

        initial_bias = diagnostics.get('initial_bias_score', 0)
        final_bias = diagnostics.get('final_bias_score', initial_bias)
        improvement = ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0

        # Get biased features with details
        biased_features = []
        bias_details = []
        for feature, test in feature_tests.items():
            if test.get('significant_bias', False):
                biased_features.append(feature)
                bias_details.append({
                    'feature': feature,
                    'p_value': test.get('p_value', 1.0),
                    'weight': DOMAIN_CONFIGS[domain]['weights'].get(feature, 0.05)
                })

        # Calculate fairness improvements
        fairness_improvements = validation.get('fairness_improvement', {})
        improvement_details = []
        for feature, imp_value in fairness_improvements.items():
            improvement_details.append({
                'feature': feature,
                'improvement_percent': imp_value,
                'weight': DOMAIN_CONFIGS[domain]['weights'].get(feature, 0.05)
            })

        # Clean up uploaded file
        os.unlink(temp_file.name)

        # RETURN COMPLETE RESULTS FOR FRONTEND
        return jsonify({
            'success': True,
            'domain': domain,
            'domain_name': DOMAIN_CONFIGS[domain]['report_labels']['domain'],
            'records_processed': len(df),
            'columns_analyzed': len(df.columns),
            
            # Bias metrics
            'initial_bias': round(initial_bias, 4),
            'final_bias': round(final_bias, 4),
            'improvement': round(improvement, 1),
            'significant_biases': len(biased_features),
            'biased_features': biased_features,
            'bias_details': bias_details,
            
            # Data integrity
            'data_retention': round(validation.get('data_integrity', {}).get('retention_rate', 100), 1),
            'records_before': validation.get('data_integrity', {}).get('records_before', len(df)),
            'records_after': validation.get('data_integrity', {}).get('records_after', len(corrected_df) if corrected_df is not None else len(df)),
            
            # Fairness improvements
            'fairness_improvements': improvement_details,
            
            # Files for download
            'download_url': download_url,
            'session_id': session_id,
            'files': {
                'corrected': corrected_filename,
                'report': f'biasclean_report_{session_id}.html',
                'validation': f'validation_{session_id}.json'
            },
            
            # Additional info
            'target_column': results.get('target_column', 'auto-detected'),
            'features_analyzed': list(results.get('feature_map', {}).keys()),
            'timestamp': datetime.now().isoformat(),
            
            # For frontend display
            'detection': {
                'n_rows': len(df),
                'n_columns': len(df.columns),
                'significant_biases': len(biased_features)
            },
            'removal': {
                'bias_reduction_percent': round(improvement, 1),
                'data_retention_percent': round(validation.get('data_integrity', {}).get('retention_rate', 100), 1),
                'production_ready': improvement > 5  # More than 5% improvement
            },
            'report_content': f'Bias analysis complete. {len(biased_features)} significant biases found and mitigated.'
        })

    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_file' in locals() and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            
        return jsonify({
            'error': 'Pipeline execution failed',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/download/<session_id>/<filename>', methods=['GET'])
def download(session_id, filename):
    """Serve files for download from session directory"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, filename)

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'File not found',
                'details': 'The requested file has expired or was deleted'
            }), 404

        # Security check
        if not filename.lower().endswith(('.csv', '.json', '.html')):
            return jsonify({
                'error': 'Invalid file type'
            }), 400

        # Determine content type
        if filename.lower().endswith('.csv'):
            mimetype = 'text/csv'
            download_name = f"biasclean_corrected_{session_id}.csv"
        elif filename.lower().endswith('.json'):
            mimetype = 'application/json'
            download_name = f"biasclean_results_{session_id}.json"
        else:
            mimetype = 'text/html'
            download_name = f"biasclean_report_{session_id}.html"

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
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


# ============================================================================
# SCHEDULED CLEANUP
# ============================================================================

def cleanup_old_files(max_age_hours=1):
    """Remove old uploaded files"""
    try:
        now = datetime.now().timestamp()
        upload_dir = app.config['UPLOAD_FOLDER']
        
        if not os.path.exists(upload_dir):
            return
            
        for item in os.listdir(upload_dir):
            item_path = os.path.join(upload_dir, item)
            
            # Check if it's a file or directory
            if os.path.isdir(item_path) and item.startswith('202'):
                # Session directory
                dir_age = now - os.path.getmtime(item_path)
                if dir_age > (max_age_hours * 3600):
                    import shutil
                    shutil.rmtree(item_path)
                    print(f"Cleaned up session directory: {item}")
            elif os.path.isfile(item_path) and item.startswith('biasclean_'):
                # Individual file
                file_age = now - os.path.getmtime(item_path)
                if file_age > (max_age_hours * 3600):
                    os.unlink(item_path)
                    print(f"Cleaned up file: {item}")
                    
    except Exception as e:
        print(f"Cleanup error: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Run cleanup on startup
    cleanup_old_files()

    # Start Flask server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
