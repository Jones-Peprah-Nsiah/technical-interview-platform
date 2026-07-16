import { useState } from "react";
import { api } from "../api";

function Dashboard({ token, user, onEnterRoom, onLogout }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [createError, setCreateError] = useState("");
  const [createdRoom, setCreatedRoom] = useState(null);
  const [creating, setCreating] = useState(false);

  const [joinRoomId, setJoinRoomId] = useState("");
  const [joinRole, setJoinRole] = useState("candidate");
  const [joinError, setJoinError] = useState("");
  const [joining, setJoining] = useState(false);

  const isInterviewer = user.role === "interviewer";

  async function handleCreateRoom(e) {
    e.preventDefault();
    setCreateError("");
    setCreating(true);

    try {
      const room = await api.createRoom({ title, description }, token);
      setCreatedRoom(room);
    } catch (err) {
      setCreateError(err.message || "Could not create room");
    } finally {
      setCreating(false);
    }
  }

  async function handleJoinRoom(e) {
    e.preventDefault();
    setJoinError("");
    setJoining(true);

    try {
      const roomId = Number(joinRoomId);

      // Room must exist before joining
      await api.getRoom(roomId);

      try {
        await api.joinRoom({ user_id: user.id, room_id: roomId, role: joinRole });
      } catch (err) {
        // If already joined, that's fine — just enter the room
        if (!/already joined/i.test(err.message || "")) {
          throw err;
        }
      }

      onEnterRoom(roomId);
    } catch (err) {
      setJoinError(err.message || "Could not join room");
    } finally {
      setJoining(false);
    }
  }

  return (
    <div className="page">
      <div className="card wide">
        <div className="dashboard-header">
          <div>
            <div className="logo">TIP</div>
            <h1>Welcome, {user.full_name}</h1>
            <p className="subtitle">
              Signed in as <strong>{user.email}</strong> · role:{" "}
              <span className="badge">{user.role}</span>
            </p>
          </div>
          <button type="button" className="secondary-button" onClick={onLogout}>
            Log out
          </button>
        </div>

        {!isInterviewer && (
          <p className="notice">
            Your account has the <strong>candidate</strong> role, so room creation is
            disabled. If you have an interviewer invite code, log out and register a
            new account with it. You can still join an existing room below.
          </p>
        )}

        <div className="dashboard-grid">
          <section className="panel">
            <h2>Create a room</h2>
            <form onSubmit={handleCreateRoom}>
              <div className="input-group">
                <label>Title</label>
                <input
                  type="text"
                  placeholder="Frontend interview - Jane"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={!isInterviewer}
                  required
                />
              </div>
              <div className="input-group">
                <label>Description</label>
                <input
                  type="text"
                  placeholder="45 min, React + system design"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={!isInterviewer}
                  required
                />
              </div>
              <button type="submit" disabled={!isInterviewer || creating}>
                {creating ? "Creating..." : "Create room"}
              </button>
            </form>

            {createError && <p className="message error">{createError}</p>}

            {createdRoom && (
              <div className="token-box">
                <strong>Room created — id #{createdRoom.id}</strong>
                <span>Share this ID with your candidate so they can join.</span>
                <button
                  type="button"
                  className="secondary-button small"
                  onClick={() => onEnterRoom(createdRoom.id)}
                >
                  Enter room
                </button>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Join a room</h2>
            <form onSubmit={handleJoinRoom}>
              <div className="input-group">
                <label>Room ID</label>
                <input
                  type="number"
                  placeholder="1"
                  value={joinRoomId}
                  onChange={(e) => setJoinRoomId(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label>Join as</label>
                <select value={joinRole} onChange={(e) => setJoinRole(e.target.value)}>
                  <option value="candidate">Candidate</option>
                  <option value="interviewer">Interviewer</option>
                </select>
              </div>
              <button type="submit" disabled={joining}>
                {joining ? "Joining..." : "Join room"}
              </button>
            </form>

            {joinError && <p className="message error">{joinError}</p>}
          </section>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
