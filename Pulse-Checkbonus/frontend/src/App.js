import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:5000";

function App() {
  const [monitors, setMonitors] = useState([]);

  // Fetch all monitors
  const fetchMonitors = async () => {
    try {
      const res = await fetch(`${API}/monitors`);
      const data = await res.json();
      setMonitors(data);
    } catch (err) {
      console.error("Failed to fetch monitors:", err);
    }
  };

  // Send heartbeat
  const heartbeat = async (id) => {
    await fetch(`${API}/monitors/${id}/heartbeat`, {
      method: "POST",
    });
    fetchMonitors();
  };

  // Pause monitor
  const pause = async (id) => {
    await fetch(`${API}/monitors/${id}/pause`, {
      method: "POST",
    });
    fetchMonitors();
  };

  // Load + auto refresh
  useEffect(() => {
    fetchMonitors();
    const interval = setInterval(fetchMonitors, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <h1>Pulse-Check Dashboard</h1>

      <table className="table">
        <thead>
          <tr>
            <th>Device ID</th>
            <th>Status</th>
            <th>Timeout</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {monitors.length === 0 ? (
            <tr>
              <td colSpan="4">No devices registered</td>
            </tr>
          ) : (
            monitors.map((m) => (
              <tr key={m.id}>
                <td>{m.id}</td>

                <td className={`status ${m.status}`}>
                  {m.status}
                </td>

                <td>{m.timeout}s</td>

                <td>
                  <button onClick={() => heartbeat(m.id)}>
                    Heartbeat
                  </button>

                  <button onClick={() => pause(m.id)}>
                    Pause
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
