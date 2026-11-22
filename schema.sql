
CREATE DATABASE IF NOT EXISTS assistencia_tecnica;
USE assistencia_tecnica;


CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100)
);

CREATE TABLE tecnicos (
    id_tecnico INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    especialidade VARCHAR(100) NOT NULL
);

CREATE TABLE equipamentos (
    id_equipamento INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    numero_serie VARCHAR(100),

    status ENUM(
        'Disponível',
        'Em análise',
        'Em manutenção',
        'Aguardando peça',
        'Pronto para entrega',
        'Entregue'
    ) NOT NULL DEFAULT 'Disponível',
    diagnostico TEXT NULL,

    CONSTRAINT fk_equipamento_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE ordens_servico (
    id_ordem INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento INT NOT NULL,
    id_tecnico INT NULL,
    defeito_relatado TEXT NOT NULL,
    diagnostico TEXT,
    servico_realizado TEXT,

    status ENUM(
        'Aberta',
        'Em manutenção',
        'Concluída',
        'Cancelada'
    ) NOT NULL DEFAULT 'Aberta',

    data_abertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_conclusao DATETIME,
    valor_servico DECIMAL(10,2),

    CONSTRAINT fk_ordem_equipamento
        FOREIGN KEY (id_equipamento)
        REFERENCES equipamentos(id_equipamento)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_ordem_tecnico
        FOREIGN KEY (id_tecnico)
        REFERENCES tecnicos(id_tecnico)
        ON DELETE RESTRICT,

    CONSTRAINT chk_valor_servico
        CHECK (
            valor_servico IS NULL
            OR valor_servico >= 0
        ),

    CONSTRAINT chk_ordem_concluida
        CHECK (
            status <> 'Concluída'
            OR (
                id_tecnico IS NOT NULL
                AND data_conclusao IS NOT NULL
            )
        )
);
