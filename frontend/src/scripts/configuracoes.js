/* Página de configurações: tema e verificação de conexão com a API. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { notificar } from '../components/notification.js';
import { aplicarTema, temaAtual } from './theme.js';
import { atualizarBotaoTema } from '../components/header.js';

export function renderizarConfiguracoes(container) {
  const base = import.meta.env.VITE_API_URL || '/api (proxy do Vite)';
  container.querySelector('#api-base').textContent = base;

  container.querySelectorAll('[data-tema]').forEach((botao) => {
    botao.addEventListener('click', () => {
      aplicarTema(botao.dataset.tema);
      atualizarBotaoTema(temaAtual());
      notificar('sucesso', `Tema ${botao.dataset.tema} aplicado.`);
    });
  });

  container.querySelector('#btn-testar-api').addEventListener('click', async (evento) => {
    const botao = evento.currentTarget;
    botao.innerHTML = '<span class="spinner"></span> Testando...';
    botao.disabled = true;
    try {
      const resposta = await api.verificarSaude();
      notificar('sucesso', resposta.message || 'API respondeu corretamente.');
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    } finally {
      botao.innerHTML = `${icone('atualizar')} Testar conexão`;
      botao.disabled = false;
    }
  });
}
