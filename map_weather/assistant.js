const DATA_SOURCE = 'json';
const JSON_FILE   = 'game_data.json';
const API_BASE    = 'http://localhost:5000/api';

let luggage   = null;
let fogCircle = null;

// ── Start ──
window.addEventListener('load', () => {
  injectStyles();
  injectUI();
});

// ── Country loading ──
async function startNewGame() {
  luggage = null;
  if (fogCircle) { fogCircle.remove(); fogCircle = null; }
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

function setFabState(state) {
  const fab = document.getElementById('lug-fab');
  if (!fab) return;
  fab.style.opacity     = state === 'loading' ? '0.6' : '1';
  fab.style.borderColor = state === 'error'   ? '#ff5c5c' : '';
  fab.title = state === 'loading' ? 'Loading...' : state === 'error' ? 'Load error — check console' : 'Show hint zone';
}

function injectUI() {
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <button id="lug-fab" onclick="showFog()" title="Show hint zone">
      <img src="../assets/mem_cat.jpg" alt="Assistant" style="width:80px;height:80px;object-fit:cover;border-radius:50%;">
    </button>
  `;
  document.body.appendChild(wrap);
}

function injectStyles() {
  const s = document.createElement('style');
  s.textContent = `
    #lug-fab {
      position: fixed; bottom: 10px; right: 24px; z-index: 10000;
      width: 80px; height: 80px; border-radius: 50%;
      background: #0e2040; border: 2px solid #1e4a7a;
      box-shadow: 0 4px 20px rgba(0,0,0,0.45);
      cursor: pointer; padding: 0; overflow: hidden;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s, opacity 0.3s;
      outline: none;
    }
    #lug-fab:hover { transform: scale(1.1); box-shadow: 0 6px 24px rgba(255,224,102,0.35); border-color: #ffe066; }
    #lug-fab:active { transform: scale(0.95); }
  `;
  document.head.appendChild(s);
}
