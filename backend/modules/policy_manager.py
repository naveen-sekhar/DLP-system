import json
import os

class PolicyManager:
    def __init__(self):
        self.policy_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'policies.json')
        self.policies = {}
        self.load_policies()

    def load_policies(self):
        try:
            with open(self.policy_file, 'r') as f:
                self.policies = json.load(f)
        except FileNotFoundError:
            print("[ERROR] policies.json not found.")
            self.policies = {}

    def apply_policies(self, activity):
        if activity['type'] == 'USB':
            return self.apply_usb_policy(activity)
        elif activity['type'] == 'upload':
            return self.apply_upload_policy(activity)
        else:
            print("[POLICY] Unknown activity type")
            return False

    def apply_usb_policy(self, activity):
        usb_policy = self.policies.get("usb_policy", {})
        allowed_devices = usb_policy.get("allowed_devices", [])
        block_unknown = usb_policy.get("block_on_unknown", True)

        if block_unknown and activity.get('device') not in allowed_devices:
            print(f"[USB BLOCKED] Device {activity['device']} not allowed")
            return False
        print(f"[USB ALLOWED] Device {activity['device']}")
        return True

    def apply_upload_policy(self, activity):
        upload_policy = self.policies.get("upload_policy", {})
        block_untrusted = upload_policy.get("block_untrusted_websites", True)
        allowed_extensions = upload_policy.get("allowed_extensions", [".pdf", ".docx", ".xlsx"])

        if block_untrusted and activity.get("website") not in ["trusted.com", "safeportal.com"]:
            print(f"[UPLOAD BLOCKED] Upload to {activity['website']} is not allowed")
            return False

        ext = os.path.splitext(activity.get("filename", ""))[1]
        if ext not in allowed_extensions:
            print(f"[UPLOAD BLOCKED] File extension {ext} not allowed")
            return False

        print(f"[UPLOAD ALLOWED] File upload passed policy check")
        return True
