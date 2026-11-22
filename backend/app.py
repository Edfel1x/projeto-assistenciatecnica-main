"""Aplicação Flask da API REST do BCDADOS.

Execução (a partir da raiz do projeto):
    python -m backend.app

O arquivo main.py da raiz NÃO é alterado: ele continua sendo o menu CLI
original. Este módulo é apenas o servidor HTTP da API.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from . import config
from .database import (
    DatabaseConfigError,
    DatabaseConstraintError,
    DatabaseUnavailable,
)
from .routes import (
    clientes_routes,
    dashboard_routes,
    equipamentos_routes,
    ordens_routes,
    tecnicos_routes,
)
from .routes.responses import erro
from .services.common import ConflictError, NotFoundError, ValidationError


def criar_app() -> Flask:
    """Fábrica da aplicação (facilita testes com Flask test_client)."""
    app = Flask(__name__)

    # CORS apenas para as origens do frontend Vite configuradas no .env.
    CORS(
        app,
        resources={r"/api/*": {"origins": config.CORS_ORIGINS}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    for blueprint in (
        clientes_routes.bp,
        tecnicos_routes.bp,
        equipamentos_routes.bp,
        ordens_routes.bp,
        dashboard_routes.bp,
    ):
        app.register_blueprint(blueprint)

    @app.get("/api/health")
    def health():
        """Verifica se a API está no ar (não consulta o banco)."""
        return jsonify({"success": True, "message": "API BCDADOS online.", "data": {"status": "ok"}})

    # -----------------------------------------------------------------------
    # Tratamento centralizado de erros: mensagens seguras, sem detalhes de SQL.
    # -----------------------------------------------------------------------
    @app.errorhandler(ValidationError)
    def tratar_validacao(excecao):
        return erro("Dados inválidos.", str(excecao), 400)

    # Não há handler para ValueError cru: services usam ValidationError.
    # Assim uma ValueError inesperada de terceiros cai no 500 genérico,
    # sem expor mensagens internas ao cliente.

    @app.errorhandler(NotFoundError)
    def tratar_nao_encontrado(excecao):
        return erro("Recurso não encontrado.", str(excecao), 404)

    @app.errorhandler(ConflictError)
    def tratar_conflito(excecao):
        return erro("Não foi possível realizar a operação.", str(excecao), 409)

    @app.errorhandler(DatabaseConstraintError)
    def tratar_restricao(excecao):
        return erro("Não foi possível realizar a operação.", str(excecao), 409)

    @app.errorhandler(DatabaseUnavailable)
    def tratar_indisponibilidade(excecao):
        return erro("Serviço indisponível.", str(excecao), 503)

    @app.errorhandler(DatabaseConfigError)
    def tratar_configuracao(excecao):
        return erro("Serviço indisponível.", str(excecao), 503)

    @app.errorhandler(404)
    def tratar_rota_inexistente(_excecao):
        return erro("Endpoint não encontrado.", status=404)

    @app.errorhandler(405)
    def tratar_metodo_invalido(_excecao):
        return erro("Método HTTP não permitido para este endpoint.", status=405)

    @app.errorhandler(415)
    def tratar_conteudo_invalido(_excecao):
        return erro("Envie os dados no formato application/json.", status=415)

    @app.errorhandler(Exception)
    def tratar_erro_interno(excecao):
        # HTTPExceptions não cobertas acima (400, 413 etc.) preservam seu
        # código. Erros inesperados são registrados no servidor, mas nunca
        # expostos ao cliente.
        if isinstance(excecao, HTTPException):
            return erro(excecao.description or "Requisição inválida.", status=excecao.code or 400)
        app.logger.exception("Erro não tratado na API BCDADOS")
        return erro("Erro interno do servidor.", status=500)

    return app


app = criar_app()


def aplicar_migracoes_startup() -> None:
    """Atualiza bancos antigos ao iniciar, sem derrubar a API se falhar.

    Atenção: a variável da exceção NÃO pode se chamar `erro` neste módulo —
    ela apagaria a função `erro` importada de routes.responses (o Python
    remove a variável de `except ... as x` ao sair do bloco) e todos os
    handlers de 400/404/409 passariam a responder 500 sem JSON.
    """
    from .migracoes import aplicar_migracoes

    try:
        colunas = aplicar_migracoes()
        if colunas:
            print("Migração aplicada: " + ", ".join(colunas), flush=True)
    except Exception as exc:  # o health-check continua disponível sem banco
        print(f"Aviso: falha ao aplicar migrações: {exc}", flush=True)


if __name__ == "__main__":
    aplicar_migracoes_startup()

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )
