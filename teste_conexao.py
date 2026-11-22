"""Teste independente da conexão com o banco de dados MySQL.

Este script apenas verifica se a conexão pode ser estabelecida.
Ele NÃO executa INSERT, UPDATE, DELETE ou qualquer operação que altere dados.
"""

from conexao import conectar


def testar_conexao():
    """Tenta conectar ao banco e exibe o resultado do teste."""
    print("Iniciando teste de conexão com o MySQL...")

    banco = conectar()

    if banco is None:
        print("Falha no teste: não foi possível estabelecer a conexão.")
        return

    try:
        # Verifica se o objeto realmente está conectado.
        if banco.is_connected():
            info_servidor = banco.get_server_info()
            print("Sucesso: conexão estabelecida com o MySQL.")
            print(f"Versão do servidor: {info_servidor}")
        else:
            print("Falha no teste: o objeto de conexão foi criado, mas não está conectado.")
    finally:
        # Fecha a conexão para não deixar recursos abertos desnecessariamente.
        if banco.is_connected():
            banco.close()
            print("Conexão encerrada corretamente.")


if __name__ == "__main__":
    testar_conexao()
