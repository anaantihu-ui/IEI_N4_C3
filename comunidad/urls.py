from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('organizaciones', views.OrganizacionViewSet, basename='organizacion')
router.register('perfiles', views.PerfilViewSet, basename='perfil')
router.register('categorias', views.CategoriaViewSet, basename='categoria')
router.register('ubicaciones', views.UbicacionViewSet, basename='ubicacion')
router.register('actividades', views.ActividadViewSet, basename='actividad')
router.register('inscripciones', views.InscripcionViewSet, basename='inscripcion')
router.register('asistencias', views.AsistenciaViewSet, basename='asistencia')
router.register('recursos', views.RecursoViewSet, basename='recurso')
router.register('asignaciones', views.AsignacionRecursoViewSet, basename='asignacion')
router.register('incidencias', views.IncidenciaViewSet, basename='incidencia')
router.register('auditoria', views.AuditoriaViewSet, basename='auditoria')
urlpatterns = router.urls
