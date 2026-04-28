import { useEffect, useState } from "react";
import "./App.css";
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:5000");


function App() {
  const [monitors, setMonitors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [now, setNow] = useState(Date.now());

  // Real-time clock (for countdown)
  useEffect(() => {
    const timer = setInterval(() => {
      setNow(Date.now());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
  socket.on("alert", (data) => {
    console.log("ALERT RECEIVED:", data);

    // 🔥 Update UI instantly
    setMonitors(prev =>
      prev.map(m =>
        m.id === data.id ? { ...m, status: "down" } : m
      )
    );

    // Optional popup
    alert(`🚨 Device ${data.id} is DOWN`);
  });

  return () => {
    socket.off("alert");
  };
}, []);

  // Fetch monitors
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:5000/monitors")
        .then(res => res.json())
        .then(data => setMonitors(data))
        .catch(err => console.error("Monitors fetch error:", err));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Fetch alerts
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:5000/alerts")
        .then(res => res.json())
        .then(data => setAlerts(data))
        .catch(err => console.error("Alerts fetch error:", err));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Auto clear alerts
  useEffect(() => {
    if (alerts.length > 0) {
      const timer = setTimeout(() => {
        setAlerts([]);
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [alerts]);

  // Create monitor
  const createMonitor = () => {
    fetch("http://localhost:5000/monitors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: "device-" + Math.floor(Math.random() * 1000),
        timeout: 15,
        alert_email: "test@email.com"
      })
    });
  };

  // Heartbeat
  const sendHeartbeat = (id) => {
    fetch(`http://localhost:5000/monitors/${id}/heartbeat`, {
      method: "POST"
    });
  };

  return (
    <div className="App">
      <h1>Pulse Check Dashboard</h1>

      <button onClick={createMonitor}>Add Test Device</button>

      {/* ALERTS */}
      <div className="alert-container">
        {alerts.map((a, i) => (
          <div key={i} className="alert-popup">
            🚨 {a.message}
          </div>
        ))}
      </div>

      {/* DEVICE CARDS */}
      <div className="card-container">
        {monitors.map((m) => {
          const remaining = Math.max(
            0,
            Math.floor((m.expiry * 1000 - now) / 1000)
          );

          const isCritical = remaining <= 3;
          const isDown = m.status === "down";

          return (
            <div
              key={m.id}
              className={`card ${m.status} ${isCritical ? "blink" : ""}`}
            >
              <h3>{m.id}</h3>

              <p>Status: <strong>{m.status}</strong></p>

              <p>
                Countdown:{" "}
                <strong style={{ color: isCritical ? "yellow" : "white" }}>
                  {remaining}s
                </strong>
              </p>

              <button onClick={() => sendHeartbeat(m.id)}>
                Send Heartbeat
              </button>

              {isDown && (
                <p style={{ color: "red", fontWeight: "bold" }}>
                  Device is DOWN
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default App;