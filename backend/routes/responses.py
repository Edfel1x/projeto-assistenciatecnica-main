"""Envelopes padronizados de resposta da API."""


def sucesso(data=None, message="Operação realizada com sucesso.", status=200):
    """Monta uma resposta JSON de sucesso.

    Formato: { success: true, message: string, data: any }
    """
    resposta = {"success": True, "message": message}
    if data is not None:
        resposta["data"] = data
    return resposta, status


def erro(message, error=None, status=400):
    """Monta uma resposta JSON de erro.

    Formato: { success: false, message: string, error: string }
    """
    resposta = {"success": False, "message": message}
    if error is not None:
        resposta["error"] = str(error)
    return resposta, status


def corpo_json():
    """Retorna o corpo JSON da requisição.

    Requisições com corpo e Content-Type diferente de application/json
    recebem 415. Corpos vazios são tratados como dict vazio para que a
    validação dos services produza mensagens claras (400).
    """
    from flask import abort, request

    if request.data and not request.is_json:
        abort(415)

    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}
