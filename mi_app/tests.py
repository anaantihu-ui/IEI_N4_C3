from django.test import SimpleTestCase
from django.urls import reverse, resolve


class InterfazGestionTests(SimpleTestCase):
    def test_dashboard_renderiza(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Panorama general")
        self.assertContains(respuesta, "/static/mi_app/js/app.js")

    def test_panel_voluntarios(self):
        respuesta = self.client.get(reverse("gestion", args=["voluntarios"]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "GESTIÓN DE REGISTROS")
        self.assertContains(respuesta, 'data-resource="voluntarios"')

    def test_los_trece_modulos_tienen_panel(self):
        from mi_app.views import PANEL_PAGES
        self.assertEqual(len(PANEL_PAGES), 13)
        for slug in PANEL_PAGES:
            with self.subTest(modulo=slug):
                self.assertEqual(self.client.get(reverse("gestion", args=[slug])).status_code, 200)

    def test_panel_desconocido_devuelve_404(self):
        self.assertEqual(self.client.get("/gestion/inexistente/").status_code, 404)

    def test_ruta_rest_sigue_registrada(self):
        coincidencia = resolve("/api/voluntarios/")
        self.assertEqual(coincidencia.func.cls.__name__, "VoluntarioViewSet")


from django.test import TestCase


class TemaAPINavegableTests(TestCase):
    def test_api_html_tiene_tema_comunidad(self):
        respuesta = self.client.get("/api/voluntarios/", HTTP_ACCEPT="text/html")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Comunidad+")
        self.assertContains(respuesta, "EXPLORADOR REST")
        self.assertContains(respuesta, "cp-hero")
        self.assertTemplateUsed(respuesta, "rest_framework/api.html")

    def test_json_no_cambia(self):
        respuesta = self.client.get("/api/voluntarios/", HTTP_ACCEPT="application/json")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), [])
