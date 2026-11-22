"""Tipos e utilitários compartilhados pelos services."""

import math
from datetime import date, datetime
from decimal import Decimal


class ValidationError(Exception):
    """Dados enviados pelo cliente são inválidos (HTTP 400/422)."""


class NotFoundError(Exception):
    """Recurso solicitado não existe (HTTP 404)."""


class ConflictError(Exception):
    """Operação conflita com o estado atual ou com regras de negócio (HTTP 409)."""


def texto_obrigatorio(valor, nome: str, tamanho_maximo: int | None = None) -> str:
    """Valida um campo de texto obrigatório e devolve a string limpa."""
    if valor is None:
        raise ValidationError(f"O campo '{nome}' é obrigatório.")
    if not isinstance(valor, str):
        raise ValidationError(f"O campo '{nome}' deve ser um texto.")
    valor = valor.strip()
    if not valor:
        raise ValidationError(f"O campo '{nome}' não pode estar vazio.")
    if tamanho_maximo is not None and len(valor) > tamanho_maximo:
        raise ValidationError(
            f"O campo '{nome}' deve ter no máximo {tamanho_maximo} caracteres."
        )
    return valor


def texto_opcional(valor, nome: str, tamanho_maximo: int | None = None) -> str | None:
    """Valida um campo opcional. String vazia é convertida para None."""
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise ValidationError(f"O campo '{nome}' deve ser um texto.")
    valor = valor.strip()
    if not valor:
        return None
    if tamanho_maximo is not None and len(valor) > tamanho_maximo:
        raise ValidationError(
            f"O campo '{nome}' deve ter no máximo {tamanho_maximo} caracteres."
        )
    return valor


def inteiro_positivo(valor, nome: str) -> int:
    """Valida um ID inteiro positivo.

    Aceita apenas int (não-booleano) ou string de dígitos. Floats são
    rejeitados para evitar truncamento silencioso (ex.: 1.9 → 1).
    """
    if valor is None or isinstance(valor, bool):
        raise ValidationError(f"O campo '{nome}' é obrigatório.")
    if isinstance(valor, int):
        numero = valor
    elif isinstance(valor, str) and valor.strip().isdigit():
        numero = int(valor.strip())
    else:
        raise ValidationError(f"O campo '{nome}' deve ser um número inteiro.")
    if numero <= 0:
        raise ValidationError(f"O campo '{nome}' deve ser maior que zero.")
    return numero


def valor_monetario(valor) -> float:
    """Valida um valor monetário não negativo.

    Aceita number ou string com vírgula decimal (ex.: '125,90'), replicando
    o comportamento da função finalizar_ordem() original.
    """
    if valor is None or isinstance(valor, bool):
        raise ValidationError("O campo 'valor_servico' é obrigatório.")
    try:
        if isinstance(valor, str):
            numero = float(valor.strip().replace(",", "."))
        else:
            numero = float(valor)
    except (TypeError, ValueError):
        raise ValidationError("Informe um valor válido para o serviço.") from None
    # float('nan') e infinitos passariam pela comparação abaixo e gerariam
    # JSON inválido ou erro no MySQL (DECIMAL).
    if not math.isfinite(numero):
        raise ValidationError("Informe um valor válido para o serviço.")
    if numero < 0:
        raise ValidationError("O valor do serviço não pode ser negativo.")
    # DECIMAL(10,2): no máximo duas casas decimais.
    return round(numero, 2)


def serializar(valor):
    """Converte tipos do MySQL para tipos serializáveis em JSON."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat(sep=" ") if isinstance(valor, datetime) else valor.isoformat()
    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")
    return valor


def serializar_registro(registro: dict | None) -> dict | None:
    """Serializa todos os valores de um registro retornado pelo cursor."""
    if registro is None:
        return None
    return {chave: serializar(valor) for chave, valor in registro.items()}
