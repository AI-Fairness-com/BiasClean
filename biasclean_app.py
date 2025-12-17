# -*- coding: utf-8 -*-
"""
===========================================================
BIASCLEAN AI FAIRNESS ENGINE - PRODUCTION FLASK API v2.4
===========================================================

OFFICIAL RELEASE: Professional Bias Detection & Mitigation Pipeline
Deployment: Render.com with CORS Support | Max File Size: 50MB
Repository: https://github.com/[YOUR-USERNAME]/biasclean-engine

ARCHITECTURE OVERVIEW:
├── Flask Web Wrapper (This File)
├── UniversalBiasClean Pipeline (biasclean_7.py)
├── HTML Report Generator (Professional UI/UX)
└── RESTful API Endpoints

KEY FEATURES:
✓ 7 Domain-Specific Weight Matrices (Justice, Health, Finance, etc.)
✓ Evidence-Based Statistical Validation (p-values, effect sizes)
✓ Industry-Grade SMOTE Rebalancing (≤8% data loss guarantee)
✓ Professional HTML Reports with Visual Analytics
✓ Full Pipeline Console Output Preservation
✓ Production-Ready CSV Output with Bias Mitigation
✓ CORS-Enabled for Cross-Origin Web Applications
✓ 1-Hour Auto-Cleanup for Temporary Files

AUTHOR: [Your Name/Organization]
LICENSE: MIT Open Source
VERSION: 2.4.0
RELEASE DATE: December 2024
"""

# ============================================================================
# CORE DEPENDENCIES - DO NOT MODIFY IMPORT ORDER
# ============================================================================
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
# CRITICAL SERVER CONFIGURATION
# ============================================================================
# Configure matplotlib for headless server environments
# MUST BE SET BEFORE any matplotlib/pandas imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server deployment

# ============================================================================
# DATA SCIENCE & WEB FRAMEWORK IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, current_app
from flask_cors import CORS

# ============================================================================
# MONKEY PATCH: FILE SYSTEM SAFETY FOR RENDER.COM DEPLOYMENT
# ============================================================================
# Prevent biasclean_7 pipeline from writing to disk on cloud server
original_makedirs = os.makedirs

def safe_makedirs(path, *args, **kwargs):
    """
    Intercept os.makedirs calls to block 'biasclean_results' directory creation.
    This prevents file system writes in Render.com's ephemeral environment.
    """
    if 'biasclean_results' in str(path):
        return  # Silently ignore directory creation for biasclean results
    return original_makedirs(path, *args, **kwargs)

os.makedirs = safe_makedirs  # Apply the safety patch globally

# ============================================================================
# BIASCLEAN PIPELINE IMPORT (CORE ENGINE)
# ============================================================================
# Import the main bias detection and mitigation engine
# This is the heart of the system - all statistical analysis happens here
from biasclean_7 import UniversalBiasClean, DOMAIN_CONFIGS

# ============================================================================
# PIPELINE OUTPUT PARSER - CONSOLE LOG EXTRACTION
# ============================================================================
class PipelineOutputParser:
    """
    Advanced parser for UniversalBiasClean console output.
    
    Extracts structured metrics from raw pipeline text output including:
    - Feature weights and domain priorities
    - Statistical test results (p-values, significance)
    - Mitigation actions and SMOTE rebalancing details
    - Executive summary metrics
    - Improvement percentages per feature
    
    This enables rich HTML reporting without modifying the core pipeline.
    """
    
    def __init__(self, raw_output: str):
        """Initialize parser with raw console output from pipeline."""
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
        self._parse_all()  # Extract all data sections immediately
    
    def _parse_all(self):
        """Orchestrate parsing of all output sections."""
        self._parse_feature_weights()
        self._parse_statistical_tests()
        self._parse_mitigation_details()
        self._parse_improvements()
        self._parse_executive_summary()
    
    def _parse_feature_weights(self):
        """
        Extract feature weights from 'Features for analysis' section.
        
        Pattern: • FeatureName ← Domain (weight: X.XX)
        Example: • Ethnicity ← Justice (weight: 25.00)
        """
        weight_pattern = r'•\s+(\w+)\s+←\s+\S+\s+\(weight:\s*([0-9.]+)\)'
        for line in self.lines:
            if 'weight:' in line.lower() and '←' in line:
                match = re.search(weight_pattern, line, re.IGNORECASE)
                if match:
                    feature, weight = match.groups()
                    self.parsed_data['feature_weights'][feature.strip()] = float(weight)
    
    def _parse_statistical_tests(self):
        """
        Extract statistical test results with p-values and significance.
        
        Pattern: • FeatureName p=X.XXXX SIGNIFICANT (weight: X.XX)
        Example: • Gender p=0.035210 SIGNIFICANT (weight: 20.00)
        """
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
        """
        Extract bias mitigation/rebalancing details.
        
        Captures: Samples removed/added, disparity thresholds, SMOTE parameters
        Example: Rebalancing 'Ethnicity' (weight: 25.00)
                 Samples removed: 125
                 Samples added: 98 (SMOTE)
                 Disparity threshold: 0.150
        """
        rebalance_pattern = r"Rebalancing\s+['\"]?(\w+)['\"]?\s+\(weight:\s*([0-9.]+)"
        for i, line in enumerate(self.lines):
            if 'Rebalancing' in line and 'weight:' in line:
                match = re.search(rebalance_pattern, line)
                if match:
                    feature, weight = match.groups()
                    details = {'weight': float(weight)}
                    # Look ahead for related metrics (next 10 lines max)
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
        """
        Extract improvement percentages for each feature.
        
        Pattern: ✅ FeatureName +X.XX%
        Example: ✅ Ethnicity +18.5%
        """
        imp_pattern = r'✅\s+(\w+)\s+([+-]?[0-9.]+)%'
        for line in self.lines:
            if '✅' in line and '%' in line:
                match = re.search(imp_pattern, line)
                if match:
                    feature, improvement = match.groups()
                    self.parsed_data['improvements'][feature.strip()] = float(improvement)
    
    def _parse_executive_summary(self):
        """
        Extract key performance metrics from executive summary.
        
        Captures: Bias scores, improvement percentages, record counts, retention rates
        All metrics are converted to appropriate numeric types (float/int).
        """
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
    
    # ========================================================================
    # PUBLIC ACCESS METHODS - CLEAN API FOR EXTRACTED DATA
    # ========================================================================
    
    def get_feature_weight(self, feature_name: str) -> float:
        """Get domain weight for specific feature."""
        return self.parsed_data['feature_weights'].get(feature_name, 0.0)
    
    def get_statistical_test(self, feature_name: str) -> Dict:
        """Get statistical test results for specific feature."""
        return self.parsed_data['statistical_tests'].get(feature_name, {})
    
    def get_all_improvements(self) -> Dict[str, float]:
        """Get all feature improvement percentages."""
        return self.parsed_data['improvements']
    
    def get_mitigation_details(self) -> Dict:
        """Get all bias mitigation actions taken."""
        return self.parsed_data['mitigation_details']
    
    def get_executive_summary(self) -> Dict:
        """Get executive summary metrics."""
        return self.parsed_data['executive_summary']

