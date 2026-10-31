"""Pruebas de contrato HTTP y persistencia para las 18 entidades."""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.test import APITestCase
from . import models


class ApiTests(APITestCase):
    def setUp(self):
        self.account = get_user_model().objects.create_user('prueba', password='ClaveSoloPruebas123!')
        self.client.force_authenticate(self.account)
        future = (timezone.now() + timedelta(days=14)).isoformat()
        self.specs = [
            ('paises', models.Pais, {'nombre': 'Chile', 'nacionalidad': 'Chilena', 'iso_2': 'CL', 'iso_3': 'CHL'}),
            ('regiones', models.Region, {'codigo': '09', 'region': 'La Araucanía'}),
            ('provincias', models.Provincia, {'codigo': '091', 'provincia': 'Cautín', 'region': '@regiones'}),
            ('comunas', models.Comuna, {'codigo': '09101', 'comuna': 'Temuco', 'provincia': '@provincias'}),
            ('direcciones', models.Direccion, {'calle': 'Prueba', 'comuna': '@comunas'}),
            ('bibliotecas', models.Biblioteca, {'nombre': 'Biblioteca de prueba', 'direccion': '@direcciones'}),
            ('autores', models.Autor, {'nombre': 'Autora de prueba', 'nacionalidad': '@paises'}),
            ('generos', models.Genero, {'genero': 'Narrativa'}),
            ('subgeneros', models.SubGenero, {'subgenero': 'Novela', 'genero': '@generos'}),
            ('editoriales', models.Editorial, {'nombre': 'Editorial de prueba'}),
            ('idiomas', models.Idioma, {'idioma': 'Español'}),
            ('ediciones', models.Edicion, {'fecha_edicion': '2025-01-01', 'editorial': '@editoriales', 'idioma': '@idiomas'}),
            ('libros', models.Libro, {'titulo': 'Libro de prueba', 'paginas': 100, 'autor': '@autores', 'subgenero': '@subgeneros', 'edicion': '@ediciones', 'biblioteca': '@bibliotecas'}),
            ('estados', models.Estado, {'estado': 'Bueno'}),
            ('ubicaciones', models.Ubicacion, {'codigo': 'A1', 'ubicacion': 'Estante A'}),
            ('inventarios', models.Inventario, {'libro': '@libros', 'estado': '@estados', 'ubicacion': '@ubicaciones', 'gtin': 'PRUEBA-001'}),
            ('usuarios', models.Usuario, {'nombre': 'Lector de prueba', 'rut': '11111111-1', 'fecha_nacimiento': '2000-01-01', 'biblioteca': '@bibliotecas'}),
            ('prestamos', models.Prestamo, {'libro': '@inventarios', 'lector': '@usuarios', 'fecha_devolucion': future}),
        ]
        self.records = {}
        self.payloads = {}
        for route, model, fields in self.specs:
            payload = {k: self.records[v[1:]].pk if isinstance(v, str) and v.startswith('@') else v for k, v in fields.items()}
            kwargs = {k + '_id' if model._meta.get_field(k).many_to_one else k: v for k, v in payload.items()}
            self.records[route] = model.objects.create(**kwargs)
            self.payloads[route] = payload

    def exercise_crud(self, route):
        model = type(self.records[route])
        payload = self.payloads[route].copy()
        base = f'/api/{route}/'
        response = self.client.post(base, payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data['id']
        self.assertTrue(model.objects.filter(pk=pk).exists())
        url = f'{base}{pk}/'
        self.assertEqual(self.client.get(base).status_code, 200)
        self.assertEqual(self.client.get(url).data['id'], pk)
        key = next(k for k in payload if isinstance(payload[k], str))
        if key.startswith('fecha_'):
            payload[key] = (timezone.now() + timedelta(days=20)).isoformat() if route == 'prestamos' else '2025-02-01'
        else:
            payload[key] = 'X'  # válido incluso para códigos cortos
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        obj = model.objects.get(pk=pk)
        self.assertEqual(str(getattr(obj, key))[:10], str(payload[key])[:10])
        patch = {'fecha_devolucion': (timezone.now() + timedelta(days=30)).isoformat()} if route == 'prestamos' else {'habilitado': False}
        response = self.client.patch(url, patch, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        obj.refresh_from_db()
        if route != 'prestamos':
            self.assertFalse(obj.habilitado)
        else:
            self.assertEqual(obj.fecha_devolucion.date().isoformat(), patch['fecha_devolucion'][:10])
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(model.objects.filter(pk=pk).exists())
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_anonymous_access_rejected(self):
        self.client.force_authenticate(None)
        for route, _, _ in self.specs:
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                url = f'/api/{route}/' if method in ['get', 'post'] else f'/api/{route}/{self.records[route].pk}/'
                self.assertEqual(getattr(self.client, method)(url).status_code, 401)

    def test_password_is_hashed_and_never_returned(self):
        data = {**self.payloads['usuarios'], 'contrasenia': 'ClaveSoloPruebas456!'}
        response = self.client.post('/api/usuarios/', data, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn('contrasenia', response.data)
        obj = models.Usuario.objects.get(pk=response.data['id'])
        self.assertTrue(check_password(data['contrasenia'], obj.contrasenia))
        self.assertNotIn('contrasenia', self.client.get(f'/api/usuarios/{obj.pk}/').data)
        response = self.client.patch(f'/api/usuarios/{obj.pk}/', {'contrasenia': 'OtraClave123!'}, format='json')
        self.assertEqual(response.status_code, 200)
        obj.refresh_from_db()
        self.assertTrue(check_password('OtraClave123!', obj.contrasenia))

    def test_invalid_data_rejected(self):
        cases = [('libros', {'paginas': 0}), ('libros', {'autor': 999999}),
                 ('usuarios', {'correo': 'no-es-email'}),
                 ('prestamos', {'fecha_devolucion': '2000-01-01T00:00:00Z'})]
        for route, changes in cases:
            response = self.client.post(f'/api/{route}/', {**self.payloads[route], **changes}, format='json')
            self.assertEqual(response.status_code, 400, response.data)

    def test_basic_login(self):
        import base64
        self.client.force_authenticate(None)
        token = base64.b64encode(b'prueba:ClaveSoloPruebas123!').decode()
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + token)
        self.assertEqual(self.client.get('/api/paises/').status_code, 200)

    def test_browser_login_redirects_to_api(self):
        self.client.force_authenticate(None)
        response = self.client.post('/api-auth/login/', {
            'username': 'prueba', 'password': 'ClaveSoloPruebas123!',
        })
        self.assertRedirects(response, '/api/')
        self.assertEqual(self.client.get('/api/paises/').status_code, 200)


def crud_test(route):
    def test(self):
        self.exercise_crud(route)
    return test

for route in ['paises', 'regiones', 'provincias', 'comunas', 'direcciones', 'bibliotecas',
              'autores', 'generos', 'subgeneros', 'editoriales', 'idiomas', 'ediciones',
              'libros', 'estados', 'ubicaciones', 'inventarios', 'usuarios', 'prestamos']:
    setattr(ApiTests, 'test_crud_' + route, crud_test(route))
