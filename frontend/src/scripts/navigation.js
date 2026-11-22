/* Roteamento simples por hash (#/dashboard, #/clientes etc.).
   Mantém a aplicação como SPA sem dependências externas. */

import { ITENS_NAVEGACAO } from '../components/sidebar.js';

const ROTAS_PADRAO = 'dashboard';

export function rotaAtual() {
  const bruto = window.location.hash.replace(/^#\/?/, '').split('/')[0];
  return ITENS_NAVEGACAO.some((item) => item.rota === bruto) ? bruto : ROTAS_PADRAO;
}

export function configurarNavegacao(aoMudar) {
  window.addEventListener('hashchange', () => aoMudar(rotaAtual()));
  if (!window.location.hash) {
    // replaceState NÃO dispara hashchange: evita renderizar o dashboard duas vezes.
    window.history.replaceState(null, '', `#/${ROTAS_PADRAO}`);
  }
  return rotaAtual();
}

export function metadadosPagina(rota) {
  const item = ITENS_NAVEGACAO.find((entrada) => entrada.rota === rota);
  const descricoes = {
    dashboard: 'Visão geral da assistência técnica',
    clientes: 'Cadastro e consulta de clientes',
    tecnicos: 'Equipe técnica e especialidades',
    equipamentos: 'Aparelhos registrados e seus proprietários',
    ordens: 'Acompanhamento do ciclo de atendimento',
    configuracoes: 'Preferências e conexão da aplicação',
  };
  return {
    titulo: item?.rotulo || 'Dashboard',
    descricao: descricoes[rota] || descricoes.dashboard,
  };
}