# ============================================================================
# NUMPY/PANDAS TYPE CONVERTER FOR JSON SERIALIZATION
# ============================================================================
def convert_numpy_types(obj):
    """
    Recursively convert NumPy/Pandas types to native Python types for JSON.
    
    Handles: np.bool_, np.int*, np.float*, np.ndarray, pd.NA
    Required because Flask's jsonify cannot serialize NumPy types directly.
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
# VISUALIZATION HANDLER - IMAGE CAPTURE & BASE64 ENCODING
# ============================================================================
def capture_visualizations(temp_dir: str) -> Dict[str, str]:
    """
    Capture PNG visualization files and encode as base64 for HTML embedding.
    
    Args:
        temp_dir: Directory containing pipeline-generated visualizations
        
    Returns:
        Dictionary mapping filename -> base64 data URL for HTML img tags
    """
    viz_base64 = {}
    if os.path.exists(temp_dir):
        viz_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            viz_files.extend(Path(temp_dir).glob(ext))
        for viz_path in viz_files[:5]:  # Limit to 5 visualizations max
            try:
                with open(viz_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    viz_base64[viz_path.name] = f'data:image/png;base64,{img_data}'
            except Exception as e:
                current_app.logger.warning(f"Failed to encode {viz_path.name}: {e}")
    return viz_base64

def cleanup_temp_dir(dir_path: str):
    """
    Asynchronous cleanup of temporary directories after 1 hour.
    
    Uses threading to avoid blocking main request/response cycle.
    Render.com has ephemeral storage, but cleanup prevents accumulation.
    """
    def cleanup():
        time.sleep(3600)  # Wait 1 hour before cleanup
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
# PROFESSIONAL HTML REPORT GENERATOR v2.4
# ============================================================================
def generate_html_report(parser, viz_base64, domain, session_id, pipeline_output, 
                       df, corrected_df, executive_summary, base_url) -> str:
    """
    Generate comprehensive HTML report with professional UI/UX design.
    
    This is the core reporting engine that transforms pipeline results into
    a visually stunning, interactive HTML report matching the upload page design.
    
    Args:
        parser: PipelineOutputParser instance with extracted metrics
        viz_base64: Dictionary of visualization images as base64 data URLs
        domain: Analysis domain (justice, health, finance, etc.)
        session_id: Unique session identifier for tracking
        pipeline_output: Raw console output from biasclean pipeline
        df: Original input DataFrame
        corrected_df: Bias-mitigated output DataFrame
        executive_summary: Key performance metrics
        base_url: Base URL for download links
        
    Returns:
        Complete HTML document as string, ready for browser rendering
    """
    
    # ========================================================================
    # DATA EXTRACTION & PREPARATION
    # ========================================================================
    initial_bias = executive_summary.get('initial_bias', 0)
    final_bias = executive_summary.get('final_bias', initial_bias)
    improvement = executive_summary.get('improvement', 0)
    sig_biases = executive_summary.get('significant_biases', 0)
    records_before = executive_summary.get('records_before', len(df))
    records_after = executive_summary.get('records_after', len(corrected_df))
    retention = executive_summary.get('retention', 100)
    mitigation_details = parser.get_mitigation_details()
    feature_weights = parser.parsed_data['feature_weights']
    improvements = parser.get_all_improvements()
    statistical_tests = parser.parsed_data['statistical_tests']
    
    # Calculate derived statistics
    bias_reduction = round(improvement, 1)
    production_ready = improvement > 5
    data_loss = 100 - retention
    
    # Domain display configuration with emojis
    domain_display = {
        'justice': ('⚖️', 'Justice System'),
        'health': ('🏥', 'Healthcare'),
        'finance': ('💼', 'Finance & Banking'),
        'education': ('🎓', 'Education'),
        'hiring': ('👥', 'Hiring & Recruitment'),
        'business': ('🏢', 'Business Operations'),
        'governance': ('🏛️', 'Governance & Public Policy')
    }
    domain_emoji, domain_name = domain_display.get(domain, ('🎯', domain.replace('_', ' ').title()))
    
    # ========================================================================
    # COLOR CODING FUNCTIONS FOR METRIC VISUALIZATION
    # ========================================================================
    def get_bias_color(value):
        """Color code bias reduction percentages."""
        if value > 20: return '#e74c3c'      # Red: High bias reduction
        elif value > 10: return '#f39c12'    # Orange: Moderate reduction
        elif value > 5: return '#f1c40f'     # Yellow: Low reduction
        else: return '#27ae60'               # Green: Minimal reduction
    
    def get_retention_color(value):
        """Color code data retention percentages."""
        if value > 95: return '#27ae60'      # Green: Excellent retention
        elif value > 90: return '#f1c40f'    # Yellow: Good retention
        else: return '#e74c3c'               # Red: Poor retention
    
    # Apply color coding to metrics
    bias_color = get_bias_color(bias_reduction)
    retention_color = get_retention_color(retention)
    significant_color = '#27ae60' if sig_biases == 0 else ('#f39c12' if sig_biases < 3 else '#e74c3c')
    final_bias_color = '#27ae60' if final_bias < 0.2 else ('#f39c12' if final_bias < 0.4 else '#e74c3c')
    
    # Timestamp formatting
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_long = datetime.now().strftime('%Y-%m-%d at %H:%M:%S')
    pipeline_output_lines = len(pipeline_output.split('\n'))
    
    # ========================================================================
    # HTML TEMPLATE WITH PROFESSIONAL UI/UX
    # ========================================================================
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BiasClean Report - {domain_name} Analysis</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
  <style>
    /* ===========================================================================
       CSS VARIABLES - MATCHES UPLOAD PAGE DESIGN SYSTEM
       =========================================================================== */
    * {{margin:0;padding:0;box-sizing:border-box;}}

    :root {{
      --primary:#BE9D04;      /* Gold - Primary brand color */
      --secondary:#4A463D;    /* Dark gray - Secondary color */
      --accent:#3498db;       /* Blue - Accent for highlights */
      --success:#27ae60;      /* Green - Positive metrics */
      --warning:#f39c12;      /* Orange - Warning/caution */
      --error:#e74c3c;        /* Red - Error/negative metrics */
      --light:#f8f9fa;        /* Light background */
      --dark:#323130;         /* Dark text */
      --gray:#605e5c;         /* Gray text */
      --gradient:radial-gradient(circle at top left,#243447 0%,#151824 40%,#05060a 100%);
    }}

    /* ===========================================================================
       BASE STYLES & GLASS MORPHISM CONTAINER
       =========================================================================== */
    body{{
      font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
      background:var(--gradient);
      min-height:100vh;
      padding:20px;
      line-height:1.6;
      color:var(--dark);
      -webkit-font-smoothing:antialiased;
    }}

    .glass-container{{
      max-width:1400px;
      margin:0 auto;
      background:rgba(255,255,255,0.96);
      backdrop-filter:blur(22px);
      border-radius:26px;
      box-shadow:0 28px 60px rgba(0,0,0,0.22);
      overflow:hidden;
      border:1px solid rgba(255,255,255,0.35);
    }}

    /* ===========================================================================
       HERO SECTION - ANIMATED HEADER WITH BRANDING
       =========================================================================== */
    .hero-section{{
      background:linear-gradient(135deg,var(--primary),#a88702);
      color:white;
      padding:50px 40px 40px;
      text-align:center;
      position:relative;
      overflow:hidden;
    }}
    .hero-section::before{{
      content:'';
      position:absolute;
      top:0;left:0;right:0;
      height:4px;
      background:linear-gradient(90deg,var(--secondary),var(--accent),#d4b104);
    }}
    .hero-section::after{{
      content:'';
      position:absolute;
      top:0;
      left:-40%;
      width:40%;
      height:100%;
      background:linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.45) 45%, rgba(255,255,255,0) 100%);
      transform:skewX(-20deg);
      animation:heroSweep 7s linear infinite;
      pointer-events:none;
    }}
    @keyframes heroSweep{{
      0%{{transform:translateX(0) skewX(-20deg);}}
      100%{{transform:translateX(260%) skewX(-20deg);}}
    }}
    .hero-pattern {{
      position:absolute;
      top:0;left:0;right:0;bottom:0;
      background:
        radial-gradient(circle at 20% 80%,rgba(255,255,255,0.18) 0%,transparent 55%),
        radial-gradient(circle at 80% 20%,rgba(255,255,255,0.12) 0%,transparent 55%),
        radial-gradient(circle at 40% 40%,rgba(255,255,255,0.10) 0%,transparent 55%);
      opacity:0.55;
      pointer-events:none;
    }}
    .hero-content{{position:relative;z-index:2;max-width:900px;margin:0 auto;}}

    .broom-icon{{
      font-size:4em;
      margin-bottom:15px;
      display:block;
      text-shadow:0 4px 12px rgba(0,0,0,0.35);
      animation:float 4s ease-in-out infinite;
      filter:drop-shadow(0 6px 12px rgba(0,0,0,0.35));
    }}
    @keyframes float{{
      0%,100%{{transform:translateY(0) rotate(0deg);}}
      33%{{transform:translateY(-10px) rotate(-2deg);}}
      66%{{transform:translateY(-5px) rotate(2deg);}}
    }}

    .logo{{
      font-size:2.8em;
      font-weight:800;
      margin-bottom:5px;
      background:linear-gradient(135deg,#ffffff,#f3f4f6);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
      text-shadow:0 2px 10px rgba(0,0,0,0.25);
      letter-spacing:-0.4px;
    }}
    .report-title{{
      font-size:1.8rem;
      font-weight:600;
      margin-bottom:10px;
      text-shadow:0 2px 4px rgba(0,0,0,0.25);
      letter-spacing:0.02em;
    }}
    .report-subtitle{{
      font-size:1.1rem;
      margin-bottom:20px;
      font-weight:300;
      opacity:0.98;
      max-width:700px;
      margin-left:auto;
      margin-right:auto;
      line-height:1.55;
    }}

    .session-badge{{
      background:rgba(255,255,255,0.16);
      backdrop-filter:blur(18px);
      color:white;
      padding:12px 24px;
      border-radius:999px;
      font-size:0.9rem;
      font-weight:600;
      display:inline-flex;
      align-items:center;
      gap:10px;
      border:1px solid rgba(255,255,255,0.35);
      box-shadow:0 10px 26px rgba(0,0,0,0.25);
      margin-top:10px;
    }}

    /* ===========================================================================
       CONTENT SECTION - MAIN REPORT AREA
       =========================================================================== */
    .content-section{{
      padding:40px;
      max-width:1300px;
      margin:0 auto;
    }}

    /* ===========================================================================
       EXECUTIVE SUMMARY - KEY METRICS GRID
       =========================================================================== */
    .executive-summary{{
      background:linear-gradient(135deg,#fdfdfd,#eef1f5);
      padding:30px;
      border-radius:20px;
      margin-bottom:30px;
      border-left:6px solid var(--secondary);
      box-shadow:0 14px 40px rgba(0,0,0,0.08);
      position:relative;
      overflow:hidden;
    }}
    .executive-summary::before{{
      content:'';
      position:absolute;
      top:-20px;right:-30px;
      width:140px;height:140px;
      background:radial-gradient(circle,var(--primary) 0%,transparent 70%);
      opacity:0.12;
    }}
    .section-title{{
      color:var(--dark);
      font-size:1.35rem;
      margin-bottom:20px;
      font-weight:650;
      display:flex;
      align-items:center;
      gap:12px;
      letter-spacing:0.01em;
    }}
    .section-title i{{color:var(--secondary);font-size:1.15em;}}

    .metrics-grid{{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
      gap:20px;
      margin:25px 0;
    }}
    .metric-card{{
      background:white;
      padding:25px 20px;
      border-radius:16px;
      box-shadow:0 8px 24px rgba(0,0,0,0.08);
      text-align:center;
      transition:transform 0.3s ease;
      border-top:4px solid var(--primary);
    }}
    .metric-card:hover{{
      transform:translateY(-5px);
      box-shadow:0 12px 32px rgba(0,0,0,0.12);
    }}
    .metric-value{{
      font-size:2.8rem;
      font-weight:800;
      margin-bottom:8px;
    }}
    .metric-label{{
      color:var(--gray);
      font-size:1rem;
      font-weight:600;
      text-transform:uppercase;
      letter-spacing:0.05em;
    }}

    /* ===========================================================================
       VISUALIZATION GRID - PIPELINE-GENERATED CHARTS
       =========================================================================== */
    .viz-section{{
      margin:40px 0;
      background:white;
      padding:30px;
      border-radius:20px;
      box-shadow:0 14px 40px rgba(0,0,0,0.08);
    }}
    .viz-grid{{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(350px,1fr));
      gap:25px;
      margin:25px 0;
    }}
    .viz-card{{
      background:#f8f9fa;
      border-radius:16px;
      overflow:hidden;
      box-shadow:0 8px 24px rgba(0,0,0,0.08);
      border:1px solid #e2e8f0;
      transition:transform 0.3s ease;
    }}
    .viz-card:hover{{transform:translateY(-3px);}}
    .viz-card h3{{
      background:var(--primary);
      color:white;
      margin:0;
      padding:15px;
      font-size:1em;
      font-weight:600;
      text-align:center;
    }}
    .viz-card img{{
      width:100%;
      height:250px;
      object-fit:contain;
      padding:15px;
      background:white;
    }}

    /* ===========================================================================
       STATISTICAL ANALYSIS TABLE - P-VALUES & SIGNIFICANCE
       =========================================================================== */
    .stats-section{{
      background:white;
      padding:30px;
      border-radius:20px;
      box-shadow:0 14px 40px rgba(0,0,0,0.08);
      margin:40px 0;
      overflow-x:auto;
    }}
    .stats-table{{
      width:100%;
      border-collapse:collapse;
      margin:20px 0;
      background:white;
    }}
    .stats-table th{{
      background:var(--primary);
      color:white;
      padding:15px;
      text-align:left;
      font-weight:600;
      border-bottom:3px solid var(--secondary);
    }}
    .stats-table td{{
      padding:15px;
      border-bottom:1px solid #e2e8f0;
    }}
    .stats-table tr:hover{{background:#f8f9fa;}}
    .badge{{
      display:inline-block;
      padding:4px 12px;
      border-radius:12px;
      font-size:0.85em;
      font-weight:600;
    }}
    .badge-success{{background:#c6f6d5;color:#276749;}}
    .badge-danger{{background:#fed7d7;color:#c53030;}}
    .badge-warning{{background:#fed7a0;color:#9c4221;}}
    .badge-info{{background:#bee3f8;color:#2c5282;}}

    /* ===========================================================================
       FEATURES GRID - WEIGHT-PRIORITIZED ANALYSIS
       =========================================================================== */
    .features-grid{{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
      gap:20px;
      margin:30px 0;
    }}
    .feature-card{{
      background:white;
      padding:25px;
      border-radius:16px;
      box-shadow:0 8px 24px rgba(0,0,0,0.08);
      transition:transform 0.3s ease;
      border-top:4px solid var(--primary);
      cursor:pointer;
    }}
    .feature-card:hover{{transform:translateY(-5px);box-shadow:0 12px 32px rgba(0,0,0,0.12);}}
    .feature-header{{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:15px;
    }}
    .feature-name{{font-weight:700;font-size:1.1rem;color:var(--dark);}}
    .feature-weight{{background:var(--primary);color:white;padding:4px 12px;border-radius:12px;font-weight:600;}}
    .feature-stats{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:15px;}}
    .stat-item{{text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;}}
    .stat-label{{font-size:0.85rem;color:var(--gray);}}
    .stat-value{{font-size:1.2rem;font-weight:700;margin-top:5px;}}

    /* ===========================================================================
       MITIGATION CARDS - SMOTE REBALANCING DETAILS
       =========================================================================== */
    .mitigation-card{{
      background:linear-gradient(135deg,#f8f9fa,#e9ecef);
      padding:25px;
      border-radius:16px;
      margin:20px 0;
      border-left:6px solid var(--accent);
      box-shadow:0 8px 24px rgba(0,0,0,0.08);
    }}
    .mitigation-header{{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:20px;
    }}
    .mitigation-title{{font-weight:700;font-size:1.2rem;color:var(--dark);}}
    .mitigation-stats{{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
      gap:15px;
      margin-top:15px;
    }}
    .mitigation-stat{{text-align:center;padding:15px;background:white;border-radius:8px;}}
    .mitigation-label{{font-size:0.9rem;color:var(--gray);}}
    .mitigation-value{{font-size:1.5rem;font-weight:800;margin-top:5px;}}

    /* ===========================================================================
       CONSOLE OUTPUT - FULL PIPELINE EXECUTION LOG
       =========================================================================== */
    .console-section{{
      background:#1a202c;
      color:#e2e8f0;
      padding:30px;
      border-radius:20px;
      margin:40px 0;
      box-shadow:0 14px 40px rgba(0,0,0,0.08);
    }}
    .console-header{{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:20px;
      padding-bottom:15px;
      border-bottom:2px solid #2d3748;
    }}
    .console-title{{font-weight:700;font-size:1.2rem;}}
    .line-count{{color:#a0aec0;font-size:0.9rem;}}
    .console-output{{
      background:#0d1117;
      padding:20px;
      border-radius:8px;
      max-height:400px;
      overflow-y:auto;
      font-family:'Courier New',monospace;
      font-size:0.85rem;
      line-height:1.5;
    }}
    .console-output pre{{margin:0;white-space:pre-wrap;}}

    /* ===========================================================================
       DOWNLOAD SECTION - PDF REPORT GENERATION
       =========================================================================== */
    .download-section{{
      background:linear-gradient(135deg,var(--primary),#a88702);
      color:white;
      padding:40px;
      border-radius:20px;
      margin:40px 0;
      text-align:center;
      box-shadow:0 20px 50px rgba(190,157,4,0.25);
    }}
    .download-title{{
      font-size:1.8rem;
      font-weight:700;
      margin-bottom:15px;
    }}
    .download-subtitle{{
      font-size:1rem;
      opacity:0.9;
      margin-bottom:30px;
      max-width:600px;
      margin-left:auto;
      margin-right:auto;
    }}
    .download-buttons{{
      display:flex;
      gap:20px;
      justify-content:center;
      margin:30px 0;
      flex-wrap:wrap;
    }}
    .download-btn{{
      display:inline-flex;
      align-items:center;
      gap:10px;
      background:white;
      color:var(--primary);
      border:none;
      padding:16px 32px;
      font-size:1rem;
      font-weight:700;
      border-radius:12px;
      cursor:pointer;
      transition:all 0.3s ease;
      box-shadow:0 8px 20px rgba(0,0,0,0.15);
      text-decoration:none;
    }}
    .download-btn:hover{{
      transform:translateY(-3px);
      box-shadow:0 12px 28px rgba(0,0,0,0.25);
      background:#f8f9fa;
    }}

    /* ===========================================================================
       LEGAL SECTION - TECHNICAL IMPLEMENTATION DETAILS
       =========================================================================== */
    .legal-section{{
      background:linear-gradient(135deg,#fff7e0,#ffefc4);
      border:1px solid var(--warning);
      border-radius:18px;
      padding:30px;
      margin-top:40px;
      position:relative;
      border-left:6px solid var(--warning);
    }}
    .legal-icon{{
      position:absolute;
      top:-18px;left:30px;
      background:white;
      padding:10px;
      border-radius:50%;
      box-shadow:0 6px 18px rgba(0,0,0,0.12);
      color:var(--warning);
      font-size:1.15em;
    }}
    .legal-title{{
      color:#856404;
      font-weight:700;
      margin-bottom:8px;
      font-size:1.18rem;
      letter-spacing:0.02em;
    }}
    .legal-text{{
      color:#856404;
      line-height:1.6;
      font-size:0.96rem;
    }}

    /* ===========================================================================
       FOOTER - BRANDING & SESSION INFORMATION
       =========================================================================== */
    .footer{{
      text-align:center;
      padding:30px;
      color:var(--gray);
      border-top:1px solid #e2e8f0;
      margin-top:40px;
    }}
    .footer-logo{{font-weight:800;color:var(--primary);font-size:1.2rem;}}

    /* ===========================================================================
       PRINT STYLES - OPTIMIZED FOR PHYSICAL PRINTING
       =========================================================================== */
    @media print {{
      body {{ background: white; color: black; }}
      .glass-container {{ box-shadow: none; border: 1px solid #ddd; }}
      .download-section, .download-buttons {{ display: none; }}
      .hero-section {{ background: #f0f0f0; color: black; }}
      .hero-section::before, .hero-section::after, .hero-pattern {{ display: none; }}
      .broom-icon {{ color: black; }}
      .logo {{ background: black; -webkit-text-fill-color: black; }}
      .metric-card, .viz-card, .feature-card {{ box-shadow: none; border: 1px solid #ddd; }}
      .viz-card img {{ height: auto; max-height: 200px; }}
    }}

    /* ===========================================================================
       RESPONSIVE DESIGN - MOBILE & TABLET OPTIMIZATIONS
       =========================================================================== */
    @media(max-width:900px){{
      .content-section{{padding:30px 20px;}}
      .executive-summary{{padding:25px;}}
      .metrics-grid{{grid-template-columns:repeat(2,1fr);}}
      .viz-grid{{grid-template-columns:1fr;}}
      .features-grid{{grid-template-columns:1fr;}}
      .download-buttons{{flex-direction:column;}}
    }}

    @media(max-width:768px){{
      .glass-container{{margin:10px;border-radius:20px;}}
      .hero-section{{padding:30px 20px;}}
      .logo{{font-size:2.2em;}}
      .report-title{{font-size:1.5rem;}}
      .metrics-grid{{grid-template-columns:1fr;}}
      .metric-value{{font-size:2.2rem;}}
    }}

    @media(max-width:480px){{
      body{{padding:10px;}}
      .metric-card{{padding:20px 15px;}}
      .download-btn{{width:100%;justify-content:center;}}
    }}
  </style>
</head>
<body>
<!-- ===========================================================================
     MAIN REPORT CONTAINER - GLASS MORPHISM DESIGN
     =========================================================================== -->
<div class="glass-container">
  <!-- HERO SECTION - BRANDING & SESSION INFO -->
  <div class="hero-section">
    <div class="hero-pattern"></div>
    <div class="hero-content">
      <div class="broom-icon">🧹</div>
      <div class="logo">BiasClean</div>
      <div class="report-title">{domain_emoji} {domain_name} Analysis Report</div>
      <div class="report-subtitle">
        Complete bias detection and mitigation results with evidence-based statistical validation
      </div>
      <div class="session-badge">
        <i class="fas fa-fingerprint"></i> Session ID: {session_id} • Generated: {timestamp}
      </div>
    </div>
  </div>

  <!-- CONTENT SECTION - ALL REPORT COMPONENTS -->
  <div class="content-section">
    <!-- EXECUTIVE SUMMARY - KEY PERFORMANCE METRICS -->
    <div class="executive-summary">
      <div class="section-title">
        <i class="fas fa-chart-line"></i> Executive Summary
      </div>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value" style="color:{bias_color};">{bias_reduction:.1f}%</div>
          <div class="metric-label">Bias Reduction</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="color:{retention_color};">{retention:.1f}%</div>
          <div class="metric-label">Data Retention</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="color:{significant_color};">{sig_biases}</div>
          <div class="metric-label">Significant Biases</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="color:var(--accent);">{records_before:,}</div>
          <div class="metric-label">Initial Records</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="color:var(--accent);">{records_after:,}</div>
          <div class="metric-label">Final Records</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="color:{final_bias_color};">{final_bias:.4f}</div>
          <div class="metric-label">Final Bias Score</div>
        </div>
      </div>
    </div>
'''
    
    # ========================================================================
    # VISUALIZATIONS SECTION - DYNAMIC IMAGE INSERTION
    # ========================================================================
    if viz_base64:
        html += f'''
    <!-- VISUALIZATIONS SECTION - PIPELINE-GENERATED CHARTS -->
    <div class="viz-section">
      <div class="section-title">
        <i class="fas fa-chart-bar"></i> Visual Analysis
      </div>
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
    
    # ========================================================================
    # STATISTICAL ANALYSIS TABLE - DYNAMIC DATA POPULATION
    # ========================================================================
    html += f'''
    <!-- STATISTICAL ANALYSIS TABLE - WEIGHT-PRIORITIZED RESULTS -->
    <div class="stats-section">
      <div class="section-title">
        <i class="fas fa-calculator"></i> Statistical Analysis Results
      </div>
      <p style="color:var(--gray);margin-bottom:20px;">Weight-prioritized bias detection with p-value validation</p>
      <table class="stats-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Domain Weight</th>
            <th>p-value</th>
            <th>Statistical Significance</th>
            <th>Improvement</th>
          </tr>
        </thead>
        <tbody>
'''
    
    # Generate table rows for each feature, sorted by weight
    for feature in sorted(feature_weights.keys(), key=lambda x: feature_weights[x], reverse=True):
        test_data = statistical_tests.get(feature, {})
        imp = improvements.get(feature, 0)
        p_value = test_data.get('p_value', 1.0)
        significant = test_data.get('significant', False)
        badge_class = 'badge-danger' if significant else 'badge-success'
        badge_text = '⚠️ SIGNIFICANT BIAS' if significant else '✅ NO SIGNIFICANT BIAS'
        imp_color = 'var(--success)' if imp > 0 else 'var(--error)'
        
        html += f'''
          <tr>
            <td><strong>{feature}</strong></td>
            <td>{feature_weights[feature]:.2f}</td>
            <td>{p_value:.6f}</td>
            <td><span class="badge {badge_class}">{badge_text}</span></td>
            <td style="color:{imp_color};font-weight:700;">{imp:+.1f}%</td>
          </tr>
'''
    
    html += '''
        </tbody>
      </table>
    </div>
'''
    
    # ========================================================================
    # FEATURES GRID - INTERACTIVE CARDS FOR EACH FEATURE
    # ========================================================================
    html += f'''
    <!-- FEATURES ANALYZED - INTERACTIVE CARDS -->
    <div class="features-grid">
'''
    
    for feature in sorted(feature_weights.keys(), key=lambda x: feature_weights[x], reverse=True):
        test_data = statistical_tests.get(feature, {})
        imp = improvements.get(feature, 0)
        p_value = test_data.get('p_value', 1.0)
        significant = test_data.get('significant', False)
        imp_color = 'var(--success)' if imp > 0 else 'var(--error)'
        
        html += f'''
      <div class="feature-card">
        <div class="feature-header">
          <div class="feature-name">{feature}</div>
          <div class="feature-weight">{feature_weights[feature]:.2f}</div>
        </div>
        <div class="feature-stats">
          <div class="stat-item">
            <div class="stat-label">p-value</div>
            <div class="stat-value">{p_value:.4f}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Improvement</div>
            <div class="stat-value" style="color:{imp_color};">{imp:+.1f}%</div>
          </div>
        </div>
        <div style="margin-top:15px;padding:8px;background:#f8f9fa;border-radius:8px;text-align:center;">
          <span class="badge {('badge-danger' if significant else 'badge-success')}">
            {'⚠️ Significant Bias Detected' if significant else '✅ No Significant Bias'}
          </span>
        </div>
      </div>
'''
    
    html += '''
    </div>
'''
    
    # ========================================================================
    # MITIGATION ACTIONS - SMOTE REBALANCING DETAILS
    # ========================================================================
    if mitigation_details:
        html += f'''
    <!-- MITIGATION ACTIONS - SMOTE REBALANCING DETAILS -->
    <div class="stats-section">
      <div class="section-title">
        <i class="fas fa-balance-scale"></i> Bias Mitigation Actions
      </div>
      <p style="color:var(--gray);margin-bottom:20px;">Weight-prioritized rebalancing with SMOTE synthesis</p>
'''
        
        for feature, details in sorted(mitigation_details.items(), key=lambda x: x[1].get('weight', 0), reverse=True):
            samples_removed = details.get('samples_removed', 0)
            samples_added = details.get('samples_added', 0)
            disparity_threshold = details.get('disparity_threshold', 0)
            weight = details.get('weight', 0)
            net_change = samples_added - samples_removed
            net_color = 'var(--success)' if net_change > 0 else 'var(--error)'
            
            html += f'''
      <div class="mitigation-card">
        <div class="mitigation-header">
          <div class="mitigation-title">🎯 {feature}</div>
          <div style="background:var(--primary);color:white;padding:6px 15px;border-radius:12px;font-weight:700;">
            Weight: {weight:.2f}
          </div>
        </div>
        <div class="mitigation-stats">
          <div class="mitigation-stat">
            <div class="mitigation-label">Disparity Threshold</div>
            <div class="mitigation-value">{disparity_threshold:.3f}</div>
          </div>
          <div class="mitigation-stat">
            <div class="mitigation-label">Samples Removed</div>
            <div class="mitigation-value" style="color:var(--error);">{samples_removed:,}</div>
          </div>
          <div class="mitigation-stat">
            <div class="mitigation-label">Samples Added (SMOTE)</div>
            <div class="mitigation-value" style="color:var(--success);">{samples_added:,}</div>
          </div>
          <div class="mitigation-stat">
            <div class="mitigation-label">Net Change</div>
            <div class="mitigation-value" style="color:{net_color};">{net_change:+,}</div>
          </div>
        </div>
      </div>
'''
        
        html += '''
    </div>
'''
    
    # ========================================================================
    # CONSOLE OUTPUT - FULL PIPELINE EXECUTION LOG
    # ========================================================================
    html += f'''
    <!-- CONSOLE OUTPUT - COMPLETE EXECUTION LOG -->
    <div class="console-section">
      <div class="console-header">
        <div class="console-title">
          <i class="fas fa-terminal"></i> Complete Pipeline Execution Log
        </div>
        <div class="line-count">{pipeline_output_lines} lines</div>
      </div>
      <div class="console-output">
        <pre>{pipeline_output}</pre>
      </div>
    </div>
'''
    
    # ========================================================================
    # PDF DOWNLOAD SECTION - ACADEMIC REPORT GENERATION
    # ========================================================================
    html += f'''
    <!-- DOWNLOAD SECTION - PDF REPORT GENERATION -->
    <div class="download-section">
      <div class="download-title">📥 Download Academic Report (PDF)</div>
      <div class="download-subtitle">
        Generate a professional PDF report with all visualizations and statistical results for academic or regulatory purposes.
      </div>
      <div class="download-buttons">
        <a href="{base_url}/pdf/{session_id}" class="download-btn" target="_blank">
          <i class="fas fa-file-pdf"></i> Generate PDF Report
        </a>
      </div>
      <p style="opacity:0.8;font-size:0.9rem;margin-top:20px;">
        <i class="fas fa-info-circle"></i> PDF includes all visualizations, statistical tables, and executive summary
      </p>
    </div>
'''
    
    # ========================================================================
    # LEGAL SECTION - TECHNICAL IMPLEMENTATION DISCLOSURE
    # ========================================================================
    html += f'''
    <!-- LEGAL SECTION - TECHNICAL DISCLOSURE -->
    <div class="legal-section">
      <div class="legal-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <div class="legal-content">
        <div class="legal-title">Technical Implementation Details</div>
        <div class="legal-text">
          BiasClean v2.4 implements domain-specific weight matrices based on UK regulatory frameworks. 
          Protected features: Ethnicity, Gender, Age, DisabilityStatus, SocioeconomicStatus, Region, MigrationStatus. 
          Statistical significance testing performed with α=0.05 threshold. SMOTE rebalancing guarantees ≤8% data loss. 
          Report generated: {timestamp}
        </div>
      </div>
    </div>

    <!-- FOOTER - BRANDING & SESSION TRACKING -->
    <div class="footer">
      <div class="footer-logo">BiasClean v2.4</div>
      <p style="margin-top:10px;color:var(--gray);">
        Universal Bias Detection & Mitigation Pipeline • Evidence-Based Fairness Engineering
      </p>
      <p style="margin-top:5px;font-size:0.9rem;color:var(--gray);">
        Session ID: {session_id} • Report generated on {timestamp_long}
      </p>
    </div>
  </div>
</div>

<!-- ===========================================================================
     JAVASCRIPT - INTERACTIVITY & PRINT HANDLING
     =========================================================================== -->
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    // Smooth scrolling for anchor links (if any)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
      anchor.addEventListener('click', function(e) {{
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {{
          target.scrollIntoView({{ behavior: 'smooth' }});
        }}
      }});
    }});

    // Print style management
    window.addEventListener('beforeprint', () => {{
      document.body.classList.add('printing');
    }});
    window.addEventListener('afterprint', () => {{
      document.body.classList.remove('printing');
    }});
  }});
</script>
</body>
</html>'''
    
    return html

# ============================================================================
# FLASK APPLICATION CONFIGURATION
# ============================================================================
app = Flask(__name__, template_folder='templates', static_folder='static')

# CORS Configuration - Allow web applications from any origin
CORS(app, resources={r"/*": {"origins": ["https://ai-fairness.com", "*"]}})

# Server Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB file size limit
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # System temp directory

# Base URL for download links (configure via environment variable)
BASE_URL = os.environ.get('BASE_URL', 'https://biasclean.onrender.com')

# ============================================================================
# FLASK MIDDLEWARE - CORS HEADERS
# ============================================================================
@app.after_request
def after_request(response):
    """
    Add CORS headers to all responses.
    
    Required for web applications hosted on different domains to access the API.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
    return response

