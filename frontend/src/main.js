/* Ponto de entrada da aplicação BCDADOS.

   Responsabilidades:
     - importar os estilos (variáveis → global → layout → componentes → responsive);
     - inicializar tema, sidebar, cabeçalho e roteamento;
     - carregar o template HTML da rota e chamar o script responsável por ela.
*/

import './styles/variables.css';
import './styles/global.css';
import './styles/layout.css';
import './styles/components.css';
import './styles/responsive.css';

import dashboardHtml from './pages/dashboard.html?raw';
import clientesHtml from './pages/clientes.html?raw';
import tecnicosHtml from './pages/tecnicos.html?raw';
import equipamentosHtml from './pages/equipamentos.html?raw';
import ordensHtml from './pages/ordens.html?raw';
import configuracoesHtml from './pages/configuracoes.html?raw';

import { renderizarSidebar, destacarRota, alternarSidebar } from './components/sidebar.js';
import { renderizarHeader, atualizarBotaoTema } from './components/header.js';
import { fecharTodosModais } from './components/modal.js';
import { renderizarDashboard } from './scripts/dashboard.js';
import { renderizarClientes } from './scripts/clientes.js';
import { renderizarTecnicos } from './scripts/tecnicos.js';
import { renderizarEquipamentos } from './scripts/equipamentos.js';
import { renderizarOrdens } from './scripts/ordens.js';
import { renderizarConfiguracoes } from './scripts/configuracoes.js';
import { configurarNavegacao, metadadosPagina, rotaAtual } from './scripts/navigation.js';
import { alternarTema, inicializarTema, temaAtual } from './scripts/theme.js';

const PAGINAS = {
  dashboard: { html: dashboardHtml, renderizar: renderizarDashboard },
  clientes: { html: clientesHtml, renderizar: renderizarClientes },
  tecnicos: { html: tecnicosHtml, renderizar: renderizarTecnicos },
  equipamentos: { html: equipamentosHtml, renderizar: renderizarEquipamentos },
  ordens: { html: ordensHtml, renderizar: renderizarOrdens },
  configuracoes: { html: configuracoesHtml, renderizar: renderizarConfiguracoes },
};

const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');
const header = document.getElementById('header');
const conteudo = document.getElementById('conteudo');

inicializarTema();

// Listeners globais registrados uma única vez (o overlay não é recriado).
overlay.addEventListener('click', () => {
  alternarSidebar(sidebar, overlay, false);
  document.getElementById('botao-menu')?.setAttribute('aria-expanded', 'false');
});
window.addEventListener('keydown', (evento) => {
  if (evento.key === 'Escape' && sidebar.classList.contains('aberta')) {
    alternarSidebar(sidebar, overlay, false);
    document.getElementById('botao-menu')?.setAttribute('aria-expanded', 'false');
  }
});

let tokenNavegacao = 0;

async function navegar(rota) {
  const token = ++tokenNavegacao;
  const pagina = PAGINAS[rota] || PAGINAS.dashboard;
  const meta = metadadosPagina(rota);

  fecharTodosModais();
  alternarSidebar(sidebar, overlay, false);
  renderizarSidebar(sidebar, rota);
  renderizarHeader(header, meta);
  atualizarBotaoTema(temaAtual());

  document.title = `${meta.titulo} — BCDADOS`;
  conteudo.innerHTML = pagina.html;
  conteudo.scrollTop = 0;
  window.scrollTo({ top: 0, behavior: 'auto' });

  // Conecta os eventos do cabeçalho após a renderização (o header é recriado).
  document.getElementById('botao-tema').addEventListener('click', () => {
    const tema = alternarTema();
    atualizarBotaoTema(tema);
  });
  document.getElementById('botao-menu').addEventListener('click', (evento) => {
    const aberto = sidebar.classList.contains('aberta');
    alternarSidebar(sidebar, overlay, !aberto);
    evento.currentTarget.setAttribute('aria-expanded', String(!aberto));
  });

  await pagina.renderizar(conteudo);
  // Descarta efeitos de uma navegação antiga que tenha terminado depois desta.
  if (token !== tokenNavegacao) return;
  destacarRota(sidebar, rota);
  conteudo.focus({ preventScroll: true });
}

configurarNavegacao((rota) => {
  navegar(rota).catch((erro) => {
    console.error('Falha ao renderizar a página:', erro);
  });
});

navegar(rotaAtual()).catch((erro) => {
  console.error('Falha ao inicializar a aplicação:', erro);
});
