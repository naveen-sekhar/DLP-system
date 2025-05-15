import logging
import os
import time
from datetime import datetime

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
upload_log_file = os.path.join(log_dir, 'upload_activity.log')

logging.basicConfig(
    filename=upload_log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def mock_upload_logger():
    # This is just a simulated logger for testing
    while True:
        logging.info(f"User attempted to upload file: sample_confidential.docx to https://fileshare.com at {datetime.now()}")
        time.sleep(60)  # Simulate an upload attempt every minute

if __name__ == "__main__":
    mock_upload_logger()
