from django.urls import path, include
from rest_framework import routers
from mi_app import views

enrutador = routers.DefaultRouter()

enrutador.register(r'regiones', views.RegionViewSet)
enrutador.register(r'comunas', views.ComunaViewSet)
enrutador.register(r'perfiles', views.PerfilViewSet)
enrutador.register(r'organizaciones', views.OrganizacionViewSet)
enrutador.register(r'categorias', views.CategoriaViewSet)
enrutador.register(r'estados', views.EstadoViewSet)
enrutador.register(r'voluntarios', views.VoluntarioViewSet)
enrutador.register(r'coordinadores', views.CoordinadorViewSet)
enrutador.register(r'actividades', views.ActividadViewSet)
enrutador.register(r'inscripciones', views.InscripcionViewSet)
enrutador.register(r'recursos', views.RecursoViewSet)
enrutador.register(r'asignaciones', views.AsignacionRecursoViewSet)
enrutador.register(r'historial', views.HistorialEstadoViewSet)

urlpatterns = [
    path('', include(enrutador.urls)),
]
