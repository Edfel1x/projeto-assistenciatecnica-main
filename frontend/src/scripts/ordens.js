/* Ordens de serviço: filtros, abertura, detalhamento e ciclo de vida completo.
   Todas as operações passam pela API, que aplica as regras de negócio do Python. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { abrirModal, confirmar, fecharModal } from '../components/modal.js';
import { carregando, comCarregamento, estadoVazio } from '../components/loading.js';
import { escapeHtml, notificar } from '../components/notification.js';
import { renderizarTabela } from '../components/table.js';
import { campo, limparErros, validarFormulario, valoresFormulario } from './form.js';
import { badgeStatus, filtrarItens, formatarData, formatarMoeda } from './util.js';

let ordens = [];
let tecnicos = [];
let equipamentos = [];
let containerAtual = null;

const ENCERRADAS = ['Concluída', 'Cancelada'];

function ordenEncerrada(ordem) {
  return ENCERRADAS.includes(ordem.status);
}

function aplicarFiltros() {
  const id = containerAtual.querySelector('#filtro-id-ordem').value.trim();
  const status = containerAtual.querySelector('#filtro-status-ordem').value;
  const idTecnico = containerAtual.querySelector('#filtro-tecnico-ordem').value;
  const texto = containerAtual.querySelector('#filtro-texto-ordem').value;

  let itens = ordens;
  if (id) itens = itens.filter((ordem) => String(ordem.id_ordem).includes(id));
  if (status) itens = itens.filter((ordem) => ordem.status === status);
  if (idTecnico) {
    itens = itens.filter((ordem) => String(ordem.id_tecnico) === idTecnico);
  }
  if (texto) {
    itens = filtrarItens(itens, texto, [
      'nome_cliente', 'tipo_equipamento', 'marca_equipamento',
      'modelo_equipamento', 'numero_serie', 'defeito_relatado', 'nome_tecnico',
    ]);
  }
  return itens;
}

function desenharTabela() {
  const itens = aplicarFiltros();
  containerAtual.querySelector('#lista-ordens').innerHTML = renderizarTabela({
    colunas: [
      { rotulo: 'Ordem', html: (item) => `<span class="mono">#${item.id_ordem}</span>` },
      {
        rotulo: 'Equipamento / cliente',
        html: (item) => `<span class="negrito">${escapeHtml(item.tipo_equipamento)} ${escapeHtml(item.marca_equipamento)}</span><br /><span class="texto-secundario">${escapeHtml(item.nome_cliente)}</span>`,
      },
      {
        rotulo: 'Defeito relatado',
        html: (item) => `<span class="truncar" title="${escapeHtml(item.defeito_relatado)}">${escapeHtml(item.defeito_relatado)}</span>`,
      },
      { rotulo: 'Técnico', html: (item) => escapeHtml(item.nome_tecnico || 'Não atribuído') },
      { rotulo: 'Status', html: (item) => badgeStatus(item.status) },
      {
        rotulo: 'Valor',
        html: (item) => item.valor_servico === null ? '—' : formatarMoeda(item.valor_servico),
      },
      { rotulo: 'Abertura', html: (item) => formatarData(item.data_abertura) },
      {
        rotulo: 'Ações',
        classe: 'coluna-acoes',
        html: (item) => `
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="ver" data-id="${item.id_ordem}" title="Detalhes" aria-label="Detalhes da ordem ${item.id_ordem}">${icone('olho')}</button>
          <button class="botao botao-icone botao-perigo" type="button" data-acao="excluir" data-id="${item.id_ordem}" title="Excluir" aria-label="Excluir ordem ${item.id_ordem}">${icone('lixeira')}</button>`,
      },
    ],
    itens,
    vazioTitulo: ordens.length ? 'Nenhuma ordem encontrada com esses filtros' : 'Nenhuma ordem de serviço aberta',
    vazioDescricao: ordens.length
      ? 'Ajuste os filtros para ver mais resultados.'
      : 'Cadastre um equipamento e abra a primeira ordem de serviço.',
  });
}

async function carregar() {
  const lista = containerAtual.querySelector('#lista-ordens');
  carregando(lista, 'Carregando ordens de serviço...');
  try {
    const [respostaOrdens, respostaTecnicos, respostaEquipamentos] = await Promise.all([
      api.listarOrdens(),
      api.listarTecnicos(),
      api.listarEquipamentos(),
    ]);
    if (!containerAtual.isConnected) return; // navegação já trocou de página
    ordens = respostaOrdens.data || [];
    tecnicos = respostaTecnicos.data || [];
    equipamentos = respostaEquipamentos.data || [];

    const select = containerAtual.querySelector('#filtro-tecnico-ordem');
    const selecionado = select.value;
    select.innerHTML = '<option value="">Todos</option>' + tecnicos
      .map((tecnico) => `<option value="${tecnico.id_tecnico}">${escapeHtml(tecnico.nome)}</option>`)
      .join('');
    select.value = selecionado;

    desenharTabela();
  } catch (erro) {
    lista.innerHTML = estadoVazio('Não foi possível carregar as ordens', erro.message, 'alerta');
    notificar('erro', erro.message, erro.detalhe);
  }
}

function abrirNovaOrdem() {
  if (!equipamentos.length) {
    notificar('aviso', 'Cadastre ao menos um equipamento antes de abrir uma ordem.');
    return;
  }
  const opcoes = equipamentos.map((equipamento) => ({
    valor: equipamento.id_equipamento,
    rotulo: `#${equipamento.id_equipamento} — ${equipamento.tipo} ${equipamento.marca} ${equipamento.modelo} (${equipamento.nome_cliente})`,
  }));
  const opcoesTecnicos = tecnicos.map((tecnico) => ({
    valor: tecnico.id_tecnico,
    rotulo: `#${tecnico.id_tecnico} — ${tecnico.nome} (${tecnico.especialidade})`,
  }));

  const modal = abrirModal({
    titulo: 'Abrir ordem de serviço',
    descricao: 'Escolha o equipamento e, se quiser, o técnico responsável.',
    conteudo: `
      <form id="form-ordem" class="formulario-grid" novalidate>
        ${campo({ nome: 'id_equipamento', rotulo: 'Equipamento', tipo: 'select', opcoes, larga: true })}
        ${campo({
          nome: 'id_tecnico', rotulo: 'Técnico responsável (opcional)', tipo: 'select',
          obrigatorio: false, opcoes: opcoesTecnicos, larga: true,
        })}
        <p class="campo-ajuda">Você pode designar o técnico agora ou depois, em Detalhes → Atribuir técnico.</p>
        ${campo({ nome: 'defeito_relatado', rotulo: 'Defeito relatado', tipo: 'textarea', placeholder: 'Descreva o problema informado pelo cliente', larga: true })}
      </form>`,
    rodape: `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-primario" type="submit" form="form-ordem">Abrir ordem</button>`,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-ordem');
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparErros(formulario);
    if (!validarFormulario(formulario)) {
      notificar('aviso', 'Verifique os campos destacados.');
      return;
    }
    const dados = valoresFormulario(formulario);
    dados.id_equipamento = Number(dados.id_equipamento);
    if (dados.id_tecnico) dados.id_tecnico = Number(dados.id_tecnico);
    else delete dados.id_tecnico;
    try {
      const resposta = await comCarregamento(api.criarOrdem(dados), 'Abrindo ordem...');
      notificar('sucesso', resposta.message || 'Ordem de serviço aberta com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

function abrirAcao(acao, ordem) {
  const titulos = {
    diagnostico: 'Atualizar diagnóstico',
    tecnico: 'Atribuir técnico',
    status: 'Atualizar status',
    finalizar: 'Finalizar ordem',
  };
  let conteudo = '';
  let rodape = `
    <button class="botao" type="button" data-fechar>Cancelar</button>
    <button class="botao botao-primario" type="submit" form="form-acao">Confirmar</button>`;

  if (acao === 'diagnostico') {
    conteudo = `<form id="form-acao" class="formulario-grid" novalidate>
      ${campo({ nome: 'diagnostico', rotulo: 'Diagnóstico técnico', tipo: 'textarea', valor: ordem.diagnostico || '', placeholder: 'Descreva a causa identificada', larga: true })}
    </form>`;
  } else if (acao === 'tecnico') {
    const opcoes = tecnicos.map((tecnico) => ({
      valor: tecnico.id_tecnico,
      rotulo: `${tecnico.nome} — ${tecnico.especialidade}`,
    }));
    conteudo = `<form id="form-acao" class="formulario-grid" novalidate>
      ${campo({ nome: 'id_tecnico', rotulo: 'Técnico responsável', tipo: 'select', valor: ordem.id_tecnico || '', opcoes, larga: true })}
    </form>`;
  } else if (acao === 'status') {
    conteudo = `<form id="form-acao" class="formulario-grid" novalidate>
      ${campo({
        nome: 'status', rotulo: 'Novo status', tipo: 'select', valor: ordem.status, larga: true,
        opcoes: [
          { valor: 'Aberta', rotulo: 'Aberta' },
          { valor: 'Em manutenção', rotulo: 'Em manutenção' },
        ],
      })}
    </form>`;
  } else if (acao === 'finalizar') {
    rodape = `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-sucesso" type="submit" form="form-acao">Finalizar ordem</button>`;
    conteudo = `<form id="form-acao" class="formulario-grid" novalidate>
      ${campo({ nome: 'valor_servico', rotulo: 'Valor do serviço (R$)', tipo: 'number', placeholder: 'Ex.: 150.00', larga: true, atributos: 'step="0.01" min="0"' })}
      <p class="texto-secundario campo-largo" style="font-size:.82rem">
        A finalização exige técnico atribuído e diagnóstico registrado.
      </p>
    </form>`;
  }

  const modal = abrirModal({
    titulo: titulos[acao],
    descricao: `Ordem #${ordem.id_ordem} — ${ordem.status}`,
    conteudo,
    rodape,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-acao');
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparErros(formulario);
    if (!validarFormulario(formulario)) {
      notificar('aviso', 'Verifique os campos destacados.');
      return;
    }

    const dados = valoresFormulario(formulario);
    const mensagens = {
      diagnostico: 'Salvar o novo diagnóstico?',
      tecnico: 'Alterar o técnico responsável por esta ordem?',
      status: 'Alterar o status desta ordem?',
      finalizar: 'Finalizar esta ordem? Ela não poderá mais ser alterada.',
    };
    const confirmado = await confirmar({
      titulo: `Confirmar: ${titulos[acao]}`,
      mensagem: mensagens[acao],
      rotuloConfirmar: 'Confirmar',
      perigo: acao === 'finalizar',
    });
    if (!confirmado) return;

    try {
      const chamadas = {
        diagnostico: api.atualizarDiagnostico(ordem.id_ordem, dados),
        tecnico: api.atribuirTecnico(ordem.id_ordem, { id_tecnico: Number(dados.id_tecnico) }),
        status: api.atualizarStatus(ordem.id_ordem, dados),
        finalizar: api.finalizarOrdem(ordem.id_ordem, { valor_servico: dados.valor_servico }),
      };
      const resposta = await comCarregamento(chamadas[acao], 'Processando operação...');
      notificar('sucesso', resposta.message || 'Operação realizada com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

function abrirDetalhes(ordem) {
  const encerrada = ordenEncerrada(ordem);
  const botoes = encerrada
    ? '<p class="texto-secundario">Esta ordem foi encerrada. Nenhuma alteração é permitida.</p>'
    : `
      <div class="formulario-grid">
        <button class="botao" type="button" data-acao-modal="diagnostico">${icone('editar')} Diagnóstico</button>
        <button class="botao" type="button" data-acao-modal="tecnico">${icone('tecnicos')} Atribuir técnico</button>
        <button class="botao" type="button" data-acao-modal="status">${icone('atualizar')} Status</button>
        <button class="botao botao-sucesso" type="button" data-acao-modal="finalizar">${icone('check')} Finalizar</button>
      </div>
      <div style="margin-top:.75rem">
        <button class="botao botao-perigo" type="button" data-acao-modal="cancelar">${icone('fechar')} Cancelar ordem</button>
      </div>`;

  const modal = abrirModal({
    titulo: `Ordem de serviço #${ordem.id_ordem}`,
    descricao: `Aberta em ${formatarData(ordem.data_abertura)}`,
    grande: true,
    conteudo: `
      <div style="margin-bottom:1rem">${badgeStatus(ordem.status)}</div>
      <dl class="detalhes-grid">
        <div class="detalhe-item"><dt>Cliente</dt><dd>${escapeHtml(ordem.nome_cliente)}</dd></div>
        <div class="detalhe-item"><dt>Telefone</dt><dd>${escapeHtml(ordem.telefone_cliente || '—')}</dd></div>
        <div class="detalhe-item"><dt>Tipo</dt><dd>${escapeHtml(ordem.tipo_equipamento)}</dd></div>
        <div class="detalhe-item"><dt>Marca / modelo</dt><dd>${escapeHtml(ordem.marca_equipamento)} ${escapeHtml(ordem.modelo_equipamento)}</dd></div>
        <div class="detalhe-item"><dt>Nº de série</dt><dd>${escapeHtml(ordem.numero_serie || '—')}</dd></div>
        <div class="detalhe-item"><dt>Técnico</dt><dd>${escapeHtml(ordem.nome_tecnico || 'Não atribuído')}</dd></div>
        <div class="detalhe-item"><dt>Valor do serviço</dt><dd>${ordem.valor_servico === null ? '—' : formatarMoeda(ordem.valor_servico)}</dd></div>
        <div class="detalhe-item"><dt>Conclusão</dt><dd>${formatarData(ordem.data_conclusao)}</dd></div>
        <div class="detalhe-item campo-largo"><dt>Defeito relatado</dt><dd>${escapeHtml(ordem.defeito_relatado)}</dd></div>
        <div class="detalhe-item campo-largo"><dt>Diagnóstico</dt><dd>${escapeHtml(ordem.diagnostico || 'Não registrado')}</dd></div>
        <div class="detalhe-item campo-largo"><dt>Serviço realizado</dt><dd>${escapeHtml(ordem.servico_realizado || 'Não informado')}</dd></div>
      </dl>
      <section class="accao-bloco">
        <h4>Operações disponíveis</h4>
        ${botoes}
      </section>`,
    rodape: `<button class="botao botao-primario" type="button" data-fechar>Fechar</button>`,
  });
  if (!modal) return;

  modal.querySelectorAll('[data-acao-modal]').forEach((botao) => {
    botao.addEventListener('click', async () => {
      const acao = botao.dataset.acaoModal;
      if (acao === 'cancelar') {
        const confirmado = await confirmar({
          titulo: 'Cancelar ordem de serviço',
          mensagem: `Deseja cancelar a ordem #${ordem.id_ordem}? Esta ação não pode ser desfeita.`,
          rotuloConfirmar: 'Cancelar ordem',
          perigo: true,
        });
        if (!confirmado) return;
        try {
          const resposta = await comCarregamento(api.cancelarOrdem(ordem.id_ordem), 'Cancelando ordem...');
          notificar('sucesso', resposta.message || 'Ordem cancelada com sucesso.');
          fecharModal();
          await carregar();
        } catch (erro) {
          notificar('erro', erro.message, erro.detalhe);
        }
        return;
      }
      fecharModal();
      abrirAcao(acao, ordem);
    });
  });
}

export async function renderizarOrdens(container) {
  containerAtual = container;
  container.querySelector('#icone-nova-ordem').innerHTML = icone('mais');

  container.querySelector('#btn-nova-ordem').addEventListener('click', abrirNovaOrdem);
  ['#filtro-id-ordem', '#filtro-status-ordem', '#filtro-tecnico-ordem', '#filtro-texto-ordem']
    .forEach((seletor) => container.querySelector(seletor).addEventListener('input', desenharTabela));

  container.querySelector('#lista-ordens').addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-acao]');
    if (!botao) return;
    const ordem = ordens.find((item) => item.id_ordem === Number(botao.dataset.id));
    if (!ordem) return;

    if (botao.dataset.acao === 'ver') {
      abrirDetalhes(ordem);
    } else if (botao.dataset.acao === 'excluir') {
      const confirmado = await confirmar({
        titulo: 'Excluir ordem de serviço',
        mensagem: `Deseja excluir a ordem #${ordem.id_ordem}? Isso libera o equipamento e o técnico vinculados e não pode ser desfeito.`,
        rotuloConfirmar: 'Excluir',
        perigo: true,
      });
      if (!confirmado) return;
      try {
        await comCarregamento(api.excluirOrdem(ordem.id_ordem), 'Excluindo ordem...');
        notificar('sucesso', 'Ordem excluída com sucesso.');
        await carregar();
      } catch (erro) {
        notificar('erro', erro.message, erro.detalhe);
      }
    }
  });

  await carregar();
}
