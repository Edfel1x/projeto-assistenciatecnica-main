"""Acesso ao MySQL para a API BCDADOS.

Este módulo é a única porta de entrada para o banco na camada HTTP. Ele:
  - abre conexões com parâmetros lidos de config.py (variáveis de ambiente);
  - garante fechamento correto via contextmanager;
  - traduz erros do MySQL em exceções de domínio com mensagens seguras,
    sem revelar SQL, credenciais ou detalhes internos ao frontend.
"""

from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error as MySQLError

from . import config


class DatabaseUnavailable(Exception):
    """O servidor MySQL não pôde ser contactado."""


class DatabaseConfigError(Exception):
    """O banco configurado não existe ou as credenciais são inválidas."""


class DatabaseConstraintError(Exception):
    """A operação violou uma regra de integridade (FK, CHECK, UNIQUE)."""

    def __init__(self, mensagem: str, codigo: str | None = None):
        super().__init__(mensagem)
        self.codigo = codigo


def conectar():
    """Abre uma conexão MySQL. Levanta DatabaseUnavailable/ConfigError.

    Nota: o módulo conexao.py da raiz continua intacto para o menu CLI.
    Aqui usamos config.py para permitir credenciais via .env.
    """
    try:
        return mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
        )
    except MySQLError as erro:
        codigo = getattr(erro, "errno", None)
        if codigo == 2003:
            raise DatabaseUnavailable(
                "Banco de dados indisponível. Verifique se o MySQL está em execução."
            ) from None
        if codigo in (1045, 1049):
            raise DatabaseConfigError(
                "Configuração do banco inválida. Verifique as variáveis de ambiente."
            ) from None
        # Demais falhas também são genéricas: nada de SQL ou credenciais vazando.
        raise DatabaseUnavailable("Não foi possível acessar o banco de dados.") from None


@contextmanager
def obter_conexao():
    """Contextmanager que fecha a conexão mesmo em caso de erro."""
    conexao = conectar()
    try:
        yield conexao
    finally:
        if conexao.is_connected():
            conexao.close()


@contextmanager
def transacao():
    """Contextmanager com commit/rollback automáticos.

    Uso típico:
        with transacao() as (conexao, cursor):
            cursor.execute(...)
    """
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            yield conexao, cursor
            conexao.commit()
        except MySQLError as erro:
            conexao.rollback()
            traduzir_erro_mysql(erro)
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()


def traduzir_erro_mysql(erro: MySQLError):
    """Converte erros do conector em exceções de domínio seguras."""
    codigo = getattr(erro, "errno", None)

    # 1216/1217 são devolvidos por algumas versões do MySQL/MariaDB quando
    # uma FK com ON DELETE RESTRICT bloqueia a exclusão (1451/1452 são os
    # códigos equivalentes em outras versões). Sem 1217 aqui, excluir um
    # cliente/técnico/equipamento com ordens vinculadas virava 503.
    if codigo in (1216, 1217, 1451, 1452):  # violação de chave estrangeira
        raise DatabaseConstraintError(
            "Este registro está vinculado a outros cadastros. Exclua os "
            "registros vinculados na tela correspondente (por exemplo, as "
            "ordens em Ordens de Serviço) e tente novamente.",
            "FOREIGN_KEY",
        ) from None

    if codigo == 1062:  # UNIQUE duplicado
        raise DatabaseConstraintError(
            "Já existe um registro com estes dados.", "DUPLICATE"
        ) from None

    if codigo == 3819:  # CHECK constraint (ex.: OS concluída sem técnico)
        raise DatabaseConstraintError(
            "A operação viola uma regra de negócio do banco de dados.",
            "CHECK",
        ) from None

    if codigo == 1406:  # dado longo demais para a coluna
        raise DatabaseConstraintError(
            "Um dos campos informados é longo demais.", "DATA_TOO_LONG"
        ) from None

    if codigo == 1265:  # valor inválido para ENUM, por exemplo
        raise DatabaseConstraintError(
            "Um dos campos informados possui um valor inválido.", "INVALID_VALUE"
        ) from None

    # Erro desconhecido: mensagem genérica, sem detalhes internos.
    raise DatabaseUnavailable("Erro interno ao processar a operação.") from None
