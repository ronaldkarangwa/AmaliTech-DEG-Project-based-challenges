import json
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

@app.route('/monitors', methods=['POST'])
def create_monitor():
    data = request.json
    monitor_id = data.get('id')
    timeout = data.get('timeout')
    email = data.get('alert_email')

    # Store Metadata in Redis
    r.set(f'monitor:{monitor_id}', json.dumps({
        "alert_email": email,
        "status": "active"
        "timeout": timeout
    }))

    # Start the Timer Key (Empty Value, expires in 'timeout' seconds)
    r.setex(f"timer:{monitor_id}", timeout, "active")

    return jsonify({"message": "Monitor created successfully", "monitor_id": monitor_id}), 201