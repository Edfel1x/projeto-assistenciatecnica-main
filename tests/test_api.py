"""Testes da camada HTTP: envelopes, health e tratamento de erros."""

from backend import config


def test_health(cliente_api):
    resposta = cliente_api.get('/api/health')
    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo['success'] is True
    assert corpo['data']['status'] == 'ok'


def test_rota_inexistente_retorna_404(cliente_api):
    resposta = cliente_api.get('/api/nao-existe')
    assert resposta.status_code == 404
    assert resposta.get_json()['success'] is False


def test_metodo_invalido_retorna_405(cliente_api):
    resposta = cliente_api.patch('/api/clientes')
    assert resposta.status_code == 405
    assert resposta.get_json()['success'] is False


def test_conteudo_nao_json_retorna_415(cliente_api):
    """O handler 415 só é atingido se corpo_json() validar o Content-Type."""
    resposta = cliente_api.post(
        '/api/clientes', data='nome=Ana', content_type='text/plain'
    )
    assert resposta.status_code == 415
    assert resposta.get_json()['success'] is False


def test_lista_clientes_usa_envelope_padrao(cliente_api, monkeypatch):
    from backend.services import clientes_service

    monkeypatch.setattr(clientes_service, 'listar', lambda: [
        {'id_cliente': 1, 'nome': 'Ana', 'telefone': '11999999999', 'email': None}
    ])

    resposta = cliente_api.get('/api/clientes')
    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo['success'] is True
    assert isinstance(corpo['data'], list)
    assert corpo['data'][0]['nome'] == 'Ana'


def test_validacao_retorna_400(cliente_api, monkeypatch):
    from backend.services import clientes_service
    from backend.services.common import ValidationError

    def falhar(_dados):
        raise ValidationError("O campo 'nome' não pode estar vazio.")

    monkeypatch.setattr(clientes_service, 'criar', falhar)
    resposta = cliente_api.post('/api/clientes', json={'nome': ''})
    assert resposta.status_code == 400
    corpo = resposta.get_json()
    assert corpo['success'] is False
    assert 'nome' in corpo['error']


def test_falha_na_migracao_preserva_handlers_de_erro(cliente_api, monkeypatch):
    """Regressão: 'except Exception as erro' no startup apagava a função erro.

    Isso acontecia quando a migração falhava (ex.: usuário sem ALTER): os
    handlers de validação passavam a responder 500 sem envelope JSON.
    """
    from backend import app as app_mod
    from backend import migracoes
    from backend.services import clientes_service
    from backend.services.common import ValidationError

    def falhar_migracao():
        raise RuntimeError("ALTER command denied")

    monkeypatch.setattr(migracoes, 'aplicar_migracoes', falhar_migracao)
    app_mod.aplicar_migracoes_startup()
    assert callable(app_mod.erro)

    def falhar_criacao(_dados):
        raise ValidationError("O campo 'nome' não pode estar vazio.")

    monkeypatch.setattr(clientes_service, 'criar', falhar_criacao)
    resposta = cliente_api.post('/api/clientes', json={'nome': ''})
    assert resposta.status_code == 400
    assert resposta.get_json()['success'] is False
    assert 'nome' in resposta.get_json()['error']


def test_nao_encontrado_retorna_404(cliente_api, monkeypatch):
    from backend.services import tecnicos_service
    from backend.services.common import NotFoundError

    def falhar(_id):
        raise NotFoundError("Técnico não encontrado.")

    monkeypatch.setattr(tecnicos_service, 'buscar_por_id', falhar)
    resposta = cliente_api.get('/api/tecnicos/999')
    assert resposta.status_code == 404


def test_conflito_retorna_409(cliente_api, monkeypatch):
    from backend.services import ordens_service
    from backend.services.common import ConflictError

    def falhar(_id, _dados):
        raise ConflictError("Esta ordem já foi encerrada.")

    monkeypatch.setattr(ordens_service, 'atualizar_diagnostico', falhar)
    resposta = cliente_api.patch('/api/ordens-de-servico/1/diagnostico', json={'diagnostico': 'x'})
    assert resposta.status_code == 409
    assert resposta.get_json()['success'] is False


def test_vinculo_bloqueia_exclusao_com_mensagem_clara(cliente_api, monkeypatch):
    """Erro de FK deve explicar o vínculo, não parecer falha do servidor."""
    from backend.services import tecnicos_service
    from backend.database import DatabaseConstraintError

    def falhar(_id):
        raise DatabaseConstraintError(
            "Este registro está vinculado a outros cadastros. Exclua os "
            "registros vinculados na tela correspondente.",
            "FOREIGN_KEY",
        )

    monkeypatch.setattr(tecnicos_service, 'excluir', falhar)
    resposta = cliente_api.delete('/api/tecnicos/1')
    assert resposta.status_code == 409
    corpo = resposta.get_json()
    assert corpo['message'] == 'Não foi possível excluir este registro.'
    assert 'vinculado' in corpo['error']
    assert 'Exclua os registros vinculados' in corpo['error']


def test_exclusao_de_ordem_pela_api(cliente_api, monkeypatch):
    """DELETE /ordens-de-servico/{id} é o caminho real para liberar vínculos."""
    from backend.services import ordens_service

    chamados = []
    monkeypatch.setattr(ordens_service, 'excluir', chamados.append)

    resposta = cliente_api.delete('/api/ordens-de-servico/7')
    assert resposta.status_code == 200
    assert chamados == [7]
    assert resposta.get_json()['message'] == 'Ordem de serviço excluída com sucesso.'


def test_banco_indisponivel_retorna_503(cliente_api, monkeypatch):
    from backend.services import dashboard_service
    from backend.database import DatabaseUnavailable

    def falhar():
        raise DatabaseUnavailable("Banco de dados indisponível.")

    monkeypatch.setattr(dashboard_service, 'obter_resumo', falhar)
    resposta = cliente_api.get('/api/dashboard')
    assert resposta.status_code == 503
    assert 'message' in resposta.get_json()


def test_cors_restrito_as_origens_configuradas(cliente_api):
    origem_permitida = config.CORS_ORIGINS[0]
    resposta = cliente_api.get(
        '/api/health', headers={'Origin': origem_permitida}
    )
    assert resposta.headers.get('Access-Control-Allow-Origin') == origem_permitida

    resposta = cliente_api.get(
        '/api/health', headers={'Origin': 'http://site-malicioso.example'}
    )
    assert 'Access-Control-Allow-Origin' not in resposta.headers
