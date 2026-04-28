import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
pubsub = r.pubsub()

pubsub.psubscribe('__keyevent@0__:expired')

print("Worker listening for expired timers...")

for msg in pubsub.listen():
    if msg["type"] != "pmessage":
        continue

    key = msg["data"]

    if not key.startswith("timer:"):
        continue

    monitor_id = key.split(":")[1]
    meta_raw = r.get(f"monitor:{monitor_id}")

    if not meta_raw:
        continue

    meta = json.loads(meta_raw)

    if meta.get("status") == "paused":
        continue

    # Mark as DOWN
    meta["status"] = "down"
    r.set(f"monitor:{monitor_id}", json.dumps(meta))

    # 🔥 Publish event (THIS is the important part)
    r.publish("alerts", json.dumps({
        "id": monitor_id,
        "status": "down"
    }))

    print(f"[ALERT] {monitor_id} is DOWN")