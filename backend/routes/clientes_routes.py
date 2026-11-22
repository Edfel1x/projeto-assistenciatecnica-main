"""Endpoints REST de clientes."""

from flask import Blueprint

from ..services import clientes_service
from .responses import corpo_json, erro, sucesso

bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


@bp.get("")
def listar_clientes():
    clientes = clientes_service.listar()
    return sucesso(clientes, "Clientes listados com sucesso.")


@bp.get("/<int:id_cliente>")
def buscar_cliente(id_cliente):
    cliente = clientes_service.buscar_por_id(id_cliente)
    if cliente is None:
        return erro("Cliente não encontrado.", status=404)
    return sucesso(cliente, "Cliente encontrado.")


@bp.post("")
def criar_cliente():
    cliente = clientes_service.criar(corpo_json())
    return sucesso(cliente, "Cliente cadastrado com sucesso.", 201)


@bp.put("/<int:id_cliente>")
def atualizar_cliente(id_cliente):
    cliente = clientes_service.atualizar(id_cliente, corpo_json())
    return sucesso(cliente, "Cliente atualizado com sucesso.")


@bp.delete("/<int:id_cliente>")
def excluir_cliente(id_cliente):
    clientes_service.excluir(id_cliente)
    return sucesso(message="Cliente excluído com sucesso.")
