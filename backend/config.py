"""Configuração centralizada da API BCDADOS.

Todas as opções podem ser definidas por variáveis de ambiente ou por um
arquivo .env na raiz do projeto (carregado por python-dotenv). Nenhuma
credencial fica gravada no código-fonte.

Podem ser configuradas:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, CORS_ORIGINS.
"""

import os

from dotenv import load_dotenv

# Procura o .env na raiz do projeto (um nível acima de backend/).
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def _int_env(nome: str, padrao: int) -> int:
    """Converte uma variável de ambiente para inteiro com valor padrão."""
    try:
        return int(os.getenv(nome, str(padrao)))
    except (TypeError, ValueError):
        return padrao


def _bool_env(nome: str, padrao: bool = False) -> bool:
    """Interpreta valores comuns de booleanos em variáveis de ambiente."""
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = _int_env("DB_PORT", 3306)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
# Padrão mantém compatibilidade com conexao.py; o schema.sql usa
# 'assistencia_tecnica'. Basta ajustar DB_NAME no .env para alternar.
DB_NAME = os.getenv("DB_NAME", "bcdados")

# ---------------------------------------------------------------------------
# Servidor Flask
# ---------------------------------------------------------------------------
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = _int_env("FLASK_PORT", 5000)
FLASK_DEBUG = _bool_env("FLASK_DEBUG", False)

# Origens permitidas pelo CORS (separadas por vírgula).
CORS_ORIGINS = [
    origem.strip()
    for origem in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origem.strip()
]