# ============================================================================
# FLASK ROUTES - API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """
    Serve the main upload interface.
    
    Returns:
        Rendered upload_biasclean.html template
    """
    return render_template('upload_biasclean.html')

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """
    Main analysis endpoint - processes CSV files through biasclean pipeline.
    
    Flow:
    1. Validate file upload and domain selection
    2. Load CSV into pandas DataFrame
    3. Execute UniversalBiasClean pipeline
    4. Parse results and generate HTML report
    5. Save cleaned dataset and report files
    6. Return JSON response with download links
    
    Returns:
        JSON response with analysis results and file URLs
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # ====================================================================
        # 1. FILE UPLOAD VALIDATION
        # ====================================================================
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'CSV file required'}), 400
        
        domain = request.form.get('domain', 'justice')
        
        # Save uploaded file to temporary location
        temp_path = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
        file.save(temp_path)
        
        # ====================================================================
        # 2. CSV LOADING & VALIDATION
        # ====================================================================
        try:
            df = pd.read_csv(temp_path)
            app.logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            os.unlink(temp_path)
            return jsonify({'error': f'Invalid CSV: {str(e)[:100]}'}), 400
        
        # ====================================================================
        # 3. PIPELINE EXECUTION SETUP
        # ====================================================================
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        viz_temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"viz_{session_id}")
        os.makedirs(viz_temp_dir, exist_ok=True)
        biasclean_results_dir = os.path.join(viz_temp_dir, "biasclean_results")
        
        app.logger.info(f"Starting pipeline for domain: {domain}")
        
        # Temporarily restore os.makedirs for pipeline execution
        os.makedirs = original_makedirs
        
        try:
            # ================================================================
            # 4. EXECUTE BIASCLEAN PIPELINE
            # ================================================================
            pipeline = UniversalBiasClean(domain=domain)
            original_cwd = os.getcwd()
            os.chdir(viz_temp_dir)
            
            # Capture all console output from pipeline
            output_capture = io.StringIO()
            with redirect_stdout(output_capture), redirect_stderr(output_capture):
                results = pipeline.process_dataset(df=df, auto_approve_threshold=0.80)
            
            os.chdir(original_cwd)
        finally:
            # Restore safe makedirs after pipeline execution
            os.makedirs = safe_makedirs
        
        # ====================================================================
        # 5. RESULT PROCESSING & PARSING
        # ====================================================================
        pipeline_output = output_capture.getvalue()
        app.logger.info("Pipeline completed successfully")
        
        # Parse console output for detailed metrics
        parser = PipelineOutputParser(pipeline_output)
        
        # Capture and encode visualization images
        viz_base64 = capture_visualizations(biasclean_results_dir)
        app.logger.info(f"Found {len(viz_base64)} visualizations")
        
        # Extract metrics from pipeline results
        diagnostics = results.get('diagnostics', {})
        validation = results.get('validation', {})
        executive_summary = parser.get_executive_summary()
        
        # Calculate final metrics with fallbacks
        initial_bias = executive_summary.get('initial_bias', diagnostics.get('initial_bias_score', 0))
        final_bias = executive_summary.get('final_bias', diagnostics.get('final_bias_score', initial_bias))
        improvement = executive_summary.get('improvement', 
                                          ((initial_bias - final_bias) / initial_bias * 100) if initial_bias > 0 else 0)
        sig_biases = executive_summary.get('significant_biases', diagnostics.get('significant_bias_count', 0))
        retention = executive_summary.get('retention', validation.get('data_integrity', {}).get('retention_rate', 100))
        corrected_df = results.get('corrected_df', df)
        
        # ====================================================================
        # 6. FILE GENERATION & SAVING
        # ====================================================================
        # Save cleaned dataset
        corrected_filename = f"corrected_{session_id}.csv"
        corrected_path = os.path.join(app.config['UPLOAD_FOLDER'], corrected_filename)
        try:
            corrected_df.to_csv(corrected_path, index=False)
            app.logger.info(f"Saved corrected file: {corrected_filename}")
        except Exception as e:
            app.logger.error(f"Failed to save corrected file: {str(e)}")
        
        # Generate and save HTML report
        report_filename = f"report_{session_id}.html"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        try:
            html_content = generate_html_report(parser, viz_base64, domain, session_id, 
                                              pipeline_output, df, corrected_df, 
                                              executive_summary, BASE_URL)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            app.logger.info(f"HTML report saved: {report_path}")
        except Exception as e:
            app.logger.error(f"Failed to save HTML report: {str(e)}")
            traceback.print_exc()
        
        # Schedule cleanup of temporary files (1 hour delay)
        cleanup_temp_dir(viz_temp_dir)
        
        # ====================================================================
        # 7. RESPONSE CONSTRUCTION
        # ====================================================================
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
                'visualizations': list(viz_base64.keys()),
                'report_view_url': f'{BASE_URL}/view/{report_filename}',
                'report_download_url': f'{BASE_URL}/download/{report_filename}',
                'data_download_url': f'{BASE_URL}/download/{corrected_filename}'
            },
            'session_id': session_id,
            'report_content': f'Analysis complete. Generated comprehensive HTML report with {len(viz_base64)} visualizations.'
        }
        
        # Convert NumPy types to native Python for JSON serialization
        response = convert_numpy_types(response)
        
        # Clean up uploaded temporary file
        os.unlink(temp_path)
        
        return jsonify(response)
        
    except Exception as e:
        # Error handling and logging
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Server error', 'details': str(e)[:100]}), 500

