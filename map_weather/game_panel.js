window.addEventListener('load', () => {
  injectPanelStyles();
  injectPanelUI();
  refreshGameView();
});

async function refreshGameView() {
  try {
    const res = await fetch('/api/game_view');
    const data = await res.json();

    const noView = !data.success || !data.view;
    const noQuestion = !noView && (!data.view.panel || !data.view.panel.question);
    const noSetup =
      !noView &&
      data.view.game &&
      !data.view.game.game_started &&
      !data.view.game.setup_stage;

    if (noView || noQuestion || noSetup) {
      await startNewGame();
      return;
    }

    renderGameView(data.view);
  } catch (err) {
    console.error('refreshGameView error:', err);
    setFeedback('Server connection error');
  }
}

async function startNewGame() {
  try {
    const startRes = await fetch('/api/start_game', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_name: 'Guest',
        level: 'level2'
      })
    });

    const startData = await startRes.json();

    if (!startData.success || !startData.view) {
      setFeedback(startData.error || 'Failed to start game');
      return;
    }

    renderGameView(startData.view);
  } catch (err) {
    console.error('startNewGame error:', err);
    setFeedback('Failed to start new game');
  }
}

function renderGameView(view) {
  const questionEl = document.getElementById('gp-question');
  const optionsEl = document.getElementById('gp-options');
  const inputEl = document.getElementById('gp-input');

  if (questionEl) {
    questionEl.textContent = view.panel?.question || 'Waiting for question...';
  }

  if (optionsEl) {
    const options = Array.isArray(view.panel?.options) ? view.panel.options : [];

    optionsEl.innerHTML = options.map((opt, idx) => {
      const safeIndex = opt.index ?? (idx + 1);
      const safeLabel = opt.label ?? opt.value ?? 'Unknown option';

      return `
        <div class="gp-option-line">
          <span class="gp-option-index">${safeIndex}.</span>
          <span class="gp-option-label">${escapeHtml(String(safeLabel))}</span>
        </div>
      `;
    }).join('');
  }

  if (inputEl) {
    inputEl.value = '';
    inputEl.focus();
  }

  setFeedback(view.panel?.feedback || '');
}

async function submitNumericAnswer() {
  const input = document.getElementById('gp-input');
  if (!input) return;

  const rawValue = input.value.trim();

  if (!rawValue) {
    setFeedback('Enter a number');
    return;
  }

  const numericValue = Number(rawValue);

  if (!Number.isInteger(numericValue) || numericValue < 1) {
    setFeedback('Enter a valid option number');
    return;
  }

  setFeedback('Submitting answer...');

  try {
    const res = await fetch('/api/submit_answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer: numericValue })
    });

    const data = await res.json();

    if (!data.success && !data.view) {
      setFeedback(data.error || data.message || 'Answer failed');
      return;
    }

    if (data.view) {
      renderGameView(data.view);
    }

    if (data.won) {
      setFeedback(data.message || 'You found the luggage!');

      try {
        const finishResponse = await fetch('/api/finish_game', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        const finishData = await finishResponse.json();

        if (finishData.success) {
          await fetch('/api/save_score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              player_name: finishData.player_name,
              difficulty_level: finishData.difficulty_level,
              score: finishData.score
            })
          });
        }
      } catch (e) {
        console.error('finish/save score error:', e);
      }

      if (typeof showVictoryScreen === 'function') {
        showVictoryScreen();
      }
    }
  } catch (err) {
    console.error('submitNumericAnswer error:', err);
    setFeedback('Server error while submitting answer');
  }
}

async function resetGameSession() {
  try {
    setFeedback('Resetting game...');

    const resetRes = await fetch('/api/reset_game', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    const resetData = await resetRes.json();

    if (!resetData.success) {
      setFeedback(resetData.error || 'Failed to reset game');
      return;
    }

    await startNewGame();
    setFeedback('');
  } catch (err) {
    console.error('resetGameSession error:', err);
    setFeedback('Reset failed');
  }
}

function setFeedback(text) {
  const feedbackEl = document.getElementById('gp-feedback');
  if (!feedbackEl) return;

  const value = text || '';

  if (value.startsWith('Flight set to ')) {
    feedbackEl.textContent = '';
    return;
  }

  feedbackEl.textContent = value;
}

function escapeHtml(str) {
  return str
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function injectPanelUI() {
  const existing = document.getElementById('game-panel');
  if (existing) existing.remove();

  const div = document.createElement('div');
  div.id = 'game-panel';
  div.innerHTML = `
    <div class="gp-main-block">
      <div class="gp-question-block">
        <div class="gp-question" id="gp-question">Loading...</div>
        <div id="gp-options" class="gp-options-list"></div>
      </div>
    </div>

    <div class="gp-input-row">
      <input
        id="gp-input"
        class="gp-input"
        type="text"
        inputmode="numeric"
        autocomplete="off"
        placeholder="Type option number..."
      >
      <button id="gp-submit" class="gp-submit" type="button">→</button>
    </div>

    <div class="gp-feedback" id="gp-feedback"></div>
  `;

  document.body.appendChild(div);

  const input = document.getElementById('gp-input');
  const submit = document.getElementById('gp-submit');
  const reset = document.getElementById('gp-reset');

  if (input) {
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        submitNumericAnswer();
      }
    });
  }

  if (submit) {
    submit.addEventListener('click', submitNumericAnswer);
  }

  if (reset) {
    reset.addEventListener('click', resetGameSession);
  }
}

