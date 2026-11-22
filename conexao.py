"""Módulo centralizado de conexão com o banco de dados MySQL.

Este arquivo concentra as configurações e a lógica necessária para
estabelecer a conexão entre a aplicação Python (BCDADOS) e o MySQL.
Os demais módulos devem importar a função conectar() deste arquivo,
em vez de criar suas próprias conexões.
"""

import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------------------------
# Configurações de conexão (placeholders)
# ---------------------------------------------------------------------------
# IMPORTANTE:
# - Não coloque senhas reais em arquivos que serão enviados ao GitHub.
# - Preencha a senha conforme o seu ambiente local.
# - Se desejar usar variáveis de ambiente/.env no futuro, solicite antes a
#   alteração da estrutura do projeto e a adição de dependências.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # CONFIGURAÇÃO A PREENCHER: informe a senha do seu MySQL
    "database": "bcdados",
}


def conectar():
    """Estabelece e retorna uma conexão com o banco de dados MySQL.

    Returns:
        mysql.connector.connection.MySQLConnection | None:
            Objeto de conexão quando a conexão é estabelecida com sucesso;
            None quando ocorre algum erro.
    """
    conexao = None

    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao

    except mysql.connector.Error as erro:
        # Mensagens específicas ajudam a identificar a causa do problema.
        # Os códigos de erro mais comuns do MySQL Connector/Python são tratados
        # abaixo; outros erros são exibidos de forma genérica.
        codigo = getattr(erro, "errno", None)

        if codigo == 2003:
            print(
                "Erro de conexão: não foi possível conectar ao servidor MySQL. "
                "Verifique se o servidor está ligado e se o host/porta estão corretos."
            )
        elif codigo == 1045:
            print(
                "Erro de autenticação: usuário ou senha inválidos. "
                "Verifique as credenciais configuradas em conexao.py."
            )
        elif codigo == 1049:
            print(
                "Erro de banco de dados: o banco 'bcdados' não foi encontrado. "
                "Verifique se o banco foi criado no MySQL."
            )
        else:
            print(f"Erro ao conectar ao MySQL: {erro}")

        return None

    except Exception as erro:
        # Captura erros inesperados que não sejam do mysql.connector,
        # sem esconder o problema silenciosamente.
        print(f"Erro inesperado ao tentar conectar ao banco de dados: {erro}")
        return None