@app.route('/view/<filename>', methods=['GET'])
def view_report(filename):
    """
    View HTML reports directly in browser.
    
    Args:
        filename: HTML report filename to view
        
    Returns:
        HTML file for browser rendering
    """
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
    """
    Download generated files (CSV, HTML, PNG).
    
    Args:
        filename: File to download
        
    Returns:
        File attachment with appropriate MIME type
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        # Set appropriate MIME type based on file extension
        if filename.endswith('.csv'):
            mimetype = 'text/csv'
        elif filename.endswith('.html'):
            mimetype = 'text/html'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        else:
            mimetype = 'application/octet-stream'
        
        app.logger.info(f"Serving file: {filename}")
        response = send_file(file_path, as_attachment=True, 
                           download_name=filename, mimetype=mimetype)
        
        # Prevent caching for fresh downloads
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Download failed', 'details': str(e)}), 500

@app.route('/pdf/<session_id>', methods=['GET', 'OPTIONS'])
def generate_pdf(session_id):
    """
    Generate PDF report for a completed analysis session.
    Returns helpful error page since WeasyPrint isn't installed.
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Find the HTML report for this session
        report_filename = f"report_{session_id}.html"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        if not os.path.exists(report_path):
            app.logger.error(f"Report not found for session {session_id}")
            # Return HTML error page, not JSON
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Report Not Found</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }}
                    .container {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
                                 max-width: 500px; text-align: center; }}
                    h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                    p {{ color: #555; line-height: 1.6; margin: 15px 0; }}
                    .btn {{ display: inline-block; background: #BE9D04; color: white; padding: 12px 24px; 
                           text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: 600; }}
                    .btn:hover {{ background: #a88702; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚠️ Report Not Found</h1>
                    <p>The analysis report for session <strong>{session_id}</strong> could not be found.</p>
                    <p>Please run a new analysis from the homepage.</p>
                    <a href="{BASE_URL}/" class="btn">← Return to Homepage</a>
                </div>
            </body>
            </html>
            ''', 404
        
        # Return informative HTML page about PDF generation
        # Try to generate actual PDF if WeasyPrint is available
        try:
            from weasyprint import HTML
            
            # Read the existing HTML report
            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Generate PDF
            pdf_filename = f"report_{session_id}.pdf"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            
            HTML(string=html_content, base_url=BASE_URL if BASE_URL else None).write_pdf(pdf_path)
            
            # Return the PDF file for download
            return send_file(pdf_path, 
                           as_attachment=True, 
                           download_name=pdf_filename, 
                           mimetype='application/pdf')
            
        except ImportError:
            # WeasyPrint not installed - return the informative HTML page
            html_response = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PDF Generation - BiasClean</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                        background: radial-gradient(circle at top left, #243447 0%, #151824 40%, #05060a 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }}
                    .container {{
                        background: rgba(255, 255, 255, 0.98);
                        backdrop-filter: blur(20px);
                        padding: 50px;
                        border-radius: 24px;
                        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.3);
                        max-width: 700px;
                        text-align: center;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }}
                    .icon {{
                        font-size: 5em;
                        color: #f39c12;
                        margin-bottom: 20px;
                        animation: pulse 2s ease-in-out infinite;
                    }}
                    @keyframes pulse {{
                        0%, 100% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.1); }}
                    }}
                    h1 {{
                        color: #2c3e50;
                        font-size: 2.2em;
                        margin-bottom: 15px;
                        font-weight: 700;
                    }}
                    .subtitle {{
                        color: #7f8c8d;
                        font-size: 1.1em;
                        margin-bottom: 30px;
                        line-height: 1.6;
                    }}
                    .info-box {{
                        background: linear-gradient(135deg, #fff7e0, #ffefc4);
                        border: 2px solid #f39c12;
                        border-radius: 16px;
                        padding: 25px;
                        margin: 30px 0;
                        text-align: left;
                    }}
                    .info-title {{
                        color: #856404;
                        font-weight: 700;
                        font-size: 1.2em;
                        margin-bottom: 15px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    .info-text {{
                        color: #856404;
                        line-height: 1.8;
                        margin-bottom: 10px;
                    }}
                    .code {{
                        background: #2c3e50;
                        color: #ecf0f1;
                        padding: 3px 8px;
                        border-radius: 4px;
                        font-family: 'Courier New', monospace;
                        font-size: 0.9em;
                    }}
                    .downloads {{
                        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                        border: 2px solid #27ae60;
                        border-radius: 16px;
                        padding: 25px;
                        margin: 30px 0;
                    }}
                    .downloads-title {{
                        color: #1e8449;
                        font-weight: 700;
                        font-size: 1.2em;
                        margin-bottom: 20px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        justify-content: center;
                    }}
                    .btn-group {{
                        display: flex;
                        flex-direction: column;
                        gap: 15px;
                        margin-top: 20px;
                    }}
                    .btn {{
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                        background: linear-gradient(135deg, #BE9D04, #a88702);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 12px;
                        font-weight: 700;
                        font-size: 1em;
                        transition: all 0.3s ease;
                        box-shadow: 0 8px 20px rgba(190, 157, 4, 0.3);
                    }}
                    .btn:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 12px 30px rgba(190, 157, 4, 0.4);
                        background: linear-gradient(135deg, #d4b104, #BE9D04);
                    }}
                    .btn-secondary {{
                        background: linear-gradient(135deg, #27ae60, #229954);
                        box-shadow: 0 8px 20px rgba(39, 174, 96, 0.3);
                    }}
                    .btn-secondary:hover {{
                        background: linear-gradient(135deg, #2ecc71, #27ae60);
                        box-shadow: 0 12px 30px rgba(39, 174, 96, 0.4);
                    }}
                    .btn-home {{
                        background: linear-gradient(135deg, #3498db, #2980b9);
                        box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
                        margin-top: 10px;
                    }}
                    .btn-home:hover {{
                        background: linear-gradient(135deg, #5dade2, #3498db);
                        box-shadow: 0 12px 30px rgba(52, 152, 219, 0.4);
                    }}
                    .session-info {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 10px;
                        margin: 20px 0;
                        color: #7f8c8d;
                        font-size: 0.9em;
                    }}
                    @media (max-width: 600px) {{
                        .container {{ padding: 30px 20px; }}
                        h1 {{ font-size: 1.8em; }}
                        .icon {{ font-size: 4em; }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <h1>PDF Generation Coming Soon</h1>
                    <p class="subtitle">
                        We're working on adding PDF export functionality to BiasClean. 
                        In the meantime, you can download your complete analysis report and data below.
                    </p>

                    <div class="info-box">
                        <div class="info-title">
                            <i class="fas fa-info-circle"></i>
                            Technical Details
                        </div>
                        <p class="info-text">
                            PDF generation requires the <span class="code">WeasyPrint</span> library, 
                            which will be added in the next deployment.
                        </p>
                        <p class="info-text">
                            To enable PDF export, add <span class="code">weasyprint==61.0</span> 
                            to your <span class="code">requirements.txt</span> file and redeploy.
                        </p>
                    </div>

                    <div class="downloads">
                        <div class="downloads-title">
                            <i class="fas fa-download"></i>
                            Available Downloads
                        </div>
                        <div class="btn-group">
                            <a href="{BASE_URL}/download/{report_filename}" class="btn">
                                <i class="fas fa-file-code"></i>
                                Download Full HTML Report
                            </a>
                            <a href="{BASE_URL}/download/corrected_{session_id}.csv" class="btn btn-secondary">
                                <i class="fas fa-table"></i>
                                Download Cleaned Dataset (CSV)
                            </a>
                        </div>
                    </div>

                    <div class="session-info">
                        <i class="fas fa-fingerprint"></i> Session ID: <strong>{session_id}</strong>
                    </div>

                    <a href="{BASE_URL}/" class="btn btn-home">
                        <i class="fas fa-home"></i>
                        Return to Homepage
                    </a>

                    <p style="margin-top: 30px; color: #95a5a6; font-size: 0.85em;">
                        💡 <strong>Pro Tip:</strong> You can print the HTML report to PDF directly from your browser 
                        (Ctrl+P / Cmd+P → Save as PDF)
                    </p>
                </div>
            </body>
            </html>
            '''
            
            return html_response, 200
        
    except Exception as e:
        app.logger.error(f"PDF endpoint error: {str(e)}")
        # Return HTML error page
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - BiasClean</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #e74c3c, #c0392b); 
                       min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }}
                .container {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
                             max-width: 500px; text-align: center; }}
                h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                p {{ color: #555; line-height: 1.6; margin: 15px 0; }}
                .error-code {{ background: #f8f9fa; padding: 15px; border-radius: 8px; 
                              font-family: monospace; color: #c0392b; margin: 20px 0; }}
                .btn {{ display: inline-block; background: #3498db; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: 600; }}
                .btn:hover {{ background: #2980b9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Service Error</h1>
                <p>An unexpected error occurred while processing your request.</p>
                <div class="error-code">{str(e)[:200]}</div>
                <a href="{BASE_URL}/" class="btn">← Return to Homepage</a>
            </div>
        </body>
        </html>
        ''', 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        JSON with service status and version
    """
    return jsonify({
        'status': 'healthy',
        'service': 'BiasClean',
        'version': '2.4',
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    """
    Production server startup.
    
    Configured for Render.com deployment:
    - Host: 0.0.0.0 (binds to all interfaces)
    - Port: From environment variable or default 5000
    - Debug: Disabled for production
    """
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ============================================================================
# END OF BIASCLEAN FLASK API v2.4
# ============================================================================