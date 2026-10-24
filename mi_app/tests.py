"""Pruebas de las páginas existentes; no agregan funcionalidad ficticia."""
from django.test import SimpleTestCase
from django.urls import reverse


class PaginaInicialTests(SimpleTestCase):
    def test_pagina_inicio_responde(self):
        response = self.client.get(reverse('bienvenida'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenido a mi aplicación')

    def test_ruta_inexistente_devuelve_404(self):
        response = self.client.get('/no-existe-en-este-proyecto/')
        self.assertEqual(response.status_code, 404)
