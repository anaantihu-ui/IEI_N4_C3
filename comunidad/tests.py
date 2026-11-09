import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from . import models as m

PASSWORD = 'PruebaComunidad-593!'


def fixtures(owner):
    User = get_user_model()
    owner.admin = User.objects.create_superuser('admin', password=PASSWORD)
    owner.org = m.Organizacion.objects.create(nombre='Red comunitaria')
    owner.other_org = m.Organizacion.objects.create(nombre='Otra organización')
    owner.coord_user = User.objects.create_user('coord', password=PASSWORD)
    owner.coord = m.Perfil.objects.create(usuario=owner.coord_user, rol='coordinador', organizacion=owner.org)
    owner.other_coord = m.Perfil.objects.create(usuario=User.objects.create_user('coord2', password=PASSWORD), rol='coordinador', organizacion=owner.other_org)
    owner.vol_user = User.objects.create_user('vol', password=PASSWORD)
    owner.vol = m.Perfil.objects.create(usuario=owner.vol_user, organizacion=owner.org)
    owner.vol2 = m.Perfil.objects.create(usuario=User.objects.create_user('vol2', password=PASSWORD), organizacion=owner.other_org)
    owner.category = m.Categoria.objects.create(nombre='Medioambiente')
    owner.place = m.Ubicacion.objects.create(organizacion=owner.org, nombre='Sede', direccion='Calle 1', comuna='Temuco')
    owner.other_place = m.Ubicacion.objects.create(organizacion=owner.other_org, nombre='Otra sede', direccion='Calle 2', comuna='Temuco')
    owner.start = timezone.now() + timedelta(days=2)
    owner.end = owner.start + timedelta(hours=3)
    owner.activity = m.Actividad.objects.create(organizacion=owner.org, coordinador=owner.coord, categoria=owner.category, ubicacion=owner.place, titulo='Jornada', inicio=owner.start, fin=owner.end, cupos=10, estado='publicada')
    owner.live = m.Actividad.objects.create(organizacion=owner.org, coordinador=owner.coord, categoria=owner.category, ubicacion=owner.place, titulo='En curso', inicio=timezone.now()-timedelta(hours=2), fin=timezone.now()+timedelta(hours=1), cupos=10, estado='en_curso')
    owner.signup = m.Inscripcion.objects.create(actividad=owner.live, voluntario=owner.vol)
    owner.resource = m.Recurso.objects.create(organizacion=owner.org, nombre='Guantes', cantidad_total=10)


