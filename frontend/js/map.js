// ============================================================
// map.js — shared by any page with a Leaflet map (student.js today).
// No dependencies on api.js — this file only knows about Leaflet
// and marker math, not the backend.
// ============================================================

function createMap(elementId, initialCenter = [30.3165, 78.0322], zoom = 14) {
  const map = L.map(elementId, { zoomControl: true }).setView(initialCenter, zoom);
  // Free OSM tiles — no API key needed. The dark look is applied via a
  // CSS filter on the tile pane instead (see .leaflet-tile-pane in
  // student.css), since free dark-styled tile servers now require keys.
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);
  return map;
}

const busIcon = L.divIcon({
  className: 'bus-marker-wrap',
  html: `<div style="
           width:34px; height:34px;
           background:#38bdf8;
           border:3px solid #0b1220;
           border-radius:50%;
           display:flex; align-items:center; justify-content:center;
           font-size:16px;
           box-shadow:0 2px 8px rgba(0,0,0,0.5);
           position:relative;
           z-index:2;
         ">🚌</div>`,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
});

const studentIcon = L.divIcon({
  className: '',
  html: '<div style="background:#4fd1c5;width:14px;height:14px;border-radius:50%;border:3px solid #0f172a;box-shadow:0 0 0 2px #4fd1c5;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

// Distance in km between two lat/lng points — same formula the backend uses.
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

// Slides a marker from its current position to a new one over `duration`
// ms instead of teleporting — makes movement look like driving, not jumping.
// Also toggles a "moving" class on the marker element for a visual pulse
// while it's in motion (see .bus-marker-wrap.moving in student.css).
function animateMarkerTo(marker, toLatLng, duration) {
  const from = marker.getLatLng();
  const fromLat = from.lat, fromLng = from.lng;
  const toLat = toLatLng[0], toLng = toLatLng[1];
  const start = performance.now();

  const el = marker.getElement();
  if (el) el.classList.add('marker-moving');

  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const lat = fromLat + (toLat - fromLat) * t;
    const lng = fromLng + (toLng - fromLng) * t;
    marker.setLatLng([lat, lng]);
    if (t < 1) {
      requestAnimationFrame(step);
    } else if (el) {
      el.classList.remove('marker-moving');
    }
  }
  requestAnimationFrame(step);
}
