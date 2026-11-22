/* Menu lateral com navegação por hash e recolhimento em telas pequenas. */

import { icone } from './icons.js';

export const ITENS_NAVEGACAO = [
  { rota: 'dashboard', rotulo: 'Dashboard', icone: 'dashboard' },
  { rota: 'clientes', rotulo: 'Clientes', icone: 'clientes' },
  { rota: 'tecnicos', rotulo: 'Técnicos', icone: 'tecnicos' },
  { rota: 'equipamentos', rotulo: 'Equipamentos', icone: 'equipamentos' },
  { rota: 'ordens', rotulo: 'Ordens de serviço', icone: 'ordens' },
  { rota: 'configuracoes', rotulo: 'Configurações', icone: 'configuracoes' },
];

export function renderizarSidebar(elemento, rotaAtiva) {
  elemento.innerHTML = `
    <div class="marca">
      <div class="marca-icone">${icone('check')}</div>
      <div>
        <div class="marca-nome">BCDADOS</div>
        <div class="marca-subtitulo">Assistência Técnica</div>
      </div>
    </div>

    <p class="nav-grupo-titulo">Gerenciamento</p>
    <nav class="navegacao">
      ${ITENS_NAVEGACAO.map(
        (item) => `
        <a href="#/${item.rota}" class="nav-item ${rotaAtiva === item.rota ? 'ativo' : ''}"
           data-rota="${item.rota}" ${rotaAtiva === item.rota ? 'aria-current="page"' : ''}>
          ${icone(item.icone)}
          <span>${item.rotulo}</span>
        </a>`
      ).join('')}
    </nav>

    <div class="sidebar-rodape">
      <strong>Sistema interno</strong><br />
      Dados sincronizados com a API.
    </div>
  `;
}

export function destacarRota(elemento, rotaAtiva) {
  elemento.querySelectorAll('.nav-item').forEach((link) => {
    const ativo = link.dataset.rota === rotaAtiva;
    link.classList.toggle('ativo', ativo);
    if (ativo) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
}

export function alternarSidebar(sidebar, overlay, abrir = null) {
  const deveAbrir = abrir ?? !sidebar.classList.contains('aberta');
  sidebar.classList.toggle('aberta', deveAbrir);
  overlay.hidden = !deveAbrir;
  document.body.style.overflow = deveAbrir ? 'hidden' : '';

  // Em telas pequenas a sidebar fica fora da área visível por transform.
  // inert/aria-hidden impedem que links invisíveis continuem no tab order
  // e sejam anunciados por leitores de tela.
  const emTelaPequena = window.matchMedia('(max-width: 900px)').matches;
  sidebar.inert = emTelaPequena && !deveAbrir;
  if (emTelaPequena) {
    sidebar.setAttribute('aria-hidden', String(!deveAbrir));
  } else {
    sidebar.removeAttribute('aria-hidden');
  }
  if (!deveAbrir && emTelaPequena) {
    document.getElementById('botao-menu')?.focus();
  }
}
