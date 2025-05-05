import sys
import os

# Ensure parent directory (DLP-system) is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template
from backend.modules.usb_monitor import monitor_usb
# You can import other backend modules similarly

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")  # Assuming dashboard.html is in templates/

if __name__ == "__main__":
    app.run(debug=True)
