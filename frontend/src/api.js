const BASE_URL = "http://127.0.0.1:8001";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    // no body
  }

  if (!res.ok) {
    const message = data?.detail || `Request failed (${res.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

export const api = {
  register: (payload) => request("/register", { method: "POST", body: payload }),
  login: (payload) => request("/login", { method: "POST", body: payload }),
  me: (token) => request("/me", { token }),
  createRoom: (payload, token) => request("/rooms", { method: "POST", body: payload, token }),
  getRoom: (roomId) => request(`/rooms/${roomId}`),
  joinRoom: (payload) => request("/join-room", { method: "POST", body: payload }),
  getParticipants: (roomId) => request(`/rooms/${roomId}/participants`),
  listQuestions: (roomId) => request(`/rooms/${roomId}/questions`),
  createQuestion: (roomId, payload, token) =>
    request(`/rooms/${roomId}/questions`, { method: "POST", body: payload, token }),
};

export const WS_BASE_URL = "ws://127.0.0.1:8001";
