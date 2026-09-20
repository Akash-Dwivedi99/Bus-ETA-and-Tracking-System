// ---- Configuration ----
// Point this at your Flask backend, e.g. "http://localhost:5000/api"
const API_BASE = "http://localhost:5000/api";
const POLL_INTERVAL_MS = 5000;
const ANIMATION_DURATION_MS = 4500; // slightly less than poll interval so each slide finishes before the next update

// ---- Map setup ----
// Starts centered on Dehradun as a fallback only — as soon as the first
// bus's stops load, the map re-centers on the real route (see fetchBusData).
const map = L.map('map', { zoomControl: true }).setView([30.3165, 78.0322], 14);
let hasCenteredMap = false;

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

const busIcon = L.divIcon({
  className: '',
  html: `<div style="
           width:32px; height:32px;
           background:#38bdf8;
           border:3px solid #0f172a;
           border-radius:50%;
           display:flex; align-items:center; justify-content:center;
           font-size:16px;
           box-shadow:0 2px 6px rgba(0,0,0,0.4);
         ">🚌</div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const studentIcon = L.divIcon({
  className: '',
  html: '<div style="background:#4fd1c5;width:14px;height:14px;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 0 2px #4fd1c5;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

let busMarker = null;
let studentMarker = null;
let lastBusLatLng = null;
let lastStudentLatLng = null;
const stopMarkers = [];

// Same formula as the backend's Haversine function — distance in km
// between two lat/lng points, done here so we don't need a server
// round-trip just to compare two points the browser already has.
function haversineKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const toRad = deg => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function updateStudentDistance() {
  const el = document.getElementById('student-distance-value');
  if (!lastBusLatLng || !lastStudentLatLng) {
    el.textContent = '— km';
    return;
  }
  const km = haversineKm(
    lastStudentLatLng[0], lastStudentLatLng[1],
    lastBusLatLng[0], lastBusLatLng[1]
  );
  el.textContent = `${km.toFixed(2)} km`;
}

// Slides a marker from its current position to a new one over `duration`
// ms, instead of teleporting — this is what makes the bus look like it's
// actually driving, the way Uber/Rapido markers move.
function animateMarkerTo(marker, toLatLng, duration) {
  const from = marker.getLatLng();
  const fromLat = from.lat, fromLng = from.lng;
  const toLat = toLatLng[0], toLng = toLatLng[1];
  const start = performance.now();

  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const lat = fromLat + (toLat - fromLat) * t;
    const lng = fromLng + (toLng - fromLng) * t;
    marker.setLatLng([lat, lng]);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function renderStops(stops) {
  // Clear old stop markers
  stopMarkers.forEach(m => map.removeLayer(m));
  stopMarkers.length = 0;

  const listEl = document.getElementById('stop-list');
  listEl.innerHTML = '';

  stops.forEach(stop => {
    const marker = L.circleMarker([stop.lat, stop.lng], {
      radius: 6,
      color: stop.reached ? '#4ade80' : '#334155',
      fillColor: stop.reached ? '#4ade80' : '#1e293b',
      fillOpacity: 1,
      weight: 2
    }).addTo(map).bindPopup(stop.name);
    stopMarkers.push(marker);

    const li = document.createElement('li');
    let cls = '';
    if (stop.reached) cls = 'reached';
    else if (stop.next) cls = 'next';
    li.className = cls;
    li.innerHTML = `<span class="marker"></span><span class="name">${stop.name}</span><span class="time">${stop.eta_min != null ? stop.eta_min + ' min' : ''}</span>`;
    listEl.appendChild(li);
  });

  // Center the map on the route the first time real stop data arrives,
  // instead of relying on the hardcoded fallback coordinates above.
  if (!hasCenteredMap && stops.length > 0) {
    map.setView([stops[0].lat, stops[0].lng], 14);
    hasCenteredMap = true;
  }
}

function renderBus(bus) {
  const latlng = [bus.lat, bus.lng];

  if (!busMarker) {
    // First time we see this bus — place it directly, nothing to animate from yet.
    busMarker = L.marker(latlng, { icon: busIcon }).addTo(map).bindPopup('Bus location');
  } else {
    animateMarkerTo(busMarker, latlng, ANIMATION_DURATION_MS);
  }

  lastBusLatLng = latlng;
  updateStudentDistance();
}

function updateSidebar(data) {
  document.getElementById('eta-value').textContent = data.eta_min != null ? `${data.eta_min} min` : '— min';
  document.getElementById('eta-stop-name').textContent = data.next_stop_name ? `to ${data.next_stop_name}` : 'Waiting for data';
  document.getElementById('distance-value').textContent = data.distance_km != null ? `${data.distance_km} km` : '— km';
  document.getElementById('last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
}

function showError(show) {
  document.getElementById('error-banner').style.display = show ? 'block' : 'none';
}

async function fetchBusData() {
  const select = document.getElementById('bus-select');
  const busId = select.value;
  if (!busId) return; // dropdown hasn't loaded any buses yet

  try {
    const res = await fetch(`${API_BASE}/bus-location?bus_id=${encodeURIComponent(busId)}`);
    if (!res.ok) throw new Error('Bad response');
    const data = await res.json();

    renderBus(data.bus);
    renderStops(data.stops || []);
    updateSidebar(data);
    showError(false);
  } catch (err) {
    showError(true);
    document.getElementById('last-updated').textContent = 'Connection lost';
  }
}

// ---- Dynamic bus/route picker ----
// Builds the <select> options from the database instead of a hardcoded
// <option> in the HTML, so adding a new bus/route needs zero frontend
// changes — it just shows up here automatically.
async function loadBuses() {
  const select = document.getElementById('bus-select');
  try {
    const res = await fetch(`${API_BASE}/buses`);
    if (!res.ok) throw new Error('Bad response');
    const buses = await res.json();

    select.innerHTML = '';
    if (buses.length === 0) {
      select.innerHTML = '<option value="">No buses found</option>';
      return;
    }

    buses.forEach(bus => {
      const opt = document.createElement('option');
      opt.value = bus.id;
      opt.textContent = `${bus.bus_number} — ${bus.route_name}`;
      select.appendChild(opt);
    });
  } catch (err) {
    select.innerHTML = '<option value="">Could not load buses</option>';
    showError(true);
  }
}

document.getElementById('bus-select').addEventListener('change', () => {
  hasCenteredMap = false; // allow re-centering when switching to a different route
  fetchBusData();
});

// Load the bus list first, THEN start polling — polling before the
// dropdown has options would just fetch with an empty bus_id.
loadBuses().then(() => {
  fetchBusData();
  setInterval(fetchBusData, POLL_INTERVAL_MS);
});

// ---- Student's own live location ----
// Runs independently of the bus polling above — the browser pushes
// updates whenever the device's GPS reports a new fix, rather than
// us asking on a timer.
function renderStudent(lat, lng) {
  const latlng = [lat, lng];
  lastStudentLatLng = latlng;
  if (!studentMarker) {
    studentMarker = L.marker(latlng, { icon: studentIcon }).addTo(map).bindPopup('Your location');
  } else {
    studentMarker.setLatLng(latlng);
  }
  updateStudentDistance();
}

if ('geolocation' in navigator) {
  navigator.geolocation.watchPosition(
    (position) => {
      renderStudent(position.coords.latitude, position.coords.longitude);
    },
    (err) => {
      // Most common case: the user clicked "Block" on the location prompt.
      document.getElementById('student-distance-value').textContent = 'Location off';
    },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
  );
} else {
  document.getElementById('student-distance-value').textContent = 'Not supported';
}