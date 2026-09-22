// ============================================================
// driver.js — driver.html only.
// Depends on: api.js (apiPost, apiGet, getSession)
// ============================================================

const SEND_INTERVAL_MS = 4000;

const session = getSession();
const busId = session.busId || 'bus-1';
const driverName = session.userName || 'Driver';

document.getElementById('driver-name').textContent = driverName;
document.getElementById('bus-label').textContent = `Bus ${busId}`;

const tripBtn = document.getElementById('trip-btn');
const tripRing = document.getElementById('trip-ring');
const stateLabel = document.getElementById('state-label');
const statusPill = document.getElementById('status-pill');
const onlineDot = document.getElementById('online-dot');
const gpsCoords = document.getElementById('gps-coords');
const gpsPill = document.getElementById('gps-pill');
const statUpdates = document.getElementById('stat-updates');
const statDuration = document.getElementById('stat-duration');
const routeNameEl = document.getElementById('route-name');
const errorBanner = document.getElementById('error-banner');

let tripActive = false;
let watchId = null;
let sendTimer = null;
let latestPosition = null;
let updateCount = 0;
let tripStartTime = null;
let durationTimer = null;

function showError(show, message) {
  errorBanner.style.display = show ? 'block' : 'none';
  if (message) errorBanner.textContent = message;
}

function formatDuration(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const mins = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const secs = String(totalSeconds % 60).padStart(2, '0');
  return `${mins}:${secs}`;
}

async function loadRouteName() {
  try {
    const buses = await apiGet('/buses');
    const mine = buses.find(b => b.id === busId);
    routeNameEl.textContent = mine ? mine.route_name : 'Unknown route';
  } catch {
    routeNameEl.textContent = 'Unknown route';
  }
}

async function sendLocation() {
  if (!latestPosition) return;
  const { latitude, longitude } = latestPosition.coords;

  try {
    await apiPost('/update-location', { bus_id: busId, lat: latitude, lng: longitude });
    updateCount += 1;
    statUpdates.textContent = updateCount;
    gpsCoords.textContent = `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
    gpsPill.textContent = 'GPS active';
    gpsPill.classList.add('on');
    showError(false);
  } catch {
    showError(true, 'Could not reach the server — updates are not being sent.');
  }
}

function startTrip() {
  if (!('geolocation' in navigator)) {
    showError(true, 'This browser does not support location sharing.');
    return;
  }

  tripActive = true;
  tripStartTime = Date.now();

  tripBtn.textContent = 'End Trip';
  tripBtn.classList.remove('start');
  tripBtn.classList.add('stop');
  tripRing.classList.add('active');
  stateLabel.textContent = 'Trip in progress';
  stateLabel.classList.add('active');
  statusPill.textContent = 'Online';
  statusPill.classList.add('on');
  onlineDot.style.background = 'var(--reached)';
  onlineDot.style.animation = 'pulse 2.2s infinite';

  watchId = navigator.geolocation.watchPosition(
    (position) => { latestPosition = position; },
    () => { showError(true, 'Location permission denied — cannot share GPS.'); },
    { enableHighAccuracy: true, maximumAge: 3000, timeout: 10000 }
  );

  sendTimer = setInterval(sendLocation, SEND_INTERVAL_MS);
  durationTimer = setInterval(() => {
    statDuration.textContent = formatDuration(Date.now() - tripStartTime);
  }, 1000);
}

function stopTrip() {
  tripActive = false;

  tripBtn.textContent = 'Start Trip';
  tripBtn.classList.remove('stop');
  tripBtn.classList.add('start');
  tripRing.classList.remove('active');
  stateLabel.textContent = 'Trip not started';
  stateLabel.classList.remove('active');
  statusPill.textContent = 'Offline';
  statusPill.classList.remove('on');
  gpsPill.textContent = 'GPS off';
  gpsPill.classList.remove('on');
  onlineDot.style.background = 'var(--muted-dim)';
  onlineDot.style.animation = 'none';

  if (watchId !== null) navigator.geolocation.clearWatch(watchId);
  clearInterval(sendTimer);
  clearInterval(durationTimer);
  watchId = null;
  latestPosition = null;
}

tripBtn.addEventListener('click', () => {
  if (tripActive) stopTrip();
  else startTrip();
});

document.getElementById('switch-direction-btn').addEventListener('click', async () => {
  try {
    await apiPost(`/buses/${busId}/toggle-direction`, {});
    showError(false);
    loadRouteName();
  } catch (err) {
    showError(true, err.message || 'Could not switch direction.');
  }
});

loadRouteName();
