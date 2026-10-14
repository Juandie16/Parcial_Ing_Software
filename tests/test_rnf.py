"""Verificación de RNF01 (modificabilidad), RNF02 (claridad de errores) y RNF03 (confiabilidad)."""
import copy
import glob
import json
import os
import random
import re
import string

import pytest

from motor import ErrorDeEleccion, HistoriaInvalida, Sesion, cargar_historia, construir
from tests.conftest import RAIZ
from tests.test_validacion import CASOS


# ---- RNF01: el contenido cambia sin tocar el código del motor ----
def test_rnf01_historia_nueva_solo_con_contenido(tmp_path):
    datos = {
        "titulo": "Prueba", "inicio": "A", "variables": {"llave": False},
        "escenas": [
            {"id": "A", "texto": "a", "final": False, "opciones": [
                {"id": "tomar", "texto": "t", "destino": "B", "efectos": {"llave": True}}]},
            {"id": "B", "texto": "b", "final": False, "opciones": [
                {"id": "abrir", "texto": "o", "destino": "C", "condiciones": {"llave": True}}]},
            {"id": "C", "texto": "c", "final": True, "opciones": []},
        ],
    }
    ruta = tmp_path / "nueva.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    s = Sesion(cargar_historia(str(ruta)))
    s.elegir("tomar")
    s.elegir("abrir")
    assert s.es_final and s.escena.id == "C"


def test_rnf01_cambiar_destino_y_condicion_solo_editando_datos(datos):
    datos = copy.deepcopy(datos)
    e3 = next(e for e in datos["escenas"] if e["id"] == "E3")
    e3["opciones"][2]["destino"] = "E4"                      # cortar ahora lleva a E4
    e3["opciones"][1]["condiciones"] = {"conoce_origen": True}  # ambas activaciones requieren origen
    s = Sesion(construir(datos))
    s.elegir("revisar"); s.elegir("continuar")
    assert [o.id for o in s.opciones_disponibles()] == ["cortar"]
    s.elegir("cortar")
    assert s.escena.id == "E4"


def test_rnf01_motor_sin_identificadores_de_la_historia():
    patron = re.compile(r"""["']E[1-6]["']|["']conoce_origen["']|["']confia_en_la_voz["']""")
    for archivo in glob.glob(os.path.join(RAIZ, "motor", "*.py")) + [os.path.join(RAIZ, "consola.py")]:
        with open(archivo, encoding="utf-8") as f:
            assert not patron.search(f.read()), f"{archivo} contiene identificadores de la historia"


# ---- RNF02: 100 % de los errores de contenido nombran el ID o campo y no hay traceback ----
@pytest.mark.parametrize("mutar, referencia", CASOS)
def test_rnf02_mensaje_con_referencia_y_sin_traceback(datos, mutar, referencia):
    mutar(datos)
    with pytest.raises(HistoriaInvalida) as exc:  # cualquier otra excepción haría fallar la prueba
        construir(datos)
    assert any(referencia in m for m in exc.value.errores)
    assert all("Traceback" not in m for m in exc.value.errores)


# ---- RNF03: 0 excepciones no controladas y estado intacto ----
@pytest.mark.parametrize("mutar, _ref", CASOS)
def test_rnf03_17_archivos_invalidos_solo_error_controlado(datos, tmp_path, mutar, _ref):
    mutar(datos)
    ruta = tmp_path / "x.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    with pytest.raises(HistoriaInvalida):
        cargar_historia(str(ruta))


def test_rnf03_cantidad_de_casos_invalidos():
    assert len(CASOS) >= 17


def test_rnf03_50_entradas_invalidas_no_alteran_estado(sesion):
    sesion.elegir("revisar"); sesion.elegir("continuar")  # E3 sin origen
    rnd = random.Random(2026)
    habilitadas = {o.id for o in sesion.opciones_disponibles()}
    rechazadas = 0
    for _ in range(50):
        entrada = "".join(rnd.choices(string.ascii_letters + string.digits + "_ ", k=rnd.randint(0, 12)))
        if entrada in habilitadas:
            continue
        antes = (sesion.escena.id, sesion.variables)
        with pytest.raises(ErrorDeEleccion):
            sesion.elegir(entrada)
        assert (sesion.escena.id, sesion.variables) == antes
        rechazadas += 1
    assert rechazadas == 50
