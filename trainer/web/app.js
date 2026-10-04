const messages = [];

async function loadProfile() {
  try {
    const r = await fetch('/profile');
    const p = await r.json();
    document.getElementById('nav-brand').textContent = p.course ? `MasterMind · ${p.course}` : 'MasterMind';
    // La lección real, del progreso del curso elegido: CS50 va por semanas, MoureDev por ejercicios.
    const pr = p.progress || {};
    document.getElementById('b-week').textContent = pr.n ? (pr.course === 'cs50' ? `Week ${pr.n}` : `Ej. ${pr.n}`) : '';
    document.getElementById('b-topic').textContent = pr.topic || '';
    document.getElementById('b-mode').textContent = p.mode;
  } catch {}
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function renderMarkdown(text) {
  // Mínimo a propósito: negrita, cursiva y código inline. Escapamos HTML primero para no abrir
  // XSS en el modo invitado (público), que muestra texto de cualquier visitante.
  let s = escapeHtml(text);
  s = s.replace(/`([^`]+?)`/g, '<code>$1</code>');
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');
  return s;
}

function addMessage(role, text) {
  const row = document.createElement('div');
  row.className = `msg-row ${role}`;
  const av = document.createElement('div');
  av.className = `avatar ${role === 'user' ? 'user' : 'bot'}`;
  av.textContent = role === 'user' ? '👤' : '🎓';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = renderMarkdown(text);
  row.appendChild(av);
  row.appendChild(bubble);
  document.getElementById('messages').appendChild(row);
  row.scrollIntoView({ behavior: 'smooth' });
}


function showTyping() {
  const row = document.createElement('div');
  row.className = 'msg-row typing';
  row.id = 'typing';
  row.innerHTML = '<div class="avatar bot">🎓</div><div class="bubble"><span></span><span></span><span></span></div>';
  document.getElementById('messages').appendChild(row);
  row.scrollIntoView({ behavior: 'smooth' });
}
function removeTyping() { document.getElementById('typing')?.remove(); }

async function streamChat(msgList) {
  const r = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: msgList, model: document.getElementById('model').value })
  });

  removeTyping();

  const row = document.createElement('div');
  row.className = 'msg-row bot';
  const av = document.createElement('div');
  av.className = 'avatar bot';
  av.textContent = '🎓';
  const bubble = document.createElement('div');
  bubble.className = 'bubble streaming';
  row.appendChild(av);
  row.appendChild(bubble);
  document.getElementById('messages').appendChild(row);
  row.scrollIntoView({ behavior: 'smooth' });

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let fullText = '';
  let buf = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6).trim();
        if (payload === '[DONE]') break;
        try {
          const parsed = JSON.parse(payload);
          if (typeof parsed === 'string') {
            fullText += parsed;
            bubble.innerHTML = renderMarkdown(hideMark(fullText));
            row.scrollIntoView({ behavior: 'smooth' });
          } else if (parsed && parsed.error) {
            bubble.innerHTML = renderMarkdown(`Error: ${parsed.error}`);
            row.className = 'msg-row error';
            bubble.classList.remove('streaming');
            return '';
          }
        } catch {}
      }
    }
  } finally {
    bubble.classList.remove('streaming');
  }
  return fullText;
}

let isAdmin = false;

// ── GUARDAR LA PARTIDA ──────────────────────────────────
// La IA pone esta marca al final del mensaje cuando apruebas el examen (Mouredev.md / CS50.md).
// Nunca se ve: se oculta mientras llega, y si llega entera se guarda la partida (solo el admin).
const MASTERED_MARK = '[[DOMINADO]]';
// Mientras dura el examen la IA pone esta otra en CADA mensaje: sirve para bloquear /kata y /read (solo valen como refuerzo antes del examen).
const EXAM_MARK = '[[EXAM]]';
let examActive = false;
// Quita la marca, y también su comienzo si todavía está llegando por trozos ("[[DOMI…").
const hideMark = t => t.replace(MASTERED_MARK, '').replace(EXAM_MARK, '').replace(/\[\[[A-Z]*\]?$/, '').trimEnd();

// Aprobado el examen, la partida se guarda sola: el tema actual pasa a dominado y el siguiente a actual.
async function saveProgress() {
  const r = await fetch('/progress/next', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  const res = await r.json();
  if (!r.ok) return addMessage('bot', `No se pudo guardar: ${res.error}`);   // p. ej. ya estás en el último tema
  const p = res.progress;
  addMessage('bot', `💾 Partida guardada: ahora estás en ${p.course === 'cs50' ? 'Week' : 'Ej.'} ${p.n} · ${p.topic}.`);
  loadProfile();                                      // la barra de arriba pasa al tema nuevo
  messages.length = 0;                                // la IA arranca el tema nuevo sin el historial del anterior
  examActive = false;
  greet();                                            // y da el enunciado del tema nuevo
}

// ── COMANDOS DEL CHAT (/ls, /back…) ─────────────────────
// Los atiende la app: NO se envían a la IA ni entran en el historial de la conversación.
const STATUS_ICONS = { mastered: '✅', current: '👉', locked: '🔒' };

// La guía de /help sale de aquí: al añadir un comando nuevo, se apunta en esta lista y aparece solo.
const EXAM_BLOCKED = ['/kata', '/read'];   // no valen durante el examen
const KATA_PROMPT = 'El estudiante ha escrito /kata. Propón ahora UNA kata sobre el tema actual: ejercicio pequeño, cerrado y ' +
  'autoverificable, en el nivel más básico, para reforzar lo que acaba de ver. No des la solución: espera su código y corrígelo ' +
  'con tus modos habituales. Una kata no es un examen: no escribas [[DOMINADO]] ni [[EXAM]].';

const COMMANDS = {
  '/help': 'Esta ayuda',
  '/ls':   'Tus ejercicios: ✅ dominados · 👉 el actual · 🔒 bloqueados',
  '/back': '/back ex1: vuelve a un ejercicio ya dominado para repasarlo (próximamente)',
  '/kata': 'Un ejercicio corto de calentamiento sobre el tema actual (no disponible en el examen)',
  '/read': 'Leer y comentar código ajeno sobre el tema actual (próximamente)',
};

// Manda a la IA una instrucción que el estudiante no ve (la respuesta sí se muestra y entra en el historial).
async function askHidden(prompt) {
  document.getElementById('send').disabled = true;
  messages.push({ role: 'user', content: prompt });
  showTyping();
  try {
    const reply = await streamChat(messages);
    if (reply) { messages.push({ role: 'assistant', content: reply }); examActive = reply.includes(EXAM_MARK); }
  } catch (e) { removeTyping(); addMessage('error', `Error de conexión: ${e.message}`); }
  document.getElementById('send').disabled = false;
}

async function runCommand(text) {
  const [cmd] = text.split(/\s+/);
  addMessage('user', text);
  if (cmd === '/help') {
    return addMessage('bot', Object.entries(COMMANDS).filter(([c]) => !(examActive && EXAM_BLOCKED.includes(c)))
      .map(([c, ayuda]) => `${c.padEnd(6)} ${ayuda}`).join('\n'));
  }
  if (examActive && EXAM_BLOCKED.includes(cmd)) return addMessage('bot', `${cmd} no está disponible durante el examen.`);
  if (cmd === '/kata') return askHidden(KATA_PROMPT);
  if (cmd === '/ls') {
    const r = await fetch('/progress');
    const d = await r.json();
    if (!r.ok) return addMessage('bot', d.error || 'No se pudo leer el progreso');
    const prefix = d.course === 'cs50' ? 'week' : 'ex';
    return addMessage('bot', d.topics.map(t => `${STATUS_ICONS[t.status]} ${prefix}${t.n}  ${t.topic}`).join('\n'));
  }
  if (COMMANDS[cmd]) return addMessage('bot', `${cmd} todavía no está hecho. Escribe /help para ver los que ya funcionan.`);
  addMessage('bot', `Comando no reconocido: ${cmd}. Escribe /help para ver los comandos.`);
}

async function send() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';
  if (text.startsWith('/')) return runCommand(text);
  document.getElementById('send').disabled = true;
  messages.push({ role: 'user', content: text });
  addMessage('user', text);
  showTyping();
  try {
    const reply = await streamChat(messages);
    if (reply) {
      messages.push({ role: 'assistant', content: reply });
      examActive = reply.includes(EXAM_MARK);
      if (isAdmin && reply.includes(MASTERED_MARK)) await saveProgress();
    }
  } catch (e) { removeTyping(); addMessage('error', `Error de conexión: ${e.message}`); }
  document.getElementById('send').disabled = false;
  input.focus();
}

async function greet() {
  showTyping();
  try {
    const hasPlan = isAdmin && planActive();      // con plan en marcha no se vuelve a preguntar el tiempo
    const reply = await streamChat([{ role: 'user', content: hasPlan ? '__greet_plan__' : '__greet__' }]);
    if (reply) {
      messages.push({ role: 'assistant', content: reply });
      if (!hasPlan) document.getElementById('quick-replies').style.display = 'flex';
    }
  } catch {}
}

document.querySelectorAll('.qr-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('quick-replies').style.display = 'none';
    planSet({ total: Number(btn.dataset.pomos), done: 0, at: Date.now() });
    document.getElementById('input').value = btn.dataset.msg;
    send();
  });
});

document.getElementById('send').addEventListener('click', send);
document.getElementById('input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
});
document.getElementById('input').addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

function makeCustomSelect(selectEl) {
  // Idempotente: si ya estaba envuelto (ej. course-select, cuyas opciones llegan por fetch
  // después de un primer envoltorio), lo deshace y lo reconstruye desde cero con las opciones
  // actuales, en vez de anidar un wrap dentro de otro.
  if (selectEl.parentNode && selectEl.parentNode.classList.contains('cs-wrap')) {
    const oldWrap = selectEl.parentNode;
    oldWrap.parentNode.insertBefore(selectEl, oldWrap);
    oldWrap.remove();
    selectEl.style.display = '';
  }
  const wrap = document.createElement('div');
  wrap.className = 'cs-wrap';
  const trigger = document.createElement('button');
  trigger.className = 'cs-trigger';
  trigger.type = 'button';
  const labelEl = document.createElement('span');
  labelEl.className = 'cs-label';
  const arrow = document.createElement('span');
  arrow.className = 'cs-arrow';
  arrow.textContent = '▾';
  trigger.appendChild(labelEl);
  trigger.appendChild(arrow);
  const list = document.createElement('ul');
  list.className = 'cs-list';
  const opts = Array.from(selectEl.options);
  const items = opts.map(opt => {
    const li = document.createElement('li');
    li.className = 'cs-item';
    li.dataset.value = opt.value;
    li.textContent = opt.text;
    li.addEventListener('click', () => {
      selectEl.value = opt.value;
      selectEl.dispatchEvent(new Event('change'));
      sync(opt.value);
      wrap.classList.remove('open');
    });
    list.appendChild(li);
    return li;
  });
  function sync(value) {
    const opt = opts.find(o => o.value === value);
    if (opt) labelEl.textContent = opt.text;
    items.forEach(li => li.classList.toggle('cs-active', li.dataset.value === value));
  }
  sync(selectEl.value);
  trigger.addEventListener('click', e => { e.stopPropagation(); wrap.classList.toggle('open'); });
  document.addEventListener('click', () => wrap.classList.remove('open'));
  selectEl.style.display = 'none';
  wrap.appendChild(trigger);
  wrap.appendChild(list);
  selectEl.parentNode.insertBefore(wrap, selectEl);
  wrap.appendChild(selectEl);
  return { sync };
}

const themeSelect = document.getElementById('theme-select');
const savedTheme = localStorage.getItem('trainer-theme') || 'harvard';
document.documentElement.setAttribute('data-theme', savedTheme);
themeSelect.value = savedTheme;

function syncThemeColor() {
  const primary = getComputedStyle(document.documentElement).getPropertyValue('--primary').trim();
  document.getElementById('meta-theme-color').setAttribute('content', primary);
}
syncThemeColor();

themeSelect.addEventListener('change', () => {
  document.documentElement.setAttribute('data-theme', themeSelect.value);
  localStorage.setItem('trainer-theme', themeSelect.value);
  syncThemeColor();
  pomoSetEmoji();
});
makeCustomSelect(themeSelect);
makeCustomSelect(document.getElementById('model'));

// ── POMODORO ──────────────────────────────────────────
const POMO_EMOJIS = {
  harvard: '🎓', oldschool: '📟', light: '☀️',
  dark: '🌙', mint: '🌿', barbie: '💅',
  dracula: '🧛', cyberpunk: '⚡'
};

function pomoSetEmoji() {}

function pomoBeep() {
  try {
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 660;
    gain.gain.setValueAtTime(0.25, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.6);
  } catch {}
}

const POMO_WORK  = 25 * 60;
const POMO_BREAK =  5 * 60;
let pomoMode      = 'work';
let pomoRemaining = POMO_WORK;
let pomoRunning   = false;
let pomoInterval  = null;
let pomoEndsAt    = 0;   // hora real (ms) a la que acaba el bloque en marcha: el reloj se calcula contra ella, no restando 1 por segundo
const POMO_KEY    = 'pomo-state';

function pomoRender() {
  pomoSetEmoji();
  const total = pomoMode === 'work' ? POMO_WORK : POMO_BREAK;
  const mins  = String(Math.floor(pomoRemaining / 60)).padStart(2, '0');
  const secs  = String(pomoRemaining % 60).padStart(2, '0');
  document.getElementById('pomo-time').textContent = `${mins}:${secs}`;
  // La línea bajo la barra se va llenando con el tiempo que ha pasado (el círculo antiguo se vaciaba).
  document.getElementById('pomo-bar').style.width = `${(1 - pomoRemaining / total) * 100}%`;
  for (const el of [document.getElementById('pomodoro'), document.getElementById('pomo-progress')]) {
    el.classList.toggle('pomo-break', pomoMode === 'break');
    el.classList.toggle('pomo-done',  pomoRemaining === 0);
  }
}

// El estado vive en el navegador para que sobreviva a recargar o cerrar la pestaña.
function pomoSave() {
  try {
    localStorage.setItem(POMO_KEY, JSON.stringify({ mode: pomoMode, remaining: pomoRemaining, endsAt: pomoRunning ? pomoEndsAt : 0 }));
  } catch {}
}

function pomoStop() {
  clearInterval(pomoInterval);
  pomoRunning = false;
  document.getElementById('pomo-toggle').textContent = '▶';
}

// ── PLAN DE POMODOROS ──────────────────────────────────
// Al elegir el tiempo se guarda un plan { total, done, at }. Mientras queden pomodoros por hacer
// (y no hayan pasado 4 h desde el último movimiento) no se vuelve a preguntar el tiempo.
const PLAN_KEY = 'pomo-plan';
const PLAN_TTL = 4 * 60 * 60 * 1000;

function planGet() {
  try { return JSON.parse(localStorage.getItem(PLAN_KEY) || 'null'); } catch { return null; }
}
function planSet(plan) {
  try { localStorage.setItem(PLAN_KEY, JSON.stringify(plan)); } catch {}
}
function planActive() {
  const p = planGet();
  return !!p && p.done < p.total && Date.now() - p.at < PLAN_TTL;
}
// Un pomodoro de trabajo completo suma uno al plan (el descanso no cuenta).
function planPomoDone() {
  const p = planGet();
  if (p && p.done < p.total) planSet({ ...p, done: p.done + 1, at: Date.now() });
}

function pomoLeft() { return Math.max(0, Math.ceil((pomoEndsAt - Date.now()) / 1000)); }

function pomoTick() {
  pomoRemaining = pomoLeft();
  if (pomoRemaining === 0) { pomoStop(); pomoBeep(); if (pomoMode === 'work') planPomoDone(); }
  pomoRender();
  pomoSave();
}

function pomoStart() {
  pomoRunning = true;
  document.getElementById('pomo-toggle').textContent = '⏸';
  pomoInterval = setInterval(pomoTick, 1000);
}

document.getElementById('pomo-toggle').addEventListener('click', () => {
  if (pomoRunning) {
    pomoRemaining = pomoLeft();
    pomoStop();
  } else {
    if (pomoRemaining === 0) {
      pomoMode = pomoMode === 'work' ? 'break' : 'work';
      pomoRemaining = pomoMode === 'work' ? POMO_WORK : POMO_BREAK;
    }
    pomoEndsAt = Date.now() + pomoRemaining * 1000;
    pomoStart();
  }
  pomoRender();
  pomoSave();
});

document.getElementById('pomo-reset').addEventListener('click', () => {
  pomoStop();
  pomoMode      = 'work';
  pomoRemaining = POMO_WORK;
  pomoRender();
  pomoSave();
});

// Al volver a la pestaña el navegador pudo haber frenado el reloj: se recalcula al momento.
document.addEventListener('visibilitychange', () => { if (pomoRunning && !document.hidden) pomoTick(); });

// Recuperar el estado guardado (si el bloque acabó mientras no estabas, aparece en 00:00 y sin pitido).
try {
  const saved = JSON.parse(localStorage.getItem(POMO_KEY) || 'null');
  if (saved && (saved.mode === 'work' || saved.mode === 'break') && Number.isFinite(saved.remaining)) {
    pomoMode = saved.mode;
    pomoRemaining = saved.remaining;
    if (saved.endsAt) {
      pomoEndsAt = saved.endsAt;
      pomoRemaining = pomoLeft();
      if (pomoRemaining > 0) pomoStart();
      else {
        if (pomoMode === 'work') planPomoDone();   // acabó mientras no estabas
        pomoSave();                                // y se guarda ya parado, para no contarlo dos veces
      }
    }
  }
} catch {}
pomoRender();

// ── LOGIN ─────────────────────────────────────────────
async function startApp() {
  document.getElementById('login-overlay').classList.add('hidden');
  if (isAdmin) {
    document.getElementById('model-row').style.display = 'flex';
  }
  await loadProfile();
  greet();
}

function showStep2() {
  const name = document.getElementById('login-name').value.trim() || 'aprendiz';
  document.getElementById('step-name').style.display = 'none';
  const step2 = document.getElementById('step-password');
  step2.style.display = 'flex';
  document.getElementById('welcome-msg').textContent = `¡Hola, ${name}! ¿Tienes cuenta?`;
  document.getElementById('login-password').focus();
}

document.getElementById('next-btn').addEventListener('click', showStep2);
document.getElementById('login-name').addEventListener('keydown', e => {
  if (e.key === 'Enter') showStep2();
});

document.getElementById('choice-pw-btn').addEventListener('click', () => {
  document.getElementById('step-choice').style.display = 'none';
  const pwInput = document.getElementById('step-pw-input');
  pwInput.style.display = 'flex';
  document.getElementById('login-password').focus();
});

// Si ya entraste antes con contraseña, se recuerda tu nombre y solo pide la contraseña.
try {
  const saved = localStorage.getItem('mm-name');
  if (saved) {
    document.getElementById('login-name').value = saved;
    showStep2();
    document.getElementById('choice-pw-btn').click();   // directo a la contraseña (sin "¿Tienes cuenta?")
    document.getElementById('welcome-msg').textContent = `¡Hola, ${saved}!`;
  }
} catch {}

document.getElementById('login-btn').addEventListener('click', async () => {
  const name = document.getElementById('login-name').value.trim();
  const pw = document.getElementById('login-password').value;
  const err = document.getElementById('login-error');
  err.style.display = 'none';
  const r = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: pw, name })
  });
  if (r.ok) {
    isAdmin = true;
    try { if (name) localStorage.setItem('mm-name', name); } catch {}   // solo se recuerda al entrar con contraseña
    showCourseStep();
  }
  else { err.style.display = 'block'; }
});

// Nombre bonito de cada curso; uno que no esté aquí se enseña tal cual (nombre del archivo en agent/).
const COURSE_LABELS = { cs50: 'CS50', mouredev: 'MoureDev', '42malaga': '42 Málaga' };

const COURSE_GREETINGS = [
  '¿A qué le atacamos hoy?',
  '¿Qué te apetece aprender hoy?',
  '¿Con qué entrenamos hoy?',
  '¿Por dónde tiramos hoy?',
];

async function showCourseStep() {
  document.getElementById('step-password').style.display = 'none';
  const step = document.getElementById('step-course');
  step.style.display = 'flex';
  const name = document.getElementById('login-name').value.trim();
  const greeting = COURSE_GREETINGS[Math.floor(Math.random() * COURSE_GREETINGS.length)];
  document.getElementById('course-greeting').textContent = name ? `¡Hola, ${name}! ${greeting}` : greeting;
  const r = await fetch('/courses');
  const { courses } = await r.json();
  const p = await (await fetch('/profile')).json();
  // Una tarjeta por curso, con su color (styles.css); el último que usaste lleva el chip "último"
  // (como hacía el select preseleccionando p.course).
  document.getElementById('course-cards').innerHTML = courses.map(c =>
    `<button class="course-card" data-course="${c}">${COURSE_LABELS[c] || c}${c === p.course ? ' <span class="course-chip">último</span>' : ''}</button>`
  ).join('');
}

document.getElementById('course-cards').addEventListener('click', async e => {
  const card = e.target.closest('button[data-course]');
  if (!card) return;
  await fetch('/update-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ course: card.dataset.course })
  });
  startApp();
});

document.getElementById('login-password').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('login-btn').click();
});

document.getElementById('guest-btn').addEventListener('click', async () => {
  await fetch('/logout', { method: 'POST' });
  const name = document.getElementById('login-name').value.trim();
  if (name) {
    await fetch('/guest-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
  }
  startApp();
});

const settingsBtn = document.getElementById('settings-btn');
const settingsDropdown = document.getElementById('settings-dropdown');
settingsBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  settingsDropdown.classList.toggle('open');
});
document.addEventListener('click', () => settingsDropdown.classList.remove('open'));
settingsDropdown.addEventListener('click', (e) => e.stopPropagation());

function showToast(msg, isError = false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.background = isError ? '#c0392b' : 'var(--text)';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}

document.getElementById('save-session-btn').addEventListener('click', async () => {
  settingsDropdown.classList.remove('open');
  if (!isAdmin) return;
  if (messages.length === 0) { showToast('No hay conversación que guardar.', true); return; }
  const sessionText = messages.map(m => `**${m.role === 'user' ? 'Estudiante' : 'Trainer'}:** ${m.content}`).join('\n\n');
  const btn = document.getElementById('save-session-btn');
  const btnOriginal = btn.innerHTML;
  btn.textContent = 'Guardando...';
  btn.disabled = true;
  try {
    const r = await fetch('/save-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: sessionText })
    });
    const data = await r.json();
    if (data.ok) {
      showToast('✓ Sesión guardada correctamente');
    } else {
      showToast('✗ No se pudo guardar. Inténtalo de nuevo.', true);
    }
  } catch (e) {
    showToast('✗ No se pudo guardar. Inténtalo de nuevo.', true);
  }
  btn.innerHTML = btnOriginal;
  btn.disabled = false;
});

document.getElementById('logout-btn').addEventListener('click', async () => {
  await fetch('/logout', { method: 'POST' });
  location.reload();
});

// No auto-start — wait for login choice

// PWA: registra el service worker (permite instalar MasterMind como app)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(reg => reg.update())   // mira si hay versión nueva cada vez que se abre, también en la app instalada
    .catch(e => console.warn('[PWA] No se pudo registrar el service worker:', e));
  // Versión nueva desplegada: se recarga sola, salvo en mitad de una conversación (se perdería el chat, que vive en
  // memoria); en ese caso la versión nueva sale la próxima vez que se abra.
  navigator.serviceWorker.addEventListener('message', e => {
    if (e.data?.type !== 'SW_UPDATED') return;
    if (messages.length === 0) window.location.reload();
    else console.info('[PWA] Hay una versión nueva: se cargará la próxima vez que abras MasterMind');
  });
}

// Editor de código — la lógica real está en code-editor.js (módulo ES)
// Este archivo expone openCodeEditor() y closeCodeEditor() como globales
document.getElementById('code-mode-btn').addEventListener('click', () => {
  if (typeof window.toggleCodeEditor === 'function') window.toggleCodeEditor();
});

document.getElementById('code-cancel').addEventListener('click', () => {
  document.getElementById('code-panel').style.display = 'none';
  document.querySelector('footer').style.display = 'flex';
  document.getElementById('input').focus();
});

document.getElementById('code-send').addEventListener('click', () => {
  if (!window.cmEditor) return;
  const code = window.cmEditor.getValue().trim();
  if (!code) return;
  const lang = document.getElementById('code-lang').value === 'text' ? '' : document.getElementById('code-lang').value;
  document.getElementById('input').value = '```' + lang + '\n' + code + '\n```';
  document.getElementById('code-panel').style.display = 'none';
  document.querySelector('footer').style.display = 'flex';
  window.cmEditor.setValue('');
  send();
});
