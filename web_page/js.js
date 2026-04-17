
// ── STARS ──
(function(){
  const c = document.getElementById('stars');
  for(let i=0;i<120;i++){
    const s = document.createElement('div');
    s.className = 'star';
    const size = Math.random()*2+0.5;
    s.style.cssText = `
      left:${Math.random()*100}vw; top:${Math.random()*100}vh;
      width:${size}px; height:${size}px;
      --d:${(Math.random()*4+2).toFixed(1)}s;
      --delay:${(Math.random()*5).toFixed(1)}s;
      --op:${(Math.random()*0.6+0.1).toFixed(2)};
    `;
    c.appendChild(s);
  }
})();

// ── TRANSLATIONS ──
const T = {
  en: {
    gameName: 'Find the Bag!',
    start: 'START', continue: 'CONTINUE', leaderboard: 'LEADERBOARD',
    gameRules: 'GAME RULES', settings: 'SETTINGS', exit: 'EXIT',
    chooseLevel: 'CHOOSE LEVEL',
    level1: 'Level 1', desc1: 'Large airports only',
    level2: 'Level 2', desc2: 'Large and medium airports',
    level3: 'Level 3', desc3: 'Large, medium and small',
    easy: 'EASY', medium: 'MEDIUM', hard: 'HARD',
    sound: 'Sound', hints: 'Hints', on: 'ON', off: 'OFF',
    topPlayers: 'TOP PLAYERS',
    back: '← Back',
    tabLogin: 'LOG IN', tabRegister: 'REGISTER',
    labelUsername: 'Username',
    labelPassword: 'Password', labelConfirm: 'Confirm Password',
    placeholderUser: 'Your username',
    placeholderPass: 'Min 6 characters', placeholderConfirm: 'Repeat password',
    btnLogin: 'LOG IN', btnRegister: 'CREATE ACCOUNT', btnGuest: 'Continue as Guest',
    or: 'or',
    errRequired: 'This field is required',
    errPassShort: 'Password must be at least 6 characters',
    errPassMatch: 'Passwords do not match',
    welcomeBack: 'WELCOME BACK,', welcomeNew: 'WELCOME,',
    preparingMsg: 'Preparing your runway...',
    loggedInAs: 'Logged in', exit: 'LOG OUT',
    logoutTitle: 'LOG OUT?', logoutMsg: 'Are you sure you want to log out?<br>Your progress will be saved.',
    cancel: 'CANCEL', confirmLogout: 'LOG OUT',
    rulesText: `<p>Guess the name of the airport shown on screen. You'll see a photo or clue — type the correct name to score points.</p><p>You have <strong style="color:#e8f4ff">3 attempts</strong> per question. Faster answers earn more points. Streaks give bonus multipliers.</p><p>Choose your level before starting. <strong style="color:#3ddc84">Level 1</strong> covers major international airports. <strong style="color:#ffb347">Level 2</strong> adds regional airports. <strong style="color:#ff5c5c">Level 3</strong> includes small and private airfields.</p>`,
  },
  fi: {
    gameName: 'Löydä laukku!',
    start: 'ALOITA', continue: 'JATKA', leaderboard: 'TULOSTAULUKKO',
    gameRules: 'PELISÄÄNNÖT', settings: 'ASETUKSET', exit: 'POISTU',
    chooseLevel: 'VALITSE TASO',
    level1: 'Taso 1', desc1: 'Vain suuret lentokentät',
    level2: 'Taso 2', desc2: 'Suuret ja keskikokoiset',
    level3: 'Taso 3', desc3: 'Kaikki lentokentät',
    easy: 'HELPPO', medium: 'KESKI', hard: 'VAIKEA',
    sound: 'Ääni', hints: 'Vihjeet', on: 'PÄÄLLE', off: 'POIS',
    topPlayers: 'PARHAAT PELAAJAT',
    back: '← Takaisin',
    tabLogin: 'KIRJAUDU', tabRegister: 'REKISTERÖIDY',
    labelUsername: 'Käyttäjänimi',
    labelPassword: 'Salasana', labelConfirm: 'Vahvista salasana',
    placeholderUser: 'Käyttäjänimesi',
    placeholderPass: 'Vähintään 6 merkkiä', placeholderConfirm: 'Toista salasana',
    btnLogin: 'KIRJAUDU', btnRegister: 'LUO TILI', btnGuest: 'Jatka vieraana',
    or: 'tai',
    errRequired: 'Tämä kenttä on pakollinen',
    errPassShort: 'Salasanan on oltava vähintään 6 merkkiä',
    errPassMatch: 'Salasanat eivät täsmää',
    welcomeBack: 'TERVETULOA TAKAISIN,', welcomeNew: 'TERVETULOA,',
    preparingMsg: 'Valmistellaan kiitotietäsi...',
    loggedInAs: 'Kirjautunut', exit: 'KIRJAUDU ULOS',
    logoutTitle: 'KIRJAUDUTAAN ULOS?', logoutMsg: 'Haluatko varmasti kirjautua ulos?<br>Edistymisesi tallennetaan.',
    cancel: 'PERUUTA', confirmLogout: 'KIRJAUDU ULOS',
    rulesText: `<p>Arvaa näytöllä näkyvän lentokentän nimi. Näet kuvan tai vihjeen — kirjoita oikea nimi saadaksesi pisteitä.</p><p>Sinulla on <strong style="color:#e8f4ff">3 yritystä</strong> per kysymys. Nopeammat vastaukset tuovat enemmän pisteitä. Peräkkäiset oikeat vastaukset antavat kerroinbonuksia.</p><p>Valitse taso ennen aloittamista. <strong style="color:#3ddc84">Taso 1</strong> kattaa suuret kansainväliset lentokentät. <strong style="color:#ffb347">Taso 2</strong> lisää alueelliset lentokentät. <strong style="color:#ff5c5c">Taso 3</strong> sisältää pienet ja yksityiset lentokentät.</p>`,
  }
};

