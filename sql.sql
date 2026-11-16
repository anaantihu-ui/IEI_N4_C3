-- Plataforma de Voluntariados y Actividades Comunitarias (IEI_N4_C3)
-- MySQL 8.0.11+ / MariaDB 10.5+ compatible con Django 5.2.
-- Ejecutar con una cuenta administradora, por ejemplo desde phpMyAdmin.
--
-- IMPORTANTE: cambie la clave de ejemplo ANTES de ejecutar este script
-- en su equipo. NO publique su contraseña real en GitHub.
-- La creación de las tablas de los 13 modelos corresponde al ORM de Django:
--     python manage.py migrate

CREATE DATABASE IF NOT EXISTS voluntariados
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'vol_app'@'localhost'
    IDENTIFIED BY 'CAMBIAR_CLAVE_MYSQL_EN_EQUIPO';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON voluntariados.*
    TO 'vol_app'@'localhost';

SHOW GRANTS FOR 'vol_app'@'localhost';

-- Si el usuario ya existe, CREATE USER IF NOT EXISTS no cambia su clave.
-- En ese caso, use ALTER USER por separado, con una contraseña PRIVADA:
-- ALTER USER 'vol_app'@'localhost' IDENTIFIED BY 'SU_CLAVE_LOCAL';
-- No suba a GitHub una versión con credenciales reales.
