// ============================================================
// api.js — shared across every page.
// Small wrappers so no other file repeats fetch boilerplate or
// hardcodes the backend URL.
// ============================================================

const API_BASE = "http://localhost:5000/api";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `GET ${path} failed (${res.status})`);
  return data;
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `POST ${path} failed (${res.status})`);
  return data;
}

// ---- Demo-only session helpers ----
// No real auth backend yet — login.html just remembers who "signed in"
// and as what role, so the next page can greet them and know their bus.
function getSession() {
  return {
    userName: sessionStorage.getItem('userName'),
    role: sessionStorage.getItem('role'),
    busId: sessionStorage.getItem('busId'),
  };
}

function setSession({ userName, role, busId } = {}) {
  if (userName != null) sessionStorage.setItem('userName', userName);
  if (role != null) sessionStorage.setItem('role', role);
  if (busId != null) sessionStorage.setItem('busId', busId);
}

function clearSession() {
  sessionStorage.clear();
}
