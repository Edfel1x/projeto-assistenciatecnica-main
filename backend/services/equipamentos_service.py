"""Operações de equipamentos sobre o MySQL.

Campos cadastrais da tabela (schema.sql):
    id_equipamento, id_cliente, tipo, marca, modelo, numero_serie
Campos de situação:
    status, diagnostico

Quando o usuário do banco não tem permissão de ALTER, `status` e
`diagnostico` ainda não existem no MySQL. Nesse caso eles são guardados em
`backend/armazenamento_situacao.py` e devolvidos junto com o equipamento.
Com as colunas presentes, o service grava nos dois lugares.
"""

from .. import armazenamento_situacao
from ..database import obter_conexao, transacao
from ..migracoes import colunas_disponiveis
from . import clientes_service
from .common import (
    NotFoundError,
    ValidationError,
    inteiro_positivo,
    serializar_registro,
    texto_obrigatorio,
    texto_opcional,
)

# Mesmos valores do frontend (equipamentos.js) e do ENUM em schema.sql.
STATUS_PERMITIDOS = (
    "Disponível",
    "Em análise",
    "Em manutenção",
    "Aguardando peça",
    "Pronto para entrega",
    "Entregue",
)
STATUS_PADRAO = "Disponível"
TAMANHO_DIAGNOSTICO = 65535  # TEXT do MySQL


def validar_status(valor) -> str:
    """Aceita apenas um dos status definidos para o equipamento."""
    if valor is None:
        raise ValidationError("O campo 'status' é obrigatório.")
    if not isinstance(valor, str):
        raise ValidationError("O campo 'status' deve ser um texto.")
    status = valor.strip()
    if status not in STATUS_PERMITIDOS:
        raise ValidationError(
            "Status inválido. Use: " + ", ".join(STATUS_PERMITIDOS) + "."
        )
    return status


def _tem_colunas_situacao() -> bool:
    colunas = colunas_disponiveis()
    return "status" in colunas and "diagnostico" in colunas


def _campos() -> str:
    """SELECT compatível com bancos migrados e não migrados."""
    base = """e.id_equipamento, e.id_cliente, e.tipo, e.marca, e.modelo,
              e.numero_serie"""
    if _tem_colunas_situacao():
        base += ", e.status, e.diagnostico"
    return base + ", c.nome AS nome_cliente"


def _completar(registro: dict | None) -> dict | None:
    """Junta a situação local ao registro vindo do MySQL."""
    if registro is None:
        return None
    situacao = armazenamento_situacao.obter(registro["id_equipamento"])
    registro["status"] = (
        situacao.get("status") or registro.get("status") or STATUS_PADRAO
    )
    registro["diagnostico"] = situacao.get(
        "diagnostico", registro.get("diagnostico")
    )
    return registro


def listar() -> list[dict]:
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {_campos()} FROM equipamentos e "
                "INNER JOIN clientes c ON e.id_cliente = c.id_cliente "
                "ORDER BY e.id_equipamento DESC"
            )
            return [_completar(serializar_registro(reg)) for reg in cursor.fetchall()]
        finally:
            cursor.close()


def buscar_por_id(id_equipamento: int) -> dict | None:
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {_campos()} FROM equipamentos e "
                "INNER JOIN clientes c ON e.id_cliente = c.id_cliente "
                "WHERE e.id_equipamento = %s",
                (id_equipamento,),
            )
            return _completar(serializar_registro(cursor.fetchone()))
        finally:
            cursor.close()


def criar(dados: dict) -> dict:
    id_cliente = inteiro_positivo(dados.get("id_cliente"), "id_cliente")
    if clientes_service.buscar_por_id(id_cliente) is None:
        raise NotFoundError("Cliente não encontrado para o equipamento.")

    tipo = texto_obrigatorio(dados.get("tipo"), "tipo", 50)
    marca = texto_obrigatorio(dados.get("marca"), "marca", 50)
    modelo = texto_obrigatorio(dados.get("modelo"), "modelo", 100)
    numero_serie = texto_obrigatorio(dados.get("numero_serie"), "numero_serie", 100)
    status = validar_status(dados["status"]) if "status" in dados else STATUS_PADRAO
    diagnostico = texto_opcional(
        dados.get("diagnostico"), "diagnostico", TAMANHO_DIAGNOSTICO
    )

    colunas = ["id_cliente", "tipo", "marca", "modelo", "numero_serie"]
    valores = [id_cliente, tipo, marca, modelo, numero_serie]
    if _tem_colunas_situacao():
        colunas += ["status", "diagnostico"]
        valores += [status, diagnostico]

    marcadores = ", ".join(["%s"] * len(colunas))
    with transacao() as (_, cursor):
        cursor.execute(
            f"INSERT INTO equipamentos ({', '.join(colunas)}) VALUES ({marcadores})",
            tuple(valores),
        )
        novo_id = cursor.lastrowid

    armazenamento_situacao.salvar(
        novo_id, status=status, diagnostico=diagnostico
    )
    return buscar_por_id(novo_id)


