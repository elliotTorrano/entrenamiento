import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from . import contenido
from .progreso import DOMINADO, EN_CURSO, PENDIENTE, Progreso

HTMX = {"HTTP_HX_REQUEST": "true"}


class ContenidoTests(SimpleTestCase):
    """Revisa que el material de modulos/ esté completo y bien formado."""

    def test_indice_consistente(self):
        etapas, modulos = contenido.indice()
        ids = {m.id for m in modulos}
        etapas_ids = {e["id"] for e in etapas}
        for m in modulos:
            self.assertTrue(m.ruta.is_dir(), m.carpeta)
            self.assertTrue((m.ruta / "leccion.md").exists(), m.carpeta)
            self.assertIn(m.etapa, etapas_ids)
            self.assertTrue(set(m.requiere) <= ids, m.id)
            self.assertTrue(m.dominio, m.id)

    def test_autoevaluaciones_validas(self):
        for m in contenido.indice()[1]:
            for p in m.autoevaluacion():
                self.assertTrue(p["pregunta"] and p["explicacion"], m.id)
                self.assertGreaterEqual(len(p["opciones"]), 2, m.id)
                self.assertIn(p["correcta"], range(len(p["opciones"])), m.id)

    def test_modulos_basicos_completos(self):
        for clave in ["M0", "M1", "M2", "M3", "M4", "M5", "M7"]:
            m = contenido.modulo(clave)
            self.assertFalse(m.es_borrador, clave)
            self.assertTrue(m.autoevaluacion(), clave)


class ProgresoTestCase(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta = Path(self.tmp.name) / "progreso.json"
        self.override = override_settings(PROGRESO_PATH=self.ruta)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.tmp.cleanup()

    def leer(self):
        return json.loads(self.ruta.read_text(encoding="utf-8"))


class ProgresoTests(ProgresoTestCase):
    def dominar(self, progreso, modulo):
        for i in range(len(modulo.dominio)):
            progreso.marcar(modulo, i, True)
        for i, p in enumerate(modulo.autoevaluacion()):
            progreso.responder(modulo, i, p["correcta"])

    def test_estados(self):
        m0 = contenido.modulo("M0")
        progreso = Progreso()
        self.assertEqual(progreso.estado(m0), PENDIENTE)
        progreso.empezar(m0)
        self.assertEqual(progreso.estado(m0), EN_CURSO)
        self.dominar(progreso, m0)
        self.assertEqual(progreso.estado(m0), DOMINADO)
        self.assertIsNotNone(progreso.de(m0)["fin"])
        progreso.marcar(m0, 0, False)
        self.assertEqual(progreso.estado(m0), EN_CURSO)
        self.assertIsNone(progreso.de(m0)["fin"])

    def test_checks_sin_autoevaluacion_aprobada_no_domina(self):
        m0 = contenido.modulo("M0")
        progreso = Progreso()
        for i in range(len(m0.dominio)):
            progreso.marcar(m0, i, True)
        for i in range(len(m0.autoevaluacion())):
            progreso.responder(m0, i, 99)
        self.assertEqual(progreso.de(m0)["mejor_puntaje"], 0)
        self.assertEqual(progreso.estado(m0), EN_CURSO)

    def test_primera_respuesta_cuenta(self):
        m0 = contenido.modulo("M0")
        progreso = Progreso()
        correcta = m0.autoevaluacion()[0]["correcta"]
        progreso.responder(m0, 0, correcta + 1)
        self.assertEqual(progreso.responder(m0, 0, correcta), correcta + 1)

    def test_mejor_puntaje_se_conserva(self):
        m0 = contenido.modulo("M0")
        progreso = Progreso()
        self.dominar(progreso, m0)
        progreso.reiniciar_autoevaluacion(m0)
        for i in range(len(m0.autoevaluacion())):
            progreso.responder(m0, i, 99)
        self.assertEqual(progreso.de(m0)["mejor_puntaje"], 1.0)
        self.assertEqual(progreso.de(m0)["intentos"], 2)

    def test_disponibilidad(self):
        _, modulos = contenido.indice()
        progreso = Progreso()
        m1 = contenido.modulo("M1")
        self.assertFalse(progreso.resumen(m1, progreso.dominados(modulos))["disponible"])
        self.dominar(progreso, contenido.modulo("M0"))
        self.assertTrue(progreso.resumen(m1, progreso.dominados(modulos))["disponible"])

    def test_guardar_y_releer(self):
        progreso = Progreso()
        progreso.guardar_notas(contenido.modulo("M2"), "Duda: ¿qué es un 302?")
        progreso.guardar()
        self.assertEqual(Progreso().de(contenido.modulo("M2"))["notas"], "Duda: ¿qué es un 302?")


class VistasTests(ProgresoTestCase):
    def test_ruta(self):
        r = self.client.get(reverse("estudio:ruta"))
        self.assertContains(r, "Ruta de aprendizaje")
        self.assertContains(r, "M0. Herramientas de trabajo")

    def test_detalle_todos_los_modulos(self):
        for m in contenido.indice()[1]:
            r = self.client.get(reverse("estudio:detalle", args=[m.id]))
            self.assertEqual(r.status_code, 200, m.id)

    def test_modulo_inexistente(self):
        self.assertEqual(self.client.get(reverse("estudio:detalle", args=["M99"])).status_code, 404)

    def test_marcar_devuelve_fragmento_y_estado_oob(self):
        r = self.client.post(reverse("estudio:marcar", args=["M0", 0]), {"hecho": "on"}, **HTMX)
        self.assertContains(r, 'id="dominio"')
        self.assertContains(r, 'hx-swap-oob="true"')
        self.assertNotContains(r, "<html")
        self.assertIs(self.leer()["modulos"]["M0"]["checks"][0], True)
        self.client.post(reverse("estudio:marcar", args=["M0", 0]), **HTMX)
        self.assertIs(self.leer()["modulos"]["M0"]["checks"][0], False)

    def test_marcar_indice_invalido(self):
        self.assertEqual(self.client.post(reverse("estudio:marcar", args=["M0", 50])).status_code, 400)

    def test_responder(self):
        correcta = contenido.modulo("M0").autoevaluacion()[0]["correcta"]
        r = self.client.post(reverse("estudio:responder", args=["M0", 0]), {"opcion": correcta}, **HTMX)
        self.assertContains(r, "Correcto.")
        self.assertContains(r, 'id="resultado"')

    def test_responder_sin_opcion(self):
        self.assertEqual(self.client.post(reverse("estudio:responder", args=["M0", 0])).status_code, 400)

    def test_notas_y_horas(self):
        self.client.post(reverse("estudio:notas", args=["M1"]), {"notas": "repasar clases"}, **HTMX)
        self.client.post(reverse("estudio:horas", args=["M1"]), {"horas": "1.5"}, **HTMX)
        datos = self.leer()["modulos"]["M1"]
        self.assertEqual(datos["notas"], "repasar clases")
        self.assertEqual(datos["horas_reales"], 1.5)
        self.assertIsNotNone(datos["inicio"])

    def test_horas_invalidas(self):
        self.assertEqual(self.client.post(reverse("estudio:horas", args=["M1"]), {"horas": "x"}).status_code, 400)

    def test_solo_post(self):
        self.assertEqual(self.client.get(reverse("estudio:empezar", args=["M0"])).status_code, 405)
