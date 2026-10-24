# Defensa individual — BiblioHub

Base docente: https://github.com/baileytorch/IEI_N4_C1 (commit e030c19).
Lee los archivos indicados y practica un CRUD completo antes de la evaluación.

## 1. ¿Cómo representas el modelo y sus relaciones?
`biblio_app/models.py` define 18 entidades. Una Provincia pertenece a una Region mediante ForeignKey. Libro se relaciona con Autor, SubGenero, Edicion y Biblioteca. Inventario representa un ejemplar; Prestamo enlaza ese ejemplar con un Usuario lector. Se mantienen las relaciones CASCADE del profesor: eliminar un padre puede eliminar sus dependientes.

## 2. ¿Qué diferencia hay entre el SQL y las migraciones?
`crear_base_datos.sql` crea la base, el usuario y sus permisos. `makemigrations` genera instrucciones de cambio de esquema y `migrate` las aplica. La migración inicial de biblio_app crea sus 18 tablas. Copiar código o ejecutar runserver no crea las tablas. En phpMyAdmin la base del proyecto es incidencias, no mysql.

## 3. ¿Para qué sirve un serializer?
Convierte modelos en datos que se pueden responder como JSON y valida los datos recibidos antes de persistirlos. Cada ModelSerializer declara su modelo y campos. Las relaciones reciben IDs. UsuarioSerializer guarda contrasenia con hash y la marca write_only: no sale en respuestas. Los lectores y las cuentas de autenticación Django son entidades diferentes.

## 4. ¿Cómo se conecta una petición con el CRUD?
`drf/urls.py` incluye `/api/`. DefaultRouter registra cada ModelViewSet. GET lista o consulta; POST crea; PUT actualiza todos los campos requeridos; PATCH cambia algunos; DELETE elimina. El queryset identifica los registros y serializer_class el serializer. Demuestra 201 al crear, 200 al consultar/editar, 204 al borrar y 404 al volver a consultar el ID borrado. Los endpoints requieren autenticación Django.

## 5. ¿Cómo separas la configuración y demuestras persistencia?
settings.py usa python-decouple y elige .env.local cuando existe; de lo contrario lee .env. Las variables del sistema prevalecen. Los archivos públicos tienen marcadores; las credenciales operativas se guardan localmente. Para demostrar persistencia MySQL, ejecuta SQL y migrate, crea un registro por POST, consúltalo por GET y comprueba la tabla en phpMyAdmin. Las pruebas realizadas con SQLite no certifican esa conexión MySQL.

## Límites que debes conocer
La API implementa CRUD del modelo del profesor. No automatiza multas, reservas, control de disponibilidad ni roles de bibliotecario/lector. El acceso académico permite operar a cualquier cuenta Django autenticada. No afirmes capacidades adicionales. Consulta VERIFICACION_Y_CAMBIOS.md para separar lo probado de lo pendiente.
