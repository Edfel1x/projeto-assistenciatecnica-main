"""Testes do store local de situação usado quando o MySQL não tem ALTER."""

from backend import armazenamento_situacao as armazenamento
from backend import config


def test_situacoes_de_bancos_diferentes_nao_se_misturam(monkeypatch, tmp_path):
    monkeypatch.setattr(armazenamento, 'CAMINHO', tmp_path / 'situacao.json')

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados')
    armazenamento.salvar(1, status='Em análise', diagnostico='Do banco principal')

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados_teste')
    assert armazenamento.obter(1) == {}
    armazenamento.salvar(1, status='Entregue', diagnostico='Do banco de testes')

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados')
    assert armazenamento.obter(1) == {
        'status': 'Em análise',
        'diagnostico': 'Do banco principal',
    }


def test_remover_apaga_apenas_o_banco_atual(monkeypatch, tmp_path):
    monkeypatch.setattr(armazenamento, 'CAMINHO', tmp_path / 'situacao.json')

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados')
    armazenamento.salvar(7, status='Em manutenção')
    monkeypatch.setattr(config, 'DB_NAME', 'bcdados_teste')
    armazenamento.salvar(7, status='Disponível')

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados')
    armazenamento.remover(7)
    assert armazenamento.obter(7) == {}

    monkeypatch.setattr(config, 'DB_NAME', 'bcdados_teste')
    assert armazenamento.obter(7)['status'] == 'Disponível'
