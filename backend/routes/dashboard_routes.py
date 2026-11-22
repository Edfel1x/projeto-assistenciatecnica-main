"""Endpoint de indicadores do dashboard."""

from flask import Blueprint

from ..services import dashboard_service
from .responses import sucesso

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/dashboard")
def dashboard():
    return sucesso(dashboard_service.obter_resumo(), "Indicadores obtidos com sucesso.")
