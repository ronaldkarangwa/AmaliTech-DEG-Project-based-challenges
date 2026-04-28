import json
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from redis_client import get_redis

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

r = get_redis()

DEFAULT_TIME_OUT = 60


# ---------------------------
# CREATE MONITOR
# ---------------------------
@app.route('/monitors', methods=['POST'])
def create_monitor():
    data = request.json or {}

    monitor_id = data.get("id")
    email = data.get("alert_email")
    timeout = data.get("timeout", DEFAULT_TIME_OUT)

    if not monitor_id or not email:
        return jsonify({"error": "id and alert_email required"}), 400

    r.set(
        f"monitor:{monitor_id}",
        json.dumps({
            "alert_email": email,
            "status": "active",
            "timeout": timeout
        })
    )

    # TTL countdown key
    r.setex(f"timer:{monitor_id}", timeout, "active")

    return jsonify({"message": "Monitor created"}), 201


# ---------------------------
# HEARTBEAT
# ---------------------------
@app.route('/monitors/<monitor_id>/heartbeat', methods=['POST'])
def heartbeat(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")

    if not metadata_raw:
        return jsonify({"error": "Monitor not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "active"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.setex(f"timer:{monitor_id}", meta["timeout"], "active")

    socketio.emit("alert", {
        "id": monitor_id,
        "message": "Heartbeat received"
    })

    return jsonify({"message": "Heartbeat received"}), 200


# ---------------------------
# PAUSE MONITOR
# ---------------------------
@app.route("/monitors/<monitor_id>/pause", methods=["POST"])
def pause(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")

    if not metadata_raw:
        return jsonify({"error": "not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "paused"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.delete(f"timer:{monitor_id}")

    socketio.emit("alert", {
        "id": monitor_id,
        "message": "Monitor paused"
    })

    return jsonify({"message": "paused"}), 200


# ---------------------------
# GET MONITORS
# ---------------------------
@app.route("/monitors", methods=["GET"])
def get_monitors():
    monitors = []

    for key in r.scan_iter("monitor:*"):
        monitor_id = key.split(":")[1]
        meta_raw = r.get(key)

        if not meta_raw:
            continue

        meta = json.loads(meta_raw)

        ttl = r.ttl(f"timer:{monitor_id}")
        remaining = ttl if ttl and ttl > 0 else 0

        monitors.append({
            "id": monitor_id,
            "status": meta["status"],
            "timeout": meta["timeout"],
            "remaining": remaining
        })

    return jsonify(monitors)


# ---------------------------
# BACKGROUND WATCHER
# ---------------------------
def redis_watcher():
    while True:
        for key in r.scan_iter("timer:*"):
            ttl = r.ttl(key)

            if ttl == -2:  # expired
                monitor_id = key.split(":")[1]

                meta_raw = r.get(f"monitor:{monitor_id}")
                if meta_raw:
                    meta = json.loads(meta_raw)
                    meta["status"] = "down"

                    r.set(f"monitor:{monitor_id}", json.dumps(meta))

                    socketio.emit("alert", {
                        "id": monitor_id,
                        "message": "Monitor is DOWN"
                    })

        time.sleep(2)


# ---------------------------
# START BACKGROUND THREAD
# ---------------------------
threading.Thread(target=redis_watcher, daemon=True).start()


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)