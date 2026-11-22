/* Indicadores de carregamento e estados vazios. */

import { icone } from './icons.js';
import { escapeHtml } from './notification.js';

let contadorOverlay = 0;

export function carregando(container, mensagem = 'Carregando dados...') {
  container.innerHTML = `
    <div class="carregando" role="status">
      <div class="spinner"></div>
      <span>${escapeHtml(mensagem)}</span>
    </div>`;
}

export function mostrarOverlay(mensagem = 'Processando...') {
  contadorOverlay += 1;
  if (document.getElementById('overlay-carregando')) return;

  const overlay = document.createElement('div');
  overlay.id = 'overlay-carregando';
  overlay.className = 'overlay-carregando';
  overlay.setAttribute('role', 'status');
  overlay.innerHTML = `
    <div class="caixa">
      <div class="spinner"></div>
      <span>${escapeHtml(mensagem)}</span>
    </div>`;
  document.body.appendChild(overlay);
}

export function ocultarOverlay() {
  contadorOverlay = Math.max(0, contadorOverlay - 1);
  if (contadorOverlay === 0) {
    document.getElementById('overlay-carregando')?.remove();
  }
}

export function estadoVazio(titulo, descricao = '', iconeNome = 'caixa') {
  return `
    <div class="estado-vazio">
      ${icone(iconeNome)}
      <strong>${escapeHtml(titulo)}</strong>
      ${descricao ? `<p>${escapeHtml(descricao)}</p>` : ''}
    </div>`;
}

/** Envolve uma Promise com overlay automático. */
export async function comCarregamento(promise, mensagem) {
  mostrarOverlay(mensagem);
  try {
    return await promise;
  } finally {
    ocultarOverlay();
  }
}
