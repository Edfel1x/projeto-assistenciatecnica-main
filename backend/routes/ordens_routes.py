"""Endpoints REST de ordens de serviço.

Os PATCHs de operações (diagnóstico, técnico, status, finalizar, cancelar)
refletem diretamente as funções de gerenciar_ordem() do módulo CLI original.
"""

from flask import Blueprint

from ..services import ordens_service
from .responses import corpo_json, erro, sucesso

bp = Blueprint("ordens", __name__, url_prefix="/api/ordens-de-servico")


@bp.get("")
def listar_ordens():
    return sucesso(
        ordens_service.listar(), "Ordens de serviço listadas com sucesso."
    )


@bp.get("/<int:id_ordem>")
def buscar_ordem(id_ordem):
    ordem = ordens_service.buscar_por_id(id_ordem)
    if ordem is None:
        return erro("Ordem de serviço não encontrada.", status=404)
    return sucesso(ordem, "Ordem de serviço encontrada.")


@bp.post("")
def criar_ordem():
    return sucesso(
        ordens_service.criar(corpo_json()),
        "Ordem de serviço aberta com sucesso.",
        201,
    )


@bp.patch("/<int:id_ordem>/diagnostico")
def atualizar_diagnostico(id_ordem):
    return sucesso(
        ordens_service.atualizar_diagnostico(id_ordem, corpo_json()),
        "Diagnóstico atualizado com sucesso.",
    )


@bp.patch("/<int:id_ordem>/tecnico")
def atribuir_tecnico(id_ordem):
    return sucesso(
        ordens_service.atribuir_tecnico(id_ordem, corpo_json()),
        "Técnico atribuído com sucesso.",
    )


@bp.patch("/<int:id_ordem>/status")
def atualizar_status(id_ordem):
    return sucesso(
        ordens_service.atualizar_status(id_ordem, corpo_json()),
        "Status atualizado com sucesso.",
    )


@bp.patch("/<int:id_ordem>/finalizar")
def finalizar_ordem(id_ordem):
    return sucesso(
        ordens_service.finalizar(id_ordem, corpo_json()),
        "Ordem de serviço finalizada com sucesso.",
    )


@bp.patch("/<int:id_ordem>/cancelar")
def cancelar_ordem(id_ordem):
    return sucesso(
        ordens_service.cancelar(id_ordem),
        "Ordem de serviço cancelada com sucesso.",
    )