class PlatformTests(APITestCase):
    def setUp(self):
        fixtures(self)
        self.client.force_authenticate(self.admin)
        self.payloads = {
            'organizaciones': {'nombre': 'Nueva red', 'descripcion': 'Prueba'},
            'perfiles': {'username': 'nuevo', 'password': PASSWORD, 'rol': 'voluntario', 'organizacion': self.org.pk, 'telefono': '123'},
            'categorias': {'nombre': 'Educación', 'descripcion': 'Prueba'},
            'ubicaciones': {'organizacion': self.org.pk, 'nombre': 'Plaza', 'direccion': 'Calle 3', 'comuna': 'Temuco'},
            'actividades': {'organizacion': self.org.pk, 'coordinador': self.coord.pk, 'categoria': self.category.pk, 'ubicacion': self.place.pk, 'titulo': 'Nueva actividad', 'inicio': self.start.isoformat(), 'fin': self.end.isoformat(), 'cupos': 5, 'estado': 'publicada'},
            'inscripciones': {'actividad': self.activity.pk, 'voluntario': self.vol.pk, 'observaciones': 'Prueba'},
            'asistencias': {'inscripcion': self.signup.pk, 'horas': '0.50', 'observaciones': 'Prueba'},
            'recursos': {'organizacion': self.org.pk, 'nombre': 'Palas', 'cantidad_total': 10},
            'asignaciones': {'actividad': self.activity.pk, 'recurso': self.resource.pk, 'cantidad': 1},
            'incidencias': {'actividad': self.activity.pk, 'descripcion': 'Falta material'},
        }

    def post(self, route, changes=None, expected=201):
        payload = {**self.payloads[route], **(changes or {})}
        response = self.client.post(f'/api/{route}/', payload, format='json')
        self.assertEqual(response.status_code, expected, response.data)
        return response

    def exercise_crud(self, route):
        obj = self.post(route).data
        url = f'/api/{route}/{obj["id"]}/'
        self.assertEqual(self.client.get(f'/api/{route}/').status_code, 200)
        self.assertEqual(self.client.get(url).data['id'], obj['id'])
        field = {'organizaciones': 'nombre', 'perfiles': 'telefono', 'categorias': 'nombre', 'ubicaciones': 'nombre', 'actividades': 'titulo', 'inscripciones': 'observaciones', 'asistencias': 'observaciones', 'recursos': 'nombre', 'asignaciones': 'cantidad', 'incidencias': 'descripcion'}[route]
        data = {**self.payloads[route], field: 2 if route == 'asignaciones' else 'Actualizado'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.get(url).data[field], data[field])
        patch = {field: 3 if route == 'asignaciones' else 'Parcial'}
        response = self.client.patch(url, patch, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.get(url).data[field], patch[field])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, getattr(response, 'data', None))
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(m.EventoAuditoria.objects.filter(accion='eliminar', objeto_id=obj['id']).count(), 1)

    def test_public_and_private_activity_visibility(self):
        self.activity.estado = 'borrador'; self.activity.save()
        self.live.publica = False; self.live.save()
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/actividades/').data['count'], 0)
        self.assertEqual(self.client.get(f'/api/actividades/{self.activity.pk}/').status_code, 404)
        self.assertEqual(self.client.get('/api/organizaciones/').status_code, 200)
        self.assertEqual(self.client.get('/api/perfiles/').status_code, 401)
        self.assertEqual(self.client.post('/api/actividades/', {}, format='json').status_code, 401)

    def test_volunteer_own_registration_and_duplicate(self):
        self.client.force_authenticate(self.vol_user)
        response = self.client.post('/api/inscripciones/', {'actividad': self.activity.pk}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['voluntario'], self.vol.pk)
        self.post('inscripciones', expected=400)
        self.post('inscripciones', {'voluntario': self.vol2.pk}, expected=400)

    def test_capacity_cancel_and_reactivate(self):
        self.activity.cupos = 1; self.activity.save()
        first = self.post('inscripciones').data
        self.post('inscripciones', {'voluntario': self.vol2.pk}, expected=400)
        url = f'/api/inscripciones/{first["id"]}/'
        self.assertEqual(self.client.patch(url, {'estado': 'cancelada'}, format='json').status_code, 200)
        self.post('inscripciones', {'voluntario': self.vol2.pk})
        self.assertEqual(self.client.patch(url, {'estado': 'confirmada'}, format='json').status_code, 400)

    def test_registration_requires_published_future_activity(self):
        self.activity.estado = 'borrador'; self.activity.save()
        self.post('inscripciones', expected=400)
        self.activity.estado = 'publicada'; self.activity.inicio = timezone.now()-timedelta(hours=1); self.activity.save()
        self.post('inscripciones', expected=400)

    def test_private_activity_requires_membership(self):
        self.activity.publica = False; self.activity.save()
        self.post('inscripciones', {'voluntario': self.vol2.pk}, expected=400)
        self.client.force_authenticate(self.vol2.usuario)
        self.assertEqual(self.client.get(f'/api/actividades/{self.activity.pk}/').status_code, 404)

    def test_organization_relations_cannot_be_mixed(self):
        self.post('actividades', {'coordinador': self.other_coord.pk}, expected=400)
        self.post('actividades', {'ubicacion': self.other_place.pk}, expected=400)
        foreign = m.Recurso.objects.create(organizacion=self.other_org, nombre='Otro', cantidad_total=10)
        self.post('asignaciones', {'recurso': foreign.pk}, expected=400)

    def test_coordinator_cannot_write_other_organization(self):
        self.client.force_authenticate(self.other_coord.usuario)
        self.post('actividades', expected=403)
        self.assertEqual(self.client.patch(f'/api/actividades/{self.activity.pk}/', {'titulo': 'Intrusión'}, format='json').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/actividades/{self.activity.pk}/').status_code, 403)
        self.assertEqual(self.client.get(f'/api/recursos/{self.resource.pk}/').status_code, 404)

    def test_volunteer_cannot_escalate_role_or_edit_activity(self):
        self.client.force_authenticate(self.vol_user)
        self.assertEqual(self.client.patch(f'/api/perfiles/{self.vol.pk}/', {'rol': 'coordinador'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(f'/api/actividades/{self.activity.pk}/', {'titulo': 'Intrusión'}, format='json').status_code, 403)
        self.assertEqual(self.client.get(f'/api/perfiles/{self.vol2.pk}/').status_code, 404)
        self.post('perfiles', expected=403)

    def test_password_hash_and_audit_privacy(self):
        obj = self.post('perfiles').data
        self.assertNotIn('password', obj)
        user = m.Perfil.objects.get(pk=obj['id']).usuario
        self.assertTrue(user.check_password(PASSWORD))
        audit_data = json.dumps(list(m.EventoAuditoria.objects.values()), default=str)
        self.assertNotIn(PASSWORD, audit_data)
        self.assertNotIn(user.password, audit_data)

    def test_weak_password_and_duplicate_username_rejected(self):
        self.post('perfiles', {'password': '123'}, expected=400)
        self.post('perfiles', {'username': 'admin'}, expected=400)
        self.post('perfiles', {'rol': 'coordinador', 'organizacion': None}, expected=400)

    def test_date_and_capacity_validation(self):
        self.post('actividades', {'fin': self.start.isoformat()}, expected=400)
        self.post('actividades', {'cupos': 0}, expected=400)
        self.post('inscripciones')
        response = self.client.patch(f'/api/actividades/{self.activity.pk}/', {'cupos': 0}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.patch(f'/api/actividades/{self.activity.pk}/', {'inicio': (self.start+timedelta(hours=1)).isoformat()}, format='json').status_code, 400)

    def test_invalid_state_transition_rejected(self):
        url = f'/api/actividades/{self.activity.pk}/'
        self.assertEqual(self.client.patch(url, {'estado': 'finalizada'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'estado': 'en_curso'}, format='json').status_code, 400)

    def test_cancel_records_history_and_releases_related_data(self):
        signup = self.post('inscripciones').data
        allocation = self.post('asignaciones').data
        response = self.client.patch(f'/api/actividades/{self.activity.pk}/', {'estado': 'cancelada'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(m.Inscripcion.objects.get(pk=signup['id']).estado, 'cancelada')
        self.assertFalse(m.AsignacionRecurso.objects.get(pk=allocation['id']).activa)
        events = m.EventoAuditoria.objects.filter(accion='modificar')
        self.assertEqual(events.count(), 3)
        self.assertTrue(events.filter(entidad='actividad', estado_anterior='publicada', estado_nuevo='cancelada', actor=self.admin).exists())

    def test_audit_is_read_only_and_scoped(self):
        self.post('categorias')
        event = m.EventoAuditoria.objects.first()
        self.assertEqual(self.client.patch(f'/api/auditoria/{event.pk}/', {'actor_nombre': 'otro'}, format='json').status_code, 405)
        self.assertEqual(self.client.delete(f'/api/auditoria/{event.pk}/').status_code, 405)
        self.client.force_authenticate(self.vol_user)
        self.assertEqual(self.client.get('/api/auditoria/').status_code, 403)
        self.client.force_authenticate(self.coord_user)
        self.assertEqual(self.client.get('/api/auditoria/').data['count'], 0)

    def test_protected_delete_rolls_back_audit(self):
        self.post('inscripciones')
        before = m.EventoAuditoria.objects.count()
        self.assertEqual(self.client.delete(f'/api/actividades/{self.activity.pk}/').status_code, 409)
        self.assertTrue(m.Actividad.objects.filter(pk=self.activity.pk).exists())
        self.assertEqual(m.EventoAuditoria.objects.count(), before)

    def test_resource_overlap_and_stock_reduction(self):
        self.post('asignaciones', {'cantidad': 8})
        other = self.post('actividades').data
        self.post('asignaciones', {'actividad': other['id'], 'cantidad': 3}, expected=400)
        self.post('asignaciones', {'actividad': other['id'], 'cantidad': 2})
        response = self.client.patch(f'/api/recursos/{self.resource.pk}/', {'cantidad_total': 9}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_resource_nonoverlap_is_reusable(self):
        self.post('asignaciones', {'cantidad': 10})
        other = self.post('actividades', {'inicio': self.end.isoformat(), 'fin': (self.end+timedelta(hours=2)).isoformat()}).data
        self.post('asignaciones', {'actividad': other['id'], 'cantidad': 10})

    def test_attendance_permission_and_hours(self):
        self.post('asistencias', {'horas': '5.00'}, expected=400)
        self.client.force_authenticate(self.vol_user)
        self.post('asistencias', expected=403)
        self.client.force_authenticate(self.coord_user)
        self.post('asistencias')
        self.post('asistencias', expected=400)

    def test_volunteer_only_sees_own_participation(self):
        self.post('inscripciones')
        other = self.post('inscripciones', {'voluntario': self.vol2.pk}).data
        self.client.force_authenticate(self.vol_user)
        self.assertEqual(self.client.get('/api/inscripciones/').data['count'], 2)
        self.assertEqual(self.client.get(f'/api/inscripciones/{other["id"]}/').status_code, 404)

    def test_incident_workflow(self):
        self.client.force_authenticate(self.vol_user)
        self.post('incidencias', expected=400)
        response = self.post('incidencias', {'actividad': self.live.pk})
        url = f'/api/incidencias/{response.data["id"]}/'
        self.assertEqual(self.client.patch(url, {'estado': 'resuelta', 'resolucion': 'Autorización falsa'}, format='json').status_code, 400)
        self.client.force_authenticate(self.coord_user)
        self.assertEqual(self.client.patch(url, {'estado': 'resuelta'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'estado': 'resuelta', 'resolucion': 'Se entregó el material'}, format='json').status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 400)

    def test_indicators_are_scoped_and_private(self):
        self.post('inscripciones')
        self.post('asistencias', {'horas': '1.00'})
        self.client.force_authenticate(self.coord_user)
        data = self.client.get('/api/actividades/indicadores/').data
        self.assertEqual(data['actividades'], 2)
        self.assertEqual(data['inscripciones'], 2)
        self.assertEqual(data['horas_voluntariado'], 1)
        self.client.force_authenticate(self.other_coord.usuario)
        self.assertEqual(self.client.get('/api/actividades/indicadores/').data['actividades'], 0)
        self.client.force_authenticate(self.vol_user)
        self.assertEqual(self.client.get('/api/actividades/indicadores/').status_code, 403)

    def test_search_filters_and_invalid_dates(self):
        response = self.client.get('/api/actividades/', {'search': 'Jornada', 'organizacion': self.org.pk})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(self.client.get('/api/actividades/', {'desde': 'incorrecto'}).status_code, 400)
        self.assertEqual(self.client.get('/api/actividades/', {'organizacion': 'abc'}).status_code, 400)

    def test_browser_login(self):
        self.client.force_authenticate(None)
        response = self.client.post('/api-auth/login/', {'username': 'vol', 'password': PASSWORD})
        self.assertRedirects(response, '/api/')
        self.assertEqual(self.client.get('/api/perfiles/').status_code, 200)

    def test_failed_create_leaves_no_audit(self):
        count = m.EventoAuditoria.objects.count()
        self.post('actividades', {'coordinador': self.other_coord.pk}, expected=400)
        self.assertEqual(m.EventoAuditoria.objects.count(), count)

    def test_inactive_organization_blocks_registration(self):
        self.org.activa = False; self.org.save()
        self.post('inscripciones', expected=400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/actividades/').data['count'], 0)

    def test_profile_links_with_history_cannot_change(self):
        response = self.client.patch(f'/api/perfiles/{self.coord.pk}/', {'organizacion': self.other_org.pk}, format='json')
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/perfiles/{self.vol.pk}/', {'rol': 'coordinador'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_coordinator_cannot_read_private_profile_history(self):
        self.post('perfiles')
        self.client.force_authenticate(self.coord_user)
        self.assertEqual(self.client.get('/api/auditoria/?entidad=perfil').data['count'], 0)


for route in ['organizaciones', 'perfiles', 'categorias', 'ubicaciones', 'actividades', 'inscripciones', 'asistencias', 'recursos', 'asignaciones', 'incidencias']:
    def test(self, route=route):
        self.exercise_crud(route)
    setattr(PlatformTests, 'test_crud_' + route, test)


@skipUnless(connection.vendor == 'mysql', 'Los bloqueos concurrentes se verifican con MySQL.')
class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        fixtures(self)

    def race(self, route, payloads):
        barrier = Barrier(2)
        def send(payload):
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(get_user_model().objects.get(pk=self.admin.pk))
                barrier.wait(timeout=10)
                response = client.post('/api/' + route + '/', payload, format='json')
                return response.status_code
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return sorted(pool.map(send, payloads))

    def test_concurrent_last_seat(self):
        self.activity.cupos = 1; self.activity.save()
        codes = self.race('inscripciones', [{'actividad': self.activity.pk, 'voluntario': p.pk} for p in [self.vol, self.vol2]])
        self.assertEqual(codes, [201, 400])
        self.assertEqual(self.activity.inscripciones.count(), 1)

    def test_concurrent_resource_reservations(self):
        codes = self.race('asignaciones', [
            {'actividad': self.activity.pk, 'recurso': self.resource.pk, 'cantidad': 8},
            {'actividad': self.live.pk, 'recurso': self.resource.pk, 'cantidad': 8},
        ])
        # Intervalos separados: ambas reservas son válidas.
        self.assertEqual(codes, [201, 201])

    def test_concurrent_overlapping_resources(self):
        self.live.inicio = self.start; self.live.fin = self.end; self.live.save()
        codes = self.race('asignaciones', [
            {'actividad': a.pk, 'recurso': self.resource.pk, 'cantidad': 8} for a in [self.activity, self.live]
        ])
        self.assertEqual(codes, [201, 400])
