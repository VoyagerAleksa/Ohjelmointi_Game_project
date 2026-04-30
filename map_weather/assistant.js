const DATA_SOURCE = 'json';
const JSON_FILE   = 'game_data.json';
const API_BASE    = 'http://localhost:5000/api';

let luggage      = null;
let guessCount   = 0;
let fogCircle    = null;
let popupVisible = false;
const distancePins = [];

// ── Start ──
window.addEventListener('load', () => {
  injectStyles();
  injectUI();
  hookMapClick();
  startNewGame();
});

// ── Country loading  ──
async function startNewGame() {
  luggage = null;
  guessCount = 0;
  if (fogCircle) { fogCircle.remove(); fogCircle = null; }
  distancePins.forEach(p => p.remove());
  distancePins.length = 0;
  updateBadge();
  setFabState('loading');

  try {
    let countries = [];

    if (DATA_SOURCE === 'json') {
      const res  = await fetch(JSON_FILE + '?t=' + Date.now());
      const data = await res.json();
      countries  = data.countries;
    } else {
      const res  = await fetch(`${API_BASE}/random-country`);
      const data = await res.json();
      if (!data.ok) throw new Error(data.error);
      luggage = data.country;
      setFabState('ready');
      return;
    }

    if (!countries || countries.length === 0) throw new Error('No countries in file');
    luggage = countries[Math.floor(Math.random() * countries.length)];
    setFabState('ready');

  } catch (err) {
    console.error('[LugAssistant] Failed to load:', err);
    setFabState('error');
  }
}

// ── Implement map click logic ──
function hookMapClick() {
  if (typeof map === 'undefined') { setTimeout(hookMapClick, 300); return; }

  map.on('click', (e) => {
    if (!luggage) return;

    const { lat, lng } = e.latlng;
    guessCount++;
    updateBadge();

    const dist  = Math.round(haversine(lat, lng, luggage.lat, luggage.lng));
    const color = dist > 2000 ? '#4db8ff' : dist > 1000 ? '#90d4f7' : dist > 500 ? '#ffb347' : dist > 150 ? '#ff6b35' : '#3ddc84';
    const emoji = dist > 2000 ? '🥶' : dist > 1000 ? '❄️' : dist > 500 ? '🌡️' : dist > 150 ? '🔥' : '🎯';

    if (distancePins.length >= 6) distancePins.shift().remove();
    distancePins.push(
      L.circleMarker([lat, lng], {
        radius: 9, color, fillColor: color, fillOpacity: 0.5, weight: 2
      })
      .addTo(map)
      .bindTooltip(`${emoji} ${dist.toLocaleString()} km`, {
        permanent: true, direction: 'top', offset: [0, -12], className: 'lug-tooltip'
      })
    );

    if (dist <= 150) foundLuggage();
  });
}

// ── Triggering the fog effect on button click ──
function showFog() {
  if (typeof map === 'undefined' || !luggage) return;
  if (fogCircle) { fogCircle.remove(); fogCircle = null; }

  fogCircle = L.circle([luggage.lat, luggage.lng], {
    radius: luggage.radius * 1500,
    color: 'transparent',
    fillColor: '#ffe066',
    fillOpacity: 0,
    interactive: false,
  }).addTo(map);

  let op = 0;
  const fadeIn = setInterval(() => {
    op = Math.min(op + 0.03, 0.30);
    fogCircle.setStyle({ fillOpacity: op });
    if (op >= 0.30) clearInterval(fadeIn);
  }, 35);

  setTimeout(() => {
    const fadeOut = setInterval(() => {
      op = Math.max(op - 0.02, 0);
      if (!fogCircle) { clearInterval(fadeOut); return; }
      fogCircle.setStyle({ fillOpacity: op });
      if (op === 0) clearInterval(fadeOut);
    }, 50);
  }, 7000);

  map.flyTo([luggage.lat, luggage.lng], 5, { animate: true, duration: 1.5 });
}

// ── Immediate fog effect activation on button click ──
function togglePopup() {
  showFog();
}


async function foundLuggage() {
  if (fogCircle) { fogCircle.remove(); fogCircle = null; }

  const icon = L.divIcon({
    html: `<div style="font-size:30px;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.5))">🧳</div>`,
    iconSize: [34, 34], iconAnchor: [17, 34], className: '',
  });
  L.marker([luggage.lat, luggage.lng], { icon })
    .addTo(map)
    .bindPopup(`<strong>🧳 Found!</strong><br>${luggage.name}<br>${guessCount} attempts`)
    .openPopup();
  map.flyTo([luggage.lat, luggage.lng], 6, { animate: true, duration: 2 });

  if (DATA_SOURCE === 'json') {
    saveToLocalLeaderboard(guessCount);
  } else {
    try {
      await fetch(`${API_BASE}/leaderboard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: 'Player',
          score: Math.max(0, 1000 - guessCount * 80),
          level: 1,
          flights_number: guessCount
        })
      });
    } catch(e) { console.warn('Leaderboard save failed:', e); }
  }
}

function saveToLocalLeaderboard(attempts) {
  try {
    const entry = {
      player_name: 'Player',
      score: Math.max(0, 1000 - attempts * 80),
      level: 1,
      flights_number: attempts,
      country: luggage.name,
      date: new Date().toLocaleDateString()
    };
    const board = JSON.parse(localStorage.getItem('lug_leaderboard') || '[]');
    board.push(entry);
    board.sort((a, b) => b.score - a.score);
    localStorage.setItem('lug_leaderboard', JSON.stringify(board.slice(0, 10)));
  } catch(e) {}
}

function setFabState(state) {
  const fab = document.getElementById('lug-fab');
  if (!fab) return;
  fab.style.opacity     = state === 'loading' ? '0.6' : '1';
  fab.style.borderColor = state === 'error'   ? '#ff5c5c' : '';
  fab.title = state === 'loading' ? 'Loading...' : state === 'error' ? 'Load error — check console' : 'Show hint zone';
}

function updateBadge() {}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 +
    Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLon/2)**2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function injectUI() {
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <button id="lug-fab" onclick="togglePopup()" title="Show hint zone">
      <img src="mem_cat.jpg" style="width:80px;height:80px;object-fit:contain;border-radius:50%;">
    </button>
  `;
  document.body.appendChild(wrap);
}

function injectStyles() {
  const s = document.createElement('style');
  s.textContent = `
    #lug-fab {
      position: fixed; bottom: 24px; right: 24px; z-index: 10000;
      width: 80px; height: 80px; border-radius: 50%;
      background: #0e2040; border: 2px solid #1e4a7a;
      box-shadow: 0 4px 20px rgba(0,0,0,0.45);
      font-size: 26px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s, opacity 0.3s;
      outline: none;
    }
    #lug-fab:hover { transform: scale(1.1); box-shadow: 0 6px 24px rgba(255,224,102,0.35); border-color: #ffe066; }
    #lug-fab:active { transform: scale(0.95); }

    .lug-badge {
      position: absolute; top: -4px; right: -4px;
      background: #4db8ff; color: #060e1e;
      font-size: 11px; font-weight: 700;
      width: 20px; height: 20px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-family: system-ui, sans-serif; border: 2px solid #fff;
    }

    .lug-tooltip {
      background: rgba(6,12,28,0.92) !important; border: 1px solid #1e4070 !important;
      color: #e8f4ff !important; font-size: 12px !important; font-weight: 600 !important;
      border-radius: 8px !important; padding: 4px 10px !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important; white-space: nowrap;
    }
    .lug-tooltip::before { display: none !important; }
  `;
  document.head.appendChild(s);
}
