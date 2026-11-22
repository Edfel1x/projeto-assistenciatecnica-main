/* Construtor de tabelas com rótulos para a versão mobile (data-label).
   O conteúdo das células já deve vir escapado de quem chama. */

import { escapeHtml } from './notification.js';
import { estadoVazio } from './loading.js';

/**
 * @param {Array<{chave:string, rotulo:string, html:(item)=>string, classe?:string}>} colunas
 */
export function renderizarTabela({ colunas, itens, vazioTitulo, vazioDescricao }) {
  if (!itens.length) {
    return estadoVazio(vazioTitulo, vazioDescricao);
  }

  const cabecalho = colunas
    .map((coluna) => `<th scope="col" class="${escapeHtml(coluna.classe || '')}">${escapeHtml(coluna.rotulo)}</th>`)
    .join('');

  const linhas = itens
    .map(
      (item) => `
      <tr>
        ${colunas
          .map(
            (coluna) => `
          <td data-label="${escapeHtml(coluna.rotulo)}" class="${escapeHtml(coluna.classe || '')}">
            ${coluna.html(item)}
          </td>`
          )
          .join('')}
      </tr>`
    )
    .join('');

  return `
    <div class="tabela-container">
      <table class="tabela">
        <thead><tr>${cabecalho}</tr></thead>
        <tbody>${linhas}</tbody>
      </table>
    </div>`;
}
