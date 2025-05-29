import os
import time
import logging
import datetime
import platform

# Windows-specific imports
try:
    import wmi
    import win32file
    import win32api
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WINDOWS_LIBS_AVAILABLE = True
except ImportError:
    WINDOWS_LIBS_AVAILABLE = False
    print("ERROR: Required Windows libraries (wmi, pywin32, watchdog) not found.")
    print("Please install them: pip install wmi pywin32 watchdog")
    exit() # Exit if critical libraries aren't available

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'monitor_logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'usb_activity.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Logging Function ---
def log_event(event_type, description):
    """Logs events to file and prints to console."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {event_type}: {description}"
    logging.info(log_message)
    print(log_message) # Also print to console for immediate feedback

# --- Functions for Detecting Removable Drives ---
def get_removable_drives():
    """Returns a list of currently connected removable drive letters (e.g., ['D:\\', 'E:\\'])."""
    drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    removable_drives = []
    for drive in drives:
        try:
            # DRIVE_REMOVABLE includes USB drives, but also floppy drives (less common now)
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                removable_drives.append(drive)
        except Exception as e:
            # Log issues with inaccessible drives without crashing
            logging.debug(f"Could not get drive type for {drive}: {e}")
    return removable_drives

# --- Common Local Monitor Paths (for files copied TO the computer) ---
def get_local_monitor_paths():
    """Returns a list of common user directories to monitor for file creations."""
    user_profile = os.environ.get('USERPROFILE')
    if not user_profile:
        log_event("WARNING", "USERPROFILE environment variable not found. Cannot determine common local monitor paths.")
        return []

    paths = [
        os.path.join(user_profile, 'Desktop'),
        os.path.join(user_profile, 'Downloads'),
        os.path.join(user_profile, 'Documents'),
        os.path.join(user_profile, 'Pictures'),
        os.path.join(user_profile, 'Videos'),
        os.path.join(user_profile, 'Music'),
    ]
    # Filter out paths that don't exist
    existing_paths = [p for p in paths if os.path.isdir(p)]
    return existing_paths

# Dictionary to keep track of watchdog observers for each USB drive AND local paths
# Key: path (e.g., 'D:\\', 'C:\\Users\\User\\Desktop\\'), Value: Observer instance
active_observers = {}

# --- File System Event Handler for USB Monitoring and Local Monitoring ---
class GeneralFileSystemEventHandler(FileSystemEventHandler):
    """Handles file system events for both USB drives and local directories."""
    def __init__(self, monitored_path_type):
        super().__init__()
        self.monitored_path_type = monitored_path_type # "USB" or "LOCAL"

    def on_created(self, event):
        if not event.is_directory:
            if self.monitored_path_type == "USB":
                log_event("FILE CREATED ON USB", f"Path: {event.src_path}")
            elif self.monitored_path_type == "LOCAL":
                log_event("FILE CREATED ON LOCAL DRIVE", f"Potential copy FROM external source. Path: {event.src_path}")
                # You could add more advanced logic here (e.g., hash comparison with connected USBs)
                # to try and confirm the source, but it adds significant complexity.
                log_event("INFERENCE TIP", "To determine if this file was copied from a pendrive, check currently connected USBs for a file with the same name/content around this time.")

    def on_modified(self, event):
        if not event.is_directory:
            if self.monitored_path_type == "USB":
                log_event("FILE MODIFIED ON USB", f"Path: {event.src_path}")
            elif self.monitored_path_type == "LOCAL":
                log_event("FILE MODIFIED ON LOCAL DRIVE", f"Path: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            if self.monitored_path_type == "USB":
                log_event("FILE DELETED ON USB", f"Path: {event.src_path}")
                log_event("INFERENCE TIP", "A file deleted from USB might indicate it was moved to local or deleted permanently.")
            elif self.monitored_path_type == "LOCAL":
                log_event("FILE DELETED FROM LOCAL DRIVE", f"Path: {event.src_path}")

# --- Functions for Starting/Stopping File System Monitoring ---
def start_file_system_monitoring(path, path_type):
    """Starts monitoring a specific path's file system for changes."""
    if path in active_observers:
        return  # Already monitoring

    log_event(f"STARTING {path_type} MONITOR", f"Monitoring path: {path}")
    event_handler = GeneralFileSystemEventHandler(monitored_path_type=path_type)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    active_observers[path] = observer

