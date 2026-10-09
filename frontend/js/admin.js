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

function renderTable(bodyId, rows, columnCount, emptyText) {
  const body = document.getElementById(bodyId);
  body.replaceChildren();
  if (!rows.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = columnCount;
    cell.className = 'empty-state';
    cell.textContent = emptyText;
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  rows.forEach(values => {
    const row = document.createElement('tr');
    values.forEach(({ text, mono = false }) => {
      const cell = document.createElement('td');
      if (mono) cell.className = 'mono-cell';
      cell.textContent = text ?? '--';
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
}

// ---- Nav switching ----
document.querySelectorAll('.admin-nav button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.admin-nav button').forEach(b => {
      b.classList.remove('active');
      b.removeAttribute('aria-current');
    });
    document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
    btn.classList.add('active');
    btn.setAttribute('aria-current', 'page');
    document.getElementById(btn.dataset.section).classList.add('active');
  });
});

// ---- Routes ----
async function loadRoutes() {
  try {
    const routes = await apiGet('/routes');
    renderTable('routes-table', routes.map(r => [
      { text: r.id, mono: true },
      { text: r.name },
      { text: r.paired_route_id, mono: true },
    ]), 3, 'No routes yet. Add a route below.');

    ['new-bus-route', 'stops-route-filter'].forEach(id => {
      const select = document.getElementById(id);
      select.replaceChildren();
      if (!routes.length) select.appendChild(new Option('Add a route first', ''));
      routes.forEach(route => select.appendChild(new Option(route.name, route.id)));
    });

    return routes;
  } catch (err) {
    showError(true, err.message || 'Could not load routes.');
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
  } catch (err) {
    showError(true, err.message || 'Could not add route.');
  }
});

// ---- Buses ----
async function loadBuses() {
  try {
    const buses = await apiGet('/buses');
    renderTable('buses-table', buses.map(b => [
      { text: b.id, mono: true },
      { text: b.bus_number },
      { text: b.route_name },
    ]), 3, 'No buses are registered yet.');
  } catch (err) {
    showError(true, err.message || 'Could not load buses.');
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
  } catch (err) {
    showError(true, err.message || 'Could not register bus. Check the Bus ID is unique.');
  }
});

// ---- Stops ----
async function loadStops(routeId) {
  if (!routeId) return;
  try {
    const stops = await apiGet(`/routes/${routeId}/stops`);
    renderTable('stops-table', stops.map(s => [
      { text: s.stop_order, mono: true },
      { text: s.name },
      { text: s.lat, mono: true },
      { text: s.lng, mono: true },
    ]), 4, 'No stops are assigned to this route yet.');
  } catch (err) {
    showError(true, err.message || 'Could not load stops.');
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
  } catch (err) {
    showError(true, err.message || 'Could not add stop.');
  }
});

// ---- Initial load ----
(async () => {
  const routes = await loadRoutes();
  await loadBuses();
  if (routes.length > 0) loadStops(routes[0].id);
  else renderTable('stops-table', [], 4, 'Add a route before adding stops.');
})();
