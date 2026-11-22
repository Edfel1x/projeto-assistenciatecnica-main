/* Modal acessível para operações rápidas e confirmações.

   Os modais são empilhados: uma confirmação pode abrir por cima de um
   formulário sem destruí-lo. O fechamento (botão, X, backdrop ou Esc)
   sempre resolve a Promise de confirmação, evitando awaits pendurados.
*/

import { icone } from './icons.js';
import { escapeHtml } from './notification.js';

const pilha = [];
let tecladoRegistrado = false;

function tratadorTeclado(evento) {
  const atual = pilha[pilha.length - 1];
  if (!atual) return;

  if (evento.key === 'Escape') {
    evento.preventDefault();
    fecharModal();
    return;
  }

  if (evento.key === 'Tab') {
    const focaveis = atual.elemento.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled])'
    );
    if (!focaveis.length) return;
    const primeiro = focaveis[0];
    const ultimo = focaveis[focaveis.length - 1];
    if (evento.shiftKey && document.activeElement === primeiro) {
      evento.preventDefault();
      ultimo.focus();
    } else if (!evento.shiftKey && document.activeElement === ultimo) {
      evento.preventDefault();
      primeiro.focus();
    }
  }
}

function registrarTeclado() {
  if (tecladoRegistrado) return;
  document.addEventListener('keydown', tratadorTeclado);
  tecladoRegistrado = true;
}

export function abrirModal({ titulo, descricao = '', conteudo = '', rodape = '', grande = false }) {
  const raiz = document.getElementById('modal-root');
  if (!raiz) return null;

  registrarTeclado();

  const fundo = document.createElement('div');
  fundo.className = 'modal-fundo';
  fundo.style.zIndex = String(60 + pilha.length);
  fundo.setAttribute('role', 'presentation');
  fundo.innerHTML = `
    <div class="modal ${grande ? 'modal-grande' : ''}" role="dialog" aria-modal="true" aria-labelledby="modal-titulo-${pilha.length}">
      <div class="modal-cabecalho">
        <div>
          <h3 id="modal-titulo-${pilha.length}">${escapeHtml(titulo)}</h3>
          ${descricao ? `<p>${escapeHtml(descricao)}</p>` : ''}
        </div>
        <button class="botao-fechar" type="button" data-fechar aria-label="Fechar">${icone('fechar')}</button>
      </div>
      <div class="modal-corpo">${conteudo}</div>
      ${rodape ? `<div class="modal-rodape">${rodape}</div>` : ''}
    </div>`;
  raiz.appendChild(fundo);

  const registro = {
    elemento: fundo,
    focoAnterior: document.activeElement,
    aoFechar: null,
  };
  pilha.push(registro);

  fundo.addEventListener('mousedown', (evento) => {
    if (evento.target === fundo) fecharModal();
  });
  fundo.querySelectorAll('[data-fechar]').forEach((botao) => {
    botao.addEventListener('click', () => fecharModal());
  });

  fundo.querySelector('.modal')?.querySelector('input, select, textarea, button')?.focus();
  return fundo.querySelector('.modal');
}

/** Fecha apenas o modal do topo da pilha. */
export function fecharModal() {
  const registro = pilha.pop();
  if (!registro) return;

  registro.elemento.remove();
  if (typeof registro.aoFechar === 'function') {
    registro.aoFechar();
  }
  if (pilha.length === 0) {
    document.removeEventListener('keydown', tratadorTeclado);
    tecladoRegistrado = false;
    document.getElementById('modal-root').innerHTML = '';
  }
  registro.focoAnterior?.focus?.();
}

/** Fecha todos os modais (usado na troca de rota). */
export function fecharTodosModais() {
  while (pilha.length) fecharModal();
}

/**
 * Confirmação visual para operações importantes.
 * Retorna uma Promise<boolean> que sempre é resolvida (true ou false).
 */
export function confirmar({ titulo, mensagem, rotuloConfirmar = 'Confirmar', perigo = false }) {
  return new Promise((resolve) => {
    const modal = abrirModal({
      titulo,
      conteudo: `<p style="color:var(--texto-secundario)">${escapeHtml(mensagem)}</p>`,
      rodape: `
        <button class="botao" type="button" data-cancelar>Cancelar</button>
        <button class="botao ${perigo ? 'botao-perigo' : 'botao-primario'}" type="button" data-confirmar>
          ${escapeHtml(rotuloConfirmar)}
        </button>`,
    });
    if (!modal) {
      resolve(false);
      return;
    }

    const registro = pilha[pilha.length - 1];
    let resolvida = false;
    const finalizar = (resposta) => {
      if (resolvida) return;
      resolvida = true;
      registro.aoFechar = null;
      // Se o modal já foi fechado pelo callback aoFechar (Esc/X/backdrop),
      // não chamar fecharModal() novamente — isso fecharia o modal abaixo.
      if (pilha.includes(registro)) fecharModal();
      resolve(resposta);
    };

    registro.aoFechar = () => finalizar(false);
    modal.querySelector('[data-confirmar]').addEventListener('click', () => finalizar(true));
    modal.querySelector('[data-cancelar]').addEventListener('click', () => finalizar(false));
  });
}
