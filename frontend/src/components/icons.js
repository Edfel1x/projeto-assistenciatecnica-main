/* Ícones SVG inline reutilizáveis.
   Centralizar aqui evita repetir markup e mantém todos os ícones
   herdam a cor do tema via currentColor. */

const caminho = (d, extra = '') =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}><path d="${d}"/></svg>`;

export const icones = {
  dashboard: caminho('M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z'),
  clientes: caminho('M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'),
  tecnicos: caminho('M14 7a4 4 0 1 0-8 0 4 4 0 0 0 8 0M20 21v-2a6 6 0 0 0-6-6H6a6 6 0 0 0-6 6v2M18 8h4M20 6v4M2 21h20'),
  equipamentos: caminho('M4 7h16v12H4zM9 7V4h6v3M4 12h16M8 16h2M14 16h2'),
  ordens: caminho('M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5'),
  configuracoes: caminho('M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21a2 2 0 1 1-4 0v-.07a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.03H3a2 2 0 1 1 0-4h.07A1.7 1.7 0 0 0 4.6 8.94a1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 8.97 4.6 1.7 1.7 0 0 0 10 3.04V3a2 2 0 1 1 4 0v.07a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.7 1.7 0 0 0-.34 1.88 1.7 1.7 0 0 0 1.56 1.03H21a2 2 0 1 1 0 4h-.07a1.7 1.7 0 0 0-1.53 1.03z'),
  sol: caminho('M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42'),
  lua: caminho('M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79'),
  menu: caminho('M3 12h18M3 6h18M3 18h18'),
  fechar: caminho('M18 6 6 18M6 6l12 12'),
  mais: caminho('M12 5v14M5 12h14'),
  olho: caminho('M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6'),
  editar: caminho('M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z'),
  lixeira: caminho('M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v5M14 11v5'),
  pesquisar: caminho('M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16M21 21l-4.35-4.35'),
  sucesso: caminho('M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4 12 14.01l-3-3'),
  alerta: caminho('M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0M12 9v4M12 17h.01'),
  info: caminho('M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20M12 16v-4M12 8h.01'),
  caixa: caminho('M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16M3.3 7 12 12l8.7-5M12 22V12'),
  relogio: caminho('M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20M12 6v6l4 2'),
  check: caminho('M20 6 9 17l-5-5'),
  seta: caminho('M5 12h14M13 6l6 6-6 6'),
  atualizar: caminho('M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16'),
};

export function icone(nome, classes = '') {
  return (icones[nome] || icones.info).replace('<svg ', `<svg class="${classes}" `);
}
