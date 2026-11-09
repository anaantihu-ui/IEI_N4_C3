-- Opcional, como administrador. Django crea y elimina esta base durante sus tests.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `test\_voluntariados`.* TO 'voluntariados_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
    ON `test\_voluntariados`.* TO 'voluntariados_app'@'localhost';
