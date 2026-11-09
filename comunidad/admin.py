from django.contrib import admin
from . import models

# Las operaciones de negocio se realizan por API: este panel permite inspección.
# Así se evita que ediciones administrativas omitan validaciones y auditoría.
class SoloLecturaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

for model in [models.Organizacion, models.Perfil, models.Categoria, models.Ubicacion,
              models.Actividad, models.Inscripcion, models.Asistencia, models.Recurso,
              models.AsignacionRecurso, models.Incidencia, models.EventoAuditoria]:
    admin.site.register(model, SoloLecturaAdmin)
