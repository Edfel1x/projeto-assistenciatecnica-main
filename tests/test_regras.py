"""Testes das regras de negócio replicadas dos módulos Python originais."""

from contextlib import contextmanager

import pytest

from backend.services import common, equipamentos_service, ordens_service
from backend.services.common import ConflictError, NotFoundError, ValidationError


class CursorFalso:
    """Cursor mínimo para testar regras sem depender do MySQL."""

    def __init__(self, resultados):
        self.resultados = list(resultados)
        self.comandos = []
        self.rowcount = 1

    def execute(self, sql, parametros=None):
        self.comandos.append((sql, parametros))

    def fetchone(self):
        return self.resultados.pop(0) if self.resultados else None

    def close(self):
        pass


@contextmanager
def transacao_falsa(*resultados):
    cursor = CursorFalso(resultados)
    yield object(), cursor


# ---------------- Validações comuns ----------------

def test_texto_obrigatorio_rejeita_vazio():
    with pytest.raises(ValidationError):
        common.texto_obrigatorio('   ', 'nome')


def test_valor_monetario_aceita_virgula():
    assert common.valor_monetario('125,90') == 125.9


def test_valor_monetario_rejeita_negativo():
    with pytest.raises(ValidationError):
        common.valor_monetario(-1)


def test_inteiro_positivo_rejeita_zero():
    with pytest.raises(ValidationError):
        common.inteiro_positivo(0, 'id_cliente')


def test_serializar_decimal():
    from decimal import Decimal

    assert common.serializar(Decimal('19.90')) == 19.9


# ---------------- Regras de equipamentos ----------------

def test_equipamento_exige_cliente_existente(monkeypatch):
    monkeypatch.setattr(equipamentos_service.clientes_service, 'buscar_por_id', lambda _id: None)
    with pytest.raises(NotFoundError):
        equipamentos_service.criar({
            'id_cliente': 99, 'tipo': 'Notebook', 'marca': 'Dell',
            'modelo': 'Latitude', 'numero_serie': 'ABC',
        })


def test_status_de_equipamento_valido_e_invalido():
    assert equipamentos_service.validar_status(' Em manutenção ') == 'Em manutenção'
    with pytest.raises(ValidationError, match='Status inválido'):
        equipamentos_service.validar_status('Quebrado')


def test_criar_equipamento_usa_status_padrao_e_salva_diagnostico(monkeypatch, tmp_path):
    monkeypatch.setattr(
        equipamentos_service.clientes_service, 'buscar_por_id',
        lambda _id: {'id_cliente': 1},
    )
    monkeypatch.setattr(equipamentos_service, 'colunas_disponiveis', lambda: set())
    monkeypatch.setattr(
        equipamentos_service.armazenamento_situacao, 'CAMINHO',
        tmp_path / 'situacao.json',
    )
    cursor = CursorFalso([])
    cursor.lastrowid = 4

    @contextmanager
    def transacao_local():
        yield object(), cursor

    monkeypatch.setattr(equipamentos_service, 'transacao', transacao_local)
    monkeypatch.setattr(
        equipamentos_service, 'buscar_por_id', lambda _id: {'id_equipamento': 4},
    )

    equipamentos_service.criar({
        'id_cliente': 1, 'tipo': 'Notebook', 'marca': 'Dell',
        'modelo': 'Latitude', 'numero_serie': 'ABC',
        'diagnostico': '  Tela com linhas  ',
    })
    sql, parametros = cursor.comandos[0]
    assert 'INSERT INTO equipamentos' in sql
    assert 'status' not in sql  # banco sem ALTER: colunas ainda não existem
    situacao = equipamentos_service.armazenamento_situacao.obter(4)
    assert situacao['status'] == 'Disponível'
    assert situacao['diagnostico'] == 'Tela com linhas'


def test_atualizar_situacao_exige_algum_campo(monkeypatch):
    monkeypatch.setattr(
        equipamentos_service, 'buscar_por_id', lambda _id: {'id_equipamento': 1},
    )
    with pytest.raises(ValidationError, match='status'):
        equipamentos_service.atualizar_situacao(1, {})


