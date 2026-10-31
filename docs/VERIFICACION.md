# Verificación de la entrega

Fecha: 31 de octubre de 2026. Comprobación en un entorno local aislado de pruebas,
con Python 3.12, Django 5.2.17, Django REST Framework 3.16.1,
mysqlclient 2.3.0 y MySQL 8.0.46. Se utilizó la configuración pública de `.env`.

## Resultados obtenidos

| Comprobación | Resultado |
|---|---|
| `crear_base_datos.sql` en MySQL | Correcto, incluida una segunda ejecución |
| `scripts/permisos_pruebas.sql` | Correcto |
| `python manage.py check --database default` | Sin problemas detectados |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes |
| `python manage.py migrate --noinput` | Migraciones aplicadas; 18 tablas de biblio_app |
| `python manage.py migrate --check` | Sin migraciones pendientes |
| `python manage.py test --noinput -v 2` con MySQL | 25 pruebas, OK |
| Mismo comando con `DB_ENGINE=sqlite` | 25 pruebas, OK |

La suite comprueba las seis operaciones (GET lista, GET detalle, POST, PUT, PATCH,
DELETE) para cada una de las 18 entidades, persistencia y eliminación de registros,
validación de datos, autenticación, redirección después de iniciar sesión,
contraseñas de lectores y las páginas existentes.

La base de pruebas `test_incidencias` se crea y elimina durante la ejecución de
la suite. Los permisos adicionales están limitados a esa base. Las migraciones
de la demostración se aplicaron a `incidencias` con el usuario de aplicación.

## Comprobación HTTP adicional

Se inició Django con `runserver`, conectado a MySQL, y se enviaron peticiones HTTP
con Basic Auth usando una cuenta temporal. Se obtuvo:

```text
GET    /api/paises/      200
POST   /api/paises/      201
GET    /api/paises/1/    200
PUT    /api/paises/1/    200
PATCH  /api/paises/1/    200
DELETE /api/paises/1/    204
GET    /api/paises/1/    404
```

El identificador 1 corresponde a esta base vacía de prueba. En otro equipo se
debe usar el identificador devuelto por POST. Se eliminaron el registro y la
cuenta de comprobación al terminar.

## Decisiones respecto de la guía de auditoría

- Se conserva `.env` con valores públicos de demostración porque la consigna
  del profesor exige incluirlo. Las claves privadas se guardan en `.env.local`,
  excluido de Git. No se incorporó una contraseña literal a `settings.py`.
- SQL y `.env` coinciden. El SQL también actualiza la contraseña de los usuarios
  de demostración existentes, por lo que se puede repetir en ese entorno local.
- SQLite se selecciona explícitamente. Un error de conexión a MySQL no cambia
  silenciosamente el almacenamiento a otra base.
- Los hosts y orígenes CSRF se configuran por variables; no se habilitó `*`.
- Se reemplazó la advertencia sobre MySQL por resultados comprobados. No se
  afirma una nota ni un cumplimiento del 100%: también se evalúan el diseño
  asignado, las evidencias presentadas y las cinco respuestas individuales.

Esta comprobación no certifica la instalación en el equipo del profesor ni en
el de la estudiante. MariaDB no se ejecutó en esta revisión. Para reproducir la
comprobación y preparar las evidencias, seguir el README.
