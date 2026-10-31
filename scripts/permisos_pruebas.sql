-- Opcional: ejecutar como administrador DESPUES de crear_base_datos.sql.
-- Django crea y elimina test_incidencias al ejecutar manage.py test.
-- No da permisos globales. El escape hace literales los guiones bajos del nombre.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `test\_incidencias`.* TO 'bibliohub_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `test\_incidencias`.* TO 'bibliohub_app'@'localhost';
