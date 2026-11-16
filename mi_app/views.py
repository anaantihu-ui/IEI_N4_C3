from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from .models import (
    Region, Comuna, Perfil, Organizacion, Categoria,
    Estado, Voluntario, Coordinador, Actividad,
    Inscripcion, Recurso, AsignacionRecurso, HistorialEstado
)
from .serializer import (
    RegionSerializer, ComunaSerializer, PerfilSerializer,
    OrganizacionSerializer, CategoriaSerializer, EstadoSerializer,
    VoluntarioSerializer, CoordinadorSerializer, ActividadSerializer,
    InscripcionSerializer, RecursoSerializer, AsignacionRecursoSerializer,
    HistorialEstadoSerializer
)


PANEL_PAGES = {
    'voluntarios': ('Voluntarios', 'Registra y administra las personas que participan en actividades comunitarias.'),
    'actividades': ('Actividades', 'Planifica las actividades comunitarias, sus fechas, cupos y responsables.'),
    'organizaciones': ('Organizaciones', 'Gestiona las organizaciones que coordinan iniciativas sociales.'),
    'inscripciones': ('Inscripciones', 'Vincula voluntarios con actividades y registra su asistencia.'),
    'recursos': ('Recursos', 'Administra los recursos disponibles para las organizaciones.'),
    'regiones': ('Regiones', 'Mantén actualizado el catálogo de regiones.'),
    'comunas': ('Comunas', 'Gestiona las comunas y su relación con las regiones.'),
    'perfiles': ('Perfiles', 'Organiza los perfiles asociados a las personas voluntarias.'),
    'categorias': ('Categorías', 'Clasifica las distintas actividades comunitarias.'),
    'estados': ('Estados', 'Administra los estados posibles de las actividades.'),
    'coordinadores': ('Coordinadores', 'Gestiona los responsables de las actividades y sus organizaciones.'),
    'asignaciones': ('Asignaciones de recursos', 'Relaciona los recursos disponibles con las actividades.'),
    'historial': ('Historial de estados', 'Consulta los cambios de estado registrados para cada actividad.'),
}


@ensure_csrf_cookie
def bienvenida(request):
    return render(request, 'dashboard.html', {
        'active_page': 'inicio',
        'page_title': 'Panel general',
    })


@ensure_csrf_cookie
def panel(request, recurso):
    page = PANEL_PAGES.get(recurso)
    if page is None:
        raise Http404('No existe ese módulo')
    return render(request, 'panel.html', {
        'active_page': recurso,
        'page_title': page[0],
        'page_description': page[1],
        'recurso': recurso,
    })


def mi_error_404(request, exception):
    return render(request, '404.html', status=404)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class ComunaViewSet(viewsets.ModelViewSet):
    queryset = Comuna.objects.all()
    serializer_class = ComunaSerializer


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


class VoluntarioViewSet(viewsets.ModelViewSet):
    queryset = Voluntario.objects.all()
    serializer_class = VoluntarioSerializer


class CoordinadorViewSet(viewsets.ModelViewSet):
    queryset = Coordinador.objects.all()
    serializer_class = CoordinadorSerializer


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer


class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer


class AsignacionRecursoViewSet(viewsets.ModelViewSet):
    queryset = AsignacionRecurso.objects.all()
    serializer_class = AsignacionRecursoSerializer


class HistorialEstadoViewSet(viewsets.ModelViewSet):
    queryset = HistorialEstado.objects.all()
    serializer_class = HistorialEstadoSerializer
