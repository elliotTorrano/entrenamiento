"""Lectura del material de estudio: modulos/indice.json y la carpeta de cada módulo."""
import json
from dataclasses import dataclass, field

import markdown
from django.conf import settings
from django.http import Http404

MARCA_BORRADOR = "> **Borrador.**"


@dataclass
class Modulo:
    id: str
    carpeta: str
    etapa: int
    horas: int
    requiere: list
    titulo: str
    resumen: str
    dominio: list = field(default_factory=list)

    @property
    def ruta(self):
        return settings.MODULOS_DIR / self.carpeta

    def texto_leccion(self):
        archivo = self.ruta / "leccion.md"
        return archivo.read_text(encoding="utf-8") if archivo.exists() else ""

    @property
    def es_borrador(self):
        return MARCA_BORRADOR in self.texto_leccion()[:600]

    def leccion_html(self):
        return markdown.markdown(
            self.texto_leccion(), extensions=["tables", "fenced_code", "sane_lists"]
        )

    def autoevaluacion(self):
        archivo = self.ruta / "autoevaluacion.json"
        if not archivo.exists():
            return []
        return json.loads(archivo.read_text(encoding="utf-8"))


def indice():
    datos = json.loads((settings.MODULOS_DIR / "indice.json").read_text(encoding="utf-8"))
    modulos = [Modulo(**m) for m in datos["modulos"]]
    return datos["etapas"], modulos


def modulo(modulo_id):
    for m in indice()[1]:
        if m.id == modulo_id:
            return m
    raise Http404(f"No existe el módulo {modulo_id}")
