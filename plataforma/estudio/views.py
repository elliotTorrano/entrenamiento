from decimal import Decimal, InvalidOperation

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import contenido
from .progreso import DOMINADO, EN_CURSO, Progreso


def ruta(request):
    etapas, modulos = contenido.indice()
    progreso = Progreso()
    dominados = progreso.dominados(modulos)
    tarjetas = [(m, progreso.resumen(m, dominados)) for m in modulos]

    en_curso = [m for m, r in tarjetas if r["estado"] == EN_CURSO]
    disponibles = [m for m, r in tarjetas if r["disponible"] and r["estado"] != DOMINADO]
    siguiente = (en_curso or disponibles or [None])[0]

    horas_total = sum(m.horas for m in modulos)
    horas_dominadas = sum(m.horas for m in modulos if m.id in dominados)
    contexto = {
        "etapas": [
            (e, [(m, r) for m, r in tarjetas if m.etapa == e["id"]]) for e in etapas
        ],
        "siguiente": siguiente,
        "horas_total": horas_total,
        "horas_dominadas": horas_dominadas,
        "horas_reales": sum(r["horas_reales"] for _, r in tarjetas),
        "porcentaje": round(100 * horas_dominadas / horas_total) if horas_total else 0,
        "dominados": len(dominados),
        "total_modulos": len(modulos),
    }
    return render(request, "estudio/ruta.html", contexto)


def detalle(request, modulo_id):
    modulo = contenido.modulo(modulo_id)
    _, modulos = contenido.indice()
    posicion = [m.id for m in modulos].index(modulo.id)
    contexto = _contexto_modulo(modulo, Progreso())
    contexto.update(
        {
            "leccion": modulo.leccion_html(),
            "anterior": modulos[posicion - 1] if posicion > 0 else None,
            "siguiente": modulos[posicion + 1] if posicion + 1 < len(modulos) else None,
        }
    )
    return render(request, "estudio/modulo.html", contexto)


@require_POST
def empezar(request, modulo_id):
    modulo = contenido.modulo(modulo_id)
    progreso = Progreso()
    progreso.empezar(modulo)
    progreso.guardar()
    return render(request, "estudio/_estado.html", _contexto_modulo(modulo, progreso))


@require_POST
def marcar(request, modulo_id, indice):
    modulo = contenido.modulo(modulo_id)
    if not 0 <= indice < len(modulo.dominio):
        return HttpResponseBadRequest("Criterio inexistente")
    progreso = Progreso()
    progreso.marcar(modulo, indice, request.POST.get("hecho") == "on")
    progreso.guardar()
    return _con_estado(request, "estudio/_dominio.html", modulo, progreso)


@require_POST
def responder(request, modulo_id, indice):
    modulo = contenido.modulo(modulo_id)
    preguntas = modulo.autoevaluacion()
    try:
        opcion = int(request.POST["opcion"])
        pregunta = preguntas[indice]
    except (KeyError, ValueError, IndexError):
        return HttpResponseBadRequest("Elige una opción")
    if not 0 <= opcion < len(pregunta["opciones"]):
        return HttpResponseBadRequest("Opción inexistente")
    progreso = Progreso()
    progreso.responder(modulo, indice, opcion)
    progreso.guardar()
    return _con_estado(
        request,
        "estudio/_pregunta.html",
        modulo,
        progreso,
        {"p": _pregunta(pregunta, indice, progreso.de(modulo)["respuestas"])},
        extra_oob=["estudio/_resultado.html"],
    )


@require_POST
def reiniciar(request, modulo_id):
    modulo = contenido.modulo(modulo_id)
    progreso = Progreso()
    progreso.reiniciar_autoevaluacion(modulo)
    progreso.guardar()
    return _con_estado(request, "estudio/_autoevaluacion.html", modulo, progreso)


@require_POST
def notas(request, modulo_id):
    modulo = contenido.modulo(modulo_id)
    progreso = Progreso()
    progreso.guardar_notas(modulo, request.POST.get("notas", ""))
    progreso.guardar()
    hora = timezone.localtime().strftime("%H:%M")
    return HttpResponse(f"Guardado a las {hora}")


@require_POST
def horas(request, modulo_id):
    modulo = contenido.modulo(modulo_id)
    try:
        cantidad = Decimal(request.POST.get("horas", ""))
    except InvalidOperation:
        return HttpResponseBadRequest("Escribe un número de horas")
    progreso = Progreso()
    progreso.sumar_horas(modulo, cantidad)
    progreso.guardar()
    return render(request, "estudio/_estado.html", _contexto_modulo(modulo, progreso))


# --- Auxiliares ---------------------------------------------------------------


def _pregunta(pregunta, indice, respuestas):
    elegida = respuestas.get(str(indice))
    return {
        "indice": indice,
        "numero": indice + 1,
        "texto": pregunta["pregunta"],
        "opciones": list(enumerate(pregunta["opciones"])),
        "correcta": pregunta["correcta"],
        "explicacion": pregunta["explicacion"],
        "elegida": elegida,
        "respondida": elegida is not None,
        "acierto": elegida == pregunta["correcta"],
    }


def _contexto_modulo(modulo, progreso):
    _, modulos = contenido.indice()
    registro = progreso.de(modulo)
    preguntas = modulo.autoevaluacion()
    return {
        "modulo": modulo,
        "resumen": progreso.resumen(modulo, progreso.dominados(modulos)),
        "criterios": list(zip(range(len(modulo.dominio)), modulo.dominio, registro["checks"])),
        "preguntas": [_pregunta(p, i, registro["respuestas"]) for i, p in enumerate(preguntas)],
        "puntaje_actual": progreso.puntaje_actual(modulo),
        "completa": bool(preguntas) and len(registro["respuestas"]) == len(preguntas),
        "notas": registro["notas"],
    }


def _con_estado(request, plantilla, modulo, progreso, extra=None, extra_oob=()):
    """Devuelve el fragmento pedido más el panel de estado, que HTMX
    coloca en su lugar por id gracias a hx-swap-oob (out of band)."""
    contexto = _contexto_modulo(modulo, progreso)
    contexto.update(extra or {})
    partes = [render_to_string(plantilla, contexto, request)]
    for oob in ["estudio/_estado.html", *extra_oob]:
        partes.append(render_to_string(oob, {**contexto, "oob": True}, request))
    return HttpResponse("".join(partes))
