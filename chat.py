import os
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

LOG_FILE = "usb_monitor_log.txt"
monitored_drives = {}

def get_removable_drives():
    drives = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        if 'removable' in p.opts.lower():
            drives.append(p.device)
    return drives

def log_event(event_type, path, extra=''):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log:        
        log.write(f"[{timestamp}] {event_type}: {path} {extra}\n")
    print(f"[{timestamp}] {event_type}: {path} {extra}")

class USBEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            log_event("File Created", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            log_event("File Deleted", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            log_event("File Modified", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            log_event("File Renamed", f"FROM '{event.src_path}'", f"--> TO '{event.dest_path}'")
def start_monitoring(path):
    if path not in monitored_drives:
        event_handler = USBEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path=path, recursive=True)
        observer.start()
        monitored_drives[path] = observer
        log_event("Monitoring Started", path)

def stop_all_observers():
    for observer in monitored_drives.values():
        observer.stop()
        observer.join()
    monitored_drives.clear()

def detect_and_monitor_usb():
    current_removable = set(get_removable_drives())
    mounted = set(monitored_drives.keys())

    # New USB inserted
    new_drives = current_removable - mounted
    for drive in new_drives:
        start_monitoring(drive)

    # USB removed
    removed_drives = mounted - current_removable
    for drive in removed_drives:
        log_event("Monitoring Stopped", drive)
        monitored_drives[drive].stop()
        monitored_drives[drive].join()
        del monitored_drives[drive]

if __name__ == "__main__":
    print("🔍 USB Monitoring (Windows Only) Started. Press Ctrl+C to stop.\n")
    try:
        while True:
            detect_and_monitor_usb()
            time.sleep(2)  # Check every 2 seconds for USB changes
    except KeyboardInterrupt:
        print("\nStopping all monitors...")
        stop_all_observers()
        print("Exited cleanly.")
