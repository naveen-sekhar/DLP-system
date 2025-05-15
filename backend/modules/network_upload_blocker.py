import requests

def block_file_upload(destination_url, allowed_websites):
    if destination_url not in allowed_websites:
        print(f"Upload attempt blocked to {destination_url}")
        return False  # Block upload
    return True
