#!/usr/bin/env python3
"""
Bejaa Digital Website Optimization Scanner - Web Application
Simple Flask app to serve the scanner interface
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from scanner import WebsiteScanner
from report_generator import generate_html_report

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Ensure directories exist
os.makedirs('reports', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

@app.route('/')
def index():
    """Render the main scanner page"""
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_website():
    """API endpoint to scan a website"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        scanner = WebsiteScanner(url)
        success = scanner.run_full_scan()

        # Strip internal-only fields before sending to frontend
        STRIP_FIELDS = {'html_content', 'response_headers'}
        payload = {k: v for k, v in scanner.results.items() if k not in STRIP_FIELDS}

        if success:
            try:
                json_filename = scanner.save_results(format="json")
                payload['report_url'] = f'/reports/{json_filename}'
            except Exception as e:
                print(f"[WARN] Could not save JSON report: {e}")

            try:
                html_filename = generate_html_report(scanner.results)
                payload['html_report_url'] = f'/reports/{html_filename}'
            except Exception as e:
                print(f"[WARN] Could not generate HTML report: {e}")

            return jsonify(payload)

        # Build a clear error message from what the scanner recorded
        conn = scanner.results.get('connectivity', {})
        scan_err = scanner.results.get('error', '')

        if conn.get('timeout'):
            msg = "Connection timeout — the website took too long to respond."
        elif conn.get('ssl_error'):
            msg = "SSL error — try scanning with http:// instead of https://"
        elif conn.get('connection_error'):
            msg = "Connection failed — the website may be down or unreachable."
        elif conn.get('status_code') and conn['status_code'] != 200:
            msg = f"Website returned HTTP {conn['status_code']} — it may be blocking automated requests or require a login."
        elif conn.get('error'):
            msg = conn['error']
        elif scan_err:
            msg = scan_err
        else:
            msg = "Scan failed. Check the URL and try again."

        return jsonify({'error': msg, 'details': conn}), 422

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500

@app.route('/reports/<filename>')
def get_report(filename):
    """Serve generated reports"""
    return send_from_directory('reports', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/examples')
def get_examples():
    """Get example websites for testing"""
    return jsonify({
        'examples': [
            'https://example.com',
            'https://google.com',
            'https://github.com',
            'https://stackoverflow.com',
            'https://bejaadigital.com',
            'https://ozocommercial.com.my'
        ]
    })

@app.route('/api/recent-reports')
def get_recent_reports():
    """Get list of recent scan reports"""
    try:
        reports = []
        reports_dir = 'reports'
        if os.path.exists(reports_dir):
            files = os.listdir(reports_dir)
            # Sort by modification time, newest first
            files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
            
            for file in files[:10]:  # Get 10 most recent
                if file.endswith('.json'):
                    filepath = os.path.join(reports_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            reports.append({
                                'filename': file,
                                'url': data.get('url', 'Unknown'),
                                'scan_date': data.get('scan_date', 'Unknown'),
                                'score': data.get('overall_score', 0),
                                'grade': data.get('grade', 'F')
                            })
                        except:
                            continue
        
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("🚀 Bejaa Digital Website Optimization Scanner")
    print("📡 Starting web server on http://localhost:5000")
    print("🔍 Access the scanner at: http://localhost:5000")
    print("\nTo install dependencies:")
    print("pip install -r requirements.txt")
    print("\nTo run the scanner directly:")
    print("python scanner.py https://example.com")
    
    app.run(debug=True, host='0.0.0.0', port=5000)