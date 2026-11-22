"""Testes da tradução de erros do MySQL para exceções de domínio."""

import pytest

from backend.database import (
    DatabaseConstraintError,
    DatabaseUnavailable,
    traduzir_erro_mysql,
)


class ErroMysqlFalso:
    """Erro mínimo: traduzir_erro_mysql só lê o atributo errno."""

    def __init__(self, errno):
        self.errno = errno


@pytest.mark.parametrize('codigo', [1216, 1217, 1451, 1452])
def test_violacao_de_chave_estrangeira_vira_conflito(codigo):
    """Registro com vínculos deve responder 409, não 503.

    Regressão: o MySQL local devolve 1217 ao excluir um técnico com ordens;
    como só 1451/1452 eram tratados, o botão de excluir exibia erro 503.
    """
    with pytest.raises(DatabaseConstraintError) as info:
        traduzir_erro_mysql(ErroMysqlFalso(codigo))
    assert 'vinculados' in str(info.value)


def test_erro_desconhecido_continua_sendo_indisponibilidade():
    with pytest.raises(DatabaseUnavailable):
        traduzir_erro_mysql(ErroMysqlFalso(9999))
