SELECT
    e.id_equipamento,
    e.tipo,
    e.marca,
    e.modelo,
    e.numero_serie,
    c.id_cliente,
    c.nome AS cliente,
    c.telefone,
    c.email

FROM equipamentos e

INNER JOIN clientes c
    ON e.id_cliente = c.id_cliente;

SELECT
    os.id_ordem,
    c.nome AS cliente,
    c.telefone,
    e.tipo AS equipamento,
    e.marca,
    e.modelo,
    e.numero_serie,
    t.nome AS tecnico,
    os.defeito_relatado,
    os.diagnostico,
    os.servico_realizado,
    os.status,
    os.data_abertura,
    os.data_conclusao,
    os.valor_servico

FROM ordens_servico os

INNER JOIN equipamentos e
    ON os.id_equipamento = e.id_equipamento

INNER JOIN clientes c
    ON e.id_cliente = c.id_cliente

LEFT JOIN tecnicos t
    ON os.id_tecnico = t.id_tecnico;
