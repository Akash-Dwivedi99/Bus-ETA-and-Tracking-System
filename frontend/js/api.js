// ============================================================
// api.js — shared across every page.
// Small wrappers so no other file repeats fetch boilerplate or
// hardcodes the backend URL.
// ============================================================

// Flask serves the frontend in normal use. If VS Code Live Server is used for
// local editing, send API calls to Flask explicitly instead of port 5500.
const liveServerPorts = new Set(['5500', '5501']);
const localHosts = new Set(['localhost', '127.0.0.1']);
const useFlaskFromLiveServer = liveServerPorts.has(window.location.port)
  && localHosts.has(window.location.hostname);
const API_BASE = useFlaskFromLiveServer
  ? `${window.location.protocol}//${window.location.hostname}:5000/api`
  : '/api';

async function apiGet(path) {
  const endpoint = `${API_BASE}${path}`;
  const res = await fetch(endpoint);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `GET ${endpoint} failed (${res.status})`);
  return data;
}

async function apiPost(path, body) {
  const endpoint = `${API_BASE}${path}`;
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `POST ${endpoint} failed (${res.status})`);
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

document.querySelectorAll('[data-signout]').forEach(link => {
  link.addEventListener('click', () => clearSession());
});
