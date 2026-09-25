const messages = [];

async function loadProfile() {
  try {
    const r = await fetch('/profile');
    const p = await r.json();
    document.getElementById('nav-brand').textContent = p.course ? `MasterMind · ${p.course}` : 'MasterMind';
    document.getElementById('b-week').textContent = `Week ${p.current_week}`;
    document.getElementById('b-topic').textContent = p.current_topic;
    document.getElementById('b-mode').textContent = p.mode;
    if (isAdmin) {
      document.getElementById('profile-topic').value = p.current_topic || '';
      document.getElementById('profile-week').value = p.current_week || 1;
    }
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
            bubble.innerHTML = renderMarkdown(fullText);
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

async function send() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('send').disabled = true;
  messages.push({ role: 'user', content: text });
  addMessage('user', text);
  showTyping();
  try {
    const reply = await streamChat(messages);
    if (reply) {
      messages.push({ role: 'assistant', content: reply });
    }
  } catch (e) { removeTyping(); addMessage('error', `Error de conexión: ${e.message}`); }
  document.getElementById('send').disabled = false;
  input.focus();
}

async function greet() {
  showTyping();
  try {
    const reply = await streamChat([{ role: 'user', content: '__greet__' }]);
    if (reply) {
      messages.push({ role: 'assistant', content: reply });
      const qr = document.getElementById('quick-replies');
      qr.style.display = 'flex';
      pomoReposition();
    }
  } catch {}
}

document.querySelectorAll('.qr-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('quick-replies').style.display = 'none';
    pomoReposition();
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
themeSelect.addEventListener('change', () => {
  document.documentElement.setAttribute('data-theme', themeSelect.value);
  localStorage.setItem('trainer-theme', themeSelect.value);
  pomoSetEmoji();
});
makeCustomSelect(themeSelect);
makeCustomSelect(document.getElementById('model'));
makeCustomSelect(document.getElementById('profile-week'));

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
const CIRC = 213.6;
let pomoMode      = 'work';
let pomoRemaining = POMO_WORK;
let pomoRunning   = false;
let pomoInterval  = null;

function pomoRender() {
  pomoSetEmoji();
  const total = pomoMode === 'work' ? POMO_WORK : POMO_BREAK;
  const mins  = String(Math.floor(pomoRemaining / 60)).padStart(2, '0');
  const secs  = String(pomoRemaining % 60).padStart(2, '0');
  document.getElementById('pomo-time').textContent = `${mins}:${secs}`;
  document.getElementById('pomo-arc').style.strokeDashoffset = CIRC * (1 - pomoRemaining / total);
  const w = document.getElementById('pomodoro');
  w.classList.toggle('pomo-break', pomoMode === 'break');
  w.classList.toggle('pomo-done',  pomoRemaining === 0);
}

document.getElementById('pomo-toggle').addEventListener('click', () => {
  if (pomoRunning) {
    clearInterval(pomoInterval);
    pomoRunning = false;
    document.getElementById('pomo-toggle').textContent = '▶';
  } else {
    if (pomoRemaining === 0) {
      pomoMode = pomoMode === 'work' ? 'break' : 'work';
      pomoRemaining = pomoMode === 'work' ? POMO_WORK : POMO_BREAK;
    }
    pomoRunning = true;
    document.getElementById('pomo-toggle').textContent = '⏸';
    pomoInterval = setInterval(() => {
      pomoRemaining--;
      pomoRender();
      if (pomoRemaining === 0) {
        clearInterval(pomoInterval);
        pomoRunning = false;
        document.getElementById('pomo-toggle').textContent = '▶';
        pomoBeep();
        pomoRender();
      }
    }, 1000);
  }
});

document.getElementById('pomo-reset').addEventListener('click', () => {
  clearInterval(pomoInterval);
  pomoRunning   = false;
  pomoMode      = 'work';
  pomoRemaining = POMO_WORK;
  document.getElementById('pomo-toggle').textContent = '▶';
  pomoRender();
});

pomoRender();

function pomoReposition() {
  const fh = document.querySelector('footer').offsetHeight +
             document.querySelector('.site-footer').offsetHeight;
  document.getElementById('pomodoro').style.bottom = (fh + 12) + 'px';
}
window.addEventListener('resize', pomoReposition);
document.getElementById('input').addEventListener('input', pomoReposition);
pomoReposition();

// ── LOGIN ─────────────────────────────────────────────
async function startApp() {
  document.getElementById('login-overlay').classList.add('hidden');
  if (isAdmin) {
    document.getElementById('model-row').style.display = 'flex';
    document.getElementById('progress-row').style.display = 'flex';
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
  if (r.ok) { isAdmin = true; showCourseStep(); }
  else { err.style.display = 'block'; }
});

async function showCourseStep() {
  document.getElementById('step-password').style.display = 'none';
  const step = document.getElementById('step-course');
  step.style.display = 'flex';
  const r = await fetch('/courses');
  const { courses } = await r.json();
  const select = document.getElementById('course-select');
  select.innerHTML = courses.map(c => `<option value="${c}">${c}</option>`).join('');
  const p = await (await fetch('/profile')).json();
  if (p.course && courses.includes(p.course)) select.value = p.course;
  makeCustomSelect(select);
}

document.getElementById('course-btn').addEventListener('click', async () => {
  const course = document.getElementById('course-select').value;
  await fetch('/update-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ course })
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

document.getElementById('save-profile-btn').addEventListener('click', async () => {
  settingsDropdown.classList.remove('open');
  const topic = document.getElementById('profile-topic').value.trim();
  const week = parseInt(document.getElementById('profile-week').value);
  const btn = document.getElementById('save-profile-btn');
  const btnOriginal = btn.innerHTML;
  btn.textContent = 'Guardando...';
  btn.disabled = true;
  try {
    const r = await fetch('/update-profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_topic: topic, current_week: week })
    });
    const data = await r.json();
    if (data.ok) {
      showToast('✓ Progreso actualizado');
      document.getElementById('b-topic').textContent = topic;
      document.getElementById('b-week').textContent = `Week ${week}`;
    } else {
      showToast('✗ No se pudo actualizar. Inténtalo de nuevo.', true);
    }
  } catch {
    showToast('✗ No se pudo actualizar. Inténtalo de nuevo.', true);
  }
  btn.innerHTML = btnOriginal;
  btn.disabled = false;
});

document.getElementById('logout-btn').addEventListener('click', async () => {
  await fetch('/logout', { method: 'POST' });
  location.reload();
});

// No auto-start — wait for login choice
