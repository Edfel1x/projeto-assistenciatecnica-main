/* Gerenciamento de técnicos: listar, pesquisar, criar, editar, consultar e excluir. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { abrirModal, confirmar, fecharModal } from '../components/modal.js';
import { carregando, comCarregamento, estadoVazio } from '../components/loading.js';
import { escapeHtml, notificar } from '../components/notification.js';
import { renderizarTabela } from '../components/table.js';
import { campo, limparErros, validarFormulario, valoresFormulario } from './form.js';
import { filtrarItens } from './util.js';

let tecnicos = [];
let containerAtual = null;

function desenharTabela() {
  const termo = containerAtual.querySelector('#pesquisa-tecnicos')?.value || '';
  const itens = filtrarItens(tecnicos, termo, ['id_tecnico', 'nome', 'especialidade', 'telefone']);
  containerAtual.querySelector('#total-tecnicos').value = String(itens.length);

  containerAtual.querySelector('#lista-tecnicos').innerHTML = renderizarTabela({
    colunas: [
      { rotulo: 'ID', html: (item) => `<span class="mono">${item.id_tecnico}</span>` },
      { rotulo: 'Nome', html: (item) => `<span class="negrito">${escapeHtml(item.nome)}</span>` },
      { rotulo: 'Especialidade', html: (item) => `<span class="badge badge-neutro">${escapeHtml(item.especialidade)}</span>` },
      { rotulo: 'Telefone', html: (item) => escapeHtml(item.telefone) },
      {
        rotulo: 'Ações',
        classe: 'coluna-acoes',
        html: (item) => `
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="ver" data-id="${item.id_tecnico}" title="Visualizar" aria-label="Visualizar técnico ${item.id_tecnico}">${icone('olho')}</button>
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="editar" data-id="${item.id_tecnico}" title="Editar" aria-label="Editar técnico ${item.id_tecnico}">${icone('editar')}</button>
          <button class="botao botao-icone botao-perigo" type="button" data-acao="excluir" data-id="${item.id_tecnico}" title="Excluir" aria-label="Excluir técnico ${item.id_tecnico}">${icone('lixeira')}</button>`,
      },
    ],
    itens,
    vazioTitulo: tecnicos.length ? 'Nenhum técnico encontrado' : 'Nenhum técnico cadastrado',
    vazioDescricao: tecnicos.length
      ? 'Tente outro termo de pesquisa.'
      : 'Use o botão “Novo técnico” para cadastrar o primeiro registro.',
  });
}

async function carregar() {
  const lista = containerAtual.querySelector('#lista-tecnicos');
  carregando(lista, 'Carregando técnicos...');
  try {
    const resposta = await api.listarTecnicos();
    if (!containerAtual.isConnected) return; // navegação já trocou de página
    tecnicos = resposta.data || [];
    desenharTabela();
  } catch (erro) {
    lista.innerHTML = estadoVazio('Não foi possível carregar os técnicos', erro.message, 'alerta');
    notificar('erro', erro.message, erro.detalhe);
  }
}

function abrirFormulario(tecnico = null) {
  const edicao = Boolean(tecnico);
  const modal = abrirModal({
    titulo: edicao ? 'Editar técnico' : 'Novo técnico',
    descricao: edicao ? `Registro #${tecnico.id_tecnico}` : 'Preencha os dados obrigatórios.',
    conteudo: `
      <form id="form-tecnico" class="formulario-grid" novalidate>
        ${campo({ nome: 'nome', rotulo: 'Nome completo', valor: tecnico?.nome || '', placeholder: 'Ex.: João Oliveira' })}
        ${campo({ nome: 'telefone', rotulo: 'Telefone', valor: tecnico?.telefone || '', placeholder: 'Somente números' })}
        ${campo({ nome: 'especialidade', rotulo: 'Especialidade', valor: tecnico?.especialidade || '', placeholder: 'Ex.: Eletrônica', larga: true })}
      </form>`,
    rodape: `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-primario" type="submit" form="form-tecnico">${edicao ? 'Salvar alterações' : 'Cadastrar'}</button>`,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-tecnico');
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
        edicao ? api.atualizarTecnico(tecnico.id_tecnico, dados) : api.criarTecnico(dados),
        edicao ? 'Salvando alterações...' : 'Cadastrando técnico...'
      );
      notificar('sucesso', edicao ? 'Técnico atualizado com sucesso.' : 'Técnico cadastrado com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

function abrirDetalhes(tecnico) {
  abrirModal({
    titulo: `Técnico #${tecnico.id_tecnico}`,
    descricao: 'Dados cadastrados no sistema',
    conteudo: `
      <dl class="detalhes-grid">
        <div class="detalhe-item"><dt>Nome</dt><dd>${escapeHtml(tecnico.nome)}</dd></div>
        <div class="detalhe-item"><dt>Telefone</dt><dd>${escapeHtml(tecnico.telefone)}</dd></div>
        <div class="detalhe-item"><dt>Especialidade</dt><dd>${escapeHtml(tecnico.especialidade)}</dd></div>
      </dl>`,
    rodape: `<button class="botao botao-primario" type="button" data-fechar>Fechar</button>`,
  });
}

export async function renderizarTecnicos(container) {
  containerAtual = container;
  container.querySelector('#icone-novo-tecnico').innerHTML = icone('mais');

  container.querySelector('#btn-novo-tecnico').addEventListener('click', () => abrirFormulario());
  container.querySelector('#pesquisa-tecnicos').addEventListener('input', desenharTabela);

  container.querySelector('#lista-tecnicos').addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-acao]');
    if (!botao) return;
    const id = Number(botao.dataset.id);
    const tecnico = tecnicos.find((item) => item.id_tecnico === id);
    if (!tecnico) return;

    if (botao.dataset.acao === 'ver') {
      abrirDetalhes(tecnico);
    } else if (botao.dataset.acao === 'editar') {
      abrirFormulario(tecnico);
    } else if (botao.dataset.acao === 'excluir') {
      const confirmado = await confirmar({
        titulo: 'Excluir técnico',
        mensagem: `Deseja realmente excluir "${tecnico.nome}"? Ordens concluídas vinculadas impedem a exclusão. Exclua-as em Ordens de Serviço primeiro.`,
        rotuloConfirmar: 'Excluir',
        perigo: true,
      });
      if (!confirmado) return;
      try {
        await comCarregamento(api.excluirTecnico(id), 'Excluindo técnico...');
        notificar('sucesso', 'Técnico excluído com sucesso.');
        await carregar();
      } catch (erro) {
        notificar('erro', erro.message, erro.detalhe);
      }
    }
  });

  await carregar();
}