function injectPanelStyles() {
  const existing = document.getElementById('game-panel-inline-style');
  if (existing) existing.remove();

  const s = document.createElement('style');
  s.id = 'game-panel-inline-style';
  s.textContent = `
    #game-panel {
      position: fixed;
      right: 0;
      bottom: 2rem;
      z-index: 9998;
      width: 18.5rem;
      height: 61vh;
      margin: 0;
      padding: 8px 0 8px 14px;
      background: transparent;
      border: none;
      border-radius: 0;
      box-shadow: none;
      backdrop-filter: none;
      font-family: 'Segoe UI', system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      gap: 8px;
      overflow: hidden;
    }

    .gp-reset {
      flex-shrink: 0;
      background: #19314f;
      color: #dcecff;
      border: 1px solid #2b4e77;
      border-right: none;
      border-radius: 8px 0 0 8px;
      padding: 8px 14px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.18s, border-color 0.18s;
    }

    .gp-reset:hover {
      background: #234366;
      border-color: #4db8ff;
    }
    
    .gp-name {
      font-size: 14px;
      font-weight: 600;
      color: #4db8ff;
      line-height: 1.3;
      word-break: break-word;
    }

    .gp-main-block {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
      min-height: 0;
    }

    .gp-question-block {
      background: #0d1e35;
      border: 1px solid #1e4070;
      border-right: none;
      border-radius: 8px 0 0 8px;
      padding: 10px 12px 10px 12px;
      flex: 1;
      min-height: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .gp-question {
      font-size: 15px;
      font-weight: 600;
      color: #e8f4ff;
      line-height: 1.45;
      margin-bottom: 5px;
      flex-shrink: 0;
      padding-right: 4px;
    }

    .gp-options-list {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      overflow-x: hidden;
      column-count: 2;
      column-gap: 10px;
      column-fill: auto;
      padding: 1px 2px 1px 0;
      font-size: 12.5px;
      color: #dcecff;
      scrollbar-width: thin;
      scrollbar-color: #29527a #0d1e35;
    }

    .gp-options-list::-webkit-scrollbar {
      width: 8px;
    }

    .gp-options-list::-webkit-scrollbar-track {
      background: #0d1e35;
    }

    .gp-options-list::-webkit-scrollbar-thumb {
      background: #29527a;
      border-radius: 8px;
    }

    .gp-option-line {
      break-inside: avoid;
      margin-bottom: 2px;
      line-height: 1.2;
      word-break: break-word;
    }

    .gp-option-index {
      color: #4db8ff;
      font-weight: 700;
      margin-right: 3px;
    }

    .gp-option-label {
      color: #dcecff;
    }

    .gp-input-row {
      display: flex;
      gap: 6px;
      flex-shrink: 0;
      padding-right: 0;
    }

    .gp-input {
      flex: 1;
      min-width: 0;
      background: #0d1e35;
      border: 1px solid #1e4070;
      border-right: none;
      border-radius: 8px 0 0 8px;
      color: #e8f4ff;
      font-size: 12px;
      padding: 10px 12px;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s, background 0.2s;
    }

    .gp-input::placeholder {
      color: #54789d;
    }

    .gp-input:focus {
      border-color: #4db8ff;
      background: #10233c;
    }

    .gp-submit {
      width: 42px;
      flex-shrink: 0;
      background: #4db8ff;
      color: #08111d;
      border: none;
      border-radius: 8px 0 0 8px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.18s, transform 0.12s;
    }

    .gp-submit:hover {
      background: #7dd3ff;
    }

    .gp-submit:active {
      transform: scale(0.96);
    }

    .gp-feedback {
      min-height: 18px;
      font-size: 12px;
      font-weight: 500;
      text-align: center;
      color: #ffcf70;
      flex-shrink: 0;
      padding-right: 8px;
    }

    @media (max-width: 1500px) {
      #game-panel {
        width: 32rem;
      }

      .gp-options-list {
        column-count: 3;
        column-gap: 6px;
      }
    }

    @media (max-width: 1280px) {
      #game-panel {
        width: 28rem;
      }

      .gp-options-list {
        column-count: 2;
        column-gap: 8px;
      }
    }

    @media (max-width: 980px) {
      #game-panel {
        width: 24rem;
        height: calc(100vh - 140px);
      }

      .gp-options-list {
        column-count: 2;
        column-gap: 8px;
      }
    }
  `;
  document.head.appendChild(s);
}