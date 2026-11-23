const messages = [];
let cursoActivo = null;   // id del curso con la sesión abierta ahora mismo; lo fija loadProfile()

// El perfil local con la forma que espera la barra de arriba (la misma que devuelve /profile).
function perfilDesdeLocal(local) {
  const n = (local.current || '').match(/(?:ex|week)(\d+)/);
  const temas = (typeof temasPorCurso !== 'undefined' && temasPorCurso[local.course]) || [];
  const tema = temas.find(t => t.folder === local.current);
  return {
    student: local.student, course: local.course, mode: 'explain',
    progress: { course: local.course, current: local.current, mastered: local.mastered || [],
                n: n ? Number(n[1]) : null, topic: tema ? tema.topic : '' }
  };
}

async function loadProfile() {
  try {
    // El perfil local no está en el servidor: la barra se pinta con lo que hay en este navegador.
    const local = typeof perfilLocal === 'function' ? perfilLocal() : null;
    if (local && local.course) await asegurarTemas(local.course);   // para poner nombre a la lección tras recargar
    const p = (local && local.course) ? perfilDesdeLocal(local) : await (await fetch('/profile')).json();
    cursoActivo = p.course || null;
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

// Color de la etiqueta de cada modelo (css: .modelo.m-*). Un modelo que no está aquí sale sin color propio.
const COLOR_MODELO = {
  'qwen/qwen3.8-27b': 'azul',
  'openai/gpt-oss-120b': 'amarillo',
  'openai/gpt-oss-20b': 'verde',
};

function crearEtiquetaModelo(info) {
  const el = document.createElement('small');
  let color = COLOR_MODELO[info.model];
  if (!color && info.provider === 'gemini') color = 'turquesa';
  el.className = 'modelo' + (color ? ' m-' + color : '') + (info.fallback ? ' respaldo' : '');
  // textContent, no innerHTML: el nombre viene del servidor.
  el.textContent = `${info.provider} · ${info.model}` + (info.fallback ? ' (respaldo)' : '');
  return el;
}

// La clave de Groq del usuario, si la ha puesto en ⚙. Vacía = se usa la del servidor.
function claveGroq() {
  try { return (localStorage.getItem('mm-groq-key') || '').trim(); } catch { return ''; }
}

// ── PERFIL LOCAL ────────────────────────────────────────
// Quien no es Nando lleva su cuenta en SU navegador: el servidor no guarda nada suyo. El perfil viaja
// en cada mensaje del chat y el servidor lo valida (ver `perfil_local` en app.py).
// Si borra los datos del navegador sin exportar, se pierde: por eso ⚙ tiene exportar/importar.
function perfilLocal() {
  try { return JSON.parse(localStorage.getItem('mm-perfil') || 'null'); } catch { return null; }
}

function guardarPerfilLocal(perfil) {
  try { localStorage.setItem('mm-perfil', JSON.stringify(perfil)); } catch {}
}

async function streamChat(msgList) {
  const r = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: msgList,
      model: document.getElementById('model').value,
      ia_key: claveGroq(),
      perfil: perfilLocal(),
      ...(cursoActivo && CURSOS_CUADERNO.includes(cursoActivo) ? { cuaderno: leerCuaderno(cursoActivo) } : {})
    })
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
  let etiqueta = null;   // el modelo que responde (lo manda el servidor justo antes del primer texto)

  // Pinta el texto y, debajo, la etiqueta del modelo con su color. Se repinta entera en cada trozo porque
  // bubble.innerHTML se reemplaza al llegar texto nuevo.
  const pintar = () => {
    bubble.innerHTML = renderMarkdown(hideMark(fullText));
    if (etiqueta) bubble.appendChild(etiqueta);
  };

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
            pintar();
            row.scrollIntoView({ behavior: 'smooth' });
          } else if (parsed && parsed.model) {
            etiqueta = crearEtiquetaModelo(parsed);
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
// Dónde va dentro de la sección: el tutor pone [[PUNTO 1.5]] al terminar un subpunto ('1.ejercicios', '1.examen',
// '2.0' al aprobar un punto). La app la oculta y la guarda en el progreso del servidor: al volver, sigue por ahí.
const POINT_MARK = /\[\[PUNTO (\d+\.(?:\d+|ejercicios|examen))\]\]/g;
async function savePoint(reply) {
  const marcas = [...reply.matchAll(POINT_MARK)];
  if (roomActive || !marcas.length) return;
  const punto = marcas[marcas.length - 1][1];
  const local = perfilLocal();
  if (local && !isAdmin) return guardarPerfilLocal({ ...local, point: punto });   // su partida vive en su navegador
  if (!isAdmin) return;
  try {
    await fetch('/progress/point', { method: 'POST', headers: { 'Content-Type': 'application/json' },
                                     body: JSON.stringify({ point: punto }) });
  } catch {}
}
const hideMark = t => {
  t = t.replace(MASTERED_MARK, '').replace(EXAM_MARK, '').replace(POINT_MARK, '')
       .replace(/\[\[[A-Z]*( [\w.]*)?\]?$/, '');
  // El cuaderno (ver CUADERNO_MARK) puede llegar en varios trozos de texto: mientras no se cierre, no se
  // enseña nada de él (sería un tablón entero parpadeando mientras se escribe).
  const abierto = t.indexOf('[[CUADERNO]]');
  if (abierto !== -1) {
    const cerrado = t.indexOf('[[/CUADERNO]]', abierto);
    t = cerrado !== -1 ? t.slice(0, abierto) + t.slice(cerrado + '[[/CUADERNO]]'.length) : t.slice(0, abierto);
  }
  return t.trimEnd();
};

// Cursos cuyo tutor construye un documento que crece con el alumno (ver agent/Japones.md): el cuaderno
// vive en SU navegador (nunca en el servidor), viaja en cada mensaje y el tutor lo devuelve entero entre
// [[CUADERNO]]...[[/CUADERNO]] cuando cambia. Un curso nuevo con el mismo método solo añade su id aquí.
const CURSOS_CUADERNO = ['japones'];
const CUADERNO_MARK = /\[\[CUADERNO\]\]([\s\S]*?)\[\[\/CUADERNO\]\]/;
const leerCuaderno = curso => { try { return localStorage.getItem(`mm-cuaderno-${curso}`) || ''; } catch { return ''; } };
const guardarCuaderno = (curso, texto) => { try { localStorage.setItem(`mm-cuaderno-${curso}`, texto); } catch {} };
async function saveCuaderno(reply) {
  if (!cursoActivo || !CURSOS_CUADERNO.includes(cursoActivo)) return;
  const m = reply.match(CUADERNO_MARK);
  if (m) guardarCuaderno(cursoActivo, m[1].trim());
}

// Los temas del curso (para avanzar y para poner nombre a la lección). Se piden una vez por sesión.
let temasPorCurso = {};
async function asegurarTemas(curso) {
  if (temasPorCurso[curso]) return temasPorCurso[curso];
  try {
    const cursos = (await (await fetch('/courses?temas=1')).json()).courses;
    temasPorCurso = Object.fromEntries(cursos.map(c => [c.course, c.topics]));
  } catch {}
  return temasPorCurso[curso] || [];
}

// Igual que saveProgress, pero sin servidor: la partida del usuario local vive en SU navegador.
async function avanzarTemaLocal(local) {
  const temas = await asegurarTemas(local.course);
  const i = temas.findIndex(t => t.folder === local.current);
  const siguiente = i >= 0 ? temas[i + 1] : temas[0];
  if (!siguiente) {
    return addMessage('bot', '🎉 ¡Has terminado todos los temas de este curso! No hay siguiente lección.');
  }
  guardarPerfilLocal({ ...local, current: siguiente.folder, point: null,
                       mastered: [...(local.mastered || []), local.current].filter(Boolean) });
  addMessage('bot', `💾 Partida guardada: ahora estás en ${local.course === 'cs50' ? 'Week' : 'Ej.'} ${siguiente.n} · ${siguiente.topic}.`);
  loadProfile();
  messages.length = 0;
  examActive = false;
  greet(true);
}

// Aprobado el examen, la partida se guarda sola: el tema actual pasa a dominado y el siguiente a actual.
async function saveProgress() {
  const local = perfilLocal();
  if (local && !isAdmin) return avanzarTemaLocal(local);
  const r = await fetch('/progress/next', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  const res = await r.json();
  if (!r.ok) return addMessage('bot', `No se pudo guardar: ${res.error}`);   // p. ej. ya estás en el último tema
  const p = res.progress;
  addMessage('bot', `💾 Partida guardada: ahora estás en ${p.course === 'cs50' ? 'Week' : 'Ej.'} ${p.n} · ${p.topic}.`);
  loadProfile();                                      // la barra de arriba pasa al tema nuevo
  messages.length = 0;                                // la IA arranca el tema nuevo sin el historial del anterior
  examActive = false;
  greet(true);                                        // y da el enunciado del tema nuevo (sin volver a preguntar el tiempo)
}

// ── COMANDOS DEL CHAT (/ls, /back…) ─────────────────────
// Los atiende la app: NO se envían a la IA ni entran en el historial de la conversación.
const STATUS_ICONS = { mastered: '✅', current: '👉', locked: '🔒' };

// La guía de /help sale de aquí: al añadir un comando nuevo, se apunta en esta lista y aparece solo.
const EXAM_BLOCKED = ['/kata', '/read'];   // no valen durante el examen
const KATA_PROMPT = 'El estudiante ha escrito /kata. Propón ahora UNA kata sobre el tema actual: ejercicio pequeño, cerrado y ' +
  'autoverificable, en el nivel más básico, para reforzar lo que acaba de ver. No des la solución: espera su código y corrígelo ' +
  'con tus modos habituales. Una kata no es un examen: no escribas [[DOMINADO]] ni [[EXAM]].';

// /read: la app tira la moneda (el modelo no es fiable "al azar": casi siempre pondría fallo) y se lo dice a la IA.
const READ_PROMPT = fallo => 'El estudiante ha escrito /read. Inventa un fragmento de código corto (10-20 líneas) sobre el tema actual, ' +
  'a su nivel, como si fuera de otro programador. ' +
  (fallo ? 'Esta vez el código tiene UN fallo realista (lógica, caso límite o seguridad). '
         : 'Esta vez el código está BIEN: no escondas ningún fallo. ') +
  'No digas si tiene fallo ni dónde. Pregunta solo: ¿qué hace?, ¿por qué así?, ¿ves algo raro? No des las respuestas: espera las suyas. ' +
  'Si no había fallo y se inventa uno, díselo. Una lectura no es un examen: no escribas [[DOMINADO]] ni [[EXAM]].';

const COMMANDS = {
  '/help': 'Esta ayuda',
  '/ls':   'Tus ejercicios: ✅ dominados · 👉 el actual · 🔒 bloqueados',
  '/back': '/back ex1: vuelve a un ejercicio ya dominado para repasarlo (próximamente)',
  '/kata': 'Un ejercicio corto de calentamiento sobre el tema actual (no disponible en el examen)',
  '/read': 'Leer y comentar código ajeno sobre el tema actual (no disponible en el examen)',
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
  if (cmd === '/read') return askHidden(READ_PROMPT(Math.random() < 0.5));
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
  if (roomActive && ROOM_EXIT.test(text)) { addMessage('user', text); return exitRoom(); }
  if (text.startsWith('/')) return runCommand(text);
  document.getElementById('send').disabled = true;
  // La respuesta al saludo de la app (el tiempo) lleva la marca de arranque: el servidor la cambia por la instrucción
  // de empezar la clase. No se ve en el chat.
  messages.push({ role: 'user', content: awaitingTime ? `${text} __start__` : text });
  awaitingTime = false;
  addMessage('user', text);
  showTyping();
  try {
    const reply = await streamChat(messages);
    if (reply) {
      messages.push({ role: 'assistant', content: reply });
      examActive = reply.includes(EXAM_MARK);
      await savePoint(reply);
      await saveCuaderno(reply);
      if ((isAdmin || perfilLocal()) && !roomActive && reply.includes(MASTERED_MARK)) await saveProgress();   // en la sala de repaso nunca se avanza
    }
  } catch (e) { removeTyping(); addMessage('error', `Error de conexión: ${e.message}`); }
  document.getElementById('send').disabled = false;
  input.focus();
}

// Saludo sin plan de pomodoros: lo escribe la APP, no la IA. Solo saluda y pregunta el tiempo; la IA no recibe nada
// hasta que el estudiante responde (con el modelo de turno, la IA a veces se adelantaba y empezaba la clase).
// No entra en el historial: el primer mensaje que ve la IA es la respuesta con el tiempo (con la marca de arranque),
// y es la IA la que entonces presenta el tema, con su toque al azar, y empieza la clase.
const GREET_OPENINGS = ['¡Hola, {n}!', '¡Buenas, {n}!', '¡Qué bien verte, {n}!', '¡Vamos allá, {n}!'];
const TIME_QUESTION = '¿Cuánto tiempo tienes para estudiar hoy? 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros).';
let awaitingTime = false;
// Plan de pomodoros a medias (de esta misma tarde, ver PLAN_TTL): se ofrece seguir con él en vez de preguntar.
function planPendiente() {
  const p = isAdmin && planActive() ? planGet() : null;
  return p ? `Tienes un plan de ${p.total} pomodoros a medias (llevas ${p.done}). ¿Seguimos con él o eliges otro tiempo?` : '';
}
// Solo hola + tiempo. Dónde te quedaste lo dice el tutor al arrancar (lo sabe por la marca guardada).
function localGreeting(sinHola) {
  const pregunta = planPendiente() || TIME_QUESTION;
  if (sinHola) return pregunta;                     // ya saludó la sala: no se repite el hola
  const name = isAdmin ? (document.getElementById('login-name').value.trim() || 'Nando') : 'aprendiz';
  const opening = GREET_OPENINGS[Math.floor(Math.random() * GREET_OPENINGS.length)].replace('{n}', name);
  return `${opening} ${pregunta}`;
}
// Botón "Seguir con el plan" (solo con un plan a medias): responde al saludo sin cambiar el plan guardado.
function botonSeguirPlan() {
  let b = document.getElementById('qr-seguir');
  if (!b) {
    b = document.createElement('button');
    b.id = 'qr-seguir';
    b.className = 'qr-btn';
    b.addEventListener('click', () => {
      const p = planGet();
      document.getElementById('quick-replies').style.display = 'none';
      document.getElementById('input').value = `Seguimos con el plan: me quedan ${p.total - p.done} pomodoros`;
      send();
    });
    document.getElementById('quick-replies').prepend(b);
  }
  b.textContent = '▶ Seguir con el plan';
  b.style.display = planPendiente() ? '' : 'none';
}

// sigueSesion = true solo al pasar de tema tras aprobar (saveProgress). Al ENTRAR en la app siempre se pregunta el
// tiempo, aunque quede un plan guardado de antes (duraba 4 h y hacía que la IA empezara la clase sin preguntar).
// sinHola = true cuando se viene de la sala (que ya saludó).
async function greet(sigueSesion = false, sinHola = false) {
  const hasPlan = sigueSesion && isAdmin && planActive();   // con plan en marcha no se vuelve a preguntar el tiempo
  if (!hasPlan) {
    addMessage('bot', localGreeting(sinHola));
    botonSeguirPlan();
    awaitingTime = true;
    document.getElementById('quick-replies').style.display = 'flex';
    return;
  }
  showTyping();
  try {
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
// La interfaz del chat son estas 6 piezas (cada una con su display de siempre). Antes, esta lista estaba copiada en
// cuatro funciones; ahora hay un solo sitio.
const CHAT_UI = [['nav', 'flex'], ['#messages', 'flex'], ['#quick-replies', 'flex'],
                 ['#cmd-hint', 'block'], ['#input-bar', 'flex'], ['#pomo-progress', 'block']];
function mostrarChatUI(visible) {
  CHAT_UI.forEach(([sel, display]) => { document.querySelector(sel).style.display = visible ? display : 'none'; });
}

async function startApp(room = false, sinHola = false) {
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('dashboard').style.display = 'none';
  mostrarChatUI(true);
  if (isAdmin) {
    document.getElementById('model-row').style.display = 'flex';
  }
  await loadProfile();
  if (room) return startRoom();
  greet(false, sinHola);
}

// ── SALA DE REPASO (antes del curso) ────────────────────
// Charla libre sobre lo ya aprendido: sin examen, sin marcas y sin guardar progreso. Se sale con el botón
// "Ir al curso" o escribiendo una frase como "vamos con el curso"; entonces arranca el saludo de siempre.
let roomActive = false;
const ROOM_EXIT = /\b(vamos|volvamos|sigamos|seguimos)\b.*\bcurso\b/i;
const ROOM_PROMPT = hechos => 'El estudiante entra en la SALA DE REPASO, antes del curso. Es charla libre, como un chat normal: ' +
  'sin examen y sin guardar progreso; no escribas [[DOMINADO]] ni [[EXAM]]. Salúdale en una frase y pregúntale qué quiere repasar. ' +
  `Lo que ha dominado hasta ahora: ${hechos.length ? hechos.join(', ') : 'nada todavía'}. Puede elegir uno de esos temas u otro. ` +
  'Cuando elija, pregúntale, proponle ejercicios, katas y lecturas de código de ese tema, con tus modos habituales pero sin ' +
  'examinarle. No des la solución antes de su intento.';

// `listo` = lo que hay que esperar antes de saludar (guardar el curso elegido). La sala se ve YA y sus botones esperan:
// guardar el curso son varias llamadas a GitHub y, mientras tanto, antes la pantalla quedaba en blanco.
async function showRoomStep(listo = Promise.resolve()) {
  // Sala: overlay visible con step-room, dashboard oculto, chat UI oculta
  document.getElementById('dashboard').style.display = 'none';
  mostrarChatUI(false);
  document.getElementById('login-overlay').classList.remove('hidden');
  document.getElementById('step-course').style.display = 'none';
  document.getElementById('step-room').style.display = 'flex';
  const name = document.getElementById('login-name').value.trim();
  const botones = ['room-review-btn', 'room-continue-btn'].map(id => document.getElementById(id));
  botones.forEach(b => { b.disabled = true; });
  document.getElementById('room-greeting').textContent = 'Preparando tu sala…';
  try {
    await listo;
    const pr = (await (await fetch('/profile')).json()).progress || {};
    // Sin nada dominado no hay nada que repasar: la sala sobra y se entra directo al curso (el saludo lo da el chat).
    if (!(pr.mastered || []).length) return startApp();
    const donde = pr.n ? ` Vas por ${pr.course === 'cs50' ? 'Week' : 'Ej.'} ${pr.n} · ${pr.topic}.` : '';
    document.getElementById('room-greeting').textContent = `¡Hola${name ? ', ' + name : ''}!${donde} ¿Repasamos lo aprendido o seguimos con el curso?`;
  } catch {
    document.getElementById('room-greeting').textContent = `¡Hola${name ? ', ' + name : ''}! ¿Repasamos lo aprendido o seguimos con el curso?`;
  }
  botones.forEach(b => { b.disabled = false; });
}

// En la sala la barra dice "Entrenamiento" en vez de la lección del curso (que aquí no se está haciendo).
function roomBadges(on) {
  document.getElementById('b-week').textContent = on ? 'Entrenamiento' : '';
  ['b-topic', 'b-mode'].forEach(id => document.getElementById(id).style.display = on ? 'none' : '');
  if (!on) loadProfile();                             // devuelve la lección real
}

async function startRoom() {
  roomActive = true;
  roomBadges(true);
  document.getElementById('room-exit').style.display = '';
  const d = await (await fetch('/progress')).json();
  askHidden(ROOM_PROMPT((d.topics || []).filter(t => t.status === 'mastered').map(t => t.topic)));
}

function exitRoom() {
  roomActive = false;
  examActive = false;
  roomBadges(false);
  document.getElementById('room-exit').style.display = 'none';
  // Ocultar overlay y dashboard, mostrar chat UI
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('dashboard').style.display = 'none';
  mostrarChatUI(true);
  messages.length = 0;
  addMessage('bot', '📚 Terminamos el repaso. Vamos con el curso.');
  greet(false, true);
}

document.getElementById('room-review-btn').addEventListener('click', () => startApp(true));
document.getElementById('room-continue-btn').addEventListener('click', () => startApp(false, true));   // la sala ya saludó
document.getElementById('room-exit').addEventListener('click', exitRoom);

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

// Quien tiene su partida en este navegador vuelve directo a su curso: si no, al recargar acabaría
// creando la cuenta otra vez y se pisaría su propio progreso.
const perfilGuardado = perfilLocal();
if (perfilGuardado && perfilGuardado.course) {
  document.getElementById('login-name').value = perfilGuardado.student || '';
  startApp();
}

// Si ya entraste antes con contraseña, se recuerda tu nombre y solo pide la contraseña.
try {
  const saved = localStorage.getItem('mm-name');
  if (saved && !(perfilGuardado && perfilGuardado.course)) {
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

// Nombre bonito de cada curso, de la tabla única window.CURSOS (dashboard.js); uno que no esté se enseña tal cual
// (nombre del archivo en agent/).
const COURSE_LABELS = Object.fromEntries(Object.entries(window.CURSOS || {}).map(([id, c]) => [id, c.nombre]));

const COURSE_GREETINGS = [
  '¿A qué le atacamos hoy?',
  '¿Qué te apetece aprender hoy?',
  '¿Con qué entrenamos hoy?',
  '¿Por dónde tiramos hoy?',
];

async function showCourseStep() {
  document.getElementById('step-password').style.display = 'none';
  const step = document.getElementById('step-course');
  const caja = document.querySelector('.login-box');
  const name = document.getElementById('login-name').value.trim();
  const greeting = COURSE_GREETINGS[Math.floor(Math.random() * COURSE_GREETINGS.length)];
  document.getElementById('course-greeting').textContent = name ? `¡Hola, ${name}! ${greeting}` : greeting;
  // Ocultar overlay de login y mostrar dashboard en body
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('dashboard').style.display = 'flex';
  mostrarChatUI(false);
  // Un marco vacío AL INSTANTE (dashboard.js)
  try { window.esqueletoDashboard(); } catch {}
  try {
    const rd = await fetch('/dashboard');
    if (!rd.ok) throw new Error('dashboard ' + rd.status);
    const datos = await rd.json();
    await window.mostrarDashboard({ etiquetas: COURSE_LABELS, ultimo: datos.last_course, alElegir: elegirCurso, datos,
                                    saludo: document.getElementById('course-greeting').textContent });
    step.style.display = 'none';
  } catch {
    const panel = document.getElementById('dashboard');
    if (panel && panel.dataset.esqueleto === '1') { panel.style.display = 'none'; delete panel.dataset.esqueleto; }
    const sigueElPanel = panel && panel.style.display !== 'none' && panel.innerHTML;
    if (!sigueElPanel) {
      // Plan B: el overlay del login se había escondido al empezar; sin volver a mostrarlo la caja salía dentro de
      // algo oculto y la pantalla se quedaba en blanco.
      document.getElementById('login-overlay').classList.remove('hidden');
      caja.style.display = '';
      step.style.display = 'flex';
      try {
        const [courses, p] = await Promise.all([
          fetch('/courses').then(r => r.json()).then(j => j.courses), fetch('/profile').then(r => r.json())]);
        document.getElementById('course-cards').innerHTML = courses.map(c =>
          `<button class="course-card" data-course="${c}"${(window.CURSOS || {})[c] ? ` style="--course-color:${window.CURSOS[c].color};--course-text:#fff"` : ''}>${COURSE_LABELS[c] || c}${c === p.course ? ' <span class="course-chip">último</span>' : ''}</button>`
        ).join('');
      } catch {}
    }
  }
}

// Elegir un curso (tarjeta pequeña o panel): guarda el curso en el perfil y abre la sala previa.
async function elegirCurso(course) {
  const perfil = perfilLocal();
  if (perfil && !isAdmin) {
    // Perfil local: empieza por el primer tema del curso y arranca el chat (sin sala: aún no hay nada que repasar).
    const temas = temasPorCurso[course] || [];
    guardarPerfilLocal({ ...perfil, course, current: temas.length ? temas[0].folder : null, mastered: [], point: null });
    return startApp();
  }
  await showRoomStep(fetch('/update-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ course })
  }));
}

document.getElementById('course-cards').addEventListener('click', async e => {
  const card = e.target.closest('button[data-course]');
  if (!card) return;
  await elegirCurso(card.dataset.course);
});

document.getElementById('login-password').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('login-btn').click();
});

// ── TU PARTIDA: copia de seguridad y paso a otro dispositivo ────
// La partida del usuario local vive solo en este navegador: si borra los datos del sitio, se pierde.
// El archivo NO lleva la clave de IA (decisión de Nando): es la credencial de otro servicio y acabaría
// en Drive o WhatsApp. Al importarla en el PC, se vuelve a pegar la clave a mano.
function pintarFilaPartida() {
  const local = perfilLocal();
  const fila = document.getElementById('partida-row');
  if (!local || !local.course) { fila.style.display = 'none'; return; }
  fila.style.display = 'flex';
  const n = (local.mastered || []).length;
  document.getElementById('partida-estado').textContent =
    `${local.student} · ${local.course} · ${n} tema${n === 1 ? '' : 's'} superado${n === 1 ? '' : 's'}. Solo en este navegador.`;
}

document.getElementById('exportar-btn').addEventListener('click', () => {
  const local = perfilLocal();
  if (!local) return;
  const datos = { app: 'mastermind', version: 1, exportado: new Date().toISOString(),
                  student: local.student, course: local.course, current: local.current,
                  mastered: local.mastered || [], point: local.point || null,
                  cuaderno: CURSOS_CUADERNO.includes(local.course) ? leerCuaderno(local.course) : undefined };
  const url = URL.createObjectURL(new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `mastermind-${(local.student || 'partida').toLowerCase().replace(/[^a-z0-9]+/g, '-')}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('✓ Datos descargados. Guárdalos donde no los pierdas.');
});

document.getElementById('importar-btn').addEventListener('click', () => document.getElementById('importar-file').click());

document.getElementById('importar-file').addEventListener('change', async e => {
  const archivo = e.target.files[0];
  if (!archivo) return;
  e.target.value = '';                                   // así re-importar el mismo archivo vuelve a disparar 'change'
  try {
    const d = JSON.parse(await archivo.text());
    if (d.app !== 'mastermind' || !d.course) throw new Error('el archivo no es de MasterMind');
    guardarPerfilLocal({ student: d.student || 'aprendiz', course: d.course, current: d.current || null,
                         mastered: Array.isArray(d.mastered) ? d.mastered : [], point: d.point || null });
    if (typeof d.cuaderno === 'string') guardarCuaderno(d.course, d.cuaderno);
    showToast('✓ Datos cargados. Entrando…');
    setTimeout(() => location.reload(), 900);
  } catch (err) {
    showToast(`No se pudo cargar: ${err.message}`, true);
  }
});

// ── 🔑 GUÍA "¿CÓMO CONSIGO UNA CLAVE?" ──────────────────
const guiaPanel = document.getElementById('guia-panel');
document.getElementById('register-help').addEventListener('click', () => { guiaPanel.hidden = false; });
document.getElementById('guia-close').addEventListener('click', () => { guiaPanel.hidden = true; });
guiaPanel.addEventListener('click', e => { if (e.target === guiaPanel) guiaPanel.hidden = true; });

// ── ☕ CAFÉ (apoyo voluntario) ───────────────────────────
const cafePanel = document.getElementById('cafe-panel');
document.getElementById('cafe-btn').addEventListener('click', () => { cafePanel.hidden = false; });
document.getElementById('cafe-close').addEventListener('click', () => { cafePanel.hidden = true; });
cafePanel.addEventListener('click', e => { if (e.target === cafePanel) cafePanel.hidden = true; });
cafePanel.addEventListener('click', async e => {
  const btn = e.target.closest('.cafe-copy');
  if (!btn || !btn.dataset.copiar) return;   // PayPal es un enlace, no tiene nada que copiar
  try {
    await navigator.clipboard.writeText(btn.dataset.copiar);
    showToast('✓ Copiado. ¡Gracias! ☕');
  } catch {
    showToast('No se pudo copiar: selecciónalo a mano.', true);
  }
});

// ── CREAR CUENTA (perfil en este dispositivo) ───────────
document.getElementById('register-btn').addEventListener('click', () => {
  document.getElementById('step-password').style.display = 'none';
  document.getElementById('step-register').style.display = 'flex';
  const nombre = document.getElementById('login-name').value.trim();
  if (nombre) document.getElementById('register-name').value = nombre;
  document.getElementById('register-key').value = claveGroq();
  document.getElementById('register-name').focus();
});

document.getElementById('register-back').addEventListener('click', () => {
  document.getElementById('step-register').style.display = 'none';
  document.getElementById('step-password').style.display = 'flex';
});

document.getElementById('register-go').addEventListener('click', async () => {
  const nombre = document.getElementById('register-name').value.trim();
  const error = document.getElementById('register-error');
  if (!nombre) { error.style.display = 'block'; return; }
  error.style.display = 'none';
  const clave = document.getElementById('register-key').value.trim();
  try {
    if (clave) localStorage.setItem('mm-groq-key', clave);
  } catch {}
  guardarPerfilLocal({ student: nombre, course: null, current: null, mastered: [], point: null });
  await mostrarCursosLocales();
});

document.getElementById('register-name').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('register-go').click();
});

// Selector de curso para el perfil local: mismas tarjetas que el plan B del admin, pero sin tocar el
// servidor — al elegir, el curso y su primer tema se guardan en este navegador.
async function mostrarCursosLocales() {
  const perfil = perfilLocal();
  document.getElementById('step-register').style.display = 'none';
  const step = document.getElementById('step-course');
  step.style.display = 'flex';
  document.getElementById('course-greeting').textContent = `¡Hola, ${perfil.student}! ¿Qué quieres aprender?`;
  const cursos = (await (await fetch('/courses?temas=1')).json()).courses;
  temasPorCurso = Object.fromEntries(cursos.map(c => [c.course, c.topics]));
  document.getElementById('course-cards').innerHTML = cursos.map(({ course: c }) =>
    `<button class="course-card" data-course="${c}"${(window.CURSOS || {})[c] ? ` style="--course-color:${window.CURSOS[c].color};--course-text:#fff"` : ''}>${COURSE_LABELS[c] || c}</button>`
  ).join('');
}

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
  pintarFilaPartida();        // el estado de la partida puede haber cambiado desde la última vez
});
document.addEventListener('click', () => settingsDropdown.classList.remove('open'));
settingsDropdown.addEventListener('click', (e) => e.stopPropagation());

// Clave de Groq propia: solo en este navegador (localStorage), nunca se guarda en el servidor.
// Viaja en cada petición del chat; si está puesta, responde Groq con la cuota de quien la pone.
const groqKeyInput = document.getElementById('groq-key');
const groqKeyState = document.getElementById('groq-key-state');

function pintarEstadoClave() {
  groqKeyState.textContent = claveGroq()
    ? '✓ Guardada en este navegador: la IA responde con tu cuota, no la de Nando.'
    : 'Sin clave: la IA responde con la cuota del servidor.';
}

groqKeyInput.addEventListener('change', () => {
  const valor = groqKeyInput.value.trim();
  try {
    if (valor) localStorage.setItem('mm-groq-key', valor);
    else localStorage.removeItem('mm-groq-key');
  } catch {}
  pintarEstadoClave();
  showToast(valor ? '✓ Clave guardada en este navegador' : 'Clave borrada');
});

try { groqKeyInput.value = localStorage.getItem('mm-groq-key') || ''; } catch {}
pintarEstadoClave();

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
  const sessionText = messages.map(m => `**${m.role === 'user' ? 'Estudiante' : 'Trainer'}:** ${m.content.replace(' __start__', '')}`).join('\n\n');
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
  // Cerrar sesión borra TODO el localStorage, y ahí vive la partida de quien no es admin: avisar antes.
  const local = perfilLocal();
  const n = (local && local.mastered || []).length;
  if (local && local.course && !confirm(
      `Tus datos (${local.course}, ${n} tema${n === 1 ? '' : 's'} superado${n === 1 ? '' : 's'}) viven solo en este navegador ` +
      'y se borrarán al cerrar sesión.\n\nSi no los has exportado (⚙ → Tus datos → Exportar), los perderás.\n\n¿Cerrar sesión igualmente?')) {
    return;
  }
  await fetch('/logout', { method: 'POST' });
  try { localStorage.clear(); sessionStorage.clear(); } catch {}   // olvida nombre, plan y pomodoro: vuelve al inicio con la opción de invitado
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
  document.querySelector('#input-bar').style.display = 'flex';
  document.getElementById('input').focus();
});

document.getElementById('code-send').addEventListener('click', () => {
  if (!window.cmEditor) return;
  const code = window.cmEditor.getValue().trim();
  if (!code) return;
  const lang = document.getElementById('code-lang').value === 'text' ? '' : document.getElementById('code-lang').value;
  document.getElementById('input').value = '```' + lang + '\n' + code + '\n```';
  document.getElementById('code-panel').style.display = 'none';
  document.querySelector('#input-bar').style.display = 'flex';
  window.cmEditor.setValue('');
  send();
});
