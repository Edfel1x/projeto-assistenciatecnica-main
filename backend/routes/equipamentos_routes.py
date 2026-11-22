"""Endpoints REST de equipamentos."""

from flask import Blueprint

from ..services import equipamentos_service
from .responses import corpo_json, erro, sucesso

bp = Blueprint("equipamentos", __name__, url_prefix="/api/equipamentos")


@bp.get("")
def listar_equipamentos():
    return sucesso(
        equipamentos_service.listar(), "Equipamentos listados com sucesso."
    )


@bp.get("/<int:id_equipamento>")
def buscar_equipamento(id_equipamento):
    equipamento = equipamentos_service.buscar_por_id(id_equipamento)
    if equipamento is None:
        return erro("Equipamento não encontrado.", status=404)
    return sucesso(equipamento, "Equipamento encontrado.")


@bp.post("")
def criar_equipamento():
    return sucesso(
        equipamentos_service.criar(corpo_json()),
        "Equipamento cadastrado com sucesso.",
        201,
    )


@bp.put("/<int:id_equipamento>")
def atualizar_equipamento(id_equipamento):
    return sucesso(
        equipamentos_service.atualizar(id_equipamento, corpo_json()),
        "Equipamento atualizado com sucesso.",
    )


@bp.patch("/<int:id_equipamento>/situacao")
def atualizar_situacao_equipamento(id_equipamento):
    return sucesso(
        equipamentos_service.atualizar_situacao(id_equipamento, corpo_json()),
        "Situação do equipamento atualizada com sucesso.",
    )


@bp.delete("/<int:id_equipamento>")
def excluir_equipamento(id_equipamento):
    equipamentos_service.excluir(id_equipamento)
    return sucesso(message="Equipamento excluído com sucesso.")
