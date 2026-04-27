import json
from datetime import datetime
from redis_client import get_redis

r = get_redis()

def check_alerts():
    pubsub = r.pubsub()
    pubsub.subscribe('__keyevent@0__:expired')

    print("Alert system is running and listening for expired keys...")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        key = message["data"]

        if not isinstance(key, str) or not key.startswith("timer:"):
            continue

        monitor_id = key.split(":")[1]
        metadata_raw = r.get(f"monitor:{monitor_id}")

        if not metadata_raw:
            continue

        try:
            meta = json.loads(metadata_raw)
        except Exception:
            continue

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