// Panel de cursos (punto 24 del ROADMAP): pinta GET /dashboard. Solo pinta: elegir un curso lo hace app.js
// (alElegir), que guarda el curso y abre la sala, igual que antes. Si algo falla, mostrarDashboard() lanza el error
// y app.js deja las tarjetas pequeñas de siempre.
// Un solo método para móvil y ordenador: dos modos ("deslizable" = .slide, o apilado/desplegado) y "cuántas caben".
(function () {
  // ÚNICA tabla de identidad de cada curso (nombre, color e icono): el panel y las tarjetas pequeñas del plan B (app.js)
  // la leen de window.CURSOS. Un curso que no esté aquí se enseña con su id y el color del tema / de PALETA.
  const CURSOS = {
    cs50: { nombre: 'CS50', color: '#a51c30', icono: '🎓' },
    mouredev: { nombre: 'MoureDev', color: '#1a6fc4', icono: '☕' },
    '42malaga': { nombre: '42 Málaga', color: '#0f8b8d', icono: '🧩' },
  };
  window.CURSOS = CURSOS;
  const PALETA = ['#7c4dff', '#e67e22', '#2e9d5b', '#1d8fe1', '#8e8e93'];
  const LOGROS = {   // id del servidor → [icono, título, descripción]
    first_topic: ['🥉', 'Primer tema', 'Domina tu primer tema'],
    topics_5: ['🖐️', 'Cinco temas', '5 temas dominados en total'],
    topics_10: ['🔟', 'Diez temas', '10 temas dominados en total'],
    half_course: ['🥈', 'Mitad de un curso', 'Pasa la mitad de cualquier curso'],
    course_complete: ['🏆', 'Curso completo', 'Termina un curso entero'],
    all_courses_started: ['🧭', 'Todos los cursos', 'Empieza todos los cursos'],
  };
  const PRONTO = [['🔥', 'Racha de 7 días'], ['🍅', '10 pomodoros']];   // aún no hay dato fiable (punto 24)
  const VISTAS = 3;                                                    // tarjetas visibles a la vez en el ordenador
  const ordenador = matchMedia('(min-width: 900px)');
  const reducir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let panel = null, timers = [], escuchando = false;

  const tarjeta = (c, i, o) => {
    const color = (CURSOS[c.course] || {}).color || PALETA[i % PALETA.length];
    const nombre = (o.etiquetas || {})[c.course] || c.course;
    const logros = [1, Math.ceil(c.total / 2), c.total].filter((n) => n > 0 && c.done >= n).length;
    const ahora = c.finished ? 'Curso completo' : (c.current_label || 'Sin empezar');
    const lineas = [];                                                 // la línea que rota bajo "Ahora"
    if (c.last_mastered_label) lineas.push(['Último dominado', c.last_mastered_label]);
    if (c.next_label) lineas.push(['Siguiente', c.next_label]);
    if (c.finished) lineas.push(['Estado', 'Terminado']);
    return `<button class="dash-card" type="button" data-course="${esc(c.course)}" style="--c:${color};--i:${i}">
      <header><span class="dash-ico">${(CURSOS[c.course] || {}).icono || '📘'}</span><h2>${esc(nombre)}</h2>
        ${c.course === o.ultimo ? '<span class="dash-chip">último</span>' : ''}</header>
      <div class="dash-big"><span class="dash-num" data-n="${c.done}">${c.done}</span><span class="dash-den">/ ${c.total}</span>
        <small>temas dominados · ${c.percent}%</small></div>
      <div class="dash-bar"><i data-pct="${c.percent}" style="width:${c.percent}%"></i></div>
      <div class="dash-now"><span class="dash-k">Ahora</span><span class="dash-v dash-solari">${esc(ahora)}</span></div>
      ${lineas.length ? `<div class="dash-live" data-lineas="${esc(JSON.stringify(lineas))}"><span class="dash-k">${esc(lineas[0][0])}</span><span class="dash-v">${esc(lineas[0][1])}</span></div>` : ''}
      <div class="dash-mini">🏅 ${logros}/3 logros del curso</div>
      <span class="dash-cta">Entrar ▶</span>
    </button>`;
  };

  const logro = (a) => {
    const [ic, t, d] = LOGROS[a.id] || ['🏅', a.id, ''];
    const pct = a.target > 0 ? Math.round(a.progress / a.target * 100) : 0;
    return `<li class="dash-lg ${a.unlocked ? 'on' : ''}"><span class="ic">${ic}</span><b>${esc(t)}</b>
      <span class="n">${a.progress}/${a.target}</span><small>${esc(d)}</small><div class="dash-bar"><i style="width:${pct}%"></i></div></li>`;
  };

  // ── Movimiento: barra y número que suben, y la línea que rota (todo se apaga con "reducir movimiento")
  const parar = () => { timers.forEach(clearInterval); timers = []; };
  const animar = () => {
    parar();
    panel.querySelectorAll('.dash-card').forEach((card, i) => {
      const num = card.querySelector('.dash-num'), fin = +num.dataset.n, barra = card.querySelector('.dash-bar i');
      if (!reducir) {
        barra.style.width = '0%';
        requestAnimationFrame(() => requestAnimationFrame(() => { barra.style.width = barra.dataset.pct + '%'; }));
        const t0 = performance.now();
        const paso = (t) => { const p = Math.min(1, (t - t0) / 500); num.textContent = Math.round(fin * p); if (p < 1) requestAnimationFrame(paso); };
        num.textContent = '0'; requestAnimationFrame(paso);
      }
      const live = card.querySelector('.dash-live');
      const ls = live ? JSON.parse(live.dataset.lineas) : [];
      if (ls.length > 1) {
        const k = live.querySelector('.dash-k'), v = live.querySelector('.dash-v'); let n = 0;
        timers.push(setInterval(() => {
          const [t, x] = ls[++n % ls.length]; k.textContent = t; v.textContent = x;
          v.classList.remove('in'); void v.offsetWidth; v.classList.add('in');
        }, 3200 + i * 500));
      }
    });
  };

  // ── Disposición: carrusel de tarjetas (.dash-grid). Logros va FUERA del carrusel (debajo) salvo en el móvil apilado,
  // donde es la última tarjeta de la pila.
  const grid = () => panel.querySelector('.dash-grid');
  const vistas = () => (ordenador.matches ? VISTAS : 1);
  const horizontal = () => grid().classList.contains('slide');
  const pagina = () => {                                   // página actual y paso entre páginas, con el eje del modo
    const g = grid(), el = [...g.children], v = vistas(), h = horizontal();
    const paginas = Math.max(1, Math.ceil(el.length / v));
    const paso = el[v] ? (h ? el[v].offsetLeft - el[0].offsetLeft : el[v].offsetTop - el[0].offsetTop) : 1;
    const pos = h ? g.scrollLeft : g.scrollTop, max = h ? g.scrollWidth - g.clientWidth : g.scrollHeight - g.clientHeight;
    return { paginas, paso, p: pos >= max - 2 ? paginas - 1 : Math.round(pos / paso) };
  };
  const irA = (p) => {                                     // destino ABSOLUTO: pulsar rápido no se acumula
    const g = grid(), el = [...g.children], { paginas } = pagina(), q = Math.max(0, Math.min(paginas - 1, p)), h = horizontal();
    const destino = h ? el[q * vistas()].offsetLeft - el[0].offsetLeft : el[q * vistas()].offsetTop - el[0].offsetTop;
    g.scrollTo({ [h ? 'left' : 'top']: destino, behavior: 'smooth' });
  };
  const marca = () => {
    if (!panel || !grid()) return;
    const { paginas, p } = pagina();
    panel.querySelector('.dash-pag').textContent = `${p + 1} / ${paginas}`;
    panel.querySelector('.dash-prev').disabled = p === 0;
    panel.querySelector('.dash-next').disabled = p >= paginas - 1;
    [...panel.querySelector('.dash-dots').children].forEach((d, j) => d.classList.toggle('on', j === p));
  };
  const textoModo = () => {
    panel.querySelector('.dash-mode').textContent = horizontal() ? '↔ Deslizable' : (ordenador.matches ? '▦ Desplegado' : '↕ Apilado');
  };
  const aplicarModo = (slide) => {
    grid().classList.toggle('slide', slide);
    panel.classList.toggle('es-slide', slide);
    colocarLogros();
    grid().scrollTo(0, 0); textoModo(); marca();
  };
  const colocarLogros = () => {
    const lg = panel.querySelector('.dash-logros'), g = grid();
    (ordenador.matches || horizontal() ? panel.querySelector('.dash-wrap') : g).appendChild(lg);
    panel.querySelector('.dash-dots').innerHTML = [...g.children].map(() => '<i></i>').join('');
  };
  const alCambiarAncho = () => {                           // por defecto: móvil = deslizable; ordenador = desplegado
    if (!panel || !grid()) return;
    aplicarModo(!ordenador.matches);
  };

  // Marco vacío al instante, mientras llegan los datos
  window.esqueletoDashboard = function () {
    panel = document.getElementById('dashboard');
    panel.dataset.esqueleto = '1';
    panel.innerHTML = `<div class="dash-wrap"><div class="dash-top"><div class="dash-hola dash-esq-t"></div></div>
      <div class="dash-grid">${'<div class="dash-card dash-esq"><i></i><i></i><i></i></div>'.repeat(3)}</div></div>`;
    panel.style.display = 'flex';
  };

  // opciones: { etiquetas: {curso: 'Nombre'}, ultimo: 'curso', saludo: 'texto', alElegir: (curso) => ...,
  //             datos: respuesta de /dashboard si ya se pidió (si no, se pide aquí) }
  window.mostrarDashboard = async function (o) {
    let d = o.datos;
    if (!d) {
      const r = await fetch('/dashboard');
      if (!r.ok) throw new Error('dashboard ' + r.status);
      d = await r.json();
    }
    if (!d.courses || !d.courses.length) throw new Error('dashboard sin cursos');
    panel = document.getElementById('dashboard');
    const desbloqueados = d.achievements.filter((a) => a.unlocked).length;
    delete panel.dataset.esqueleto;
    panel.dataset.sobran = d.courses.length > VISTAS ? '1' : '0';
    panel.innerHTML = `<div class="dash-wrap">
      <div class="dash-top"><div class="dash-hola">${esc(o.saludo || '¿Qué entrenamos hoy?')}</div>
        <div class="dash-ctl"><div class="dash-dots"></div>
          <div class="dash-pager"><button type="button" class="dash-prev" aria-label="Anterior">‹</button><span class="dash-pag"></span><button type="button" class="dash-next" aria-label="Siguiente">›</button></div>
          <button type="button" class="dash-mode"></button></div></div>
      <div class="dash-grid" tabindex="0">${d.courses.map((c, i) => tarjeta(c, i, o)).join('')}</div>
      <section class="dash-logros"><h2>🏅 Logros <span class="dash-chip">${desbloqueados}/${d.achievements.length}</span></h2>
        <ul class="dash-lista">${d.achievements.map(logro).join('')}${PRONTO.map(([ic, t]) =>
          `<li class="dash-lg pronto"><span class="ic">${ic}</span><b>${t}</b><span class="n">pronto</span><small>Necesita registrar la actividad</small></li>`).join('')}</ul>
      </section></div>`;
    panel.onclick = (e) => {
      const b = e.target.closest('button, .dash-dots i');
      if (!b) return;
      if (b.dataset && b.dataset.course) {
        parar(); panel.style.display = 'none';
        return o.alElegir(b.dataset.course);
      }
      if (b.classList.contains('dash-mode')) return aplicarModo(!horizontal());
      if (b.classList.contains('dash-prev')) return irA(pagina().p - 1);
      if (b.classList.contains('dash-next')) return irA(pagina().p + 1);
      if (b.parentElement.classList.contains('dash-dots')) irA([...b.parentElement.children].indexOf(b));
    };
    const g = grid();
    g.addEventListener('scroll', marca, { passive: true });
    g.addEventListener('keydown', (e) => {
      if (!horizontal() || !['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      e.preventDefault(); irA(pagina().p + (e.key === 'ArrowRight' ? 1 : -1));
    });
    if (!escuchando) { ordenador.addEventListener('change', alCambiarAncho); escuchando = true; }
    panel.style.display = 'flex';
    alCambiarAncho();
    animar();
  };
})();
