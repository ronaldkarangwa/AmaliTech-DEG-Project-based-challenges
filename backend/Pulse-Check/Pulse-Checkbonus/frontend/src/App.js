import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:5000";

function App() {
  const [monitors, setMonitors] = useState([]);

  const fetchMonitors = async () => {
    const res = await fetch(`${API}/monitors`);
    const data = await res.json();
    setMonitors(data);
  };

  const createMonitor = async () => {
    await fetch(`${API}/monitors`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: "device-" + Date.now(),
        timeout: 15,
        alert_email: "test@critmon.com"
      })
    });
    fetchMonitors();
  };

  const heartbeat = async (id) => {
    await fetch(`${API}/monitors/${id}/heartbeat`, { method: "POST" });
    fetchMonitors();
  };

  const DEFAULT_TIMEOUT = 60; // seconds
  const getCountdown = (expiresAt, timeout = DEFAULT_TIMEOUT) => {
  const now = Math.floor(Date.now() / 1000);
  const diff = expiresAt - now;

  if (diff <= 0) return "0s";

  const m = Math.floor(diff / 60);
  const s = diff % 60;

  return `${m}m ${s}s`;
};
  const getProgress = (expiresAt, timeout = 60) => {
  const now = Math.floor(Date.now() / 1000);
  const remaining = expiresAt - now;

  return Math.max(0, Math.min(100, (remaining / timeout) * 100));
};

  const pause = async (id) => {
    await fetch(`${API}/monitors/${id}/pause`, { method: "POST" });
    fetchMonitors();
  };

  useEffect(() => {
    fetchMonitors();
    const interval = setInterval(fetchMonitors, 1000); // every second
    return () => clearInterval(interval);
  }, []);

  return (
    
    <div className="container">
      <h1>Pulse-Check Dashboard</h1>

      <button className="add-btn" onClick={createMonitor}>
        + Add Device
      </button>

      <div className="grid">
        {monitors.map((m) => (
          <div key={m.id} className={`card ${m.status}`}>
            <h2>{m.id}</h2>

            <p>Status: {m.status}</p>

            <p>Timeout: {m.timeout}s</p>

            <p className="timer">
              ⏳ {m.status === "active" ? m.remaining : "-"}s
            </p>

            <div className="actions">
              <button onClick={() => heartbeat(m.id)}>
                Heartbeat
              </button>

              <button onClick={() => pause(m.id)}>
                Pause
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;