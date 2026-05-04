window.showVictory = function({ airports = [], time = '—', points = 0 } = {}) {
  injectVictoryStyles();

  const old = document.getElementById('victory-overlay');
  if (old) old.remove();

  const airportListHTML = airports.length
    ? airports.map((code, i) => `
        <div class="vic-airport-row">
          <span class="vic-airport-num">${i + 1}</span>
          <span class="vic-airport-code">✈ ${code}</span>
        </div>`).join('')
    : `<div style="color:#3d6a99;font-size:13px;padding:8px 0">No airports recorded</div>`;

  const overlay = document.createElement('div');
  overlay.id = 'victory-overlay';
  overlay.innerHTML = `
    <div class="vic-modal" id="vic-modal">

      <!-- Header -->
      <div class="vic-header">
        <div class="vic-title-row">
          <img src="../assets/pepega.jpg" alt="trophy" style="width:48px;height:48px;object-fit:cover;border-radius:50%;">
          <div>
            <div class="vic-title">LUGGAGE FOUND!</div>
            <div class="vic-subtitle">Mission accomplished!</div>
          </div>
        </div>
        <button class="vic-close-btn" onclick="closeVictory()" title="Back to main menu">✕</button>
      </div>

      <!-- GIF + текст -->
      <div class="vic-gif-block">
        <div class="vic-gif-wrap">
          <img src="../assets/giphy.gif" alt="Win animation" style="width:100%;height:100%;object-fit:cover;">
        </div>
        <div class="vic-congrats-text">
          <p>You successfully tracked down<br>the lost luggage across Europe!</p>
        </div>
      </div>

      <!-- Статистика -->
      <div class="vic-stats-row">
        <div class="vic-stat-card">
          <div class="vic-stat-val" style="color:#ffe066" id="vic-points">${points}</div>
          <div class="vic-stat-lbl">Points</div>
        </div>
        <div class="vic-stat-card">
          <div class="vic-stat-val" style="color:#4db8ff" id="vic-time">${time}</div>
          <div class="vic-stat-lbl">Time</div>
        </div>
        <div class="vic-stat-card">
          <div class="vic-stat-val" style="color:#3ddc84" id="vic-airport-count">${airports.length}</div>
          <div class="vic-stat-lbl">Airports</div>
        </div>
      </div>

      <!-- Список аэропортов -->
      <div class="vic-section">
        <div class="vic-section-title">✈ Visited Airports</div>
        <div class="vic-airport-list" id="vic-airport-list">
          ${airportListHTML}
        </div>
      </div>

      <!-- Кнопки -->
      <div class="vic-buttons">
        <button class="vic-btn vic-btn-route" onclick="onShowRoute()">
           Show Route
        </button>
        <button class="vic-btn vic-btn-leaders" onclick="onShowLeaderboard()">
           Leaderboard
        </button>
        <button class="vic-btn vic-btn-close" onclick="closeVictory()">
           Main Menu
        </button>
      </div>

    </div>
  `;

  document.body.appendChild(overlay);

  // анимация появления
  requestAnimationFrame(() => overlay.classList.add('vic-show'));
};

// ── ЗАКРЫТЬ → возврат на главное меню ──
window.closeVictory = function() {
  const overlay = document.getElementById('victory-overlay');
  if (!overlay) return;
  overlay.classList.remove('vic-show');
  overlay.classList.add('vic-hide');
  setTimeout(() => {
    overlay.remove();
    if (typeof go === 'function') go('screen-main');
  }, 350);
};

// ── КНОПКИ ──
window.onShowRoute = function() {
  closeVictory();
  const routeBtn = document.getElementById('show_route');
  if (routeBtn) routeBtn.click();
};

window.onShowLeaderboard = function() {
  const overlay = document.getElementById('victory-overlay');
  if (overlay) {
    overlay.classList.remove('vic-show');
    overlay.classList.add('vic-hide');
    setTimeout(() => {
      overlay.remove();
      if (typeof go === 'function') go('screen-leaderboard');
    }, 350);
  }
};


