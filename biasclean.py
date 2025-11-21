from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import os
import uuid
from datetime import datetime
from biasclean_pipeline import (
    biasclean_detect,
    biasclean_remove,
    biasclean_report,
    biasclean_visualize,
    biasclean_validate
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Allowed domains
DOMAINS = [
    'justice', 'health', 'finance', 'education', 
    'hiring', 'business', 'governance'
]

@app.route('/')
def index():
    return render_template('upload_biasclean.html')

@app.route('/biasclean/biasclean-audit', methods=['POST'])
def biasclean_audit():
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get domain from form
        domain = request.form.get('domain', 'health')
        if domain not in DOMAINS:
            return jsonify({'error': 'Invalid domain selected'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Save uploaded file
        input_filename = f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        input_path = os.path.join(upload_dir, input_filename)
        file.save(input_path)
        
        # Step 1: Detect biases
        print(f"🔍 Step 1: Detecting biases for domain: {domain}")
        detect_results = biasclean_detect(input_path, domain)
        
        # Step 2: Remove biases (industry mode)
        print(f"🔄 Step 2: Removing biases using industry mode")
        corrected_filename = f"corrected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        corrected_path = os.path.join(results_dir, corrected_filename)
        
        remove_summary, corrected_file_path = biasclean_remove(
            input_path, 
            domain, 
            mode="industry",
            output_path=corrected_path
        )
        
        # Step 3: Generate report
        print(f"📊 Step 3: Generating comprehensive report")
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(results_dir, report_filename)
        
        biasclean_report(
            input_path,
            domain,
            mode="industry",
            report_path=report_path,
            corrected_path=corrected_file_path
        )
        
        # Step 4: Generate visualizations
        print(f"🎨 Step 4: Creating visualizations")
        viz_dir = os.path.join(results_dir, "visualizations")
        
        biasclean_visualize(
            input_path,
            corrected_file_path,
            domain,
            output_dir=viz_dir
        )
        
        # Step 5: Comprehensive validation
        print(f"✅ Step 5: Running industry validation")
        validation_filename = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        validation_path = os.path.join(results_dir, validation_filename)
        
        biasclean_validate(
            input_path,
            corrected_file_path,
            domain,
            validation_path=validation_path
        )
        
        # Read report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # Prepare response
        response_data = {
            'session_id': session_id,
            'domain': domain,
            'detection': detect_results,
            'removal': remove_summary,
            'report_content': report_content,
            'files': {
                'input': input_filename,
                'corrected': corrected_filename,
                'report': report_filename,
                'validation': validation_filename
            },
            'visualizations': os.listdir(viz_dir) if os.path.exists(viz_dir) else []
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in biasclean audit: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/biasclean/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """Download result files"""
    try:
        file_path = os.path.join(app.config['RESULTS_FOLDER'], session_id, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/biasclean/visualization/<session_id>/<viz_filename>')
def get_visualization(session_id, viz_filename):
    """Serve visualization images"""
    try:
        viz_path = os.path.join(app.config['RESULTS_FOLDER'], session_id, 'visualizations', viz_filename)
        if os.path.exists(viz_path):
            return send_file(viz_path)
        else:
            return jsonify({'error': 'Visualization not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)