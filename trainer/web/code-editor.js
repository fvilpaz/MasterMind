// CodeMirror 5 — cargado vía CDN en index.html como script clásico
(function() {
  const LANG_MODES = {
    python: 'python',
    javascript: 'javascript',
    html: 'htmlmixed',
    css: 'css',
    bash: 'shell',
    text: null
  };

  const wrap = document.getElementById('code-editor-wrap');
  const langSelect = document.getElementById('code-lang');

  window.cmEditor = CodeMirror(wrap, {
    value: '',
    mode: 'python',
    theme: 'dracula',
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
