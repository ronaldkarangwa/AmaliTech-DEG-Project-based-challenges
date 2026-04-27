import redis
import json
from datetime import datetime

r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def check_alerts():
    # Subscribe to Redis key expiration events
    pubsub = r.pubsub()
    pubsub.subscribe('__keyevent@0__:expired')
    print("Alert system is running and listening for expired keys...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            expired_key = message['data']
            
            # Check if the expired key is a timer key
            if expired_key.startswith("timer:"):
                monitor_id = expired_key.split(":")[1]
                # Fetch monitor metadata to get alert email
                metadata_raw = r.get(f'monitor:{monitor_id}')
                if metadata_raw:
                    metadata = json.loads(metadata_raw)
                    # Update status to 'down' in metadata
                    metadata["status"] = "down"
                    r.set(f'monitor:{monitor_id}', json.dumps(metadata))
                    # Trigger alert
                    alert_payload = {
                        "ALERT": f"Monitor {monitor_id} is down!",
                        "email": metadata["alert_email"],
                        "time": datetime.now().isoformat()
                    }
                    print(json.dumps(alert_payload, indent=2))  # Simulate sending alert (e.g., via email or webhook)

if __name__ == "__main__":
    check_alerts()
