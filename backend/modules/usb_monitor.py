import os
import time
import logging
import win32file
import win32api
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'usb_activity.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to get all removable drives
def get_removable_drives():
    drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    removable_drives = []
    for drive in drives:
        if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
            removable_drives.append(drive)
    return removable_drives

# File system event handler for USB monitoring
class USBFileSystemEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"[FILE CREATED] {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"[FILE MODIFIED] {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logging.info(f"[FILE DELETED] {event.src_path}")

# Dictionary to keep track of observers for each USB drive
active_observers = {}

# Start monitoring a USB drive
def start_monitoring(drive):
    if drive in active_observers:
        return  # Already monitoring

    print(f"[USB DETECTED] Monitoring: {drive}")
    event_handler = USBFileSystemEventHandler()
    observer = Observer()
    observer.schedule(event_handler, drive, recursive=True)
    observer.start()
    active_observers[drive] = observer
    logging.info(f"[START MONITORING] {drive}")

# Stop monitoring a USB drive
def stop_monitoring(drive):
    observer = active_observers.pop(drive, None)
    if observer:
        observer.stop()
        observer.join()
        print(f"[USB REMOVED] Stopped monitoring: {drive}")
        logging.info(f"[STOP MONITORING] {drive}")

# Main monitoring loop
def monitor_usb_continuously(poll_interval=5):
    print("[USB MONITOR] Started. Waiting for USB activity...")

    try:
        while True:
            current_usb_drives = set(get_removable_drives())
            monitored_drives = set(active_observers.keys())

            # Start monitoring new USBs
            for drive in current_usb_drives - monitored_drives:
                start_monitoring(drive)

            # Stop monitoring removed USBs
            for drive in monitored_drives - current_usb_drives:
                stop_monitoring(drive)

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("[USB MONITOR] Stopping...")
        for drive in list(active_observers.keys()):
            stop_monitoring(drive)

if __name__ == "__main__":
    monitor_usb_continuously()
