import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:5000";

function App() {
  const [monitors, setMonitors] = useState([]);

  // GET all devices
  const fetchMonitors = async () => {
    try {
      const res = await fetch(`${API}/monitors`);
      const data = await res.json();
      setMonitors(data);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  // Create device
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

  // Heartbeat
  const heartbeat = async (id) => {
    await fetch(`${API}/monitors/${id}/heartbeat`, {
      method: "POST"
    });

    fetchMonitors();
  };

  // Pause
  const pause = async (id) => {
    await fetch(`${API}/monitors/${id}/pause`, {
      method: "POST"
    });

    fetchMonitors();
  };

  // Auto refresh
  useEffect(() => {
    fetchMonitors();
    const interval = setInterval(fetchMonitors, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Pulse Check Dashboard</h1>

      <button onClick={createMonitor}>
        Add Device
      </button>

      <table border="1" cellPadding="10" width="100%">
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Timeout</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {monitors.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td>

              <td style={{
                color:
                  m.status === "down"
                    ? "red"
                    : m.status === "paused"
                    ? "orange"
                    : "green",
                fontWeight: "bold"
              }}>
                {m.status}
              </td>

              <td>{m.timeout}</td>

              <td>
                <button onClick={() => heartbeat(m.id)}>
                  Heartbeat
                </button>

                <button onClick={() => pause(m.id)}>
                  Pause
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;