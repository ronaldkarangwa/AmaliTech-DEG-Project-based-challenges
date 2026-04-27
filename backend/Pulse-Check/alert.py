import redis
import json
from datetime import datetime
from app.redis_client import get_redis


r = get_redis()

def check_alerts():
    # Subscribe to Redis key expiration events
    pubsub = r.pubsub()

    # Requires Redis to be configured with 'notify-keyspace-events Ex' to receive expired key events    
    pubsub.subscribe('__keyevent@0__:expired')
    print("Alert system is running and listening for expired keys...")

    # The infinite loop to listen for expired keys 
    for message in pubsub.listen():
        if message['type'] == 'message':
            continue
        
        key = msg["data"]

        if not isinstance(key, str) or not key.startswith("timer:"):
            continue

        monitor_id = key.split(":")[1]
        metadata_raw = r.get(f"monitor:{monitor_id}")

        if not metadata_raw:
            continue

        meta = json.loads(metadata_raw)

        # PAUSE SAFETY CHECK: If the monitor is paused, we should not mark it as down
        if meta.get("status") == "paused":
            continue

        meta["status"] = "down"
        r.set(f"monitor:{monitor_id}", json.dumps(meta))

        print(json.dumps({
            "ALERT": f"Device {monitor_id} is down!",
            "time": datetime.utcnow().isoformat()
        }))


if __name__ == "__main__":
    check_alerts()