def test_atualizar_situacao_rejeita_status_fora_do_enum(monkeypatch):
    monkeypatch.setattr(
        equipamentos_service, 'buscar_por_id', lambda _id: {'id_equipamento': 1},
    )
    with pytest.raises(ValidationError, match='Status inválido'):
        equipamentos_service.atualizar_situacao(1, {'status': 'Quebrado'})


def test_atualizar_situacao_limpa_diagnostico_quando_vazio(monkeypatch, tmp_path):
    monkeypatch.setattr(
        equipamentos_service, 'buscar_por_id',
        lambda _id: {'id_equipamento': 1, 'status': 'Em manutenção', 'diagnostico': None},
    )
    monkeypatch.setattr(equipamentos_service, 'colunas_disponiveis', lambda: set())
    monkeypatch.setattr(
        equipamentos_service.armazenamento_situacao, 'CAMINHO',
        tmp_path / 'situacao.json',
    )
    equipamentos_service.armazenamento_situacao.salvar(
        1, status='Em manutenção', diagnostico='Antigo'
    )
    cursor = CursorFalso([])

    @contextmanager
    def transacao_local():
        yield object(), cursor

    monkeypatch.setattr(equipamentos_service, 'transacao', transacao_local)

    equipamentos_service.atualizar_situacao(1, {'diagnostico': '   '})
    assert not cursor.comandos  # sem colunas no banco, nada de UPDATE em equipamentos
    situacao = equipamentos_service.armazenamento_situacao.obter(1)
    assert situacao['status'] == 'Em manutenção'
    assert 'diagnostico' not in situacao


def test_atualizar_situacao_tambem_grava_no_banco_quando_colunas_existem(monkeypatch, tmp_path):
    monkeypatch.setattr(
        equipamentos_service, 'buscar_por_id',
        lambda _id: {'id_equipamento': 1, 'status': 'Disponível', 'diagnostico': None},
    )
    monkeypatch.setattr(
        equipamentos_service, 'colunas_disponiveis',
        lambda: {'status', 'diagnostico'},
    )
    monkeypatch.setattr(
        equipamentos_service.armazenamento_situacao, 'CAMINHO',
        tmp_path / 'situacao.json',
    )
    cursor = CursorFalso([])

    @contextmanager
    def transacao_local():
        yield object(), cursor

    monkeypatch.setattr(equipamentos_service, 'transacao', transacao_local)

    equipamentos_service.atualizar_situacao(1, {
        'status': 'Em manutenção', 'diagnostico': 'Fonte em curto',
    })
    sql, parametros = cursor.comandos[0]
    assert 'status = %s' in sql and 'diagnostico = %s' in sql
    assert parametros[0] == 'Em manutenção'
    assert parametros[1] == 'Fonte em curto'


# ---------------- Regras de ordens de serviço ----------------

def test_criar_ordem_exige_equipamento_existente(monkeypatch):
    monkeypatch.setattr(ordens_service.equipamentos_service, 'buscar_por_id', lambda _id: None)
    with pytest.raises(NotFoundError):
        ordens_service.criar({'id_equipamento': 99, 'defeito_relatado': 'Não liga'})


def test_criar_ordem_exige_defeito(monkeypatch):
    monkeypatch.setattr(ordens_service.equipamentos_service, 'buscar_por_id', lambda _id: {'id_equipamento': 1})
    with pytest.raises(ValidationError):
        ordens_service.criar({'id_equipamento': 1, 'defeito_relatado': ''})


def test_criar_ordem_rejeita_tecnico_inexistente(monkeypatch):
    monkeypatch.setattr(
        ordens_service.equipamentos_service, 'buscar_por_id',
        lambda _id: {'id_equipamento': 1},
    )
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa())
    with pytest.raises(NotFoundError, match='Técnico'):
        ordens_service.criar({
            'id_equipamento': 1, 'defeito_relatado': 'Não liga', 'id_tecnico': 99,
        })


