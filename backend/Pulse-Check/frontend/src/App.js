import React, { useEffect, useState } from "react";
import axios from "axios";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

function App() {
  const [monitors, setMonitors] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Fetch monitors
  const fetchMonitors = async () => {
    try {
      const res = await axios.get("http://localhost:5000/monitors");
      setMonitors(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  // WebSocket listener
  useEffect(() => {
    socket.on("alert", (data) => {
      setAlerts((prev) => [...prev, data]);
      fetchMonitors(); // refresh state when alert comes
    });

    fetchMonitors();

    return () => socket.off("alert");
  }, []);

  // Countdown updater
  useEffect(() => {
    const interval = setInterval(() => {
      setMonitors((prev) =>
        prev.map((m) => ({
          ...m,
          remaining: m.remaining > 0 ? m.remaining - 1 : 0
        }))
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    if (status === "active") return "#22c55e";
    if (status === "paused") return "#f59e0b";
    if (status === "down") return "#ef4444";
    return "#64748b";
  };

  return (
    <div className="container">
      <h1>Pulse Check Dashboard</h1>

      <div className="grid">
        {monitors.map((m) => (
          <div className="card" key={m.id}>
            <h2>{m.id}</h2>

            <div
              className="status"
              style={{ background: getStatusColor(m.status) }}
            >
              {m.status.toUpperCase()}
            </div>

            <p>Timeout: {m.timeout}s</p>
            <p>Remaining: {m.remaining}s</p>

            <div className="progress-bar">
              <div
                className="progress"
                style={{
                  width: `${(m.remaining / m.timeout) * 100}%`
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="alerts">
        <h2>Alerts</h2>
        {alerts.map((a, i) => (
          <div key={i} className="alert">
            {a.id}: {a.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
