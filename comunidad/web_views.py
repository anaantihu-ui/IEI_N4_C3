from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.exceptions import ValidationError, PermissionDenied as APIPermissionDenied
from .web_services import ENTIDADES, viewset, puede_escribir, exigir_permiso, guardar, eliminar


def etiqueta(obj):
    for name in ['titulo', 'nombre', 'usuario']:
        if hasattr(obj, name):
            return str(getattr(obj, name))
    if hasattr(obj, 'actividad'):
        return f'{obj.actividad} · #{obj.pk}'
    return f'Registro #{obj.pk}'


def errores_formulario(form, detail):
    if isinstance(detail, dict):
        for field, errors in detail.items():
            errores = errors if isinstance(errors, list) else [errors]
            for error in errores:
                form.add_error(field if field in form.fields else None, str(error))
    else:
        for error in detail if isinstance(detail, list) else [detail]:
            form.add_error(None, str(error))


class EntidadMixin(LoginRequiredMixin):
    login_url = reverse_lazy('web:login')
    entidad = None
    accion = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.accion:
            exigir_permiso(self.entidad, request.user, self.accion)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = viewset(self.entidad, self.request).get_queryset().order_by('pk')
        if self.accion in ['editar', 'eliminar'] and not self.request.user.is_superuser:
            if self.entidad == 'actividades':
                qs = qs.filter(organizacion=self.request.user.perfil.organizacion)
        return qs

    def get_form_class(self):
        return ENTIDADES[self.entidad][1]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # DeleteView usa un Form vacío para confirmar, no un ModelForm.
        if self.accion != 'eliminar':
            kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse(f'web:{self.entidad}_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(titulo=ENTIDADES[self.entidad][0], entidad=self.entidad,
                       menu=[(slug, config[0]) for slug, config in ENTIDADES.items()],
                       list_url=reverse(f'web:{self.entidad}_list'),
                       create_url=reverse(f'web:{self.entidad}_create'),
                       puede_crear=puede_escribir(self.entidad, self.request.user, 'crear'))
        obj = getattr(self, 'object', None)
        if obj:
            context.update(etiqueta=etiqueta(obj),
                detail_url=reverse(f'web:{self.entidad}_detail', args=[obj.pk]),
                edit_url=reverse(f'web:{self.entidad}_update', args=[obj.pk]),
                delete_url=reverse(f'web:{self.entidad}_delete', args=[obj.pk]),
                puede_editar=puede_escribir(self.entidad, self.request.user, 'editar', obj),
                puede_eliminar=puede_escribir(self.entidad, self.request.user, 'eliminar', obj))
        return context


class ListaView(EntidadMixin, ListView):
    template_name = 'comunidad/registro_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query:
            fields = [f.name for f in qs.model._meta.fields if f.name in ['nombre', 'titulo', 'descripcion', 'observaciones', 'habilidades']]
            condition = Q(pk__in=[])
            for field in fields:
                condition |= Q(**{field+'__icontains': query})
            if self.entidad == 'perfiles':
                condition |= Q(usuario__username__icontains=query)
            qs = qs.filter(condition)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['filas'] = [(obj.pk, etiqueta(obj), getattr(obj, 'estado', ''), reverse(f'web:{self.entidad}_detail', args=[obj.pk])) for obj in context['object_list']]
        return context


class DetalleView(EntidadMixin, DetailView):
    template_name = 'comunidad/registro_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = []
        for field in self.object._meta.fields:
            value = getattr(self.object, field.name)
            if field.choices:
                value = getattr(self.object, 'get_'+field.name+'_display')()
            if isinstance(value, bool):
                value = 'Sí' if value else 'No'
            fields.append((field.verbose_name, value if value is not None and value != '' else '—'))
        context['campos'] = fields
        return context


class GuardarMixin:
    def form_valid(self, form):
        try:
            self.object = guardar(self.entidad, self.request, form.payload(), self.object.pk if self.object else None)
        except APIPermissionDenied as exc:
            raise PermissionDenied(str(exc.detail)) from exc
        except ValidationError as exc:
            errores_formulario(form, exc.detail)
            return self.form_invalid(form)
        except IntegrityError:
            form.add_error(None, 'El registro viola una restricción de integridad. Revisa los datos.')
            return self.form_invalid(form)
        messages.success(self.request, 'Registro creado correctamente.' if self.accion == 'crear' else 'Cambios guardados correctamente.')
        return HttpResponseRedirect(reverse(f'web:{self.entidad}_detail', args=[self.object.pk]))


class CrearView(GuardarMixin, EntidadMixin, CreateView):
    accion = 'crear'
    template_name = 'comunidad/registro_form.html'


class EditarView(GuardarMixin, EntidadMixin, UpdateView):
    accion = 'editar'
    template_name = 'comunidad/registro_form.html'