def test_criar_ordem_com_tecnico_grava_id_no_insert(monkeypatch):
    monkeypatch.setattr(
        ordens_service.equipamentos_service, 'buscar_por_id',
        lambda _id: {'id_equipamento': 1},
    )
    cursor = CursorFalso([{'ok': 1}])  # SELECT 1 FROM tecnicos
    cursor.lastrowid = 7

    @contextmanager
    def transacao_local():
        yield object(), cursor

    monkeypatch.setattr(ordens_service, 'transacao', transacao_local)
    monkeypatch.setattr(
        ordens_service, 'buscar_por_id',
        lambda _id: {'id_ordem': 7, 'id_tecnico': 2},
    )

    ordem = ordens_service.criar({
        'id_equipamento': 1, 'defeito_relatado': 'Não liga', 'id_tecnico': 2,
    })
    assert ordem['id_tecnico'] == 2
    assert any(
        'INSERT' in sql and 'id_tecnico' in sql for sql, _ in cursor.comandos
    )


def test_finalizar_exige_tecnico(monkeypatch):
    ordem = {'id_ordem': 1, 'status': 'Aberta', 'id_tecnico': None, 'diagnostico': 'Placa queimada'}
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa(ordem))
    with pytest.raises(ConflictError, match='técnico'):
        ordens_service.finalizar(1, {'valor_servico': '100,00'})


def test_finalizar_exige_diagnostico(monkeypatch):
    ordem = {'id_ordem': 1, 'status': 'Em manutenção', 'id_tecnico': 2, 'diagnostico': '   '}
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa(ordem))
    with pytest.raises(ConflictError, match='diagnóstico'):
        ordens_service.finalizar(1, {'valor_servico': 100})


def test_nao_altera_ordem_encerrada(monkeypatch):
    ordem = {'id_ordem': 1, 'status': 'Concluída', 'id_tecnico': 2, 'diagnostico': 'ok'}
    # Cada chamada cria um cursor próprio: o de diagnóstico faz 1 consulta;
    # o de técnico faria 2 (ordem + técnico), mas para na primeira (409).
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa(ordem, {'id_tecnico': 3}))
    with pytest.raises(ConflictError):
        ordens_service.atualizar_diagnostico(1, {'diagnostico': 'novo'})
    with pytest.raises(ConflictError):
        ordens_service.atribuir_tecnico(1, {'id_tecnico': 3})


def test_status_de_ordem_encerrada_e_bloqueado(monkeypatch):
    ordem = {'id_ordem': 1, 'status': 'Cancelada', 'id_tecnico': 2, 'diagnostico': 'ok'}
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa(ordem))
    with pytest.raises(ConflictError, match='Cancelada'):
        ordens_service.atualizar_status(1, {'status': 'Aberta'})


def test_status_so_aceita_aberta_e_manutencao(monkeypatch):
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa({
        'id_ordem': 1, 'status': 'Aberta', 'id_tecnico': None, 'diagnostico': ''
    }))
    with pytest.raises(ConflictError):
        ordens_service.atualizar_status(1, {'status': 'Concluída'})
    with pytest.raises(ValidationError):
        ordens_service.atualizar_status(1, {'status': 'Inexistente'})


def test_nao_cancela_ordem_concluida(monkeypatch):
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa({
        'id_ordem': 1, 'status': 'Concluída', 'id_tecnico': 2, 'diagnostico': 'ok'
    }))
    with pytest.raises(ConflictError):
        ordens_service.cancelar(1)


def test_atribuir_tecnico_exige_tecnico_existente(monkeypatch):
    ordem = {'id_ordem': 1, 'status': 'Aberta', 'id_tecnico': None, 'diagnostico': ''}
    # 1ª consulta: a ordem; 2ª consulta: técnico inexistente (None).
    monkeypatch.setattr(ordens_service, 'transacao', lambda: transacao_falsa(ordem, None))
    with pytest.raises(NotFoundError):
        ordens_service.atribuir_tecnico(1, {'id_tecnico': 99})
