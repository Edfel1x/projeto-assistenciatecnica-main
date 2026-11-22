/* Notificações visuais integradas ao design (substituem alertas nativos). */

import { icone } from './icons.js';

const ICONES = { sucesso: 'sucesso', erro: 'alerta', aviso: 'info', info: 'info' };
const TITULOS = { sucesso: 'Sucesso', erro: 'Erro', aviso: 'Atenção', info: 'Informação' };

export function notificar(tipo, mensagem, detalhe = '', duracao = 4500) {
  const area = document.getElementById('notificacoes');
  if (!area) return;

  const elemento = document.createElement('div');
  elemento.className = `notificacao ${tipo}`;
  elemento.setAttribute('role', tipo === 'erro' ? 'alert' : 'status');
  elemento.innerHTML = `
    ${icone(ICONES[tipo] || 'info')}
    <div>
      <strong>${TITULOS[tipo] || 'Informação'}</strong>
      <span>${escapeHtml(mensagem)}${detalhe ? `<br />${escapeHtml(detalhe)}` : ''}</span>
    </div>
  `;
  area.appendChild(elemento);

  const remover = () => {
    elemento.classList.add('sair');
    elemento.addEventListener('animationend', () => elemento.remove(), { once: true });
    setTimeout(() => elemento.remove(), 300);
  };
  setTimeout(remover, duracao);
}

/* Escapa conteúdo antes de inserir no DOM: proteção contra XSS. */
export function escapeHtml(valor) {
  return String(valor ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
