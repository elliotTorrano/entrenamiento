from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .forms import RequerimientoForm
from .models import Dependencia, Requerimiento
from .reglas import validar_folio

HTMX = {"HTTP_HX_REQUEST": "true"}


class ReglasTests(TestCase):
    def test_folio(self):
        self.assertTrue(validar_folio("SSC-0012/2026", "SSC-####/AAAA"))
        self.assertFalse(validar_folio("SSC-12/2026", "SSC-####/AAAA"))


class VistasTests(TestCase):
    fixtures = ["datos_ficticios"]

    def test_cancelado_cuenta_cero(self):
        r = Requerimiento.objects.get(folio="SSC-0003/2026")
        self.assertEqual(r.monto_efectivo, Decimal("0"))

    def test_lista_completa_y_parcial(self):
        url = reverse("requerimientos:lista")
        completa = self.client.get(url)
        self.assertContains(completa, "<html")
        parcial = self.client.get(url, {"estatus": "cancelado"}, **HTMX)
        self.assertNotContains(parcial, "<html")
        self.assertContains(parcial, "SSC-0003/2026")
        self.assertNotContains(parcial, "SSC-0001/2026")

    def test_busqueda(self):
        r = self.client.get(reverse("requerimientos:lista"), {"q": "grúa"}, **HTMX)
        self.assertContains(r, "DGT/01/2026")
        self.assertNotContains(r, "SSC-0002/2026")

    def test_cambiar_estatus_devuelve_fila(self):
        r = Requerimiento.objects.get(folio="SSC-0004/2026")
        resp = self.client.post(reverse("requerimientos:cambiar_estatus", args=[r.pk]), {"estatus": "cancelado"}, **HTMX)
        self.assertContains(resp, f'id="req-{r.pk}"')
        r.refresh_from_db()
        self.assertEqual(r.estatus, "cancelado")

    def test_cambiar_estatus_requiere_post(self):
        r = Requerimiento.objects.first()
        self.assertEqual(self.client.get(reverse("requerimientos:cambiar_estatus", args=[r.pk])).status_code, 405)

    def test_alta_con_folio_invalido(self):
        dep = Dependencia.objects.get(nombre="SSC")
        form = RequerimientoForm(data={"folio": "SSC-1/2026", "dependencia": dep.pk, "monto": "10", "estatus": "pendiente", "fecha": "2026-09-30"})
        self.assertFalse(form.is_valid())
        self.assertIn("folio", form.errors)

    def test_alta_normal_redirige(self):
        dep = Dependencia.objects.get(nombre="SSC")
        datos = {"folio": "SSC-0100/2026", "dependencia": dep.pk, "monto": "10", "estatus": "pendiente", "fecha": "2026-09-30"}
        resp = self.client.post(reverse("requerimientos:nuevo"), datos)
        self.assertRedirects(resp, reverse("requerimientos:lista"))

    def test_alta_htmx_responde_204_con_evento(self):
        dep = Dependencia.objects.get(nombre="SSC")
        datos = {"folio": "SSC-0101/2026", "dependencia": dep.pk, "monto": "10", "estatus": "pendiente", "fecha": "2026-09-30"}
        resp = self.client.post(reverse("requerimientos:nuevo"), datos, **HTMX)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(resp["HX-Trigger"], "requerimiento-guardado")

    def test_borrar_htmx(self):
        r = Requerimiento.objects.get(folio="PC-002-2026")
        resp = self.client.post(reverse("requerimientos:borrar", args=[r.pk]), **HTMX)
        self.assertEqual(resp.content, b"")
        self.assertFalse(Requerimiento.objects.filter(pk=r.pk).exists())
