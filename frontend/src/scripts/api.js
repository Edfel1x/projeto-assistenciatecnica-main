/* Camada única de comunicação com a API REST.
   Nenhuma credencial de banco fica no frontend. A URL base vem de
   VITE_API_URL (.env do frontend) ou, por padrão, do proxy do Vite (/api). */

const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, status, detalhe) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detalhe = detalhe;
  }
}

async function requisitar(caminho, opcoes = {}) {
  let resposta;
  try {
    resposta = await fetch(`${API_BASE}${caminho}`, {
      ...opcoes,
      headers: {
        ...(opcoes.body ? { 'Content-Type': 'application/json' } : {}),
        ...(opcoes.headers || {}),
      },
    });
  } catch (_erro) {
    throw new ApiError(
      'Não foi possível conectar à API. Verifique se o backend Flask está em execução.',
      0,
      'ConnectionError'
    );
  }

  let corpo = null;
  try {
    corpo = await resposta.json();
  } catch (_erro) {
    // Respostas sem JSON (ex.: erro de proxy) também viram erro amigável.
  }

  if (!resposta.ok) {
    throw new ApiError(
      corpo?.message || 'Não foi possível realizar a operação.',
      resposta.status,
      corpo?.error || `HTTP ${resposta.status}`
    );
  }

  return corpo;
}

// Cuidado: json(metodo)(caminho) EXECUTA a requisição imediatamente.
// Para expor uma função pública (ex.: criarCliente), envolva em
// (dados) => json('POST')('/clientes', dados). Chamá-lo diretamente na
// definição do objeto cria uma Promise no lugar da função e dispara um
// POST inválido no carregamento do módulo.
const json = (metodo) => (caminho, dados) =>
  requisitar(caminho, {
    method: metodo,
    ...(dados !== undefined ? { body: JSON.stringify(dados) } : {}),
  });

export const api = {
  // Clientes
  listarClientes: () => requisitar('/clientes'),
  buscarCliente: (id) => requisitar(`/clientes/${id}`),
  criarCliente: (dados) => json('POST')('/clientes', dados),
  atualizarCliente: (id, dados) => json('PUT')(`/clientes/${id}`, dados),
  excluirCliente: (id) => json('DELETE')(`/clientes/${id}`),

  // Técnicos
  listarTecnicos: () => requisitar('/tecnicos'),
  buscarTecnico: (id) => requisitar(`/tecnicos/${id}`),
  criarTecnico: (dados) => json('POST')('/tecnicos', dados),
  atualizarTecnico: (id, dados) => json('PUT')(`/tecnicos/${id}`, dados),
  excluirTecnico: (id) => json('DELETE')(`/tecnicos/${id}`),

  // Equipamentos
  listarEquipamentos: () => requisitar('/equipamentos'),
  buscarEquipamento: (id) => requisitar(`/equipamentos/${id}`),
  criarEquipamento: (dados) => json('POST')('/equipamentos', dados),
  atualizarEquipamento: (id, dados) => json('PUT')(`/equipamentos/${id}`, dados),
  atualizarSituacaoEquipamento: (id, dados) => json('PATCH')(`/equipamentos/${id}/situacao`, dados),
  excluirEquipamento: (id) => json('DELETE')(`/equipamentos/${id}`),
  excluirOrdem: (id) => json('DELETE')(`/ordens-de-servico/${id}`),

  // Ordens de serviço
  listarOrdens: () => requisitar('/ordens-de-servico'),
  buscarOrdem: (id) => requisitar(`/ordens-de-servico/${id}`),
  criarOrdem: (dados) => json('POST')('/ordens-de-servico', dados),
  atualizarDiagnostico: (id, dados) => json('PATCH')(`/ordens-de-servico/${id}/diagnostico`, dados),
  atribuirTecnico: (id, dados) => json('PATCH')(`/ordens-de-servico/${id}/tecnico`, dados),
  atualizarStatus: (id, dados) => json('PATCH')(`/ordens-de-servico/${id}/status`, dados),
  finalizarOrdem: (id, dados) => json('PATCH')(`/ordens-de-servico/${id}/finalizar`, dados),
  cancelarOrdem: (id) => json('PATCH')(`/ordens-de-servico/${id}/cancelar`),

  // Dashboard
  buscarDashboard: () => requisitar('/dashboard'),

  // Saúde da API
  verificarSaude: () => requisitar('/health'),
};
