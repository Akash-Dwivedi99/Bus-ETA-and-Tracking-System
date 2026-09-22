// ============================================================
// admin.js — admin.html only.
// Depends on: api.js (apiGet, apiPost, getSession)
// ============================================================

document.getElementById('admin-name').textContent = getSession().userName || 'Admin';

const errorBanner = document.getElementById('error-banner');
function showError(show, message) {
  errorBanner.style.display = show ? 'block' : 'none';
  if (message) errorBanner.textContent = message;
}

// ---- Nav switching ----
document.querySelectorAll('.admin-nav button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.admin-nav button').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.section).classList.add('active');
  });
});

// ---- Routes ----
async function loadRoutes() {
  try {
    const routes = await apiGet('/routes');

    document.getElementById('routes-table').innerHTML = routes.map(r => `
      <tr>
        <td class="mono-cell">${r.id}</td>
        <td>${r.name}</td>
        <td class="mono-cell">${r.paired_route_id ?? '—'}</td>
      </tr>
    `).join('');

    const routeOptions = routes.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
    document.getElementById('new-bus-route').innerHTML = routeOptions;
    document.getElementById('stops-route-filter').innerHTML = routeOptions;

    return routes;
  } catch {
    showError(true, 'Could not load routes.');
    return [];
  }
}

document.getElementById('add-route-btn').addEventListener('click', async () => {
  const name = document.getElementById('new-route-name').value.trim();
  if (!name) return;

  try {
    await apiPost('/routes', { name });
    document.getElementById('new-route-name').value = '';
    showError(false);
    await loadRoutes();
  } catch {
    showError(true, 'Could not add route.');
  }
});

// ---- Buses ----
async function loadBuses() {
  try {
    const buses = await apiGet('/buses');
    document.getElementById('buses-table').innerHTML = buses.map(b => `
      <tr>
        <td class="mono-cell">${b.id}</td>
        <td>${b.bus_number}</td>
        <td>${b.route_name}</td>
      </tr>
    `).join('');
  } catch {
    showError(true, 'Could not load buses.');
  }
}

document.getElementById('add-bus-btn').addEventListener('click', async () => {
  const id = document.getElementById('new-bus-id').value.trim();
  const bus_number = document.getElementById('new-bus-number').value.trim();
  const route_id = document.getElementById('new-bus-route').value;
  if (!id || !bus_number || !route_id) return;

  try {
    await apiPost('/buses', { id, bus_number, route_id });
    document.getElementById('new-bus-id').value = '';
    document.getElementById('new-bus-number').value = '';
    showError(false);
    await loadBuses();
  } catch {
    showError(true, 'Could not register bus — check the Bus ID is unique.');
  }
});

// ---- Stops ----
async function loadStops(routeId) {
  if (!routeId) return;
  try {
    const stops = await apiGet(`/routes/${routeId}/stops`);
    document.getElementById('stops-table').innerHTML = stops.map(s => `
      <tr>
        <td class="mono-cell">${s.stop_order}</td>
        <td>${s.name}</td>
        <td class="mono-cell">${s.lat}</td>
        <td class="mono-cell">${s.lng}</td>
      </tr>
    `).join('');
  } catch {
    showError(true, 'Could not load stops.');
  }
}

document.getElementById('stops-route-filter').addEventListener('change', (e) => {
  loadStops(e.target.value);
});

document.getElementById('add-stop-btn').addEventListener('click', async () => {
  const route_id = document.getElementById('stops-route-filter').value;
  const name = document.getElementById('new-stop-name').value.trim();
  const lat = parseFloat(document.getElementById('new-stop-lat').value);
  const lng = parseFloat(document.getElementById('new-stop-lng').value);
  const stop_order = parseInt(document.getElementById('new-stop-order').value, 10);

  if (!route_id || !name || isNaN(lat) || isNaN(lng) || isNaN(stop_order)) {
    showError(true, 'Fill in all stop fields correctly.');
    return;
  }

  try {
    await apiPost('/stops', { route_id, name, lat, lng, stop_order });
    document.getElementById('new-stop-name').value = '';
    document.getElementById('new-stop-lat').value = '';
    document.getElementById('new-stop-lng').value = '';
    document.getElementById('new-stop-order').value = '';
    showError(false);
    await loadStops(route_id);
  } catch {
    showError(true, 'Could not add stop.');
  }
});

// ---- Initial load ----
(async () => {
  const routes = await loadRoutes();
  await loadBuses();
  if (routes.length > 0) loadStops(routes[0].id);
})();
