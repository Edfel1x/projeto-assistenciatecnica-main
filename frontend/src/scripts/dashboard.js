/* Tela inicial: indicadores e ordens recentes obtidos de GET /api/dashboard. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { carregando, estadoVazio } from '../components/loading.js';
import { escapeHtml, notificar } from '../components/notification.js';
import { renderizarTabela } from '../components/table.js';
import { badgeStatus, formatarData, formatarMoeda } from './util.js';

const INDICADORES = [
  { chave: 'total_clientes', titulo: 'Clientes cadastrados', icone: 'clientes', cor: '' },
  { chave: 'total_tecnicos', titulo: 'Técnicos cadastrados', icone: 'tecnicos', cor: '' },
  { chave: 'total_equipamentos', titulo: 'Equipamentos registrados', icone: 'equipamentos', cor: '' },
  { chave: 'total_ordens', titulo: 'Ordens de serviço', icone: 'ordens', cor: '' },
  { chave: 'ordens_em_andamento', titulo: 'Em andamento', icone: 'relogio', cor: 'cor-info' },
  { chave: 'ordens_finalizadas', titulo: 'Finalizadas', icone: 'check', cor: 'cor-sucesso' },
  { chave: 'ordens_pendentes', titulo: 'Pendentes (Abertas)', icone: 'alerta', cor: 'cor-aviso' },
  { chave: 'ordens_canceladas', titulo: 'Canceladas', icone: 'fechar', cor: 'cor-perigo' },
];

const STATUS_GRAFICO = [
  { chave: 'Aberta', rotulo: 'Aberta' },
  { chave: 'Em manutenção', rotulo: 'Em manutenção' },
  { chave: 'Concluída', rotulo: 'Concluída' },
  { chave: 'Cancelada', rotulo: 'Cancelada' },
];

export async function renderizarDashboard(container) {
  container.querySelector('#icone-atualizar').innerHTML = icone('atualizar');
  const cards = container.querySelector('#cards-dashboard');
  const grafico = container.querySelector('#grafico-status');
  const recentes = container.querySelector('#ordens-recentes');

  carregando(cards, 'Carregando indicadores...');
  recentes.innerHTML = '';
  grafico.innerHTML = '';

  container.querySelector('#btn-atualizar-dashboard').addEventListener('click', () => carregar());

  async function carregar() {
    carregando(cards, 'Carregando indicadores...');
    try {
      const resposta = await api.buscarDashboard();
      const dados = resposta.data || {};

      cards.innerHTML = INDICADORES.map(
        (indicador) => `
        <article class="card card-indicador card-destaque ${indicador.cor}">
          <div class="indicador-topo">
            <div class="indicador-icone">${icone(indicador.icone)}</div>
          </div>
          <div class="indicador-valor">${Number(dados[indicador.chave] ?? 0)}</div>
          <div class="indicador-titulo">${indicador.titulo}</div>
        </article>`
      ).join('');

      const porStatus = dados.ordens_por_status || {};
      const maior = Math.max(1, ...Object.values(porStatus).map(Number));
      grafico.innerHTML = `
        <div class="grafico-barras">
          ${STATUS_GRAFICO.map((status) => {
            const quantidade = Number(porStatus[status.chave] || 0);
            const altura = Math.max(4, Math.round((quantidade / maior) * 100));
            return `
            <div class="grafico-barra" title="${status.rotulo}: ${quantidade}">
              <span class="valor">${quantidade}</span>
              <div class="barra" style="height:${altura}%"></div>
              <span class="legenda">${status.rotulo}</span>
            </div>`;
          }).join('')}
        </div>`;

      const ordens = dados.ordens_recentes || [];
      recentes.innerHTML = renderizarTabela({
        colunas: [
          { rotulo: 'Ordem', html: (item) => `<span class="mono">#${item.id_ordem}</span>` },
          { rotulo: 'Cliente', html: (item) => `<span class="truncar" title="${escapeHtml(item.nome_cliente)}">${escapeHtml(item.nome_cliente)}</span>` },
          { rotulo: 'Equipamento', html: (item) => `${escapeHtml(item.tipo_equipamento)} ${escapeHtml(item.marca_equipamento)}` },
          { rotulo: 'Defeito', html: (item) => `<span class="truncar" title="${escapeHtml(item.defeito_relatado)}">${escapeHtml(item.defeito_relatado)}</span>` },
          { rotulo: 'Status', html: (item) => badgeStatus(item.status) },
          { rotulo: 'Abertura', html: (item) => formatarData(item.data_abertura) },
        ],
        itens: ordens,
        vazioTitulo: 'Nenhuma ordem registrada',
        vazioDescricao: 'As ordens abertas aparecerão aqui automaticamente.',
      });
    } catch (erro) {
      cards.innerHTML = estadoVazio('Não foi possível carregar os indicadores', erro.message, 'alerta');
      grafico.innerHTML = '';
      recentes.innerHTML = '';
      notificar('erro', erro.message, erro.detalhe);
    }
  }

  await carregar();
}
