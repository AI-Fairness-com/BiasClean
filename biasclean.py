from flask import Flask, request, jsonify, render_template, send_file, session
import pandas as pd
import os
import uuid
import secrets
from datetime import datetime
from biasclean_pipeline import (
    biasclean_detect,
    biasclean_remove,
    biasclean_report,
    biasclean_visualize,
    biasclean_validate
)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
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
            return render_template('upload_biasclean.html', error='No file provided')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload_biasclean.html', error='No file selected')
        
        # Get domain from form
        domain = request.form.get('domain', 'health')
        if domain not in DOMAINS:
            return render_template('upload_biasclean.html', error='Invalid domain selected')
        
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
        
        # Step 1: Detect biases for auto-confirm
        print(f"🔍 Step 1: Detecting biases for domain: {domain}")
        detect_results = biasclean_detect(input_path, domain)
        
        # STORE IN SESSION - CRITICAL FIX
        session['biasclean_session_id'] = session_id
        session['biasclean_domain'] = domain
        session['biasclean_filename'] = file.filename
        session['biasclean_input_path'] = input_path
        
        # Render auto-confirm page with detected features
        return render_template('auto_confirm_biasclean.html',
                            filename=file.filename,
                            domain=domain,
                            session_id=session_id,
                            detection=detect_results)
        
    except Exception as e:
        print(f"❌ Error in biasclean audit: {str(e)}")
        return render_template('upload_biasclean.html', error=f'Processing failed: {str(e)}')

@app.route('/biasclean/run-audit', methods=['POST'])
def run_biasclean_audit():
    """Run full bias audit after confirmation"""
    try:
        # RETRIEVE FROM SESSION - CRITICAL FIX
        session_id = session.get('biasclean_session_id')
        domain = session.get('biasclean_domain')
        filename = session.get('biasclean_filename')
        input_path = session.get('biasclean_input_path')
        
        if not session_id or not domain:
            return render_template('upload_biasclean.html', error='Session expired. Please upload again.')
        
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        
        # Use the stored input path instead of searching
        if not input_path or not os.path.exists(input_path):
            # Fallback: search for input file
            input_files = [f for f in os.listdir(upload_dir) if f.startswith('input_')]
            if not input_files:
                return render_template('upload_biasclean.html', error='Uploaded file not found')
            input_path = os.path.join(upload_dir, input_files[0])
        
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
        
        # Render results page
        return render_template('biasclean_results.html',
                            session_id=session_id,
                            domain=domain,
                            detection=remove_summary,
                            removal=remove_summary,
                            report_content=report_content,
                            production_ready=remove_summary.get('production_ready', False))
        
    except Exception as e:
        print(f"❌ Error in run_biasclean_audit: {str(e)}")
        return render_template('upload_biasclean.html', error=f'Audit failed: {str(e)}')

@app.route('/biasclean/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """Download result files with pattern matching for timestamped files"""
    try:
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        
        if not os.path.exists(results_dir):
            return f"Session not found: {session_id}", 404
        
        # Pattern matching for timestamped files
        if "corrected" in filename:
            pattern = "corrected_*.csv"
        elif "report" in filename:
            pattern = "report_*.txt"
        elif "validation" in filename:
            pattern = "validation_*.json"
        else:
            return f"Invalid file type: {filename}", 400
        
        # Find matching files
        import glob
        matching_files = glob.glob(os.path.join(results_dir, pattern))
        
        if matching_files:
            # Get the most recent file if multiple exist
            latest_file = max(matching_files, key=os.path.getctime)
            return send_file(latest_file, as_attachment=True)
        else:
            return f"No {pattern} files found in session {session_id}", 404
            
    except Exception as e:
        return f"Download error: {str(e)}", 500

@app.route('/biasclean/visualization/<session_id>/<viz_filename>')
def get_visualization(session_id, viz_filename):
    """Serve visualization images with pattern matching"""
    try:
        viz_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id, 'visualizations')
        
        if not os.path.exists(viz_dir):
            return "Visualizations directory not found", 404
        
        # Pattern matching for visualization files
        if "comprehensive_dashboard" in viz_filename:
            pattern = "01_comprehensive_dashboard.png"
        elif "feature_distributions" in viz_filename:
            pattern = "02_feature_distributions.png"
        elif "bias_score_comparison" in viz_filename:
            pattern = "03_bias_score_comparison.png"
        elif "data_retention" in viz_filename:
            pattern = "04_data_retention.png"
        elif "industry_readiness" in viz_filename:
            pattern = "05_industry_readiness.png"
        else:
            return f"Invalid visualization type: {viz_filename}", 400
        
        viz_path = os.path.join(viz_dir, pattern)
        
        if os.path.exists(viz_path):
            return send_file(viz_path)
        else:
            return f"Visualization {pattern} not found", 404
            
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
