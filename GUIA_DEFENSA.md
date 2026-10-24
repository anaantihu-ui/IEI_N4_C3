# Preguntas para la defensa

1. **¿Cómo se relacionan los modelos?**  
   Se usan claves foráneas. Un libro pertenece a una biblioteca y tiene autor, subgénero y edición. Inventario representa sus ejemplares y Prestamo relaciona un ejemplar con un lector.

2. **¿Qué hacen el SQL y las migraciones?**  
   El SQL crea la base, el usuario y los permisos. `makemigrations` genera los cambios de estructura y `migrate` los aplica a la base.

3. **¿Para qué sirve un serializer?**  
   Convierte los modelos a datos para responder en JSON y valida los datos recibidos antes de guardarlos.

4. **¿Cómo funciona el CRUD?**  
   El Router conecta las URLs con los ModelViewSet. GET consulta, POST crea, PUT actualiza los campos requeridos, PATCH modifica algunos y DELETE elimina.

5. **¿Dónde se guarda la configuración?**  
   En `.env.local` se guardan la conexión y la clave privada. `settings.py` las lee con python-decouple. Las variables del sistema tienen prioridad.

Para practicar, crea un país, consúltalo, modifica su nombre y elimínalo. Luego repite la prueba con MySQL y revisa los datos en phpMyAdmin.
