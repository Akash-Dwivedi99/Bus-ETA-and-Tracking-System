// ============================================================
// auth.js — login.html only.
// Depends on: api.js (setSession)
// ============================================================

const roleButtons = document.querySelectorAll('.role-tabs button');
const busField = document.getElementById('bus-field');
const formTitle = document.getElementById('form-title');
const formSub = document.getElementById('form-sub');
const errorBanner = document.getElementById('error-banner');

const ROLE_COPY = {
  student: { title: 'Continue as Student', sub: 'Track your bus in real time.', destination: 'student.html' },
  driver:  { title: 'Continue as Driver',  sub: 'Share your live location with students.', destination: 'driver.html' },
  admin:   { title: 'Continue as Admin',   sub: 'Manage buses, routes, and stops.', destination: 'admin.html' },
};

let selectedRole = 'student';
let busLoadError = '';

async function loadBuses() {
  const busSelect = document.getElementById('assigned-bus');
  try {
    const buses = await apiGet('/buses');
    busSelect.replaceChildren();
    buses.forEach(bus => {
      const option = document.createElement('option');
      option.value = bus.id;
      option.textContent = `${bus.bus_number} · ${bus.route_name}`;
      busSelect.appendChild(option);
    });
    if (!buses.length) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = 'No buses available';
      busSelect.appendChild(option);
    }
  } catch (err) {
    busLoadError = err.message || 'Check that the backend and MySQL are running.';
    busSelect.replaceChildren(new Option(`Could not load buses: ${busLoadError}`, ''));
  }
}

roleButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    roleButtons.forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-pressed', 'false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');
    selectedRole = btn.dataset.role;

    const copy = ROLE_COPY[selectedRole];
    formTitle.textContent = copy.title;
    formSub.textContent = copy.sub;
    busField.hidden = selectedRole !== 'driver';
    if (selectedRole === 'driver' && busLoadError) {
      errorBanner.textContent = `Bus list unavailable. ${busLoadError}`;
      errorBanner.style.display = 'block';
    } else {
      errorBanner.style.display = 'none';
    }
  });
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value.trim();
  if (!name) {
    errorBanner.textContent = 'Please enter a name to continue.';
    errorBanner.style.display = 'block';
    return;
  }
  if (selectedRole === 'driver' && !document.getElementById('assigned-bus').value) {
    errorBanner.textContent = busLoadError
      ? `Could not load buses. ${busLoadError}`
      : 'Choose an assigned bus to continue.';
    errorBanner.style.display = 'block';
    return;
  }
  errorBanner.style.display = 'none';

  const busId = selectedRole === 'driver' ? document.getElementById('assigned-bus').value : undefined;
  try {
    await apiPost('/auth/login', { name, role: selectedRole });
  } catch (err) {
    errorBanner.textContent = err.message || 'Could not connect to the server.';
    errorBanner.style.display = 'block';
    return;
  }

  setSession({
    userName: name,
    role: selectedRole,
    busId,
  });

  window.location.href = ROLE_COPY[selectedRole].destination;
});

loadBuses();
