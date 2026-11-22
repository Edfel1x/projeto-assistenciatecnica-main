"""Migrações idempotentes para bancos já existentes.

O schema.sql atende instalações novas. Quem já cadastrou equipamentos antes
do campo de status/diagnóstico precisa apenas iniciar o servidor uma vez:
`python -m backend.app` aplica esta migração automaticamente.

A função também pode ser chamada diretamente:
    python -m backend.migracoes
"""

from .database import conectar

_CACHE_COLUNAS = None

# Definições SQL das colunas acrescentadas à tabela equipamentos.
COLUNAS_EQUIPAMENTOS = {
    "status": """ENUM('Disponível', 'Em análise', 'Em manutenção',
                      'Aguardando peça', 'Pronto para entrega', 'Entregue')
                 NOT NULL DEFAULT 'Disponível'""",
    "diagnostico": "TEXT NULL",
}


def colunas_disponiveis() -> set[str]:
    """Nome das colunas de equipamentos existentes no banco em uso.

    Resultado cacheado por processo. Se a consulta falhar (banco fora do ar
    ou usuário sem acesso ao INFORMATION_SCHEMA), devolve conjunto vazio:
    o service então usa apenas o armazenamento local de situação.
    """
    global _CACHE_COLUNAS
    if _CACHE_COLUNAS is None:
        try:
            conexao = conectar()
            try:
                cursor = conexao.cursor()
                try:
                    cursor.execute(
                        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                        "WHERE TABLE_SCHEMA = DATABASE() "
                        "AND TABLE_NAME = 'equipamentos'"
                    )
                    _CACHE_COLUNAS = {linha[0] for linha in cursor.fetchall()}
                finally:
                    cursor.close()
            finally:
                if conexao.is_connected():
                    conexao.close()
        except Exception:
            _CACHE_COLUNAS = set()
    return _CACHE_COLUNAS


def aplicar_migracoes() -> list[str]:
    """Cria colunas ausentes. Retorna a lista de alterações realizadas.

    Segura para executar várias vezes: consulta INFORMATION_SCHEMA antes de
    cada ALTER TABLE e nunca remove nem modifica dados existentes.
    """
    alteracoes = []
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        try:
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'equipamentos'"
            )
            existentes = {linha[0] for linha in cursor.fetchall()}

            for coluna, definicao in COLUNAS_EQUIPAMENTOS.items():
                if coluna in existentes:
                    continue
                cursor.execute(
                    f"ALTER TABLE equipamentos ADD COLUMN {coluna} {definicao}"
                )
                alteracoes.append(coluna)

            conexao.commit()
            global _CACHE_COLUNAS
            _CACHE_COLUNAS = existentes | set(alteracoes)
        finally:
            cursor.close()
    finally:
        if conexao.is_connected():
            conexao.close()
    return alteracoes


if __name__ == "__main__":
    feitas = aplicar_migracoes()
    if feitas:
        print("Migração aplicada. Colunas adicionadas:", ", ".join(feitas))
    else:
        print("Banco já estava atualizado. Nenhuma alteração necessária.")
