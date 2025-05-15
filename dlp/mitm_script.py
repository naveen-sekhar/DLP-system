from mitmproxy import http
from notifier import notify_user

# List of blacklisted domains where file uploads will be blocked
BLACKLISTED_DOMAINS = [
    "chat.openai.com",    # Example sites where uploads are blocked
    "mail.google.com", 
    "drive.google.com",
    "wetransfer.com",
    "transfer.sh"
]

def request(flow: http.HTTPFlow):
    # Check if the request is a file upload (multipart/form-data)
    if "multipart/form-data" in flow.request.headers.get("content-type", ""):
        domain = flow.request.pretty_host
        
        # Block uploads to blacklisted domains
        if domain in BLACKLISTED_DOMAINS:
            message = f"File upload to '{domain}' was blocked."
            notify_user(message)
            flow.response = http.Response.make(
                403,  # HTTP Status Code: Forbidden
                b"Upload blocked by DLP policy.", 
                {"Content-Type": "text/html"}
            )

def response(flow: http.HTTPFlow):
    # Allow download requests (detecting "Content-Disposition" header)
    if "attachment" in flow.response.headers.get("Content-Disposition", ""):
        # Allow the download
        pass  # No modification to response needed
