"""Endpoints REST de técnicos."""

from flask import Blueprint

from ..services import tecnicos_service
from .responses import corpo_json, erro, sucesso

bp = Blueprint("tecnicos", __name__, url_prefix="/api/tecnicos")


@bp.get("")
def listar_tecnicos():
    return sucesso(tecnicos_service.listar(), "Técnicos listados com sucesso.")


@bp.get("/<int:id_tecnico>")
def buscar_tecnico(id_tecnico):
    tecnico = tecnicos_service.buscar_por_id(id_tecnico)
    if tecnico is None:
        return erro("Técnico não encontrado.", status=404)
    return sucesso(tecnico, "Técnico encontrado.")


@bp.post("")
def criar_tecnico():
    return sucesso(tecnicos_service.criar(corpo_json()), "Técnico cadastrado com sucesso.", 201)


@bp.put("/<int:id_tecnico>")
def atualizar_tecnico(id_tecnico):
    return sucesso(
        tecnicos_service.atualizar(id_tecnico, corpo_json()),
        "Técnico atualizado com sucesso.",
    )


@bp.delete("/<int:id_tecnico>")
def excluir_tecnico(id_tecnico):
    tecnicos_service.excluir(id_tecnico)
    return sucesso(message="Técnico excluído com sucesso.")
