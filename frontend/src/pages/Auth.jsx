import { useState } from "react";
import { api } from "../api";

function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "register") {
        await api.register({
          full_name: fullName,
          email,
          password,
          invite_code: inviteCode || undefined,
        });
      }

      const { access_token } = await api.login({ email, password });
      const user = await api.me(access_token);

      localStorage.setItem("token", access_token);
      onAuthenticated({ token: access_token, user });
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <div className="logo">TIP</div>
        <h1>Technical Interview Platform</h1>
        <p className="subtitle">
          {mode === "login"
            ? "Sign in to manage interview rooms, questions, and live coding sessions."
            : "Create an account to start interviewing or practicing."}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <div className="input-group">
              <label>Full name</label>
              <input
                type="text"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {mode === "register" && (
            <div className="input-group">
              <label>Interviewer invite code (optional)</label>
              <input
                type="text"
                placeholder="Leave blank to register as a candidate"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
              />
              <p className="hint">
                Have an invite code from your team? Enter it to register as an
                interviewer instead of a candidate.
              </p>
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
          </button>
        </form>

        {error && <p className="message error">{error}</p>}

        <p className="switch-mode">
          {mode === "login" ? "Need an account?" : "Already have an account?"}{" "}
          <button
            type="button"
            className="link-button"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError("");
            }}
          >
            {mode === "login" ? "Register" : "Login"}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Auth;
