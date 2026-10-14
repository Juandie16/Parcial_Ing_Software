"""I1: lectura de archivos reales + motor hasta alcanzar finales; segunda historia sin tocar el motor."""
import pytest

from motor import Sesion, cargar_historia
from tests.conftest import RUTA_FARO, RUTA_REFERENCIA

RUTAS = {
    "E4": ["revisar", "investigar", "activar_codigo"],
    "E5": ["revisar", "continuar", "activar_sin_verificar"],
    "E6": ["revisar", "continuar", "cortar"],
}


@pytest.mark.parametrize("final, camino", RUTAS.items())
def test_i1_archivo_real_hasta_cada_final(final, camino):
    s = Sesion(cargar_historia(RUTA_REFERENCIA))
    for paso in camino:
        assert not s.es_final
        s.elegir(paso)
    assert s.es_final and s.escena.id == final and s.opciones_disponibles() == []
    s.reiniciar()
    assert s.escena.id == "E1" and not s.es_final


def test_historia_de_referencia_tiene_seis_escenas_y_tres_finales():
    h = cargar_historia(RUTA_REFERENCIA)
    assert len(h.escenas) == 6
    assert sorted(e.id for e in h.escenas.values() if e.final) == ["E4", "E5", "E6"]


def test_segunda_historia_funciona_con_el_mismo_motor():
    s = Sesion(cargar_historia(RUTA_FARO))
    assert [o.id for o in s.opciones_disponibles()] == ["almacen", "subir_oscuras"]
    s.elegir("almacen")
    assert s.variables == {"tiene_linterna": True}
    assert [o.id for o in s.opciones_disponibles()] == ["subir_linterna", "rendirse"]
    s.elegir("subir_linterna")
    assert s.es_final and s.escena.id == "F3"
