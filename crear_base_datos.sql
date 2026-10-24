-- IEI_N4_C3: preparación de base de datos MySQL/MariaDB.
-- EJECUTAR como administrador en un servidor local COMPATIBLE con Django.
-- ANTES DE EJECUTAR: sustituir el marcador por una clave PRIVADA robusta.
-- NO subir una versión con la contraseña real a GitHub.
-- No crea las tablas de Django: se crean después con `python manage.py migrate`.

CREATE DATABASE IF NOT EXISTS `incidencias`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'bibliohub_app'@'127.0.0.1'
    IDENTIFIED BY 'REEMPLAZAR_CON_PASSWORD_LOCAL';

-- Derechos de datos y modificaciones estructurales requeridos por migraciones.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `incidencias`.* TO 'bibliohub_app'@'127.0.0.1';

SHOW GRANTS FOR 'bibliohub_app'@'127.0.0.1';
