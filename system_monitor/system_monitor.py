import psutil
import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime
import os
import socket

# --- Configuration ---
SERVICE_ACCOUNT_KEY_PATH = 'serviceAccountKey.json'
DATABASE_URL = 'https://dlp-system-monitor-default-rtdb.firebaseio.com/'  # Replace this

# --- Firebase Initialization ---
try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    print("Firebase Realtime Database initialized successfully.")
except FileNotFoundError:
    print(f"Error: Service account key not found at '{SERVICE_ACCOUNT_KEY_PATH}'.")
    exit()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    exit()

# --- Health Monitoring Function ---
def get_computer_health():
    """
    Gathers various computer health metrics, including total RAM and Disk Storage.
    Returns a dictionary containing the current health data.
    """
    health_data = {}

    # CPU Usage
    health_data['cpu_percent'] = psutil.cpu_percent(interval=1)

    # Memory (RAM) Usage
    memory = psutil.virtual_memory()
    health_data['memory_total_gb'] = round(memory.total / (1024**3), 2)  # Total installed RAM
    health_data['memory_used_gb'] = round(memory.used / (1024**3), 2)    # RAM currently in use
    health_data['memory_percent'] = memory.percent                       # Percentage of RAM used

    # Disk Usage (Total Storage - often referred to as 'ROM' by users)
    # Note: 'ROM' (Read-Only Memory) is technically firmware. This reports total usable storage (HDD/SSD).
    try:
        # Use 'C:\\' for Windows, '/' for Linux/macOS
        disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
        health_data['disk_total_gb'] = round(disk.total / (1024**3), 2)  # Total disk space (HDD/SSD)
        health_data['disk_used_gb'] = round(disk.used / (1024**3), 2)    # Disk space currently used
        health_data['disk_percent'] = disk.percent                       # Percentage of disk used
    except Exception as e:
        print(f"Warning: Could not get disk usage. Error: {e}")
        health_data['disk_total_gb'] = None
        health_data['disk_used_gb'] = None
        health_data['disk_percent'] = None

    # Network I/O
    net_io = psutil.net_io_counters()
    health_data['network_bytes_sent_mb'] = round(net_io.bytes_sent / (1024**2), 2)
    health_data['network_bytes_recv_mb'] = round(net_io.bytes_recv / (1024**2), 2)

    # Boot Time
    health_data['boot_time'] = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')

    # Current Timestamp
    health_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Hostname
    health_data['hostname'] = socket.gethostname()

    return health_data

# --- Upload to Firebase Realtime Database ---
def send_data_to_firebase(data):
    try:
        hostname = data['hostname']
        # Realtime DB paths cannot contain '.', '#', '$', '[', or ']'
        # Replacing colons and spaces for a cleaner path
        timestamp = data['timestamp'].replace(":", "-").replace(" ", "_")
        
        ref = db.reference(f'computer_health/{hostname}/{timestamp}')
        ref.set(data)
        print(f"Data uploaded to Realtime DB under node: computer_health/{hostname}/{timestamp}")
    except Exception as e:
        print(f"Error uploading to Realtime DB: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    MONITOR_INTERVAL_SECONDS = 120  # 5 minutes
    print("--- Starting System Health Monitor ---")
    print(f"Data will be sent to Firebase Realtime Database every {MONITOR_INTERVAL_SECONDS} seconds.")
    print("Press Ctrl+C to stop the script.")

    while True:
        try:
            health_data = get_computer_health()
            
            print(f"\n--- Health Data Collected at {health_data['timestamp']} ---")
            print(f"  CPU Usage: {health_data['cpu_percent']}%")
            print(f"  Total RAM: {health_data['memory_total_gb']} GB")
            print(f"  Used RAM: {health_data['memory_used_gb']} GB ({health_data['memory_percent']}%)")
            print(f"  Total Disk Space: {health_data['disk_total_gb']} GB")
            print(f"  Used Disk Space: {health_data['disk_used_gb']} GB ({health_data['disk_percent']}%)")
            print(f"  Network Sent: {health_data['network_bytes_sent_mb']} MB")
            print(f"  Network Received: {health_data['network_bytes_recv_mb']} MB")
            print(f"  Boot Time: {health_data['boot_time']}")
            print(f"  Hostname: {health_data['hostname']}")

            send_data_to_firebase(health_data)
            
            time.sleep(MONITOR_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\nStopped by user (Ctrl+C). Exiting.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print(f"Retrying in {MONITOR_INTERVAL_SECONDS} seconds...")
            time.sleep(MONITOR_INTERVAL_SECONDS)

