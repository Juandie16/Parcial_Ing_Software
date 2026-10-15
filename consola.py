"""Interfaz de consola. Solo presenta y pide datos; las reglas viven en `motor`."""
import argparse
import sys

from motor import ErrorDeEleccion, HistoriaInvalida, Sesion, cargar_historia

RUTA_POR_DEFECTO = "historias/la_ultima_transmision.json"


COMANDO_DESHACER = "d"


def jugar(historia, entrada=input, salida=print):
    sesion = Sesion(historia)
    salida(f"\n=== {historia.titulo} ===")
    while True:
        salida(f"\n{sesion.escena.texto}")
        if sesion.es_final or sesion.bloqueada:
            if sesion.es_final:
                salida("\n-- FIN --")
            else:
                salida("\n[Bloqueo] Ninguna opción está disponible en esta escena. Revisa el contenido.")
            accion = _preguntar_al_terminar(sesion, entrada, salida)
            if accion == "reiniciar":
                sesion.reiniciar()
                continue
            if accion == "deshacer":
                sesion.deshacer()
                salida("Se deshizo la última decisión.")
                continue
            return
        opciones = sesion.opciones_disponibles()
        for n, o in enumerate(opciones, 1):
            salida(f"  {n}. {o.texto}")
        if sesion.puede_deshacer:
            salida(f"  {COMANDO_DESHACER}. Deshacer la última decisión")
        texto = entrada("> ").strip().lower()
        if texto == COMANDO_DESHACER:
            if sesion.deshacer():
                salida("Se deshizo la última decisión.")
            else:
                salida("No hay ninguna decisión para deshacer.")
            continue
        if not (texto.isdigit() and 1 <= int(texto) <= len(opciones)):
            salida(f"Entrada no válida. Escribe un número entre 1 y {len(opciones)}.")
            continue
        try:
            sesion.elegir(opciones[int(texto) - 1].id)
        except ErrorDeEleccion as e:
            salida(str(e))


def _preguntar_al_terminar(sesion, entrada, salida):
    """Devuelve 'reiniciar', 'deshacer' o 'salir'."""
    extra = f", {COMANDO_DESHACER} = deshacer la última decisión" if sesion.puede_deshacer else ""
    while True:
        r = entrada(f"¿Jugar de nuevo? (s/n{extra}) ").strip().lower()
        if r == COMANDO_DESHACER:
            if sesion.puede_deshacer:
                return "deshacer"
            salida("No hay ninguna decisión para deshacer.")
            continue
        return "reiniciar" if r in ("s", "si", "sí") else "salir"


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
    try:
        jugar(historia)
    except (EOFError, KeyboardInterrupt):
        print("\nPartida terminada por el usuario.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
