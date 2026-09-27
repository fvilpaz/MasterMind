// CodeMirror 5 — cargado vía CDN en index.html como script clásico
(function() {
  const LANG_MODES = {
    python: 'python',
    java: 'text/x-java',   // MoureDev (modo clike)
    c: 'text/x-csrc',      // CS50 (modo clike)
    javascript: 'javascript',
    html: 'htmlmixed',
    css: 'css',
    bash: 'shell',
    text: null
  };

  // Tema del editor a juego con el de la app (claro con claro, oscuro con oscuro). Elegidos midiendo 25
  // temas de CodeMirror con código Java: los únicos que dan color propio a tipos, palabras clave, textos,
  // números, comentarios y nombres, y en los que todo se lee (contraste ≥ 3). De los claros solo pasa eclipse
  // (idea, yeti, duotone-light… pintan los tipos igual que el texto). Si el tema no está aquí: dracula.
  const EDITOR_THEMES = {
    light: 'eclipse',
    harvard: 'eclipse',
    mint: 'eclipse',
    barbie: 'eclipse',
    oldschool: 'eclipse',
    dark: 'darcula',       // el oscuro de IntelliJ, pensado para Java
    dracula: 'dracula',
    cyberpunk: 'monokai'
  };
  const editorTheme = () => EDITOR_THEMES[document.documentElement.getAttribute('data-theme')] || 'dracula';

  const wrap = document.getElementById('code-editor-wrap');
  const langSelect = document.getElementById('code-lang');

  window.cmEditor = CodeMirror(wrap, {
    value: '',
    mode: 'python',
    theme: editorTheme(),
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    extraKeys: {
      Tab: cm => cm.execCommand('indentMore'),
      'Shift-Tab': cm => cm.execCommand('indentLess'),
    }
  });

  // Observer: el editor se entera solo cuando cambia el tema de la app (data-theme en <html>),
  // sin que el código del selector de temas tenga que saber que existe un editor.
  new MutationObserver(() => window.cmEditor.setOption('theme', editorTheme()))
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  langSelect.addEventListener('change', e => {
    const mode = LANG_MODES[e.target.value] || 'text/plain';
    window.cmEditor.setOption('mode', mode);
  });

  window.toggleCodeEditor = function() {
    const panel = document.getElementById('code-panel');
    const footer = document.querySelector('footer');
    const isOpen = panel.style.display === 'flex';
    if (isOpen) {
      panel.style.display = 'none';
      footer.style.display = 'flex';
    } else {
      panel.style.display = 'flex';
      footer.style.display = 'none';
      window.cmEditor.refresh();
      window.cmEditor.focus();
    }
  };
})();
