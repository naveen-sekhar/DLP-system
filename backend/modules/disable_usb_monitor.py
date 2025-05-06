import os
import time
import logging
import win32file
import win32api
from plyer import notification
import subprocess

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'diaable_logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'usb_activity.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get all removable drives
def get_removable_drives():
    drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    removable_drives = []
    for drive in drives:
        if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
            removable_drives.append(drive)
    return removable_drives

# Disable USB drive via diskpart
def disable_usb_drive(drive_letter):
    try:
        diskpart_cmd = f"""
        select volume {drive_letter[0]}
        remove
        offline volume
        """
        script_path = os.path.join(os.getcwd(), "disable_usb.txt")
        with open(script_path, "w") as f:
            f.write(diskpart_cmd)
        
        subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True)
        logging.info(f"[BLOCKED] USB drive {drive_letter} has been disabled.")
        os.remove(script_path)
    except Exception as e:
        logging.error(f"[ERROR] Failed to disable USB {drive_letter}: {e}")

# Show notification
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="USB Monitor",
        timeout=5
    )

# Monitor for new USB devices and block them
def monitor_and_block_usb():
    known_drives = set(get_removable_drives())
    print("[USB Monitor] Running...")

    try:
        while True:
            current_drives = set(get_removable_drives())
            new_drives = current_drives - known_drives
            if new_drives:
                for drive in new_drives:
                    logging.info(f"[DETECTED] USB Drive inserted: {drive}")
                    show_notification("USB Blocked", "USB not allowed")
                    disable_usb_drive(drive)
                known_drives = current_drives
            time.sleep(2)
    except KeyboardInterrupt:
        print("[USB Monitor] Stopped")

if __name__ == "__main__":
    monitor_and_block_usb()
