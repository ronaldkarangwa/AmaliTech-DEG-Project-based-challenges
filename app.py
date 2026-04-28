import json
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from redis_client import get_redis

DEFAULT_TIMEOUT = 60

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
r = get_redis()

alerts = []


# ---------------------------
# LIVE MONITOR BROADCAST
# ---------------------------
def emit_monitors_update():
    keys = r.keys("monitor:*")
    monitors = []

    now = int(time.time())

    for key in keys:
        data = r.get(key)
        if not data:
            continue

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

    socketio.emit("monitors:update", monitors)


# ---------------------------
# REDIS ALERT LISTENER
# ---------------------------
def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("alerts")

    for msg in pubsub.listen():
        if msg["type"] != "message":
            continue

        data = json.loads(msg["data"])
        alerts.append(data)

        socketio.emit("alert", data)
        emit_monitors_update()


# ---------------------------
# EXPIRY WATCHER
# ---------------------------
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
        emit_monitors_update()


# ---------------------------
# START BACKGROUND WORKERS
# ---------------------------
threading.Thread(target=redis_listener, daemon=True).start()
threading.Thread(target=expiry_watcher, daemon=True).start()


# ---------------------------
# API ROUTES
# ---------------------------
@app.route('/monitors', methods=['POST'])
def create_monitor():
    data = request.json

    monitor_id = data["id"]
    timeout = data.get("timeout", DEFAULT_TIMEOUT)  # 🔥 default 60s
    email = data["alert_email"]

    r.set(
        f"monitor:{monitor_id}",
        json.dumps({
            "alert_email": email,
            "status": "active",
            "timeout": timeout
        })
    )

    # ALWAYS 60 seconds if not provided
    r.setex(f"timer:{monitor_id}", timeout, "active")

    emit_monitors_update()

    return jsonify({"message": "Monitor created"}), 201


@app.route("/monitors/<monitor_id>/heartbeat", methods=["POST"])
def heartbeat(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")
    if not metadata_raw:
        return jsonify({"error": "not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "active"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.setex(f"timer:{monitor_id}", meta["timeout"], "active")

    emit_monitors_update()

    return jsonify({"message": "heartbeat ok"}), 200


@app.route("/monitors/<monitor_id>/pause", methods=["POST"])
def pause(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")
    if not metadata_raw:
        return jsonify({"error": "not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "paused"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.delete(f"timer:{monitor_id}")

    emit_monitors_update()

    return jsonify({"message": "paused"}), 200


@app.route("/alerts", methods=["GET"])
def get_alerts():
    return jsonify(alerts)

@socketio.on("connect")
def on_connect():
    emit_monitors_update()


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)