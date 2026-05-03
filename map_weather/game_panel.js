window.addEventListener('load', () => {
  injectPanelStyles();
  injectPanelUI();
});

// Python/Flask endpoint for updating airport data
// setCurrentAirport('Helsinki-Vantaa');
window.setCurrentAirport = function(name) {
  const el = document.getElementById('gp-airport-name');
  if (el) el.textContent = name || '—';
};

// ── Python question retrieval ──
// setQuestion('Which country is this airport in?');
window.setQuestion = function(text) {
  const el = document.getElementById('gp-question');
  if (el) el.textContent = text || '';
};

//  Answer validation
function checkAnswer() {
  const input    = document.getElementById('gp-input');
  const feedback = document.getElementById('gp-feedback');
  const val      = input.value.trim();
  if (!val) return;

  // Deferred integration of answer‑validation logic via Python/Flask
  console.log('[GamePanel] Answer submitted:', val);
  input.value = '';
}

function injectPanelUI() {
  const div = document.createElement('div');
  div.id = 'game-panel';
  div.innerHTML = `

    <div class="gp-block">
      <div class="gp-label">CURRENT AIRPORT</div>
      <div class="gp-airport-block">
        <div class="gp-name" id="gp-airport-name">—</div>
      </div>
    </div>

    <div class="gp-divider"></div>

    <div class="gp-block">
      <div class="gp-label">QUESTION</div>
      <div class="gp-question-block">
        <div class="gp-question" id="gp-question">Waiting for question...</div>
      </div>
    </div>

    <div class="gp-input-row">
      <input
        id="gp-input"
        class="gp-input"
        type="text"
        placeholder="Type your answer..."
        onkeydown="if(event.key==='Enter') checkAnswer()"
      >
      <button class="gp-submit" onclick="checkAnswer()">→</button>
    </div>
    <div class="gp-feedback" id="gp-feedback"></div>
  `;
  document.body.appendChild(div);
}

function injectPanelStyles() {
  const s = document.createElement('style');
  s.textContent = `
    #game-panel {
      position: fixed;
      bottom: 180px;
      right: 0;
      z-index: 9998;
      width: 340px;
      background: transparent;
      border: none;
      border-top: 1px solid #1e4070;
      border-radius: 0;
      padding: 14px 16px;
      box-shadow: none;
      backdrop-filter: none;
      font-family: 'Segoe UI', system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .gp-block {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .gp-label {
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 1.2px;
      color: #3d6a99;
      text-transform: uppercase;
    }

    .gp-airport-block {
      background: #0d1e35;
      border: 1px solid #1e4070;
      border-radius: 8px;
      padding: 8px 12px;
    }

    .gp-name {
      font-size: 14px;
      font-weight: 600;
      color: #4db8ff;
    }

    .gp-divider {
      height: 1px;
      background: #1e4070;
    }

    .gp-question-block {
      background: #0d1e35;
      border: 1px solid #1e4070;
      border-radius: 8px;
      padding: 10px 12px;
      min-height: 60px;
    }

    .gp-question {
      font-size: 13px;
      color: #e8f4ff;
      line-height: 1.6;
    }

    .gp-input-row {
      display: flex;
      gap: 6px;
    }

    .gp-input {
      flex: 1;
      background: #0d1e35;
      border: 1px solid #1e4070;
      border-radius: 8px;
      color: #e8f4ff;
      font-size: 12px;
      padding: 9px 11px;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s;
    }
    .gp-input::placeholder { color: #3d6a99; }
    .gp-input:focus { border-color: #4db8ff; }

    .gp-submit {
      width: 34px;
      background: #4db8ff;
      border: none;
      border-radius: 8px;
      color: #060e1e;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.18s;
      flex-shrink: 0;
    }
    .gp-submit:hover { background: #7dd3ff; }
    .gp-submit:active { transform: scale(0.95); }

    .gp-feedback {
      font-size: 12px;
      font-weight: 500;
      min-height: 16px;
      text-align: center;
    }
  `;
  document.head.appendChild(s);
}
