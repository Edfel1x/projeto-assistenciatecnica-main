-- Script para criar o usuário dedicado à aplicação BCDADOS.
-- Execute no MySQL com uma conta administrativa:
--   mysql -u root -p < docs/sql/usuario_teste.sql
--
-- Depois, copie .env.example para .env e use:
--   DB_USER=bcdados_app
--   DB_PASSWORD=(deixe em branco, conforme criado abaixo)
--   DB_NAME=bcdados   (ou assistencia_tecnica, se usar o schema.sql original)
--   DB_NAME_TEST=bcdados_teste   (banco exclusivo dos testes de integração)

CREATE USER IF NOT EXISTS 'bcdados_app'@'localhost' IDENTIFIED BY '';

-- Aplicação: apenas as operações necessárias para o CRUD.
-- Ajuste o nome do banco conforme o configurado em DB_NAME no .env.
GRANT SELECT, INSERT, UPDATE, DELETE ON bcdados.* TO 'bcdados_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON assistencia_tecnica.* TO 'bcdados_app'@'localhost';

-- Testes de integração: a suíte recria as tabelas a partir do schema.sql,
-- portanto precisa de CREATE/DROP neste banco exclusivo.
-- Importante: CREATE DATABASE exige privilégio global, que NÃO é concedido
-- ao usuário da aplicação. Por isso o banco é criado aqui, pela conta admin.
CREATE DATABASE IF NOT EXISTS bcdados_teste;
GRANT ALL PRIVILEGES ON bcdados_teste.* TO 'bcdados_app'@'localhost';

FLUSH PRIVILEGES;
