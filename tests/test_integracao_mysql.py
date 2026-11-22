"""Testes de integração REAL com MySQL.

Para executar, configure no .env um banco exclusivo de testes:
    DB_NAME_TEST=bcdados_teste

O banco deve ser criado antes (o script docs/sql/usuario_teste.sql já faz isso),
pois conceder CREATE DATABASE exigiria privilégio global. O usuário precisa ter
permissão para CRIAR e REMOVER TABELAS nesse banco. Os testes recriam o schema
a partir do schema.sql original (sem duplicá-lo) e não tocam no banco de DB_NAME.
"""

import os
import re
from pathlib import Path

import mysql.connector
import pytest

from backend import config
from backend.app import criar_app


BANCO_TESTE = os.getenv('DB_NAME_TEST', '').strip()


@pytest.fixture
def banco_teste():
    """Cria o schema de testes e devolve uma conexão configurada."""
    if not BANCO_TESTE:
        pytest.skip('Defina DB_NAME_TEST no .env para testes de integração com MySQL.')
    if not re.fullmatch(r'[A-Za-z0-9_]+', BANCO_TESTE):
        pytest.skip('DB_NAME_TEST deve conter apenas letras, números e sublinhados.')

    conexao = mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )
    try:
        cursor = conexao.cursor()
        # O banco é criado pela conta administrativa em
        # docs/sql/usuario_teste.sql: CREATE DATABASE exige privilégio global,
        # que o usuário da aplicação deliberadamente não possui.
        cursor.execute(f'USE `{BANCO_TESTE}`')
        for tabela in ('ordens_servico', 'equipamentos', 'tecnicos', 'clientes'):
            cursor.execute(f'DROP TABLE IF EXISTS `{tabela}`')

        schema = Path(__file__).resolve().parents[1] / 'schema.sql'
        sql = schema.read_text(encoding='utf-8')
        # Remove apenas CREATE DATABASE/USE: o restante é o schema original.
        sql = '\n'.join(
            linha for linha in sql.splitlines()
            if not linha.strip().upper().startswith(('CREATE DATABASE', 'USE '))
        )
        for comando in sql.split(';'):
            if comando.strip():
                cursor.execute(comando)
        conexao.commit()
        cursor.close()

        original = config.DB_NAME
        config.DB_NAME = BANCO_TESTE
        yield conexao
        config.DB_NAME = original
    finally:
        if conexao.is_connected():
            conexao.close()


def test_crud_real_de_clientes(banco_teste, monkeypatch):
    app = criar_app()
    app.config.update(TESTING=True)
    monkeypatch.setattr(config, 'DB_NAME', BANCO_TESTE)

    with app.test_client() as cliente:
        resposta = cliente.post('/api/clientes', json={
            'nome': 'Cliente Teste Integração',
            'telefone': '11999990000',
            'email': 'teste@example.com',
        })
        assert resposta.status_code == 201
        novo = resposta.get_json()['data']
        assert novo['nome'] == 'Cliente Teste Integração'

        resposta = cliente.get(f"/api/clientes/{novo['id_cliente']}")
        assert resposta.status_code == 200

        resposta = cliente.put(f"/api/clientes/{novo['id_cliente']}", json={'telefone': '11888880000'})
        assert resposta.status_code == 200
        assert resposta.get_json()['data']['telefone'] == '11888880000'

        # Cliente sem dependências pode ser excluído.
        resposta = cliente.delete(f"/api/clientes/{novo['id_cliente']}")
        assert resposta.status_code == 200


def test_ciclo_completo_de_ordem_de_servico(banco_teste, monkeypatch):
    app = criar_app()
    app.config.update(TESTING=True)
    monkeypatch.setattr(config, 'DB_NAME', BANCO_TESTE)

    with app.test_client() as cliente:
        cli = cliente.post('/api/clientes', json={
            'nome': 'Cliente OS Teste', 'telefone': '11777770000',
        }).get_json()['data']

        tec = cliente.post('/api/tecnicos', json={
            'nome': 'Técnico Teste', 'telefone': '11666660000',
            'especialidade': 'Eletrônica',
        }).get_json()['data']

        equ = cliente.post('/api/equipamentos', json={
            'id_cliente': cli['id_cliente'], 'tipo': 'Notebook', 'marca': 'Dell',
            'modelo': 'Latitude', 'numero_serie': 'TESTE123',
        }).get_json()['data']
        assert equ['status'] == 'Disponível'

        situacao = cliente.patch(
            f"/api/equipamentos/{equ['id_equipamento']}/situacao",
            json={'status': 'Em análise', 'diagnostico': 'Tela com linhas verticais'},
        )
        assert situacao.status_code == 200
        dados_situacao = situacao.get_json()['data']
        assert dados_situacao['status'] == 'Em análise'
        assert dados_situacao['diagnostico'] == 'Tela com linhas verticais'

        invalida = cliente.patch(
            f"/api/equipamentos/{equ['id_equipamento']}/situacao",
            json={'status': 'Quebrado'},
        )
        assert invalida.status_code == 400

        ordem = cliente.post('/api/ordens-de-servico', json={
            'id_equipamento': equ['id_equipamento'],
            'defeito_relatado': 'Não liga após queda',
        }).get_json()['data']
        assert ordem['status'] == 'Aberta'

        diagnostico = cliente.patch(
            f"/api/ordens-de-servico/{ordem['id_ordem']}/diagnostico",
            json={'diagnostico': 'Placa mãe danificada'},
        )
        assert diagnostico.status_code == 200
        assert diagnostico.get_json()['data']['diagnostico'] == 'Placa mãe danificada'

        atribuicao = cliente.patch(
            f"/api/ordens-de-servico/{ordem['id_ordem']}/tecnico",
            json={'id_tecnico': tec['id_tecnico']},
        )
        assert atribuicao.status_code == 200
        assert atribuicao.get_json()['data']['id_tecnico'] == tec['id_tecnico']

        manutencao = cliente.patch(
            f"/api/ordens-de-servico/{ordem['id_ordem']}/status",
            json={'status': 'Em manutenção'},
        )
        assert manutencao.status_code == 200
        assert manutencao.get_json()['data']['status'] == 'Em manutenção'

        finalizada = cliente.patch(
            f"/api/ordens-de-servico/{ordem['id_ordem']}/finalizar",
            json={'valor_servico': '320,50'},
        )
        assert finalizada.status_code == 200
        dados = finalizada.get_json()['data']
        assert dados['status'] == 'Concluída'
        assert dados['valor_servico'] == 320.5
        assert dados['data_conclusao']

        # Regra original: ordem encerrada não aceita novo diagnóstico.
        bloqueio = cliente.patch(
            f"/api/ordens-de-servico/{ordem['id_ordem']}/diagnostico",
            json={'diagnostico': 'Novo diagnóstico'},
        )
        assert bloqueio.status_code == 409

        # Integridade referencial: equipamento com OS não pode ser excluído.
        bloqueio = cliente.delete(f"/api/equipamentos/{equ['id_equipamento']}")
        assert bloqueio.status_code == 409

        # Dashboard reflete os dados persistidos (nada fictício).
        painel = cliente.get('/api/dashboard').get_json()['data']
        assert painel['total_clientes'] >= 1
        assert painel['ordens_finalizadas'] >= 1
