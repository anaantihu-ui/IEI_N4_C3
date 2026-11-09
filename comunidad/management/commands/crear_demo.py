"""Carga datos ficticios por los mismos serializers de la API, con auditoría."""
import getpass
import os
from datetime import timedelta
from types import SimpleNamespace
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from comunidad import models as m, serializers as s
from comunidad.views import audit


class Command(BaseCommand):
    help = 'Crea una organización, coordinador, voluntario y actividad ficticios para la defensa.'

    def add_arguments(self, parser):
        parser.add_argument('--administrador', default='admin', help='Superusuario existente que figurará como autor.')
        parser.add_argument('--noinput', action='store_true', help='Lee la contraseña de DEMO_PASSWORD.')

    def handle(self, *args, **options):
        actor = get_user_model().objects.filter(username=options['administrador'], is_superuser=True, is_active=True).first()
        if not actor:
            raise CommandError('Primero ejecuta createsuperuser e indica su nombre con --administrador.')
        password = os.environ.get('DEMO_PASSWORD')
        if not password and not options['noinput']:
            password = getpass.getpass('Contraseña para las dos cuentas de demostración: ')
        if not password:
            raise CommandError('Se requiere una contraseña interactiva o DEMO_PASSWORD.')
        context = {'request': SimpleNamespace(user=actor)}

        def create(model, serializer_class, lookup, data):
            existing = model.objects.filter(**lookup).first()
            if existing:
                return existing
            serializer = serializer_class(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            audit(obj, actor, 'crear', {}, serializer_class(obj, context=context).data)
            return obj

        try:
            with transaction.atomic():
                list(m.Organizacion.objects.select_for_update().order_by('pk'))
                org = create(m.Organizacion, s.OrganizacionSerializer, {'nombre': 'Red Comunitaria Demo'}, {'nombre': 'Red Comunitaria Demo', 'descripcion': 'Organización ficticia para practicar.'})
                profiles = []
                for username, role in [('coordinador_demo', 'coordinador'), ('voluntario_demo', 'voluntario')]:
                    existing = m.Perfil.objects.filter(usuario__username=username).first()
                    if existing and (existing.organizacion_id != org.pk or existing.rol != role):
                        raise CommandError('Una cuenta demo ya existe con otra organización o rol.')
                    profiles.append(create(m.Perfil, s.PerfilSerializer, {'usuario__username': username}, {'username': username, 'password': password, 'rol': role, 'organizacion': org.pk}))
                category = create(m.Categoria, s.CategoriaSerializer, {'nombre': 'Medioambiente'}, {'nombre': 'Medioambiente'})
                place = create(m.Ubicacion, s.UbicacionSerializer, {'nombre': 'Plaza Demo', 'organizacion': org}, {'nombre': 'Plaza Demo', 'organizacion': org.pk, 'direccion': 'Dirección ficticia 123', 'comuna': 'Temuco'})
                start = timezone.now() + timedelta(days=7)
                activity = create(m.Actividad, s.ActividadSerializer, {'titulo': 'Limpieza comunitaria Demo', 'organizacion': org}, {'titulo': 'Limpieza comunitaria Demo', 'organizacion': org.pk, 'coordinador': profiles[0].pk, 'categoria': category.pk, 'ubicacion': place.pk, 'inicio': start, 'fin': start+timedelta(hours=3), 'cupos': 20, 'estado': 'publicada'})
                create(m.Recurso, s.RecursoSerializer, {'nombre': 'Guantes Demo', 'organizacion': org}, {'nombre': 'Guantes Demo', 'organizacion': org.pk, 'cantidad_total': 20})
        except ValidationError as exc:
            raise CommandError(str(exc.detail)) from exc
        self.stdout.write(self.style.SUCCESS('Datos demo preparados. Cuentas: coordinador_demo y voluntario_demo.'))
        self.stdout.write(f'Actividad: /api/actividades/{activity.pk}/. Las cuentas existentes conservan su contraseña.')
