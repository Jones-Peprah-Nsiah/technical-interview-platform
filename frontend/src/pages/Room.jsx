import { useEffect, useRef, useState } from "react";
import { WS_BASE_URL, api } from "../api";

const LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "go"];

function Room({ roomId, token, user, onLeave }) {
  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [chatInput, setChatInput] = useState("");
  const [events, setEvents] = useState([]); // chat + system messages, newest last

  const socketRef = useRef(null);
  const skipNextBroadcastRef = useRef(false);
  const eventsEndRef = useRef(null);

  // Load room metadata + current participants once
  useEffect(() => {
    let cancelled = false;

    api
      .getRoom(roomId)
      .then((data) => !cancelled && setRoom(data))
      .catch(() => {});

    api
      .getParticipants(roomId)
      .then((data) => !cancelled && setParticipants(data))
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [roomId]);

  // Open the websocket connection
  useEffect(() => {
    const socket = new WebSocket(
      `${WS_BASE_URL}/ws/rooms/${roomId}?token=${encodeURIComponent(token)}`
    );
    socketRef.current = socket;

    socket.onopen = () => setConnectionStatus("connected");
    socket.onclose = () => setConnectionStatus("disconnected");
    socket.onerror = () => setConnectionStatus("error");

    socket.onmessage = (rawEvent) => {
      let message;
      try {
        message = JSON.parse(rawEvent.data);
      } catch {
        return;
      }

      switch (message.type) {
        case "code_update":
          // Don't let our own broadcast echo reset the cursor position
          if (message.user_id === user.id) return;
          skipNextBroadcastRef.current = true;
          setCode(message.content ?? "");
          if (message.language) setLanguage(message.language);
          break;

        case "chat_message":
          setEvents((prev) => [
            ...prev,
            {
              kind: "chat",
              userId: message.user_id,
              role: message.role,
              content: message.content,
              mine: message.user_id === user.id,
            },
          ]);
          break;

        case "user_joined":
        case "user_left":
          setEvents((prev) => [
            ...prev,
            { kind: "system", content: message.message },
          ]);
          break;

        case "error":
          setEvents((prev) => [
            ...prev,
            { kind: "system", content: `Error: ${message.message}` },
          ]);
          break;

        default:
          break;
      }
    };

    return () => socket.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, token]);

  useEffect(() => {
    eventsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  function sendMessage(payload) {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  }

  function handleCodeChange(e) {
    const value = e.target.value;
    setCode(value);

    if (skipNextBroadcastRef.current) {
      skipNextBroadcastRef.current = false;
      return;
    }

    sendMessage({ type: "code_update", content: value, language });
  }

  function handleLanguageChange(e) {
    const value = e.target.value;
    setLanguage(value);
    sendMessage({ type: "code_update", content: code, language: value });
  }

  function handleSendChat(e) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    sendMessage({ type: "chat_message", content: chatInput.trim() });
    setChatInput("");
  }

  return (
    <div className="room-page">
      <header className="room-header">
        <div>
          <h1>{room?.title || `Room #${roomId}`}</h1>
          {room?.description && <p className="subtitle">{room.description}</p>}
        </div>
        <div className="room-header-right">
          <span className={`status-pill status-${connectionStatus}`}>
            {connectionStatus}
          </span>
          <button type="button" className="secondary-button" onClick={onLeave}>
            Leave room
          </button>
        </div>
      </header>

      <div className="room-body">
        <section className="editor-panel">
          <div className="editor-toolbar">
            <span>Live shared editor</span>
            <select value={language} onChange={handleLanguageChange}>
              {LANGUAGES.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
          <textarea
            className="code-editor"
            spellCheck={false}
            value={code}
            onChange={handleCodeChange}
            placeholder="// Start typing — everyone in this room sees it live"
          />
        </section>

        <aside className="side-panel">
          <div className="participants-box">
            <h3>Participants</h3>
            <ul>
              {participants.map((p) => (
                <li key={p.id}>
                  User #{p.user_id} <span className="badge">{p.role}</span>
                </li>
              ))}
              {participants.length === 0 && <li className="muted">None yet</li>}
            </ul>
          </div>

          <div className="chat-box">
            <h3>Chat</h3>
            <div className="chat-messages">
              {events.map((event, i) =>
                event.kind === "system" ? (
                  <div key={i} className="chat-system">
                    {event.content}
                  </div>
                ) : (
                  <div
                    key={i}
                    className={`chat-bubble ${event.mine ? "mine" : ""}`}
                  >
                    <span className="chat-meta">
                      {event.mine ? "You" : `User #${event.userId}`} ·{" "}
                      {event.role}
                    </span>
                    {event.content}
                  </div>
                )
              )}
              <div ref={eventsEndRef} />
            </div>
            <form className="chat-input-row" onSubmit={handleSendChat}>
              <input
                type="text"
                placeholder="Type a message..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit">Send</button>
            </form>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default Room;
