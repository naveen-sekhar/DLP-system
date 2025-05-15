class AnomalyDetector:
    def __init__(self):
        self.normal_behavior = {}  # Define thresholds for normal behavior

    def detect_anomaly(self, user_id, action):
        # Check if the action is anomalous
        if user_id not in self.normal_behavior:
            self.normal_behavior[user_id] = {"file_access_count": 0}
        
        if action == "file_access":
            self.normal_behavior[user_id]["file_access_count"] += 1
            if self.normal_behavior[user_id]["file_access_count"] > 10:  # Anomaly threshold
                print(f"Anomaly detected for {user_id}")
                # Trigger alert/response action
