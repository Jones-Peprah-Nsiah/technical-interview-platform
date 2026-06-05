import { useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("jones4@example.com");
  const [password, setPassword] = useState("w");
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8001/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || "Login failed");
        return;
      }

      setToken(data.access_token);
      localStorage.setItem("token", data.access_token);
      setMessage("Login successful");
    } catch (error) {
      setMessage("Cannot connect to backend");
    }
  }

  return (
    <div className="page">
      <div className="card">
        <div className="logo">TIP</div>

        <h1>Technical Interview Platform</h1>
        <p className="subtitle">
          Sign in to manage interview rooms, questions, and live coding sessions.
        </p>

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit">Login</button>
        </form>

        {message && <p className="message">{message}</p>}

        {token && (
          <div className="token-box">
            <strong>Token saved</strong>
            <span>{token.slice(0, 60)}...</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;