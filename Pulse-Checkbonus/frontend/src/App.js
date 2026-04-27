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
        timeout: 10,
        alert_email: "test@critmon.com"
      })
    });
    fetchMonitors();
  };

  const heartbeat = async (id) => {
    await fetch(`${API}/monitors/${id}/heartbeat`, { method: "POST" });
    fetchMonitors();
  };

  const pause = async (id) => {
    await fetch(`${API}/monitors/${id}/pause`, { method: "POST" });
    fetchMonitors();
  };

  useEffect(() => {
    fetchMonitors();
    const interval = setInterval(fetchMonitors, 2000);
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

            <p>
              Status: <span className="status">{m.status}</span>
            </p>

            <p>Timeout: {m.timeout}s</p>

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