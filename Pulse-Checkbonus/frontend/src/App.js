import { useEffect, useState } from "react";
import { socket } from "./socket";
import "./App.css";

function App() {
  const [monitors, setMonitors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [tick, setTick] = useState(0);

  const [form, setForm] = useState({
    id: "",
    alert_email: "",
    timeout: 60
  });

  // force re-render every second (for countdown)
  useEffect(() => {
    const interval = setInterval(() => {
      setTick(t => t + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // WebSocket
  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected:", socket.id);
    });

    socket.on("monitors:update", (data) => {
      setMonitors(data);
    });

    socket.on("alert", (data) => {
      setAlerts(prev => [data, ...prev]);
    });

    return () => {
      socket.off("connect");
      socket.off("monitors:update");
      socket.off("alert");
    };
  }, []);

  // countdown
  const getCountdown = (expiresAt) => {
    const now = Math.floor(Date.now() / 1000);
    const diff = expiresAt - now;

    if (diff <= 0) return "0s";

    const m = Math.floor(diff / 60);
    const s = diff % 60;

    return `${m}m ${s}s`;
  };

  // progress bar
  const getProgress = (expiresAt, timeout = 60) => {
    const now = Math.floor(Date.now() / 1000);
    const remaining = expiresAt - now;

    return Math.max(0, Math.min(100, (remaining / timeout) * 100));
  };

  // add monitor
  const addMonitor = async () => {
    if (!form.id || !form.alert_email) {
      alert("Fill all fields");
      return;
    }

    await fetch("http://127.0.0.1:5000/monitors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    setForm({ id: "", alert_email: "", timeout: 60 });
  };

  return (
    <div className="App">
      <h1>Pulse Check Dashboard</h1>

      {/* ADD MONITOR */}
      <div className="form">
        <input
          placeholder="Device ID"
          value={form.id}
          onChange={(e) => setForm({ ...form, id: e.target.value })}
        />

        <input
          placeholder="Email"
          value={form.alert_email}
          onChange={(e) => setForm({ ...form, alert_email: e.target.value })}
        />

        <input
          type="number"
          value={form.timeout}
          onChange={(e) => setForm({ ...form, timeout: Number(e.target.value) })}
        />

        <button onClick={addMonitor}>Add Monitor</button>
      </div>

      {/* ALERTS */}
      <h2>🚨 Alerts</h2>
      <div className="alerts">
        {alerts.map((a, i) => (
          <div key={i} className="alert">
            {a.message}
          </div>
        ))}
      </div>

      {/* MONITORS */}
      <h2>📡 Devices</h2>

      <div className="grid">
        {monitors.map((m) => (
          <div key={m.id} className={`card ${m.status}`}>
            <h3>{m.id}</h3>

            <p>
              Status: <span className="status">{m.status}</span>
            </p>

            <p>Timeout: {m.timeout}s</p>

            <p>Countdown: {getCountdown(m.expires_at)}</p>

            <div className="bar">
              <div
                className="fill"
                style={{
                  width: `${getProgress(m.expires_at, m.timeout)}%`
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;