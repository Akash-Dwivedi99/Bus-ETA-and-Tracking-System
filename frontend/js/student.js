// ============================================================
// student.js — student.html only.
// Depends on: api.js (apiGet), map.js (createMap, busIcon, studentIcon,
// haversineKm, animateMarkerTo)
// ============================================================

const POLL_INTERVAL_MS = 5000;
const ANIMATION_DURATION_MS = 4500;

const map = createMap('map');
let hasCenteredMap = false;

let busMarker = null;
let studentMarker = null;
let lastBusLatLng = null;
let lastStudentLatLng = null;
const stopMarkers = [];
let routeLine = null;

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

function renderStops(stops) {
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
      weight: 2,
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

  // Draw a dotted line through the stops in order, showing the route path
  // on the map instead of leaving the stops as disconnected dots.
  if (routeLine) map.removeLayer(routeLine);
  if (stops.length > 1) {
    routeLine = L.polyline(
      stops.map(s => [s.lat, s.lng]),
      { className: 'route-line', weight: 3 }
    ).addTo(map);
    routeLine.bringToBack();
  }

  if (!hasCenteredMap && stops.length > 0) {
    map.setView([stops[0].lat, stops[0].lng], 14);
    hasCenteredMap = true;
  }
}

function renderBus(bus) {
  const latlng = [bus.lat, bus.lng];

  if (!busMarker) {
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
  if (!busId) return;

  try {
    const data = await apiGet(`/bus-location?bus_id=${encodeURIComponent(busId)}`);
    renderBus(data.bus);
    renderStops(data.stops || []);
    updateSidebar(data);
    showError(false);
  } catch (err) {
    showError(true);
    document.getElementById('last-updated').textContent = 'Connection lost';
  }
}

async function loadBuses() {
  const select = document.getElementById('bus-select');
  try {
    const buses = await apiGet('/buses');
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
  hasCenteredMap = false;
  fetchBusData();
});

loadBuses().then(() => {
  fetchBusData();
  setInterval(fetchBusData, POLL_INTERVAL_MS);
});

// ---- Student's own live location ----
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
    (position) => renderStudent(position.coords.latitude, position.coords.longitude),
    () => { document.getElementById('student-distance-value').textContent = 'Location off'; },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
  );
} else {
  document.getElementById('student-distance-value').textContent = 'Not supported';
}
