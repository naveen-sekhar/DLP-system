import subprocess
import time
import logging
import os

# Setup logging for Sysmon
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'sysmon_activity.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to start Sysmon
def run_sysmon():
    sysmon_path = r'C:\Sysmon\Sysmon64.exe'
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sysmon-config.xml')
    
    # Run Sysmon as subprocess
    process = subprocess.Popen([sysmon_path, '-c', config_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Read the logs continuously
    while True:
        output = process.stdout.readline()
        if output:
            logging.info(output.decode('utf-8').strip())
        else:
            break
    
# Run Sysmon monitoring
if __name__ == "__main__":
    run_sysmon()
