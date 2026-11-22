/* Gerenciamento de equipamentos com seleção de cliente vinda da API. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { abrirModal, confirmar, fecharModal } from '../components/modal.js';
import { carregando, comCarregamento, estadoVazio } from '../components/loading.js';
import { escapeHtml, notificar } from '../components/notification.js';
import { renderizarTabela } from '../components/table.js';
import { campo, limparErros, validarFormulario, valoresFormulario } from './form.js';
import { badgeStatusEquipamento, filtrarItens } from './util.js';

// Mantido em sincronia com o ENUM de schema.sql e com equipamentos_service.py.
const STATUS_EQUIPAMENTO = [
  'Disponível',
  'Em análise',
  'Em manutenção',
  'Aguardando peça',
  'Pronto para entrega',
  'Entregue',
];
const STATUS_PADRAO = 'Disponível';

let equipamentos = [];
let clientes = [];
let containerAtual = null;

function opcoesStatus() {
  return STATUS_EQUIPAMENTO.map((status) => ({ valor: status, rotulo: status }));
}

function desenharTabela() {
  const termo = containerAtual.querySelector('#pesquisa-equipamentos')?.value || '';
  const status = containerAtual.querySelector('#filtro-status-equipamento')?.value || '';
  let itens = filtrarItens(equipamentos, termo, [
    'id_equipamento', 'tipo', 'marca', 'modelo', 'numero_serie', 'nome_cliente', 'diagnostico',
  ]);
  if (status) itens = itens.filter((item) => item.status === status);
  containerAtual.querySelector('#total-equipamentos').value = String(itens.length);

  containerAtual.querySelector('#lista-equipamentos').innerHTML = renderizarTabela({
    colunas: [
      { rotulo: 'ID', html: (item) => `<span class="mono">${item.id_equipamento}</span>` },
      {
        rotulo: 'Equipamento',
        html: (item) => `<span class="negrito">${escapeHtml(item.tipo)} ${escapeHtml(item.marca)}</span><br /><span class="texto-secundario">${escapeHtml(item.modelo)}</span>`,
      },
      { rotulo: 'Status', html: (item) => badgeStatusEquipamento(item.status) },
      { rotulo: 'Nº de série', html: (item) => `<span class="mono">${escapeHtml(item.numero_serie)}</span>` },
      { rotulo: 'Cliente', html: (item) => escapeHtml(item.nome_cliente) },
      {
        rotulo: 'Ações',
        classe: 'coluna-acoes',
        html: (item) => `
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="situacao" data-id="${item.id_equipamento}" title="Status e diagnóstico" aria-label="Status e diagnóstico do equipamento ${item.id_equipamento}">${icone('atualizar')}</button>
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="ver" data-id="${item.id_equipamento}" title="Visualizar" aria-label="Visualizar equipamento ${item.id_equipamento}">${icone('olho')}</button>
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="editar" data-id="${item.id_equipamento}" title="Editar" aria-label="Editar equipamento ${item.id_equipamento}">${icone('editar')}</button>
          <button class="botao botao-icone botao-perigo" type="button" data-acao="excluir" data-id="${item.id_equipamento}" title="Excluir" aria-label="Excluir equipamento ${item.id_equipamento}">${icone('lixeira')}</button>`,
      },
    ],
    itens,
    vazioTitulo: equipamentos.length ? 'Nenhum equipamento encontrado' : 'Nenhum equipamento cadastrado',
    vazioDescricao: equipamentos.length
      ? 'Tente outro termo ou status de pesquisa.'
      : 'Cadastre um cliente antes de registrar equipamentos.',
  });
}

async function carregar() {
  const lista = containerAtual.querySelector('#lista-equipamentos');
  carregando(lista, 'Carregando equipamentos...');
  try {
    const [respostaEquipamentos, respostaClientes] = await Promise.all([
      api.listarEquipamentos(),
      api.listarClientes(),
    ]);
    if (!containerAtual.isConnected) return; // navegação já trocou de página
    equipamentos = respostaEquipamentos.data || [];
    clientes = respostaClientes.data || [];
    desenharTabela();
  } catch (erro) {
    lista.innerHTML = estadoVazio('Não foi possível carregar os equipamentos', erro.message, 'alerta');
    notificar('erro', erro.message, erro.detalhe);
  }
}

function abrirFormulario(equipamento = null) {
  const edicao = Boolean(equipamento);
  if (!clientes.length) {
    notificar('aviso', 'Cadastre ao menos um cliente antes de criar um equipamento.');
    return;
  }

  const opcoesClientes = clientes.map((cliente) => ({
    valor: cliente.id_cliente,
    rotulo: `#${cliente.id_cliente} — ${cliente.nome}`,
  }));

  const modal = abrirModal({
    titulo: edicao ? 'Editar equipamento' : 'Novo equipamento',
    descricao: edicao ? `Registro #${equipamento.id_equipamento}` : 'O proprietário é obrigatório no banco de dados.',
    conteudo: `
      <form id="form-equipamento" class="formulario-grid" novalidate>
        ${campo({ nome: 'id_cliente', rotulo: 'Cliente proprietário', tipo: 'select', valor: equipamento?.id_cliente || '', opcoes: opcoesClientes })}
        ${campo({ nome: 'tipo', rotulo: 'Tipo', valor: equipamento?.tipo || '', placeholder: 'Ex.: Notebook' })}
        ${campo({ nome: 'marca', rotulo: 'Marca', valor: equipamento?.marca || '', placeholder: 'Ex.: Dell' })}
        ${campo({ nome: 'modelo', rotulo: 'Modelo', valor: equipamento?.modelo || '', placeholder: 'Ex.: Latitude 5420' })}
        ${campo({ nome: 'numero_serie', rotulo: 'Número de série', valor: equipamento?.numero_serie || '', placeholder: 'Ex.: ABC123456', larga: true })}
      </form>`,
    rodape: `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-primario" type="submit" form="form-equipamento">${edicao ? 'Salvar alterações' : 'Cadastrar'}</button>`,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-equipamento');
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparErros(formulario);
    if (!validarFormulario(formulario)) {
      notificar('aviso', 'Verifique os campos destacados.');
      return;
    }
    const dados = valoresFormulario(formulario);
    dados.id_cliente = Number(dados.id_cliente);
    try {
      await comCarregamento(
        edicao ? api.atualizarEquipamento(equipamento.id_equipamento, dados) : api.criarEquipamento(dados),
        edicao ? 'Salvando alterações...' : 'Cadastrando equipamento...'
      );
      notificar('sucesso', edicao ? 'Equipamento atualizado com sucesso.' : 'Equipamento cadastrado com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

/** Modal específico para acompanhar a situação do aparelho na oficina. */
async function abrirSituacao(equipamento) {
  let ordensRelacionadas = [];
  try {
    const resposta = await comCarregamento(api.listarOrdens(), 'Carregando histórico do equipamento...');
    ordensRelacionadas = (resposta.data || []).filter(
      (ordem) => ordem.id_equipamento === equipamento.id_equipamento
    );
  } catch (erro) {
    notificar('aviso', 'Histórico indisponível; você ainda pode salvar o diagnóstico.', erro.message);
  }

  const recente = ordensRelacionadas[0]; // a API devolve da mais recente para a mais antiga
  const historico = recente
    ? `<div class="historico-defeito">
         <h4>Ordem #${recente.id_ordem} — defeito relatado</h4>
         <p><strong>Defeito:</strong> ${escapeHtml(recente.defeito_relatado || '—')}</p>
         <p><strong>Diagnóstico registrado na ordem:</strong> ${escapeHtml(recente.diagnostico || '—')}</p>
       </div>`
    : '<p class="campo-ajuda">Nenhuma ordem de serviço vinculada a este equipamento.</p>';

  const modal = abrirModal({
    titulo: `Status e diagnóstico — #${equipamento.id_equipamento}`,
    descricao: `${equipamento.tipo} ${equipamento.marca} ${equipamento.modelo} · ${equipamento.nome_cliente}`,
    grande: true,
    conteudo: `
      <form id="form-situacao" class="formulario-grid" novalidate>
        ${campo({
          nome: 'status', rotulo: 'Status do equipamento', tipo: 'select',
          valor: equipamento.status || STATUS_PADRAO, opcoes: opcoesStatus(),
        })}
        ${campo({
          nome: 'diagnostico', rotulo: 'Diagnóstico do defeito', tipo: 'textarea',
          valor: equipamento.diagnostico || '', obrigatorio: false, larga: true,
          placeholder: 'Ex.: Placa de alimentação em curto; aguardando peça.',
        })}
        <p class="campo-ajuda">O diagnóstico fica no equipamento e pode ser atualizado quantas vezes for necessário. Deixe em branco para apagar.</p>
        ${historico}
      </form>`,
    rodape: `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-primario" type="submit" form="form-situacao">Salvar situação</button>`,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-situacao');
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparErros(formulario);
    if (!validarFormulario(formulario)) {
      notificar('aviso', 'Verifique os campos destacados.');
      return;
    }
    const dados = valoresFormulario(formulario);
    try {
      await comCarregamento(
        api.atualizarSituacaoEquipamento(equipamento.id_equipamento, dados),
        'Salvando situação...'
      );
      notificar('sucesso', 'Status e diagnóstico atualizados com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

function abrirDetalhes(equipamento) {
  abrirModal({
    titulo: `Equipamento #${equipamento.id_equipamento}`,
    descricao: 'Dados cadastrados no sistema',
    conteudo: `
      <dl class="detalhes-grid">
        <div class="detalhe-item"><dt>Tipo</dt><dd>${escapeHtml(equipamento.tipo)}</dd></div>
        <div class="detalhe-item"><dt>Marca</dt><dd>${escapeHtml(equipamento.marca)}</dd></div>
        <div class="detalhe-item"><dt>Modelo</dt><dd>${escapeHtml(equipamento.modelo)}</dd></div>
        <div class="detalhe-item"><dt>Número de série</dt><dd>${escapeHtml(equipamento.numero_serie)}</dd></div>
        <div class="detalhe-item"><dt>Cliente</dt><dd>${escapeHtml(equipamento.nome_cliente)}</dd></div>
        <div class="detalhe-item"><dt>ID do cliente</dt><dd>${equipamento.id_cliente}</dd></div>
        <div class="detalhe-item"><dt>Status</dt><dd>${badgeStatusEquipamento(equipamento.status)}</dd></div>
        <div class="detalhe-item campo-largo"><dt>Diagnóstico</dt><dd>${escapeHtml(equipamento.diagnostico || '—')}</dd></div>
      </dl>`,
    rodape: `<button class="botao botao-primario" type="button" data-fechar>Fechar</button>`,
  });
}

export async function renderizarEquipamentos(container) {
  containerAtual = container;
  container.querySelector('#icone-novo-equipamento').innerHTML = icone('mais');

  const filtroStatus = container.querySelector('#filtro-status-equipamento');
  filtroStatus.innerHTML = '<option value="">Todos</option>' + STATUS_EQUIPAMENTO
    .map((status) => `<option value="${status}">${status}</option>`)
    .join('');
  filtroStatus.addEventListener('change', desenharTabela);

  container.querySelector('#btn-novo-equipamento').addEventListener('click', () => abrirFormulario());
  container.querySelector('#pesquisa-equipamentos').addEventListener('input', desenharTabela);

  container.querySelector('#lista-equipamentos').addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-acao]');
    if (!botao) return;
    const id = Number(botao.dataset.id);
    const equipamento = equipamentos.find((item) => item.id_equipamento === id);
    if (!equipamento) return;

    if (botao.dataset.acao === 'situacao') {
      await abrirSituacao(equipamento);
    } else if (botao.dataset.acao === 'ver') {
      abrirDetalhes(equipamento);
    } else if (botao.dataset.acao === 'editar') {
      abrirFormulario(equipamento);
    } else if (botao.dataset.acao === 'excluir') {
      const confirmado = await confirmar({
        titulo: 'Excluir equipamento',
        mensagem: `Deseja excluir o equipamento #${id}? Registros com ordens de serviço vinculadas não podem ser excluídos.`,
        rotuloConfirmar: 'Excluir',
        perigo: true,
      });
      if (!confirmado) return;
      try {
        await comCarregamento(api.excluirEquipamento(id), 'Excluindo equipamento...');
        notificar('sucesso', 'Equipamento excluído com sucesso.');
        await carregar();
      } catch (erro) {
        notificar('erro', erro.message, erro.detalhe);
      }
    }
  });

  await carregar();
}
