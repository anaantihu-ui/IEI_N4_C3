# Guía para explicar los cambios ante el profesor

## Qué se hizo realmente

Se mejoró la **configuración de un proyecto Django de clases**. Se agregó un script de creación de base MySQL/MariaDB con usuario y permisos, un `.env` público de ejemplo, un `.env.local` privado opcional, la configuración de MySQL en `settings.py`, dependencias y documentación. Se conservaron las páginas existentes y la ruta administrativa.

## Respuestas breves

**¿Para qué sirve `crear_base_datos.sql`?** Crea la base `incidencias`, el usuario `bibliohub_app` y le otorga permisos sobre ella. Django crea las tablas con `migrate`.

**¿Para qué sirve `.env`?** Para separar parámetros de configuración del código. Por requisito académico se publica **solo con valores ficticios**. Los datos reales se dejan en `.env.local` o en variables del sistema.

**¿Por qué modificar `.gitignore`?** Git ignoraba `.env`; ahora permite subir la plantilla académica, pero excluye `.env.local`, los entornos virtuales, cachés y bases SQLite locales.

**¿Qué hace `settings.py`?** Registra apps, middleware, plantillas, claves y motor de base de datos; aquí lee los valores mediante `python-decouple`.

**¿Qué hacen `makemigrations` y `migrate`?** El primero genera cambios de esquemas desde modelos; el segundo aplica migraciones a la BD.

**¿Qué diferencia hay entre SQLite y MySQL?** SQLite guarda datos en un archivo; MySQL es un servidor de base de datos con autenticación y permisos.

**¿Qué modelos y API se entregan?** En el ZIP suministrado los `models.py` están vacíos y no hay API REST. No debes afirmar que tiene 18 modelos bibliotecarios o endpoints ModelViewSet sin aportar otra versión del código.

**¿Qué falta comprobar?** Ejecutar la instalación con MySQL local compatible, efectuar migraciones y confirmar la ejecución en el computador de entrega.
