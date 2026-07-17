import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import { WS_BASE_URL, api } from "../api";

const LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "go"];

const DIFFICULTIES = ["easy", "medium", "hard"];

function Room({ roomId, token, user, onLeave }) {
  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [chatInput, setChatInput] = useState("");
  const [events, setEvents] = useState([]); // chat + system messages, newest last

  const [questions, setQuestions] = useState([]);
  const [activeQuestion, setActiveQuestion] = useState(null);
  const [newQuestion, setNewQuestion] = useState({
    title: "",
    description: "",
    difficulty: "easy",
  });
  const [questionError, setQuestionError] = useState("");
  const [addingQuestion, setAddingQuestion] = useState(false);

  const [output, setOutput] = useState(null);
  const [ranBy, setRanBy] = useState("");
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState("");

  const socketRef = useRef(null);
  const skipNextBroadcastRef = useRef(false);
  const eventsEndRef = useRef(null);

  const canManageQuestions =
    room && user.role === "interviewer" && room.user_id === user.id;

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

    api
      .listQuestions(roomId)
      .then((data) => !cancelled && setQuestions(data))
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

        case "question_selected":
          setActiveQuestion(message.content ?? null);
          break;

        case "run_output":
          setOutput(message.content ?? null);
          setRanBy(message.user_id === user.id ? "You" : `User #${message.user_id}`);
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

  function handleCodeChange(value) {
    const newValue = value ?? "";
    setCode(newValue);

    if (skipNextBroadcastRef.current) {
      skipNextBroadcastRef.current = false;
      return;
    }

    sendMessage({ type: "code_update", content: newValue, language });
  }

  async function handleRun() {
    setRunning(true);
    setRunError("");
    setOutput(null);

    try {
      const result = await api.executeCode({ code, language }, token);
      sendMessage({ type: "run_output", content: result });
    } catch (err) {
      setRunError(err.message || "Could not run code");
    } finally {
      setRunning(false);
    }
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

  async function handleAddQuestion(e) {
    e.preventDefault();
    setQuestionError("");
    setAddingQuestion(true);

    try {
      const question = await api.createQuestion(roomId, newQuestion, token);
      setQuestions((prev) => [...prev, question]);
      setNewQuestion({ title: "", description: "", difficulty: "easy" });
    } catch (err) {
      setQuestionError(err.message || "Could not add question");
    } finally {
      setAddingQuestion(false);
    }
  }

  function handleSelectQuestion(question) {
    setActiveQuestion(question);
    sendMessage({ type: "question_selected", content: question });
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
          {activeQuestion && (
            <div className="active-question">
              <div className="active-question-header">
                <strong>{activeQuestion.title}</strong>
                <span className={`badge difficulty-${activeQuestion.difficulty}`}>
                  {activeQuestion.difficulty}
                </span>
              </div>
              <p>{activeQuestion.description}</p>
            </div>
          )}

          <div className="editor-toolbar">
            <span>Live shared editor</span>
            <div className="editor-toolbar-right">
              <select value={language} onChange={handleLanguageChange}>
                {LANGUAGES.map((lang) => (
                  <option key={lang} value={lang}>
                    {lang}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="secondary-button small"
                onClick={handleRun}
                disabled={running}
              >
                {running ? "Running..." : "Run"}
              </button>
            </div>
          </div>

          <div className="monaco-wrapper">
            <Editor
              language={language}
              theme="vs-dark"
              value={code}
              onChange={handleCodeChange}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                automaticLayout: true,
              }}
            />
          </div>

          {(output || runError) && (
            <div className="output-panel">
              <div className="output-panel-header">
                <span>
                  Output {output?.status ? `— ${output.status}` : ""}
                  {ranBy && ` (run by ${ranBy})`}
                </span>
                <button
                  type="button"
                  className="link-button"
                  onClick={() => {
                    setOutput(null);
                    setRunError("");
                    setRanBy("");
                  }}
                >
                  Clear
                </button>
              </div>
              {runError && <pre className="output-stderr">{runError}</pre>}
              {output?.compile_output && (
                <pre className="output-stderr">{output.compile_output}</pre>
              )}
              {output?.stdout && <pre className="output-stdout">{output.stdout}</pre>}
              {output?.stderr && <pre className="output-stderr">{output.stderr}</pre>}
              {output && !output.stdout && !output.stderr && !output.compile_output && (
                <pre className="output-stdout muted">(no output)</pre>
              )}
            </div>
          )}
        </section>

        <aside className="side-panel">
          <div className="questions-box">
            <h3>Questions</h3>
            <ul className="questions-list">
              {questions.map((q) => (
                <li
                  key={q.id}
                  className={
                    activeQuestion?.id === q.id ? "question-item active" : "question-item"
                  }
                >
                  <div className="question-item-main">
                    <span>{q.title}</span>
                    <span className={`badge difficulty-${q.difficulty}`}>
                      {q.difficulty}
                    </span>
                  </div>
                  {canManageQuestions && activeQuestion?.id !== q.id && (
                    <button
                      type="button"
                      className="secondary-button small"
                      onClick={() => handleSelectQuestion(q)}
                    >
                      Use this question
                    </button>
                  )}
                </li>
              ))}
              {questions.length === 0 && <li className="muted">No questions yet</li>}
            </ul>

            {canManageQuestions && (
              <form className="add-question-form" onSubmit={handleAddQuestion}>
                <input
                  type="text"
                  placeholder="Question title"
                  value={newQuestion.title}
                  onChange={(e) =>
                    setNewQuestion((prev) => ({ ...prev, title: e.target.value }))
                  }
                  required
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={newQuestion.description}
                  onChange={(e) =>
                    setNewQuestion((prev) => ({ ...prev, description: e.target.value }))
                  }
                  required
                />
                <select
                  value={newQuestion.difficulty}
                  onChange={(e) =>
                    setNewQuestion((prev) => ({ ...prev, difficulty: e.target.value }))
                  }
                >
                  {DIFFICULTIES.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
                <button type="submit" disabled={addingQuestion}>
                  {addingQuestion ? "Adding..." : "Add question"}
                </button>
                {questionError && <p className="message error">{questionError}</p>}
              </form>
            )}
          </div>

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
