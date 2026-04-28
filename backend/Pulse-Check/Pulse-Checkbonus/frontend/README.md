# 📡 Pulse Check Dashboard (Frontend)

A real-time monitoring dashboard for tracking device health using WebSockets and live countdown timers.

This frontend connects to a Flask backend and displays:
- 📡 Active devices (monitors)
- ⏱ Live countdown timers (TTL-based)
- 🚨 Instant alerts when devices go down
- 🔄 Real-time updates via WebSockets (no polling)

---

## 🚀 Features

- ⚡ Real-time updates using WebSockets (Socket.IO)
- ⏱ Accurate countdown timers (updated every second)
- 🚨 Live alert popups when a device goes down
- 🎯 Status-based UI (active / down / paused)
- 📊 Clean card-based dashboard layout

---

## 🧠 Architecture Overview
Frontend (React)
↓ WebSocket (Socket.IO)
Backend (Flask + SocketIO)
↓ Pub/Sub
Redis (TTL + Keyspace Events)


- Backend sends `expires_at` timestamps
- Frontend calculates countdown locally (efficient)
- Alerts are pushed instantly via WebSocket

---

## 📦 Tech Stack

- React
- Socket.IO Client
- CSS
- Fetch API

---

</> Markdown
```bash
## 📁 Project Structure
frontend/
│
├── src/
│ ├── App.js
│ ├── socket.js
│ ├── App.css
│ └── index.js
│
├── public/
├── package.json
└── README.md


---

## ⚙️ Installation

## 1. Navigate to frontend

```bash
cd frontend

2. Install dependencies
npm install

3. Start the app
npm start

App runs on:
http://127.0.0.1:5000


## 🔗 WebSocket Connection

Defined in:
// src/socket.js
import { io } from "socket.io-client";

export const socket = io("http://127.0.0.1:5000");

## ⏱ Countdown Logic

The countdown is calculated on the frontend:
const diff = expires_at - current_time;

## 🚨 Alerts System

When a device goes down:

Redis detects key expiration
Backend publishes alert
WebSocket pushes alert
UI displays popup instantly

Example:
{
  "id": "device1",
  "message": "🚨 device1 is DOWN",
  "time": 1710000000
}

## 🎨 UI States
| Status | Color | Behavior          |
| ------ | ----- | ----------------- |
| active | Green | Countdown running |
| down   | Red   | Alert state       |
| paused | Gray  | Timer stopped     |



WebSocket not connecting

Check browser console:
Connected: <socket_id>

## 📈 Future Improvements
Authentication
Historical logs
Notifications (email/SMS)
Docker deployment

👨‍💻 Author

Real-time monitoring dashboard built with React, Flask, Redis, and WebSockets.
