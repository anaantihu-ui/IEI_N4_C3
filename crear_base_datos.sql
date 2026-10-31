-- IEI_N4_C3: preparación de base de datos MySQL/MariaDB.
-- Ejecutar como administrador en MySQL 8 o MariaDB 10.5+ LOCAL.
-- Credenciales PUBLICAS de demostracion: coinciden con .env y .env.example.
-- Solo para un entorno academico aislado; no usar con datos reales.
-- Al repetir el script se restablece la clave de estos usuarios de demostracion.
-- Para claves privadas, editar una copia crear_base_datos_local.sql y .env.local.
-- No crea las tablas de Django: se crean después con `python manage.py migrate`.

CREATE DATABASE IF NOT EXISTS `incidencias`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'bibliohub_app'@'127.0.0.1'
    IDENTIFIED BY 'bibliohub_pass2026';
CREATE USER IF NOT EXISTS 'bibliohub_app'@'localhost'
    IDENTIFIED BY 'bibliohub_pass2026';
ALTER USER 'bibliohub_app'@'127.0.0.1' IDENTIFIED BY 'bibliohub_pass2026';
ALTER USER 'bibliohub_app'@'localhost' IDENTIFIED BY 'bibliohub_pass2026';

-- Derechos de datos y modificaciones estructurales requeridos por migraciones.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `incidencias`.* TO 'bibliohub_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `incidencias`.* TO 'bibliohub_app'@'localhost';

SHOW GRANTS FOR 'bibliohub_app'@'127.0.0.1';
SHOW GRANTS FOR 'bibliohub_app'@'localhost';
