from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .tests import fixtures, PASSWORD
from . import models as m


class WebTests(TestCase):
    def setUp(self):
        fixtures(self)
        self.client.force_login(self.admin)
        self.payloads = {
            'organizaciones': {'nombre': 'Nueva red', 'descripcion': 'Prueba', 'activa': True},
            'perfiles': {'username': 'nuevo_web', 'password': PASSWORD, 'rol': 'voluntario', 'organizacion': self.org.pk},
            'categorias': {'nombre': 'Educación web', 'descripcion': 'Prueba'},
            'ubicaciones': {'organizacion': self.org.pk, 'nombre': 'Plaza', 'direccion': 'Calle 3', 'comuna': 'Temuco'},
            'actividades': {'organizacion': self.org.pk, 'coordinador': self.coord.pk, 'categoria': self.category.pk, 'ubicacion': self.place.pk, 'titulo': 'Nueva actividad', 'inicio': timezone.localtime(self.start).strftime('%Y-%m-%dT%H:%M'), 'fin': timezone.localtime(self.end).strftime('%Y-%m-%dT%H:%M'), 'cupos': 5, 'estado': 'publicada', 'publica': True},
            'inscripciones': {'actividad': self.activity.pk, 'voluntario': self.vol.pk, 'estado': 'confirmada', 'observaciones': 'Prueba'},
            'asistencias': {'inscripcion': self.signup.pk, 'horas': '0.50', 'observaciones': 'Prueba'},
            'recursos': {'organizacion': self.org.pk, 'nombre': 'Palas', 'cantidad_total': 10},
            'asignaciones': {'actividad': self.activity.pk, 'recurso': self.resource.pk, 'cantidad': 1, 'activa': True},
            'incidencias': {'actividad': self.activity.pk, 'descripcion': 'Falta material', 'estado': 'abierta'},
        }

    def url(self, slug, action, pk=None):
        return reverse(f'web:{slug}_{action}', args=[pk] if pk else [])

    def crud(self, slug):
        create = self.url(slug, 'create')
        self.assertContains(self.client.get(create), 'csrfmiddlewaretoken')
        response = self.client.post(create, self.payloads[slug])
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['form'].errors)
        detail = response.url
        pk = int(detail.strip('/').split('/')[-1])
        response = self.client.get(detail)
        self.assertContains(response, 'Registro creado correctamente.')
        self.assertContains(self.client.get(self.url(slug, 'list')), 'Ver detalle')
        data = dict(self.payloads[slug])
        field = {'perfiles': 'telefono', 'actividades': 'titulo', 'inscripciones': 'observaciones', 'asistencias': 'observaciones', 'asignaciones': 'cantidad', 'incidencias': 'descripcion'}.get(slug, 'nombre')
        data[field] = '2' if slug == 'asignaciones' else 'Editado desde web'
        if slug == 'perfiles':
            data['password'] = ''
        self.assertEqual(self.client.get(self.url(slug, 'update', pk)).status_code, 200)
        response = self.client.post(self.url(slug, 'update', pk), data)
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['form'].errors)
        self.assertContains(self.client.get(detail), data[field])
        confirm = self.url(slug, 'delete', pk)
        self.assertContains(self.client.get(confirm), 'Confirmar eliminación')
        self.assertEqual(self.client.get(detail).status_code, 200)  # GET no borra.
        response = self.client.post(confirm)
        self.assertRedirects(response, self.url(slug, 'list'))
        self.assertEqual(self.client.get(detail).status_code, 404)
        self.assertEqual(m.EventoAuditoria.objects.filter(accion='eliminar').count(), 1)

    def test_login_and_logout(self):
        self.client.logout()
        url = self.url('actividades', 'list')
        self.assertRedirects(self.client.get(url), reverse('web:login')+'?next='+url)
        response = self.client.post(reverse('web:login'), {'username': 'admin', 'password': PASSWORD})
        self.assertRedirects(response, url)
        self.assertEqual(self.client.get(reverse('web:logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('web:logout')), reverse('web:login'))

    def test_csrf_required_and_no_get_delete(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        self.assertEqual(client.post(self.url('categorias', 'create'), {'nombre': 'Ataque'}).status_code, 403)
        self.assertEqual(client.post(self.url('categorias', 'delete', self.category.pk)).status_code, 403)
        self.assertTrue(m.Categoria.objects.filter(pk=self.category.pk).exists())

    def test_invalid_dates_and_audit_rollback(self):
        data = {**self.payloads['actividades'], 'fin': self.payloads['actividades']['inicio']}
        response = self.client.post(self.url('actividades', 'create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(m.EventoAuditoria.objects.exists())

    def test_original_state_used_for_validation_and_audit(self):
        url = self.url('actividades', 'update', self.activity.pk)
        data = {**self.payloads['actividades'], 'estado': 'finalizada'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.estado, 'publicada')
        data = {**self.payloads['actividades'], 'titulo': 'Título nuevo'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        audit = m.EventoAuditoria.objects.get(entidad='actividad')
        self.assertEqual(audit.anterior['titulo'], 'Jornada')
        self.assertEqual(audit.posterior['titulo'], 'Título nuevo')

    def test_protected_delete_keeps_history(self):
        count = m.EventoAuditoria.objects.count()
        response = self.client.post(self.url('organizaciones', 'delete', self.org.pk))
        self.assertContains(response, 'Hay registros relacionados')
        self.assertTrue(m.Organizacion.objects.filter(pk=self.org.pk).exists())
        self.assertEqual(m.EventoAuditoria.objects.count(), count)

    def test_volunteer_permissions_and_own_signup(self):
        self.client.force_login(self.vol_user)
        for slug in ['actividades', 'organizaciones', 'categorias', 'perfiles', 'recursos']:
            self.assertEqual(self.client.post(self.url(slug, 'create'), self.payloads[slug]).status_code, 403)
        data = {'actividad': self.activity.pk, 'voluntario': self.vol2.pk, 'estado': 'confirmada'}
        response = self.client.post(self.url('inscripciones', 'create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(m.Inscripcion.objects.filter(actividad=self.activity, voluntario=self.vol).exists())
        self.assertFalse(m.Inscripcion.objects.filter(actividad=self.activity, voluntario=self.vol2).exists())
        response = self.client.post(self.url('inscripciones', 'create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(self.client.get(self.url('perfiles', 'detail', self.vol2.pk)).status_code, 404)

    def test_coordinator_scoped_choices_and_writes(self):
        self.client.force_login(self.other_coord.usuario)
        response = self.client.get(self.url('actividades', 'create'))
        self.assertNotIn(self.org, response.context['form'].fields['organizacion'].queryset)
        response = self.client.post(self.url('actividades', 'create'), self.payloads['actividades'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(self.client.get(self.url('actividades', 'update', self.activity.pk)).status_code, 404)
        self.assertEqual(self.client.post(self.url('actividades', 'delete', self.activity.pk)).status_code, 404)

    def test_capacity_and_cancellation_share_api_rules(self):
        self.activity.cupos = 1
        self.activity.save()
        first = self.client.post(self.url('inscripciones', 'create'), self.payloads['inscripciones'])
        self.assertEqual(first.status_code, 302)
        response = self.client.post(self.url('inscripciones', 'create'), {**self.payloads['inscripciones'], 'voluntario': self.vol2.pk})
        self.assertContains(response, 'No quedan cupos')
        data = {**self.payloads['actividades'], 'estado': 'cancelada', 'inicio': timezone.localtime(self.start).isoformat(), 'fin': timezone.localtime(self.end).isoformat()}
        # El formulario conserva las fechas exactas cuando hay inscripciones.
        response = self.client.post(self.url('actividades', 'update', self.activity.pk), data)
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['form'].errors)
        self.assertEqual(self.activity.inscripciones.get().estado, 'cancelada')

    def test_search_pagination_and_escape(self):
        m.Categoria.objects.create(nombre='<script>alert(1)</script>')
        for i in range(14):
            m.Categoria.objects.create(nombre=f'Categoría {i}')
        response = self.client.get(self.url('categorias', 'list'), {'q': 'script'})
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertTrue(self.client.get(self.url('categorias', 'list')).context['is_paginated'])


for slug in ['organizaciones', 'perfiles', 'categorias', 'ubicaciones', 'actividades', 'inscripciones', 'asistencias', 'recursos', 'asignaciones', 'incidencias']:
    def test(self, slug=slug):
        self.crud(slug)
    setattr(WebTests, 'test_crud_'+slug, test)
