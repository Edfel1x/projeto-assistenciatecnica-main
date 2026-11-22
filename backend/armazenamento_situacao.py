"""Guarda status/diagnóstico dos equipamentos quando o MySQL não permite ALTER.

O usuário da API (bcdados_app) tem SELECT/INSERT/UPDATE/DELETE, mas não
ALTER em `bcdados`. Enquanto as colunas `status`/`diagnostico` não existem
na tabela equipamentos, estes dois campos vivem neste JSON local, com
escrita atômica. Se as colunas existirem, o service gravam nos dois lugares
e o JSON prevalece na leitura (é sempre o valor mais recente).

O arquivo fica em `dados/situacao_equipamentos.json` e é ignorado pelo Git.
As chaves incluem o nome do banco (config.DB_NAME) para que os testes de
integração, que usam `bcdados_teste`, nunca sobrescrevam a situação dos
equipamentos do banco principal com o mesmo ID.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from . import config

CAMINHO = Path(__file__).resolve().parents[1] / 'dados' / 'situacao_equipamentos.json'


def _chave(id_equipamento: int) -> str:
    """Identifica o equipamento dentro do banco em uso."""
    banco = (getattr(config, 'DB_NAME', '') or 'padrao').strip()
    return f"{banco}:{id_equipamento}"


def _carregar() -> dict:
    try:
        return json.loads(CAMINHO.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _gravar(dados: dict) -> None:
    CAMINHO.parent.mkdir(parents=True, exist_ok=True)
    temporario = CAMINHO.with_suffix('.tmp')
    temporario.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    os.replace(temporario, CAMINHO)


def obter(id_equipamento: int) -> dict:
    """Devolve {'status': ..., 'diagnostico': ...} ou {} se não houver registro."""
    return dict(_carregar().get(_chave(id_equipamento), {}))


def salvar(id_equipamento: int, **campos) -> dict:
    """Mescla os campos enviados. Valor None/vazio remove o campo (limpa)."""
    dados = _carregar()
    chave = _chave(id_equipamento)
    atual = dict(dados.get(chave, {}))
    for nome, valor in campos.items():
        if valor is None or valor == '':
            atual.pop(nome, None)
        else:
            atual[nome] = valor
    if atual:
        dados[chave] = atual
    else:
        dados.pop(chave, None)
    _gravar(dados)
    return atual


def remover(id_equipamento: int) -> None:
    dados = _carregar()
    if dados.pop(_chave(id_equipamento), None) is not None:
        _gravar(dados)
