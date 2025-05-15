import os
import time

def block_ip(ip):
    # Block outgoing connections to the specified IP address using netsh
    block_command = f'netsh advfirewall firewall add rule name="Block {ip}" dir=out action=block remoteip={ip}'
    os.system(block_command)
    print(f"Blocked outbound traffic to {ip}")

def unblock_ip(ip):
    # Unblock IP address by removing the firewall rule
    unblock_command = f'netsh advfirewall firewall delete rule name="Block {ip}"'
    os.system(unblock_command)
    print(f"Unblocked outbound traffic to {ip}")

def check_ip_blacklist():
    # Read the blacklist of IPs from a file
    with open('config/blacklist.txt', 'r') as f:
        blacklisted_ips = f.readlines()
    
    for ip in blacklisted_ips:
        ip = ip.strip()
        block_ip(ip)
        time.sleep(1)  # Adding delay to prevent overloading the firewall with requests

if __name__ == '__main__':
    while True:
        check_ip_blacklist()
        time.sleep(3600)  # Run the check every hour
