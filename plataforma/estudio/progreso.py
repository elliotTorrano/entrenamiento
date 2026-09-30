"""Avance del estudiante, guardado en progreso.json en la raíz del repositorio.

Es un archivo de texto a propósito: se sube a Git y así el agente docente
puede leer el avance, las notas y las dudas para ajustar el plan.
"""
import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings

APROBATORIO = 0.8

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
DOMINADO = "dominado"


class Progreso:
    def __init__(self, ruta=None):
        self.ruta = Path(ruta or settings.PROGRESO_PATH)
        if self.ruta.exists():
            self.datos = json.loads(self.ruta.read_text(encoding="utf-8"))
        else:
            self.datos = {"modulos": {}}

    def guardar(self):
        self.datos["actualizado"] = datetime.now().isoformat(timespec="seconds")
        temporal = self.ruta.with_suffix(".tmp")
        temporal.write_text(
            json.dumps(self.datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporal, self.ruta)

    def de(self, modulo):
        registro = self.datos["modulos"].setdefault(modulo.id, {})
        registro.setdefault("inicio", None)
        registro.setdefault("fin", None)
        registro.setdefault("checks", [])
        registro.setdefault("respuestas", {})
        registro.setdefault("mejor_puntaje", None)
        registro.setdefault("intentos", 0)
        registro.setdefault("horas_reales", 0)
        registro.setdefault("notas", "")
        faltan = len(modulo.dominio) - len(registro["checks"])
        if faltan > 0:
            registro["checks"].extend([False] * faltan)
        del registro["checks"][len(modulo.dominio):]
        return registro

    # --- Acciones -----------------------------------------------------------

    def empezar(self, modulo):
        registro = self.de(modulo)
        registro["inicio"] = registro["inicio"] or date.today().isoformat()
        self._cerrar(modulo)

    def marcar(self, modulo, indice, hecho):
        self.empezar(modulo)
        self.de(modulo)["checks"][indice] = hecho
        self._cerrar(modulo)

    def responder(self, modulo, indice, opcion):
        """Guarda la primera respuesta a una pregunta. Devuelve la opción guardada."""
        self.empezar(modulo)
        registro = self.de(modulo)
        clave = str(indice)
        if clave not in registro["respuestas"]:
            registro["respuestas"][clave] = opcion
            preguntas = modulo.autoevaluacion()
            if len(registro["respuestas"]) == len(preguntas):
                registro["intentos"] += 1
                puntaje = self.puntaje_actual(modulo)
                if registro["mejor_puntaje"] is None or puntaje > registro["mejor_puntaje"]:
                    registro["mejor_puntaje"] = puntaje
        self._cerrar(modulo)
        return registro["respuestas"][clave]

    def reiniciar_autoevaluacion(self, modulo):
        self.de(modulo)["respuestas"] = {}

    def guardar_notas(self, modulo, texto):
        self.de(modulo)["notas"] = texto

    def sumar_horas(self, modulo, horas):
        self.empezar(modulo)
        registro = self.de(modulo)
        total = Decimal(str(registro["horas_reales"])) + horas
        registro["horas_reales"] = float(max(total, Decimal("0")))

    def _cerrar(self, modulo):
        registro = self.de(modulo)
        if self.estado(modulo) == DOMINADO:
            registro["fin"] = registro["fin"] or date.today().isoformat()
        else:
            registro["fin"] = None

    # --- Consultas ----------------------------------------------------------

    def puntaje_actual(self, modulo):
        preguntas = modulo.autoevaluacion()
        respuestas = self.de(modulo)["respuestas"]
        if not preguntas:
            return None
        aciertos = sum(
            1 for i, p in enumerate(preguntas) if respuestas.get(str(i)) == p["correcta"]
        )
        return round(aciertos / len(preguntas), 2)

    def autoevaluacion_aprobada(self, modulo):
        if not modulo.autoevaluacion():
            return True
        mejor = self.de(modulo)["mejor_puntaje"]
        return mejor is not None and mejor >= APROBATORIO

    def estado(self, modulo):
        registro = self.de(modulo)
        if registro["checks"] and all(registro["checks"]) and self.autoevaluacion_aprobada(modulo):
            return DOMINADO
        if registro["inicio"]:
            return EN_CURSO
        return PENDIENTE

    def resumen(self, modulo, dominados):
        registro = self.de(modulo)
        return {
            "estado": self.estado(modulo),
            "disponible": all(r in dominados for r in modulo.requiere),
            "faltan": [r for r in modulo.requiere if r not in dominados],
            "checks_hechos": sum(registro["checks"]),
            "checks_total": len(registro["checks"]),
            "mejor_puntaje": registro["mejor_puntaje"],
            "aprobado": self.autoevaluacion_aprobada(modulo),
            "tiene_autoevaluacion": bool(modulo.autoevaluacion()),
            "horas_reales": registro["horas_reales"],
            "inicio": registro["inicio"],
            "fin": registro["fin"],
        }

    def dominados(self, modulos):
        return {m.id for m in modulos if self.estado(m) == DOMINADO}
