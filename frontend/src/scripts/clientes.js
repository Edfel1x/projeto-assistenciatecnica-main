/* Gerenciamento de clientes: listar, pesquisar, criar, editar, consultar e excluir. */

import { api } from './api.js';
import { icone } from '../components/icons.js';
import { abrirModal, confirmar, fecharModal } from '../components/modal.js';
import { carregando, comCarregamento, estadoVazio } from '../components/loading.js';
import { escapeHtml, notificar } from '../components/notification.js';
import { renderizarTabela } from '../components/table.js';
import { campo, limparErros, validarFormulario, valoresFormulario } from './form.js';
import { filtrarItens } from './util.js';

let clientes = [];
let containerAtual = null;

function desenharTabela() {
  const termo = containerAtual.querySelector('#pesquisa-clientes')?.value || '';
  const itens = filtrarItens(clientes, termo, ['id_cliente', 'nome', 'telefone', 'email']);
  containerAtual.querySelector('#total-clientes').value = String(itens.length);

  containerAtual.querySelector('#lista-clientes').innerHTML = renderizarTabela({
    colunas: [
      { rotulo: 'ID', html: (item) => `<span class="mono">${item.id_cliente}</span>` },
      { rotulo: 'Nome', html: (item) => `<span class="negrito">${escapeHtml(item.nome)}</span>` },
      { rotulo: 'Telefone', html: (item) => escapeHtml(item.telefone) },
      { rotulo: 'E-mail', html: (item) => escapeHtml(item.email || '—') },
      {
        rotulo: 'Ações',
        classe: 'coluna-acoes',
        html: (item) => `
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="ver" data-id="${item.id_cliente}" title="Visualizar" aria-label="Visualizar cliente ${item.id_cliente}">${icone('olho')}</button>
          <button class="botao botao-icone botao-fantasma" type="button" data-acao="editar" data-id="${item.id_cliente}" title="Editar" aria-label="Editar cliente ${item.id_cliente}">${icone('editar')}</button>
          <button class="botao botao-icone botao-perigo" type="button" data-acao="excluir" data-id="${item.id_cliente}" title="Excluir" aria-label="Excluir cliente ${item.id_cliente}">${icone('lixeira')}</button>`,
      },
    ],
    itens,
    vazioTitulo: clientes.length ? 'Nenhum cliente encontrado' : 'Nenhum cliente cadastrado',
    vazioDescricao: clientes.length
      ? 'Tente outro termo de pesquisa.'
      : 'Use o botão “Novo cliente” para cadastrar o primeiro registro.',
  });
}

async function carregar() {
  const lista = containerAtual.querySelector('#lista-clientes');
  carregando(lista, 'Carregando clientes...');
  try {
    const resposta = await api.listarClientes();
    if (!containerAtual.isConnected) return; // navegação já trocou de página
    clientes = resposta.data || [];
    desenharTabela();
  } catch (erro) {
    lista.innerHTML = estadoVazio('Não foi possível carregar os clientes', erro.message, 'alerta');
    notificar('erro', erro.message, erro.detalhe);
  }
}

function abrirFormulario(cliente = null) {
  const edicao = Boolean(cliente);
  const modal = abrirModal({
    titulo: edicao ? 'Editar cliente' : 'Novo cliente',
    descricao: edicao ? `Registro #${cliente.id_cliente}` : 'Preencha os dados obrigatórios.',
    conteudo: `
      <form id="form-cliente" class="formulario-grid" novalidate>
        ${campo({ nome: 'nome', rotulo: 'Nome completo', valor: cliente?.nome || '', placeholder: 'Ex.: Maria Silva' })}
        ${campo({ nome: 'telefone', rotulo: 'Telefone', valor: cliente?.telefone || '', placeholder: 'Somente números' })}
        ${campo({ nome: 'email', rotulo: 'E-mail', tipo: 'email', valor: cliente?.email || '', obrigatorio: false, placeholder: 'opcional@exemplo.com', larga: true })}
      </form>`,
    rodape: `
      <button class="botao" type="button" data-fechar>Cancelar</button>
      <button class="botao botao-primario" type="submit" form="form-cliente">${edicao ? 'Salvar alterações' : 'Cadastrar'}</button>`,
  });
  if (!modal) return;

  const formulario = modal.querySelector('#form-cliente');
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
        edicao ? api.atualizarCliente(cliente.id_cliente, dados) : api.criarCliente(dados),
        edicao ? 'Salvando alterações...' : 'Cadastrando cliente...'
      );
      notificar('sucesso', edicao ? 'Cliente atualizado com sucesso.' : 'Cliente cadastrado com sucesso.');
      fecharModal();
      await carregar();
    } catch (erro) {
      notificar('erro', erro.message, erro.detalhe);
    }
  });
}

function abrirDetalhes(cliente) {
  abrirModal({
    titulo: `Cliente #${cliente.id_cliente}`,
    descricao: 'Dados cadastrados no sistema',
    conteudo: `
      <dl class="detalhes-grid">
        <div class="detalhe-item"><dt>Nome</dt><dd>${escapeHtml(cliente.nome)}</dd></div>
        <div class="detalhe-item"><dt>Telefone</dt><dd>${escapeHtml(cliente.telefone)}</dd></div>
        <div class="detalhe-item"><dt>E-mail</dt><dd>${escapeHtml(cliente.email || 'Não informado')}</dd></div>
      </dl>`,
    rodape: `<button class="botao botao-primario" type="button" data-fechar>Fechar</button>`,
  });
}

export async function renderizarClientes(container) {
  containerAtual = container;
  container.querySelector('#icone-novo-cliente').innerHTML = icone('mais');

  container.querySelector('#btn-novo-cliente').addEventListener('click', () => abrirFormulario());
  container.querySelector('#pesquisa-clientes').addEventListener('input', desenharTabela);

  container.querySelector('#lista-clientes').addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-acao]');
    if (!botao) return;
    const id = Number(botao.dataset.id);
    const cliente = clientes.find((item) => item.id_cliente === id);
    if (!cliente) return;

    if (botao.dataset.acao === 'ver') {
      abrirDetalhes(cliente);
    } else if (botao.dataset.acao === 'editar') {
      abrirFormulario(cliente);
    } else if (botao.dataset.acao === 'excluir') {
      const confirmado = await confirmar({
        titulo: 'Excluir cliente',
        mensagem: `Deseja realmente excluir "${cliente.nome}"? Clientes com vínculos não podem ser excluídos. Exclua antes os equipamentos e ordens nas telas correspondentes.`,
        rotuloConfirmar: 'Excluir',
        perigo: true,
      });
      if (!confirmado) return;
      try {
        await comCarregamento(api.excluirCliente(id), 'Excluindo cliente...');
        notificar('sucesso', 'Cliente excluído com sucesso.');
        await carregar();
      } catch (erro) {
        notificar('erro', erro.message, erro.detalhe);
      }
    }
  });

  await carregar();
}
