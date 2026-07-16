import { useEffect, useState } from "react";
import "./App.css";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Room from "./pages/Room";
import { api } from "./api";

function App() {
  const [session, setSession] = useState(null); // { token, user } | null
  const [activeRoomId, setActiveRoomId] = useState(null);
  const [restoring, setRestoring] = useState(() => !!localStorage.getItem("token"));

  // Restore session from a saved token on first load, if one exists
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (!savedToken) return;

    api
      .me(savedToken)
      .then((user) => setSession({ token: savedToken, user }))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setRestoring(false));
  }, []);

  function handleLogout() {
    localStorage.removeItem("token");
    setSession(null);
    setActiveRoomId(null);
  }

  if (restoring) {
    return (
      <div className="page">
        <p className="subtitle">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return <Auth onAuthenticated={setSession} />;
  }

  if (activeRoomId) {
    return (
      <Room
        roomId={activeRoomId}
        token={session.token}
        user={session.user}
        onLeave={() => setActiveRoomId(null)}
      />
    );
  }

  return (
    <Dashboard
      token={session.token}
      user={session.user}
      onEnterRoom={setActiveRoomId}
      onLogout={handleLogout}
    />
  );
}

export default App;
