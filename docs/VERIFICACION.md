# Verificación de la plataforma de voluntariados

Comprobación realizada el 9 de noviembre de 2026 en un entorno aislado con
Python 3.12.14, Django 5.2.17, DRF 3.16.1, mysqlclient 2.3.0 y MySQL 8.0.46.
Se instalaron las dependencias de requirements.txt y se usó el .env público.

| Comprobación | Resultado |
|---|---|
| SQL de creación ejecutado dos veces | Correcto |
| SQL de permisos de pruebas | Correcto |
| `check --database default` | Sin problemas |
| `makemigrations --check --dry-run` | Sin cambios pendientes |
| `migrate --noinput` y `migrate --check` | Migraciones aplicadas, sin pendientes |
| Suite en MySQL | **40 pruebas aprobadas**, ninguna omitida |
| Suite en SQLite | **37 aprobadas y 3 omitidas**, exclusivamente las de concurrencia MySQL |
| Carga demo repetida dos veces | Correcta, sin duplicar cuentas ni actividad |
| HTTP real: GET lista/detalle, POST, PUT, PATCH, DELETE | Estados esperados: 200, 201 y 204 |
| HTTP después de eliminar | 404 |
| HTTP de voluntario: inscripción y cancelación | 201 y 200 |
| HTTP de coordinador: indicadores y auditoría | 200 |
| HTTP de voluntario: acceso a auditoría | 403 |

Las pruebas abarcan CRUD de las diez entidades operativas, aislamiento entre
organizaciones, perfiles privados, roles, contraseñas, fechas, cupos, inscripciones
duplicadas, asistencia, recursos superpuestos, transiciones, incidencias,
indicadores y auditoría con reversión ante errores.

Las tres pruebas concurrentes de MySQL comprobaron: dos personas disputando el
último cupo (una aceptada y otra rechazada), dos reservas superpuestas por encima
del inventario (una aceptada y otra rechazada) y reservas en horarios separados
(ambas aceptadas).

## Salidas conservadas

- [Suite MySQL](evidencias/mysql-tests.txt).
- [Suite SQLite](evidencias/sqlite-tests.txt).
- [Preparación, carga demo y prueba HTTP](evidencias/mysql-http.txt).

Los IDs de las pruebas HTTP corresponden a esa base aislada y pueden variar en
otra instalación. No se utilizaron datos personales reales. La carga demo y la
cuenta técnica de comprobación existieron únicamente en ese entorno de pruebas.

Esto demuestra la ejecución de esta versión en el entorno indicado. No sustituye
la instalación y demostración en el equipo de entrega, ni las cinco respuestas
individuales. No certifica una calificación. El alcance y las decisiones derivadas
del enunciado se detallan en MODELO_Y_REGLAS.md.
