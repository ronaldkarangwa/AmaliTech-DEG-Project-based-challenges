import json
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from redis_client import get_redis

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
r = get_redis()

alerts = []  # ✅ FIX

# 🔥 Listen to Redis alerts channel → push to React
def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("alerts")

    for msg in pubsub.listen():
        if msg["type"] != "message":
            continue

        data = json.loads(msg["data"])
        alerts.append(data)  # store history

        socketio.emit("alert", data)

# 🔥 Watch Redis expiry → generate alerts
def expiry_watcher():
    pubsub = r.pubsub()
    pubsub.psubscribe("__keyevent@0__:expired")

    for msg in pubsub.listen():
        if msg["type"] != "pmessage":
            continue

        key = msg["data"]

        if not isinstance(key, str) or not key.startswith("timer:"):
            continue

        monitor_id = key.split(":")[1]

        metadata_raw = r.get(f"monitor:{monitor_id}")
        if not metadata_raw:
            continue

        meta = json.loads(metadata_raw)

        if meta.get("status") == "paused":
            continue

        meta["status"] = "down"
        r.set(f"monitor:{monitor_id}", json.dumps(meta))

        alert = {
            "id": monitor_id,
            "message": f"Device {monitor_id} is DOWN",
            "time": int(time.time())
        }

        r.publish("alerts", json.dumps(alert))

threading.Thread(target=redis_listener, daemon=True).start()
threading.Thread(target=expiry_watcher, daemon=True).start()


@app.route('/monitors', methods=['GET'])
def get_monitors():
    keys = r.keys("monitor:*")
    monitors = []

    now = int(time.time())

    for key in keys:
        data = r.get(key)
        if data:
            monitor_id = key.split(":")[1]

            meta = json.loads(data)
            ttl = r.ttl(f"timer:{monitor_id}")
            expires_at = now + ttl if ttl > 0 else now

            monitors.append({
                "id": monitor_id,
                "status": meta["status"],
                "timeout": meta["timeout"],
                "expires_at": expires_at
            })

    return jsonify(monitors)