"""Lectura de archivos JSON y construcción del modelo. Rechaza contenido inválido."""
import json

from .errores import HistoriaInvalida
from .modelo import Escena, Historia, Opcion
from .validacion import validar


def construir(datos):
    """Valida `datos` (dict) y construye una Historia; lanza HistoriaInvalida si hay errores."""
    errores = validar(datos)
    if errores:
        raise HistoriaInvalida(errores)
    escenas = {}
    for e in datos["escenas"]:
        opciones = tuple(
            Opcion(o["id"], o["texto"], o["destino"], dict(o.get("condiciones", {})), dict(o.get("efectos", {})))
            for o in e["opciones"]
        )
        escenas[e["id"]] = Escena(e["id"], e["texto"], e["final"], opciones)
    return Historia(datos["titulo"], datos["inicio"], dict(datos["variables"]), escenas)


def cargar_historia(ruta):
    """Lee un archivo JSON y devuelve una Historia válida o lanza HistoriaInvalida."""
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        raise HistoriaInvalida([f"Archivo ilegible: no se encontró '{ruta}'."])
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        raise HistoriaInvalida([f"Archivo ilegible: '{ruta}' no es un JSON válido ({e})."])
    return construir(datos)
