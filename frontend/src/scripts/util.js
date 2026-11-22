/* Formatação compartilhada entre as páginas. */

import { escapeHtml } from '../components/notification.js';

const CLASSES_STATUS = {
  Aberta: 'badge-aberta',
  'Em manutenção': 'badge-em-manutencao',
  Concluída: 'badge-concluida',
  Cancelada: 'badge-cancelada',
};

export function badgeStatus(status) {
  const classe = CLASSES_STATUS[status] || 'badge-neutro';
  return `<span class="badge ${classe}">${escapeHtml(status || '—')}</span>`;
}

const CLASSES_STATUS_EQUIPAMENTO = {
  Disponível: 'badge-neutro',
  'Em análise': 'badge-aberta',
  'Em manutenção': 'badge-em-manutencao',
  'Aguardando peça': 'badge-aberta',
  'Pronto para entrega': 'badge-concluida',
  Entregue: 'badge-concluida',
};

export function badgeStatusEquipamento(status) {
  const classe = CLASSES_STATUS_EQUIPAMENTO[status] || 'badge-neutro';
  return `<span class="badge ${classe}">${escapeHtml(status || '—')}</span>`;
}

export function formatarData(valor) {
  if (!valor) return '—';
  // O backend envia ISO (YYYY-MM-DD HH:MM:SS). Extrai a parte legível.
  const [data, hora] = String(valor).split(/[T ]/);
  const partes = data.split('-');
  if (partes.length !== 3) return escapeHtml(valor);
  const dataFormatada = `${partes[2]}/${partes[1]}/${partes[0]}`;
  return hora ? `${dataFormatada} ${hora.slice(0, 5)}` : dataFormatada;
}

export function formatarMoeda(valor) {
  if (valor === null || valor === undefined) return '—';
  return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

export function filtrarItens(itens, termo, campos) {
  const busca = String(termo || '').trim().toLocaleLowerCase('pt-BR');
  if (!busca) return itens;
  return itens.filter((item) =>
    campos.some((campo) =>
      String(item[campo] ?? '')
        .toLocaleLowerCase('pt-BR')
        .includes(busca)
    )
  );
}