function injectVictoryStyles() {
  if (document.getElementById('vic-styles')) return;
  const s = document.createElement('style');
  s.id = 'vic-styles';
  s.textContent = `
    /* Overlay */
    #victory-overlay {
      position: fixed; inset: 0; z-index: 20000;
      background: rgba(4, 10, 22, 0.82);
      backdrop-filter: blur(6px);
      display: flex; align-items: center; justify-content: center;
      padding: 16px;
      opacity: 0; transition: opacity 0.35s ease;
      font-family: 'Segoe UI', system-ui, sans-serif;
    }
    #victory-overlay.vic-show  { opacity: 1; }
    #victory-overlay.vic-hide  { opacity: 0; }

    /* Modal card */
    .vic-modal {
      background: #07101e;
      border: 1px solid #1e4070;
      border-radius: 18px;
      width: 100%; max-width: 480px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0,0,0,0.7), 0 0 0 1px #4db8ff22;
      transform: translateY(24px) scale(0.96);
      transition: transform 0.4s cubic-bezier(0.16,1,0.3,1);
      scrollbar-width: thin; scrollbar-color: #1e4070 transparent;
    }
    #victory-overlay.vic-show .vic-modal { transform: translateY(0) scale(1); }

    /* Header */
    .vic-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 18px 20px 14px;
      border-bottom: 1px solid #1e4070;
    }
    .vic-title-row { display: flex; align-items: center; gap: 12px; }
    .vic-trophy { font-size: 36px; filter: drop-shadow(0 0 10px #ffd70088); }
    .vic-title {
      font-family: 'Bebas Neue', 'Impact', sans-serif;
      font-size: 28px; letter-spacing: 3px;
      color: #ffe066;
      line-height: 1;
    }
    .vic-subtitle { font-size: 12px; color: #3d6a99; margin-top: 3px; letter-spacing: 0.5px; }
    .vic-close-btn {
      background: transparent; border: 1px solid #1e4070;
      border-radius: 8px; color: #3d6a99; font-size: 16px;
      width: 32px; height: 32px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.18s; flex-shrink: 0;
    }
    .vic-close-btn:hover { border-color: #ff5c5c; color: #ff5c5c; }

    /* GIF блок */
    .vic-gif-block {
      display: flex; align-items: center; gap: 16px;
      padding: 16px 20px;
      border-bottom: 1px solid #1e4070;
      background: #080f1e;
    }
    .vic-gif-wrap {
      width: 80px; height: 80px; flex-shrink: 0;
      border-radius: 12px;
      border: 1px solid #1e4070;
      background: #0e2040;
      display: flex; align-items: center; justify-content: center;
      overflow: hidden;
    }
    /* Если есть GIF — замени .vic-gif-placeholder на <img src="win.gif"> */
    .vic-gif-placeholder { font-size: 40px; animation: gifFloat 2s ease-in-out infinite; }
    @keyframes gifFloat {
      0%,100% { transform: translateY(0); }
      50%      { transform: translateY(-6px); }
    }
    .vic-congrats-text { font-size: 14px; color: #a0c4e8; line-height: 1.6; }
    .vic-congrats-text p { margin: 0 0 4px; }
    .vic-congrats-small { font-size: 12px; color: #3d6a99; }

    /* Статы */
    .vic-stats-row {
      display: flex; gap: 0;
      border-bottom: 1px solid #1e4070;
    }
    .vic-stat-card {
      flex: 1; text-align: center;
      padding: 14px 8px;
      border-right: 1px solid #1e4070;
    }
    .vic-stat-card:last-child { border-right: none; }
    .vic-stat-val {
      font-family: 'Bebas Neue', 'Impact', sans-serif;
      font-size: 30px; letter-spacing: 1px; line-height: 1;
    }
    .vic-stat-lbl { font-size: 10px; color: #3d6a99; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 4px; }

    /* Список аэропортов */
    .vic-section { padding: 14px 20px; border-bottom: 1px solid #1e4070; }
    .vic-section-title {
      font-size: 11px; font-weight: 600; letter-spacing: 1px;
      color: #3d6a99; text-transform: uppercase; margin-bottom: 10px;
    }
    .vic-airport-list {
      display: flex; flex-direction: column; gap: 6px;
      max-height: 160px; overflow-y: auto;
      scrollbar-width: thin; scrollbar-color: #1e4070 transparent;
    }
    .vic-airport-row {
      display: flex; align-items: center; gap: 10px;
      background: #0d1e35; border: 1px solid #1e4070;
      border-radius: 8px; padding: 7px 12px;
    }
    .vic-airport-num {
      font-size: 11px; color: #3d6a99; font-weight: 600;
      width: 18px; text-align: center; flex-shrink: 0;
    }
    .vic-airport-code { font-size: 13px; color: #4db8ff; font-weight: 600; letter-spacing: 0.5px; }

    /* Кнопки */
    .vic-buttons {
      display: flex; flex-direction: column; gap: 8px;
      padding: 16px 20px 20px;
    }
    .vic-btn {
      width: 100%; padding: 12px;
      border-radius: 10px; font-size: 14px; font-weight: 600;
      cursor: pointer; transition: all 0.18s;
      font-family: inherit; letter-spacing: 0.3px;
      display: flex; align-items: center; justify-content: center; gap: 8px;
    }
    .vic-btn-route {
      background: rgba(77,184,255,0.12);
      border: 1px solid rgba(77,184,255,0.3);
      color: #4db8ff;
    }
    .vic-btn-route:hover { background: rgba(77,184,255,0.22); border-color: #4db8ff; }

    .vic-btn-leaders {
      background: rgba(255,215,0,0.1);
      border: 1px solid rgba(255,215,0,0.25);
      color: #ffd700;
    }
    .vic-btn-leaders:hover { background: rgba(255,215,0,0.2); border-color: #ffd700; }

    .vic-btn-close {
      background: transparent;
      border: 1px solid #1e4070;
      color: #7aaed6;
    }
    .vic-btn-close:hover { border-color: #4db8ff; color: #e8f4ff; }
  `;
  document.head.appendChild(s);
}
