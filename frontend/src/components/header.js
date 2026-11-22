/* Cabeçalho superior: título da página, alternância de tema e menu mobile. */

import { icone } from './icons.js';
import { escapeHtml } from './notification.js';

export function renderizarHeader(elemento, pagina) {
  elemento.innerHTML = `
    <button class="botao-menu" id="botao-menu" type="button" aria-label="Abrir menu" aria-expanded="false">
      ${icone('menu')}
    </button>

    <div class="header-titulo">
      <h1>${escapeHtml(pagina.titulo)}</h1>
      <p>${escapeHtml(pagina.descricao)}</p>
    </div>

    <div class="header-acoes">
      <button class="botao botao-fantasma" id="botao-tema" type="button"
              aria-label="Alternar tema" title="Alternar tema claro/escuro">
        <span id="icone-tema"></span>
        <span class="rotulo-tema" id="rotulo-tema"></span>
      </button>
    </div>
  `;
}

export function atualizarBotaoTema(tema) {
  const iconeEl = document.getElementById('icone-tema');
  const rotuloEl = document.getElementById('rotulo-tema');
  if (!iconeEl || !rotuloEl) return;

  const claro = tema === 'claro';
  iconeEl.innerHTML = icone(claro ? 'lua' : 'sol');
  rotuloEl.textContent = claro ? 'Tema claro' : 'Tema escuro';
  document.getElementById('botao-tema')?.setAttribute(
    'aria-label',
    `Alternar para tema ${claro ? 'escuro' : 'claro'}`
  );
}
