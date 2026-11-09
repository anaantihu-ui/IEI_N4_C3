-- Solo para demostracion LOCAL. Coincide con .env publico requerido en la entrega.
-- Para claves privadas usar crear_base_datos_local.sql y .env.local, excluidos de Git.
-- Las tablas se crean con python manage.py migrate.
CREATE DATABASE IF NOT EXISTS `voluntariados`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'voluntariados_app'@'127.0.0.1' IDENTIFIED BY 'demo_voluntariados2026';
CREATE USER IF NOT EXISTS 'voluntariados_app'@'localhost' IDENTIFIED BY 'demo_voluntariados2026';
-- Repetir el script restablece SOLO la clave de estos usuarios de demostracion.
ALTER USER 'voluntariados_app'@'127.0.0.1' IDENTIFIED BY 'demo_voluntariados2026';
ALTER USER 'voluntariados_app'@'localhost' IDENTIFIED BY 'demo_voluntariados2026';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `voluntariados`.* TO 'voluntariados_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `voluntariados`.* TO 'voluntariados_app'@'localhost';
SHOW GRANTS FOR 'voluntariados_app'@'127.0.0.1';
