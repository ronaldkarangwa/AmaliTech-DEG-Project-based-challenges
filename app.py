import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from redis_client import get_redis

app = Flask(__name__)
CORS(app)  

r = get_redis() 
alerts = []
expiry = int(time()) + timeout

@app.route('/monitors', methods=['POST'])
def create_monitor():
    data = request.json

    monitor_id = data["id"]
    timeout = data["timeout"]
    email = data["alert_email"]

    r.set(
        f"monitor:{monitor_id}",
        json.dumps({
            "alert_email": email,
            "status": "active",
            "timeout": timeout
        })
    )

    r.setex(f"timer:{monitor_id}", timeout, "active")

    return jsonify({"message": "Monitor created successfully"}), 201


@app.route('/monitors/<monitor_id>/heartbeat', methods=['POST'])
def heartbeat(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")
    if not metadata_raw:
        return jsonify({"error": "Monitor not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "active"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.setex(f"timer:{monitor_id}", meta["timeout"], "active")

    return jsonify({"message": "Heartbeat received"}), 200


@app.route("/monitors/<monitor_id>/pause", methods=["POST"])
def pause(monitor_id):
    metadata_raw = r.get(f"monitor:{monitor_id}")
    if not metadata_raw:
        return jsonify({"error": "not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "paused"

    r.set(f"monitor:{monitor_id}", json.dumps(meta))
    r.delete(f"timer:{monitor_id}")

    return jsonify({"message": "paused"}), 200



@app.route("/monitors", methods=["GET"])
def get_monitors():
    keys = r.keys("monitor:*")
    monitors = []

    for key in keys:
        monitor_id = key.split(":")[1]
        meta = json.loads(r.get(key))

        ttl = r.ttl(f"timer:{monitor_id}")  # seconds remaining

        monitors.append({
            "id": monitor_id,
            "status": meta["status"],
            "timeout": meta["timeout"],
            "remaining": ttl if ttl > 0 else 0
        })

    return jsonify(monitors)

@app.route("/alerts", methods=["POST"])
def receive_alert():
    data = request.json
    alerts.append(data)
    return {"status": "received"}, 200


@app.route("/alerts", methods=["GET"])
def get_alerts():
    return jsonify(alerts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)