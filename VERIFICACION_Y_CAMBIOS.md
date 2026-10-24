# Verificación y cambios de la entrega

## Base examinada

Se utilizó el contenido de `IEI_N4_C3-main (2).zip` proporcionado en esta conversación. En la copia analizada:

- `drf/settings.py` usaba SQLite y contenía la clave `SECRET_KEY` escrita en el código.
- `.gitignore` ignoraba `.env`.
- `drf/urls.py` redefinía `urlpatterns` dos veces.
- `incidencias/models.py` y `mi_app/models.py` no definían modelos.
- `requirements.txt` estaba en UTF-16 y no contenía `python-decouple` ni `mysqlclient`.
- La carpeta ZIP incluía `.git/`, dos entornos virtuales y `db.sqlite3` local.
- No se encontraron serializers, API REST ni modelos del sistema bibliotecario descrito previamente.

## Cambios incorporados

1. `crear_base_datos.sql` con `CREATE DATABASE`, `CREATE USER`, `GRANT` y `SHOW GRANTS`.
2. `.env` con marcadores para publicación académica y `.env.example`.
3. Configuración privada alternativa `.env.local`, ignorada por Git y **no incluida**.
4. `.gitignore` modificado para permitir `.env`, excluir archivos privados, bases locales y entornos.
5. `drf/settings.py` configurado para MySQL por defecto, con SQLite opcional solo para pruebas; se quitó la clave literal del código.
6. `drf/urls.py` simplificado, conservando las rutas existentes y el manejador de 404.
7. `requirements.txt` pasado a UTF-8 y actualizado con las dependencias de configuración/MySQL.
8. `README.md` actualizado con instrucciones reales de instalación, seguridad y alcance.
9. `mi_app/tests.py` con pruebas para las vistas existentes.
10. `scripts/verificar_entrega.py` y `GUIA_DEFENSA.md`.

## Pruebas realizadas

- **OK:** compilación sintáctica de los archivos Python.
- **OK:** verificación estática de archivos exigidos y cláusulas SQL presentes.
- **OK:** `python manage.py check` con `DB_ENGINE=sqlite`, usando la copia de Django contenida en el ZIP original y un adaptador temporal de pruebas en lugar de `python-decouple` (no disponible para instalar en el entorno de validación). El adaptador **no está incluido** en la entrega.
- **OK:** 2 pruebas de `mi_app` (inicio 200 y ruta inexistente 404) en esas mismas condiciones de prueba.
- **PENDIENTE:** instalar y verificar las dependencias reales desde `requirements.txt` en el equipo de entrega.
- **PENDIENTE:** ejecutar el SQL contra un MySQL/MariaDB compatible, realizar `migrate` y comprobar la conexión real de Django.
- **PENDIENTE:** subir al repositorio GitHub de la usuaria y confirmar su contenido público.

**La verificación no demuestra que exista un sistema bibliotecario completo; el código recibido no lo contiene.**

## Notas de seguridad

El `.env` requerido por la evaluación es público y contiene únicamente texto de ejemplo. Para una ejecución real, crea `.env.local` y `crear_base_datos_local.sql`, que se excluyen de Git. No entregues contraseñas reales a un repositorio público. Si la `SECRET_KEY` que antes figuraba en GitHub se usó para una aplicación real, debe considerarse expuesta y reemplazarse.
