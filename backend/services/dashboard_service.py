"""Indicadores do dashboard, calculados diretamente no MySQL."""

from ..database import obter_conexao
from .common import serializar_registro

JOINS_STATUS = """FROM ordens_servico os
                  INNER JOIN equipamentos e ON os.id_equipamento = e.id_equipamento
                  INNER JOIN clientes c ON e.id_cliente = c.id_cliente
                  LEFT JOIN tecnicos t ON os.id_tecnico = t.id_tecnico"""


def obter_resumo() -> dict:
    """Retorna contagens e ordens recentes reais do banco."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT
                     (SELECT COUNT(*) FROM clientes) AS total_clientes,
                     (SELECT COUNT(*) FROM tecnicos) AS total_tecnicos,
                     (SELECT COUNT(*) FROM equipamentos) AS total_equipamentos,
                     (SELECT COUNT(*) FROM ordens_servico) AS total_ordens,
                     (SELECT COUNT(*) FROM ordens_servico
                       WHERE status = 'Em manutenção') AS ordens_em_andamento,
                     (SELECT COUNT(*) FROM ordens_servico
                       WHERE status = 'Concluída') AS ordens_finalizadas,
                     (SELECT COUNT(*) FROM ordens_servico
                       WHERE status = 'Aberta') AS ordens_pendentes,
                     (SELECT COUNT(*) FROM ordens_servico
                       WHERE status = 'Cancelada') AS ordens_canceladas"""
            )
            resumo = cursor.fetchone() or {}

            cursor.execute(
                f"""SELECT os.id_ordem, os.defeito_relatado, os.status,
                           os.data_abertura, os.data_conclusao, os.valor_servico,
                           e.tipo AS tipo_equipamento, e.marca AS marca_equipamento,
                           e.modelo AS modelo_equipamento,
                           c.nome AS nome_cliente,
                           t.nome AS nome_tecnico
                    {JOINS_STATUS}
                    ORDER BY os.data_abertura DESC, os.id_ordem DESC
                    LIMIT 5"""
            )
            recentes = [
                serializar_registro(reg) for reg in cursor.fetchall()
            ]

            cursor.execute(
                """SELECT status, COUNT(*) AS quantidade
                   FROM ordens_servico GROUP BY status ORDER BY status"""
            )
            por_status = {
                reg["status"]: reg["quantidade"] for reg in cursor.fetchall()
            }
        finally:
            cursor.close()

    resultado = serializar_registro(resumo) or {}
    resultado["ordens_recentes"] = recentes
    resultado["ordens_por_status"] = por_status
    return resultado
