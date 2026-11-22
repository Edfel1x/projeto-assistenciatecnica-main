/* Alternância de tema sem recarregar a página, com persistência em localStorage. */

const CHAVE = 'bcdados-tema';
const TEMAS = ['escuro', 'claro'];

export function temaAtual() {
  return document.documentElement.dataset.theme === 'claro' ? 'claro' : 'escuro';
}

export function aplicarTema(tema) {
  const normalizado = TEMAS.includes(tema) ? tema : 'escuro';
  document.documentElement.dataset.theme = normalizado;
  try {
    localStorage.setItem(CHAVE, normalizado);
  } catch (_erro) {
    // Ambientes com storage bloqueado ainda usam o tema desta sessão.
  }
  return normalizado;
}

export function alternarTema() {
  return aplicarTema(temaAtual() === 'escuro' ? 'claro' : 'escuro');
}

/** Chamado uma única vez na inicialização. */
export function inicializarTema() {
  let salvo = null;
  try {
    salvo = localStorage.getItem(CHAVE);
  } catch (_erro) {
    // ignore
  }
  return aplicarTema(salvo || 'escuro');
}