let lang = 'en';
let currentUser = '';

function setLang(l) {
  lang = l;
  document.querySelectorAll('.lang-btn').forEach(b =>
    b.classList.toggle('active', b.textContent === l.toUpperCase())
  );
  document.querySelectorAll('[data-t]').forEach(el => {
    const key = el.getAttribute('data-t');
    if (T[l][key] !== undefined) el.textContent = T[l][key];
  });
  document.querySelectorAll('[data-t-html]').forEach(el => {
    const key = el.getAttribute('data-t-html');
    if (T[l][key] !== undefined) el.innerHTML = T[l][key];
  });
  document.querySelectorAll('[data-t-ph]').forEach(el => {
    const key = el.getAttribute('data-t-ph');
    if (T[l][key] !== undefined) el.placeholder = T[l][key];
  });
  const logoName = document.querySelector('.auth-logo-name');
  if (logoName) logoName.textContent = T[l].gameName;
}

// init
setLang('en');

// ── AUTH ──
function switchTab(tab) {
  ['login','register'].forEach(t => {
    document.getElementById('tab-'+t).classList.toggle('active', t===tab);
    document.getElementById('panel-'+t).classList.toggle('active', t===tab);
  });
  clearErrors();
}

function clearErrors() {
  document.querySelectorAll('.field-error').forEach(e => { e.classList.remove('show'); e.textContent=''; });
  document.querySelectorAll('.field-input').forEach(i => i.classList.remove('error'));
}

function showErr(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg; el.classList.add('show');
  document.getElementById(id.replace('-err','')).classList.add('error');
  return false;
}

function isEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

function doLogin() {
  clearErrors();
  const user = document.getElementById('login-user').value.trim();
  const pass = document.getElementById('login-pass').value;
  let ok = true;
  if (!user) ok = showErr('login-user-err', T[lang].errRequired);
  if (!pass) ok = showErr('login-pass-err', T[lang].errRequired);
  if (!ok) return;
  showSuccess(T[lang].welcomeBack + ' ' + user.toUpperCase(), user);
}

function doRegister() {
  clearErrors();
  const user    = document.getElementById('reg-user').value.trim();
  const email   = document.getElementById('reg-email').value.trim();
  const pass    = document.getElementById('reg-pass').value;
  const confirm = document.getElementById('reg-confirm').value;
  let ok = true;
  if (!user)               ok = showErr('reg-user-err',    T[lang].errRequired);
  if (!email)              ok = showErr('reg-email-err',   T[lang].errRequired);
  else if (!isEmail(email))ok = showErr('reg-email-err',   T[lang].errEmail);
  if (!pass)               ok = showErr('reg-pass-err',    T[lang].errRequired);
  else if (pass.length<6)  ok = showErr('reg-pass-err',    T[lang].errPassShort);
  if (!confirm)            ok = showErr('reg-confirm-err', T[lang].errRequired);
  else if (pass!==confirm) ok = showErr('reg-confirm-err', T[lang].errPassMatch);
  if (!ok) return;
  showSuccess(T[lang].welcomeNew + ' ' + user.toUpperCase(), user);
}

function doGuest() {
  const name = lang === 'fi' ? 'VIERAS' : 'GUEST';
  showSuccess((lang==='fi'?'TERVETULOA, ':'WELCOME, ') + name, name);
}

function showSuccess(nameMsg, username) {
  currentUser = username || nameMsg.split(' ').pop();
  document.querySelectorAll('.auth-panel').forEach(p => p.classList.remove('active'));
  const s = document.getElementById('auth-success');
  document.getElementById('success-name').textContent = nameMsg;
  document.getElementById('success-msg').textContent = T[lang].preparingMsg;
  s.classList.add('show');
  setTimeout(() => {
    const ov = document.getElementById('auth-overlay');
    ov.classList.add('hide');
    setTimeout(() => {
      ov.style.display = 'none';
      document.getElementById('menu-username').textContent = currentUser;
    }, 350);
  }, 1600);
}

// ── LOGOUT ──
function showLogout() {
  document.getElementById('logout-overlay').classList.add('show');
}
function hideLogout() {
  document.getElementById('logout-overlay').classList.remove('show');
}
function doLogout() {
  hideLogout();
  currentUser = '';
  // Reset auth form
  ['login-user','login-pass','reg-user','reg-email','reg-pass','reg-confirm']
    .forEach(id => { const el = document.getElementById(id); if(el) el.value=''; });
  clearErrors();
  document.getElementById('auth-success').classList.remove('show');
  document.querySelectorAll('.auth-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-login').classList.add('active');
  switchTab('login');
  // Show auth overlay again
  const ov = document.getElementById('auth-overlay');
  ov.style.display = 'flex';
  ov.classList.remove('hide');
  ov.style.animation = 'none';
  void ov.offsetWidth;
  ov.style.animation = 'fadeIn 0.35s ease';
  // Go back to main screen (so menu is reset)
  go('screen-main');
}

// ── NAVIGATION ──
function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function startGame(level) {
  const msg = lang === 'fi'
    ? `Peli alkaa tasolta ${level}! (Tähän tulee pelinäkymä)`
    : `Starting game at Level ${level}! (Game screen goes here)`;
  alert(msg);
}

function toggle(setting, val) {
  const on  = document.getElementById(setting + '-on');
  const off = document.getElementById(setting + '-off');
  on.classList.toggle('active',  val === 'on');
  off.classList.toggle('active', val === 'off');
}
