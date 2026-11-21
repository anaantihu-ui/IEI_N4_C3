"""Formularios HTML. Las escrituras pasan por las reglas compartidas de la API."""
from django import forms
from django.db.models import Model
from . import models as m
from .access import administrador, coordinador, perfil, actividades_visibles


class FormularioComunidad(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'control'
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'control'})
                field.input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3
        if administrador(user):
            return
        p = perfil(user)
        org_id = p.organizacion_id if p else None
        for name, field in self.fields.items():
            if not isinstance(field, forms.ModelChoiceField):
                continue
            model = field.queryset.model
            if model == m.Organizacion:
                field.queryset = field.queryset.filter(pk=org_id)
            elif model in [m.Ubicacion, m.Recurso]:
                field.queryset = field.queryset.filter(organizacion_id=org_id) if coordinador(user) else field.queryset.none()
            elif model == m.Perfil:
                if name == 'coordinador':
                    field.queryset = field.queryset.filter(rol='coordinador', organizacion_id=org_id)
                elif coordinador(user):
                    # Solo participantes de la propia organización; el administrador puede vincular externos.
                    field.queryset = field.queryset.filter(rol='voluntario', organizacion_id=org_id)
                else:
                    field.queryset = field.queryset.filter(usuario=user)
            elif model == m.Actividad:
                field.queryset = actividades_visibles(user)
                if coordinador(user):
                    field.queryset = field.queryset.filter(organizacion_id=org_id)
            elif model == m.Inscripcion:
                field.queryset = field.queryset.filter(actividad__organizacion_id=org_id) if coordinador(user) else field.queryset.filter(voluntario__usuario=user)

    def payload(self):
        data = {name: value.pk if isinstance(value, Model) else value for name, value in self.cleaned_data.items()}
        if 'password' in data and not data['password']:
            data.pop('password')
        return data


class OrganizacionForm(FormularioComunidad):
    class Meta:
        model = m.Organizacion
        fields = ['nombre', 'descripcion', 'correo_publico', 'activa']


class PerfilForm(FormularioComunidad):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    email = forms.EmailField(label='Correo', required=False)
    first_name = forms.CharField(label='Nombre', max_length=150, required=False)
    last_name = forms.CharField(label='Apellido', max_length=150, required=False)
    password = forms.CharField(label='Contraseña', required=False, strip=False, widget=forms.PasswordInput, help_text='Al editar, deja vacío para conservar la contraseña.')

    class Meta:
        model = m.Perfil
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'rol', 'organizacion', 'telefono', 'habilidades']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for field in ['username', 'email', 'first_name', 'last_name']:
                self.initial[field] = getattr(self.instance.usuario, field)
        else:
            self.fields['password'].required = True
        if not administrador(self.user):
            for name in ['rol', 'organizacion']:
                self.fields[name].disabled = True


class CategoriaForm(FormularioComunidad):
    class Meta:
        model = m.Categoria
        fields = ['nombre', 'descripcion']


class UbicacionForm(FormularioComunidad):
    class Meta:
        model = m.Ubicacion
        fields = ['organizacion', 'nombre', 'direccion', 'comuna']


class ActividadForm(FormularioComunidad):
    class Meta:
        model = m.Actividad
        fields = ['titulo', 'descripcion', 'organizacion', 'coordinador', 'categoria', 'ubicacion', 'inicio', 'fin', 'cupos', 'publica', 'estado']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and (self.instance.inscripciones.exists() or self.instance.asignaciones.exists()):
            for name in ['inicio', 'fin']:
                self.fields[name].disabled = True
                self.fields[name].widget.supports_microseconds = True
                self.fields[name].help_text = 'La fecha se conserva porque existen inscripciones o recursos asociados.'


class InscripcionForm(FormularioComunidad):
    class Meta:
        model = m.Inscripcion
        fields = ['actividad', 'voluntario', 'estado', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not administrador(self.user) and not coordinador(self.user):
            self.initial['voluntario'] = perfil(self.user)
            self.fields['voluntario'].disabled = True


class AsistenciaForm(FormularioComunidad):
    class Meta:
        model = m.Asistencia
        fields = ['inscripcion', 'horas', 'observaciones']


class RecursoForm(FormularioComunidad):
    class Meta:
        model = m.Recurso
        fields = ['organizacion', 'nombre', 'cantidad_total', 'descripcion']


class AsignacionRecursoForm(FormularioComunidad):
    class Meta:
        model = m.AsignacionRecurso
        fields = ['actividad', 'recurso', 'cantidad', 'activa']


class IncidenciaForm(FormularioComunidad):
    class Meta:
        model = m.Incidencia
        fields = ['actividad', 'descripcion', 'estado', 'resolucion']