def _campos_cadastro(dados: dict) -> tuple[list[str], list]:
    """Cláusulas/valores dos campos cadastrais enviados na atualização."""
    atualizacoes = []
    valores = []
    if "id_cliente" in dados:
        id_cliente = inteiro_positivo(dados["id_cliente"], "id_cliente")
        if clientes_service.buscar_por_id(id_cliente) is None:
            raise NotFoundError("Cliente não encontrado para o equipamento.")
        atualizacoes.append("id_cliente = %s")
        valores.append(id_cliente)
    for campo, tamanho in (("tipo", 50), ("marca", 50), ("modelo", 100), ("numero_serie", 100)):
        if campo in dados:
            atualizacoes.append(f"{campo} = %s")
            valores.append(texto_obrigatorio(dados[campo], campo, tamanho))
    return atualizacoes, valores


def _normalizar_situacao(dados: dict) -> dict:
    """Valida e devolve somente status/diagnostico presentes no payload."""
    situacao = {}
    if "status" in dados:
        situacao["status"] = validar_status(dados["status"])
    if "diagnostico" in dados:
        # Texto vazio limpa o diagnóstico (volta para None).
        situacao["diagnostico"] = texto_opcional(
            dados["diagnostico"], "diagnostico", TAMANHO_DIAGNOSTICO
        )
    return situacao


def _clausulas_situacao(situacao: dict) -> tuple[list[str], list]:
    """Cláusulas SQL apenas se as colunas existirem no banco em uso."""
    if not _tem_colunas_situacao():
        return [], []
    atualizacoes = []
    valores = []
    for campo in ("status", "diagnostico"):
        if campo in situacao:
            atualizacoes.append(f"{campo} = %s")
            valores.append(situacao[campo])
    return atualizacoes, valores


def _salvar(id_equipamento: int, atualizacoes: list[str], valores: list) -> dict:
    if atualizacoes:
        valores.append(id_equipamento)
        with transacao() as (_, cursor):
            cursor.execute(
                f"UPDATE equipamentos SET {', '.join(atualizacoes)} "
                "WHERE id_equipamento = %s",
                tuple(valores),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Equipamento não encontrado.")
    return buscar_por_id(id_equipamento)


def atualizar(id_equipamento: int, dados: dict) -> dict:
    if buscar_por_id(id_equipamento) is None:
        raise NotFoundError("Equipamento não encontrado.")

    atualizacoes, valores = _campos_cadastro(dados)
    situacao = _normalizar_situacao(dados)
    sit_sql, sit_valores = _clausulas_situacao(situacao)
    atualizacoes += sit_sql
    valores += sit_valores

    if not atualizacoes:
        raise ValidationError("Nenhum campo válido foi informado para atualização.")

    if situacao:
        armazenamento_situacao.salvar(id_equipamento, **situacao)
    return _salvar(id_equipamento, atualizacoes, valores)


def atualizar_situacao(id_equipamento: int, dados: dict) -> dict:
    """Atualiza somente status e/ou diagnóstico do equipamento."""
    if buscar_por_id(id_equipamento) is None:
        raise NotFoundError("Equipamento não encontrado.")

    situacao = _normalizar_situacao(dados)
    if not situacao:
        raise ValidationError("Informe 'status' e/ou 'diagnostico'.")

    atualizacoes, valores = _clausulas_situacao(situacao)
    armazenamento_situacao.salvar(id_equipamento, **situacao)
    return _salvar(id_equipamento, atualizacoes, valores)


def excluir(id_equipamento: int) -> None:
    with transacao() as (_, cursor):
        cursor.execute(
            "DELETE FROM equipamentos WHERE id_equipamento = %s", (id_equipamento,)
        )
        if cursor.rowcount == 0:
            raise NotFoundError("Equipamento não encontrado.")
    armazenamento_situacao.remover(id_equipamento)
