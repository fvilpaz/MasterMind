import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightActiveLine } from '@codemirror/view';
import { EditorState, Compartment } from '@codemirror/state';
import { defaultKeymap, indentWithTab, history, historyKeymap, indentOnInput, bracketMatching, syntaxHighlighting, defaultHighlightStyle } from 'codemirror';
import { oneDark } from '@codemirror/theme-one-dark';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';

const langCompartment = new Compartment();

function getLang(name) {
  if (name === 'python') return python();
  if (name === 'javascript') return javascript();
  if (name === 'html') return html();
  if (name === 'css') return css();
  return [];
}

const state = EditorState.create({
  doc: '',
  extensions: [
    history(),
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightActiveLine(),
    indentOnInput(),
    bracketMatching(),
    syntaxHighlighting(defaultHighlightStyle),
    oneDark,
    langCompartment.of(getLang('python')),
    keymap.of([indentWithTab, ...historyKeymap, ...defaultKeymap]),
    EditorView.lineWrapping,
  ]
});

window.cmEditor = new EditorView({ state, parent: document.getElementById('code-editor-wrap') });

document.getElementById('code-lang').addEventListener('change', e => {
  window.cmEditor.dispatch({ effects: langCompartment.reconfigure(getLang(e.target.value)) });
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
    window.cmEditor.focus();
  }
};
