// Panel de cursos (punto 24 del ROADMAP): pinta GET /dashboard. Solo pinta: elegir un curso lo hace app.js
// (alElegir), que guarda el curso y abre la sala, igual que antes. Si algo falla, mostrarDashboard() lanza el error
// y app.js deja las tarjetas pequeñas de siempre.
(function () {
  const COLORES = { cs50: '#a51c30', mouredev: '#1a6fc4', '42malaga': '#0f8b8d' };
  const PALETA = ['#7c4dff', '#e67e22', '#2e9d5b', '#1d8fe1', '#8e8e93'];
  const ICONOS = { cs50: '🎓', mouredev: '☕', '42malaga': '🧩' };
  const LOGROS = {   // id del servidor → [icono, título, descripción]
    first_topic: ['🥉', 'Primer tema', 'Domina tu primer tema'],
    topics_5: ['🖐️', 'Cinco temas', '5 temas dominados en total'],
    topics_10: ['🔟', 'Diez temas', '10 temas dominados en total'],
    half_course: ['🥈', 'Mitad de un curso', 'Pasa la mitad de cualquier curso'],
    course_complete: ['🏆', 'Curso completo', 'Termina un curso entero'],
    all_courses_started: ['🧭', 'Todos los cursos', 'Empieza todos los cursos'],
  };
  const PRONTO = [['🔥', 'Racha de 7 días'], ['🍅', '10 pomodoros']];   // aún no hay dato fiable (punto 24)
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const tarjeta = (c, i, o) => {
    const color = COLORES[c.course] || PALETA[i % PALETA.length];
    const nombre = (o.etiquetas || {})[c.course] || c.course;
    const logros = [1, Math.ceil(c.total / 2), c.total].filter((n) => n > 0 && c.done >= n).length;
    const ahora = c.finished ? 'Curso completo' : (c.current_label || 'Sin empezar');
    const otra = c.last_mastered_label ? ['Último dominado', c.last_mastered_label] : (c.next_label ? ['Siguiente', c.next_label] : null);
    return `<button class="dash-card" type="button" data-course="${esc(c.course)}" style="--c:${color}">
      <header><span class="dash-ico">${ICONOS[c.course] || '📘'}</span><h2>${esc(nombre)}</h2>
        ${c.course === o.ultimo ? '<span class="dash-chip">último</span>' : ''}</header>
      <div class="dash-big"><span class="dash-num">${c.done}</span><span class="dash-den">/ ${c.total}</span>
        <small>temas dominados · ${c.percent}%</small></div>
      <div class="dash-bar"><i style="width:${c.percent}%"></i></div>
      <div><span class="dash-k">Ahora</span><span class="dash-v">${esc(ahora)}</span></div>
      ${otra ? `<div><span class="dash-k">${otra[0]}</span><span class="dash-v">${esc(otra[1])}</span></div>` : ''}
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

  // opciones: { etiquetas: {curso: 'Nombre'}, ultimo: 'curso', saludo: 'texto', alElegir: (curso) => ... }
  window.mostrarDashboard = async function (o) {
    const r = await fetch('/dashboard');
    if (!r.ok) throw new Error('dashboard ' + r.status);
    const d = await r.json();
    if (!d.courses || !d.courses.length) throw new Error('dashboard sin cursos');
    const overlay = document.getElementById('login-overlay');
    const caja = overlay.querySelector('.login-box');
    let panel = document.getElementById('dashboard');
    if (!panel) { panel = document.createElement('div'); panel.id = 'dashboard'; overlay.appendChild(panel); }
    const reales = d.achievements.filter((a) => a.unlocked).length;
    panel.innerHTML = `<div class="dash-wrap">
      <div class="dash-hola">${esc(o.saludo || '¿Qué entrenamos hoy?')}</div>
      <div class="dash-grid">${d.courses.map((c, i) => tarjeta(c, i, o)).join('')}</div>
      <section class="dash-logros"><h2>🏅 Logros <span class="dash-chip">${reales}/${d.achievements.length}</span></h2>
        <ul class="dash-lista">${d.achievements.map(logro).join('')}${PRONTO.map(([ic, t]) =>
          `<li class="dash-lg pronto"><span class="ic">${ic}</span><b>${t}</b><span class="n">pronto</span><small>Necesita registrar la actividad</small></li>`).join('')}</ul>
      </section></div>`;
    panel.onclick = (e) => {
      const b = e.target.closest('button[data-course]');
      if (!b) return;
      panel.style.display = 'none';
      caja.style.display = '';                      // la sala previa vive dentro de la caja del login
      o.alElegir(b.dataset.course);
    };
    caja.style.display = 'none';
    panel.style.display = '';
  };
})();
