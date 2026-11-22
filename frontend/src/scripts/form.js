/* Helpers de formulário: geração de campos, validação e leitura de valores. */

import { escapeHtml } from '../components/notification.js';

export function campo({ nome, rotulo, tipo = 'text', valor = '', obrigatorio = true, opcoes = null, placeholder = '', larga = false, atributos = '' }) {
  const id = `campo-${nome}`;
  const obrigatorioHtml = obrigatorio ? '<span class="obrigatorio">*</span>' : '';
  let controle;

  if (tipo === 'select') {
    controle = `
      <select id="${id}" name="${nome}" ${obrigatorio ? 'required' : ''}>
        ${obrigatorio ? '<option value="">Selecione...</option>' : '<option value="">Nenhum</option>'}
        ${(opcoes || [])
          .map(
            (opcao) =>
              `<option value="${escapeHtml(opcao.valor)}" ${String(valor) === String(opcao.valor) ? 'selected' : ''}>${escapeHtml(opcao.rotulo)}</option>`
          )
          .join('')}
      </select>`;
  } else if (tipo === 'textarea') {
    controle = `<textarea id="${id}" name="${nome}" placeholder="${escapeHtml(placeholder)}" ${obrigatorio ? 'required' : ''}>${escapeHtml(valor)}</textarea>`;
  } else {
    controle = `<input id="${id}" name="${nome}" type="${tipo}" value="${escapeHtml(valor)}" placeholder="${escapeHtml(placeholder)}" ${obrigatorio ? 'required' : ''} ${atributos} />`;
  }

  return `
    <div class="campo ${larga ? 'campo-largo' : ''}">
      <label for="${id}">${escapeHtml(rotulo)}${obrigatorioHtml}</label>
      ${controle}
      <small class="erro-campo" data-erro="${nome}"></small>
    </div>`;
}

/** Valida campos required. Retorna false e marca os inválidos. */
export function validarFormulario(formulario) {
  let valido = true;
  formulario.querySelectorAll('[required]').forEach((controle) => {
    const campoPai = controle.closest('.campo');
    const erro = formulario.querySelector(`[data-erro="${controle.name}"]`);
    const vazio = !String(controle.value ?? '').trim();

    campoPai?.classList.toggle('invalido', vazio);
    if (erro) erro.textContent = vazio ? 'Este campo é obrigatório.' : '';

    if (vazio && valido) controle.focus();
    if (vazio) valido = false;
  });
  return valido;
}

/** Lê todos os controles nomeados do formulário. */
export function valoresFormulario(formulario) {
  const dados = {};
  new FormData(formulario).forEach((valor, chave) => {
    dados[chave] = typeof valor === 'string' ? valor.trim() : valor;
  });
  return dados;
}

export function limparErros(formulario) {
  formulario.querySelectorAll('.campo').forEach((campoEl) => campoEl.classList.remove('invalido'));
  formulario.querySelectorAll('.erro-campo').forEach((erro) => (erro.textContent = ''));
}
