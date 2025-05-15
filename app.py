import sys
import os
from flask import Flask, render_template, jsonify
from backend.modules.usb_monitor import monitor_usb
from backend.modules.policy_manager import PolicyManager
from backend.modules.anomaly_detector import AnomalyDetector
from backend.modules.network_upload_blocker import block_file_upload

# Ensure parent directory (DLP-system) is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")  # Assuming dashboard.html is in templates/

@app.route("/api/get_dashboard_data")
def get_dashboard_data():
    # Example data for the dashboard
    data = {
        'usb_activity': [3, 7, 4],  # Example data
        'upload_attempts': [2, 5, 1],  # Example data
        'anomalies_detected': [0, 2, 3]  # Example data
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
