// ============================================================
// auth.js — login.html only.
// Depends on: api.js (setSession)
// ============================================================

const roleButtons = document.querySelectorAll('.role-tabs button');
const busField = document.getElementById('bus-field');
const formTitle = document.getElementById('form-title');
const formSub = document.getElementById('form-sub');

const ROLE_COPY = {
  student: { title: 'Continue as Student', sub: 'Track your bus in real time.', destination: 'student.html' },
  driver:  { title: 'Continue as Driver',  sub: 'Share your live location with students.', destination: 'driver.html' },
  admin:   { title: 'Continue as Admin',   sub: 'Manage buses, routes, and stops.', destination: 'admin.html' },
};

let selectedRole = 'student';

roleButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    roleButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedRole = btn.dataset.role;

    const copy = ROLE_COPY[selectedRole];
    formTitle.textContent = copy.title;
    formSub.textContent = copy.sub;
    busField.style.display = selectedRole === 'driver' ? 'block' : 'none';
  });
});

document.getElementById('login-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value.trim();
  const errorBanner = document.getElementById('error-banner');

  if (!name) {
    errorBanner.style.display = 'block';
    return;
  }
  errorBanner.style.display = 'none';

  setSession({
    userName: name,
    role: selectedRole,
    busId: selectedRole === 'driver' ? document.getElementById('assigned-bus').value : undefined,
  });

  window.location.href = ROLE_COPY[selectedRole].destination;
});
