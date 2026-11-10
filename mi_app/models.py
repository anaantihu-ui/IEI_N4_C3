from django.db import models


class Region(models.Model):
    nombre = models.CharField("Región", max_length=100, null=False)
    codigo = models.CharField("Código", max_length=5, null=False)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "region"
        verbose_name = "Región"
        verbose_name_plural = "Regiones"

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    nombre = models.CharField("Comuna", max_length=100, null=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Región")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "comuna"
        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    nombre = models.CharField("Perfil", max_length=50, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "perfil"
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.nombre


class Organizacion(models.Model):
    nombre = models.CharField("Nombre", max_length=150, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    correo = models.EmailField("Correo", null=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, verbose_name="Comuna")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "organizacion"
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField("Categoría", max_length=100, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "categoria"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField("Estado", max_length=50, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "estado"
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.nombre


class Voluntario(models.Model):
    nombre = models.CharField("Nombre", max_length=150, null=False)
    rut = models.CharField("RUT", max_length=12, null=False, unique=True)
    correo = models.EmailField("Correo", null=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField("Fecha Nacimiento", null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, verbose_name="Comuna")
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, verbose_name="Perfil")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "voluntario"
        verbose_name = "Voluntario"
        verbose_name_plural = "Voluntarios"

    def __str__(self):
        return self.nombre


class Coordinador(models.Model):
    nombre = models.CharField("Nombre", max_length=150, null=False)
    rut = models.CharField("RUT", max_length=12, null=False, unique=True)
    correo = models.EmailField("Correo", null=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, verbose_name="Organización")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "coordinador"
        verbose_name = "Coordinador"
        verbose_name_plural = "Coordinadores"

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    nombre = models.CharField("Nombre", max_length=200, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    fecha_inicio = models.DateTimeField("Fecha Inicio", null=False)
    fecha_fin = models.DateTimeField("Fecha Fin", null=True, blank=True)
    cupo_maximo = models.IntegerField("Cupo Máximo", default=0)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, verbose_name="Organización")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name="Categoría")
    coordinador = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, null=True, verbose_name="Coordinador")
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, verbose_name="Estado")
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, verbose_name="Comuna")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "actividad"
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self):
        return self.nombre


class Inscripcion(models.Model):
    voluntario = models.ForeignKey(Voluntario, on_delete=models.CASCADE, verbose_name="Voluntario")
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, verbose_name="Actividad")
    fecha_inscripcion = models.DateTimeField("Fecha Inscripción", auto_now_add=True)
    asistio = models.BooleanField("Asistió", default=False)
    observaciones = models.TextField("Observaciones", null=True, blank=True)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "inscripcion"
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"

    def __str__(self):
        return f"{self.voluntario} - {self.actividad}"


class Recurso(models.Model):
    nombre = models.CharField("Nombre", max_length=150, null=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    cantidad_disponible = models.IntegerField("Cantidad Disponible", default=0)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, verbose_name="Organización")
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "recurso"
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"

    def __str__(self):
        return self.nombre


class AsignacionRecurso(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, verbose_name="Actividad")
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, verbose_name="Recurso")
    cantidad = models.IntegerField("Cantidad", default=1)
    observaciones = models.TextField("Observaciones", null=True, blank=True)
    habilitado = models.BooleanField("Habilitado", default=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha Actualización", auto_now=True)

    class Meta:
        db_table = "asignacion_recurso"
        verbose_name = "Asignación de Recurso"
        verbose_name_plural = "Asignaciones de Recursos"

    def __str__(self):
        return f"{self.recurso} -> {self.actividad}"


class HistorialEstado(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, verbose_name="Actividad")
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, verbose_name="Estado")
    observacion = models.TextField("Observación", null=True, blank=True)
    fecha_cambio = models.DateTimeField("Fecha Cambio", auto_now_add=True)
    created_at = models.DateTimeField("Fecha Creación", auto_now_add=True)

    class Meta:
        db_table = "historial_estado"
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historial de Estados"

    def __str__(self):
        return f"{self.actividad} - {self.estado}"
