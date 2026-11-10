-- ============================================================
-- Script SQL - Plataforma de Voluntariados y Actividades Comunitarias
-- Sistema: IEI_N4_C3
-- Motor: SQLite (desarrollo) / MySQL o PostgreSQL (produccion)
-- ============================================================

-- Para SQLite: la base de datos se genera automaticamente con:
--   python manage.py migrate

-- Para MySQL (produccion):
-- CREATE DATABASE voluntariados CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- CREATE USER 'vol_user'@'localhost' IDENTIFIED BY 'password123';
-- GRANT ALL PRIVILEGES ON voluntariados.* TO 'vol_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Para PostgreSQL (produccion):
-- CREATE DATABASE voluntariados;
-- CREATE USER vol_user WITH PASSWORD 'password123';
-- GRANT ALL PRIVILEGES ON DATABASE voluntariados TO vol_user;

-- ============================================================
-- Tablas del sistema (generadas por Django ORM / migraciones)
-- ============================================================
-- region            : Regiones geograficas
-- comuna            : Comunas por region
-- perfil            : Perfiles de acceso al sistema
-- organizacion      : Organizaciones sociales
-- categoria         : Categorias de actividades
-- estado            : Estados posibles de actividades
-- voluntario        : Personas voluntarias registradas
-- coordinador       : Coordinadores de actividades
-- actividad         : Actividades comunitarias
-- inscripcion       : Inscripciones de voluntarios
-- recurso           : Recursos disponibles
-- asignacion_recurso: Recursos asignados a actividades
-- historial_estado  : Auditoria de cambios de estado
-- ============================================================
