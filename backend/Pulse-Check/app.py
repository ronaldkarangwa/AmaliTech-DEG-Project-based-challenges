import json
from flask import Flask, request, jsonify
from redis_client import get_redis

app = Flask(__name__)
r = get_redis()

@app.route('/monitors', methods=['POST'])
def create_monitor():
    data = request.json

    monitor_id = data["id"]
    timeout = data["timeout"]
    email = data["alert_email"]

    # Store Metadata in Redis
    r.set(
        f"monitor:{monitor_id}",
        json.dumps({
            "alert_email": email,
            "status": "active",
            "timeout": timeout
        })
    )

    # Start the Timer Key (Empty Value, expires in 'timeout' seconds)
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

@app.route("/monitors/<id>/pause", methods=["POST"])
def pause(id):
    metadata_raw = r.get(f"monitor:{id}")
    if not metadata_raw:
        return jsonify({"error": "not found"}), 404

    meta = json.loads(metadata_raw)
    meta["status"] = "paused"

    r.set(f"monitor:{id}", json.dumps(meta))
    r.delete(f"timer:{id}")

    return jsonify({"message": "paused"}), 200


if __name__ == "__main__":
    app.run(port=5000)