class EliminarView(EntidadMixin, DeleteView):
    accion = 'eliminar'
    template_name = 'comunidad/registro_confirm_delete.html'

    def get_form_class(self):
        return DeleteView.form_class

    def form_valid(self, form):
        try:
            eliminar(self.entidad, self.request, self.object.pk)
        except APIPermissionDenied as exc:
            raise PermissionDenied(str(exc.detail)) from exc
        except ProtectedError:
            form.add_error(None, 'Hay registros relacionados. Conserva el historial y cambia el estado en lugar de eliminar.')
            return self.form_invalid(form)
        except ValidationError as exc:
            errores_formulario(form, exc.detail)
            return self.form_invalid(form)
        except IntegrityError:
            form.add_error(None, 'No se pudo eliminar debido a una restricción de integridad.')
            return self.form_invalid(form)
        messages.success(self.request, 'Registro eliminado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class IniciarSesionView(LoginView):
    template_name = 'registration/login.html'

    def get_default_redirect_url(self):
        return reverse('web:actividades_list')


class CerrarSesionView(LogoutView):
    http_method_names = ['post', 'options']
    next_page = reverse_lazy('web:login')


class OrganizacionListView(ListaView):
    entidad = 'organizaciones'


class OrganizacionDetailView(DetalleView):
    entidad = 'organizaciones'


class OrganizacionCreateView(CrearView):
    entidad = 'organizaciones'


class OrganizacionUpdateView(EditarView):
    entidad = 'organizaciones'


class OrganizacionDeleteView(EliminarView):
    entidad = 'organizaciones'


class PerfilListView(ListaView):
    entidad = 'perfiles'


class PerfilDetailView(DetalleView):
    entidad = 'perfiles'


class PerfilCreateView(CrearView):
    entidad = 'perfiles'


class PerfilUpdateView(EditarView):
    entidad = 'perfiles'


class PerfilDeleteView(EliminarView):
    entidad = 'perfiles'


class CategoriaListView(ListaView):
    entidad = 'categorias'


class CategoriaDetailView(DetalleView):
    entidad = 'categorias'


class CategoriaCreateView(CrearView):
    entidad = 'categorias'


class CategoriaUpdateView(EditarView):
    entidad = 'categorias'


class CategoriaDeleteView(EliminarView):
    entidad = 'categorias'


class UbicacionListView(ListaView):
    entidad = 'ubicaciones'


class UbicacionDetailView(DetalleView):
    entidad = 'ubicaciones'


class UbicacionCreateView(CrearView):
    entidad = 'ubicaciones'


class UbicacionUpdateView(EditarView):
    entidad = 'ubicaciones'


class UbicacionDeleteView(EliminarView):
    entidad = 'ubicaciones'


class ActividadListView(ListaView):
    entidad = 'actividades'


class ActividadDetailView(DetalleView):
    entidad = 'actividades'


class ActividadCreateView(CrearView):
    entidad = 'actividades'


class ActividadUpdateView(EditarView):
    entidad = 'actividades'


class ActividadDeleteView(EliminarView):
    entidad = 'actividades'


class InscripcionListView(ListaView):
    entidad = 'inscripciones'


class InscripcionDetailView(DetalleView):
    entidad = 'inscripciones'


class InscripcionCreateView(CrearView):
    entidad = 'inscripciones'


class InscripcionUpdateView(EditarView):
    entidad = 'inscripciones'


class InscripcionDeleteView(EliminarView):
    entidad = 'inscripciones'


class AsistenciaListView(ListaView):
    entidad = 'asistencias'


class AsistenciaDetailView(DetalleView):
    entidad = 'asistencias'


class AsistenciaCreateView(CrearView):
    entidad = 'asistencias'


class AsistenciaUpdateView(EditarView):
    entidad = 'asistencias'


class AsistenciaDeleteView(EliminarView):
    entidad = 'asistencias'


class RecursoListView(ListaView):
    entidad = 'recursos'


class RecursoDetailView(DetalleView):
    entidad = 'recursos'


class RecursoCreateView(CrearView):
    entidad = 'recursos'


class RecursoUpdateView(EditarView):
    entidad = 'recursos'


class RecursoDeleteView(EliminarView):
    entidad = 'recursos'


class AsignacionRecursoListView(ListaView):
    entidad = 'asignaciones'


class AsignacionRecursoDetailView(DetalleView):
    entidad = 'asignaciones'


class AsignacionRecursoCreateView(CrearView):
    entidad = 'asignaciones'


class AsignacionRecursoUpdateView(EditarView):
    entidad = 'asignaciones'


class AsignacionRecursoDeleteView(EliminarView):
    entidad = 'asignaciones'


class IncidenciaListView(ListaView):
    entidad = 'incidencias'


class IncidenciaDetailView(DetalleView):
    entidad = 'incidencias'


class IncidenciaCreateView(CrearView):
    entidad = 'incidencias'


class IncidenciaUpdateView(EditarView):
    entidad = 'incidencias'


class IncidenciaDeleteView(EliminarView):
    entidad = 'incidencias'