def stop_file_system_monitoring(path):
    """Stops monitoring a specific path's file system."""
    observer = active_observers.pop(path, None)
    if observer:
        observer.stop()
        observer.join()
        log_event(f"STOPPED MONITOR", f"Monitoring stopped for path: {path}")

# --- Main USB Monitoring Logic for Windows ---
def monitor_windows_usb_activity():
    """Continuously monitors USB device connections/disconnections and file system changes."""
    c = wmi.WMI()
    log_event("USB MONITOR STATUS", "Started. Waiting for USB device activity and local file changes...")
    print(f"Detailed logs are being saved to: {log_file}")

    # Track currently detected WMI USB devices by their DeviceID
    current_wmi_usb_device_ids = set()
    # Track currently monitored removable drive letters (for USBs)
    current_monitored_removable_drives = set()
    # Track currently monitored local paths (these are static once set up)
    current_monitored_local_paths = set()


    # Initial scan for currently connected USB devices (WMI)
    for usb in c.Win32_PnPEntity():
        if usb.Caption and ("USB" in usb.Caption or "Mass Storage" in usb.Caption or "Disk Drive" in usb.Caption):
            if usb.DeviceID:
                current_wmi_usb_device_ids.add(usb.DeviceID)
                log_event("INITIAL USB DETECTED (WMI)", f"Caption: {usb.Caption}, Device ID: {usb.DeviceID}")

    # Initial scan for removable drives and start file system monitoring on them
    initial_removable_drives = get_removable_drives()
    for drive in initial_removable_drives:
        start_file_system_monitoring(drive, "USB")
        current_monitored_removable_drives.add(drive)

    # Initial setup for local path monitoring
    local_paths_to_monitor = get_local_monitor_paths()
    if local_paths_to_monitor:
        for path in local_paths_to_monitor:
            start_file_system_monitoring(path, "LOCAL")
            current_monitored_local_paths.add(path)
    else:
        log_event("WARNING", "No common local directories found to monitor for files copied to computer.")


    try:
        while True:
            # --- WMI-based USB Connection/Disconnection Detection ---
            new_wmi_device_ids = set()
            for usb in c.Win32_PnPEntity():
                if usb.Caption and ("USB" in usb.Caption or "Mass Storage" in usb.Caption or "Disk Drive" in usb.Caption):
                    if usb.DeviceID:
                        new_wmi_device_ids.add(usb.DeviceID)

            # Detect newly connected devices (WMI)
            connected_wmi_devices = new_wmi_device_ids - current_wmi_usb_device_ids
            for device_id in connected_wmi_devices:
                for usb in c.Win32_PnPEntity(DeviceID=device_id):
                    log_event("USB CONNECTED (WMI)", f"Caption: {usb.Caption}, Device ID: {usb.DeviceID}")

            # Detect disconnected devices (WMI)
            disconnected_wmi_devices = current_wmi_usb_device_ids - new_wmi_device_ids
            for device_id in disconnected_wmi_devices:
                log_event("USB DISCONNECTED (WMI)", f"Device ID: {device_id}")

            current_wmi_usb_device_ids = new_wmi_device_ids # Update WMI state

            # --- Removable Drive File System Monitoring (Watchdog) ---
            current_removable_drives = set(get_removable_drives())

            # Start monitoring new removable drives
            for drive in current_removable_drives - current_monitored_removable_drives:
                start_file_system_monitoring(drive, "USB")

            # Stop monitoring removed removable drives
            for drive in current_monitored_removable_drives - current_removable_drives:
                stop_file_system_monitoring(drive)

            current_monitored_removable_drives = current_removable_drives # Update USB watchdog state

            # Local paths are monitored continuously via the observers started initially.
            # No dynamic changes needed for them in the loop.

            time.sleep(2) # Check every 2 seconds for new/removed drives

    except KeyboardInterrupt:
        log_event("USB MONITOR STATUS", "Stopping monitoring due to user interruption (Ctrl+C).")
        # Ensure all watchdog observers are stopped cleanly
        for path in list(active_observers.keys()):
            stop_file_system_monitoring(path)
    except Exception as e:
        log_event("CRITICAL ERROR", f"An unhandled error occurred: {e}")
        logging.critical("Unhandled exception in main monitoring loop", exc_info=True)


if __name__ == "__main__":
    if platform.system() == "Windows":
        monitor_windows_usb_activity()
    else:
        log_event("UNSUPPORTED OS", f"This script is designed for Windows. Detected OS: {platform.system()}")
        print("This script is specifically for Windows. Please run it on a Windows machine.")