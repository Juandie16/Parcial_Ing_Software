"""Interfaz de consola. Solo presenta y pide datos; las reglas viven en `motor`."""
import argparse
import sys

from motor import ErrorDeEleccion, HistoriaInvalida, Sesion, cargar_historia

RUTA_POR_DEFECTO = "historias/la_ultima_transmision.json"


def jugar(historia, entrada=input, salida=print):
    sesion = Sesion(historia)
    salida(f"\n=== {historia.titulo} ===")
    while True:
        salida(f"\n{sesion.escena.texto}")
        if sesion.es_final:
            salida("\n-- FIN --")
            if _preguntar_reinicio(entrada, salida):
                sesion.reiniciar()
                continue
            return
        if sesion.bloqueada:
            salida("\n[Bloqueo] Ninguna opción está disponible en esta escena. Revisa el contenido.")
            if _preguntar_reinicio(entrada, salida):
                sesion.reiniciar()
                continue
            return
        opciones = sesion.opciones_disponibles()
        for n, o in enumerate(opciones, 1):
            salida(f"  {n}. {o.texto}")
        texto = entrada("> ").strip()
        if not (texto.isdigit() and 1 <= int(texto) <= len(opciones)):
            salida(f"Entrada no válida. Escribe un número entre 1 y {len(opciones)}.")
            continue
        try:
            sesion.elegir(opciones[int(texto) - 1].id)
        except ErrorDeEleccion as e:
            salida(str(e))


def _preguntar_reinicio(entrada, salida):
    return entrada("¿Jugar de nuevo? (s/n) ").strip().lower() in ("s", "si", "sí")


def main(argv=None):
    p = argparse.ArgumentParser(description="Motor de historias interactivas")
    p.add_argument("historia", nargs="?", default=RUTA_POR_DEFECTO, help="ruta del archivo JSON")
    args = p.parse_args(argv)
    try:
        historia = cargar_historia(args.historia)
    except HistoriaInvalida as e:
        print(f"No se puede iniciar: el archivo '{args.historia}' tiene {len(e.errores)} error(es):")
        for err in e.errores:
            print(f"  - {err}")
        return 1
    jugar(historia)
    return 0


if __name__ == "__main__":
    sys.exit(main())
