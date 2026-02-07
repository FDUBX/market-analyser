#!/usr/bin/env python3
"""
Send Telegram notification by creating a request file for the agent to process
"""
import sys
import json
from datetime import datetime
import os

def send_notification(message):
    """Create a notification request file"""
    notifications_dir = "/home/pi/.openclaw/workspace/skills/market-analyzer/notifications"
    os.makedirs(notifications_dir, exist_ok=True)
    
    # Create notification file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{notifications_dir}/notify_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "channel": "telegram",
        "target": "6812190723",
        "processed": False
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Notification queued: {filename}")
    return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: send_telegram.py <message>")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    send_notification(message)
