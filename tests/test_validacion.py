"""U4: errores de contenido producen rechazo controlado con causa e identificador (CA03)."""
import json

import pytest

from motor import HistoriaInvalida, cargar_historia, construir


def e3(datos):
    return next(e for e in datos["escenas"] if e["id"] == "E3")


def quitar(clave):
    return lambda d: d.pop(clave)


def inicio_inexistente(d):
    d["inicio"] = "E99"


def escena_duplicada(d):
    d["escenas"].append(dict(d["escenas"][3]))


def opcion_duplicada(d):
    e3(d)["opciones"].append(dict(e3(d)["opciones"][0]))


def destino_inexistente(d):
    e3(d)["opciones"][0]["destino"] = "E99"


def condicion_no_declarada(d):
    e3(d)["opciones"][0]["condiciones"] = {"fantasma": True}


def efecto_no_declarado(d):
    e3(d)["opciones"][0]["efectos"] = {"fantasma": True}


def condicion_no_booleana(d):
    e3(d)["opciones"][0]["condiciones"] = {"conoce_origen": "si"}


def efecto_no_booleano(d):
    e3(d)["opciones"][0]["efectos"] = {"conoce_origen": 1}


def final_con_opciones(d):
    d["escenas"][3]["opciones"] = [dict(e3(d)["opciones"][2])]


def no_final_sin_opciones(d):
    d["escenas"][0]["opciones"] = []


def escena_sin_texto(d):
    del d["escenas"][0]["texto"]


def opcion_sin_destino(d):
    del e3(d)["opciones"][0]["destino"]


def variable_inicial_no_booleana(d):
    d["variables"]["conoce_origen"] = "no"


CASOS = [
    (quitar("titulo"), "titulo"),
    (quitar("inicio"), "inicio"),
    (quitar("variables"), "variables"),
    (quitar("escenas"), "escenas"),
    (escena_sin_texto, "texto"),
    (opcion_sin_destino, "destino"),
    (inicio_inexistente, "E99"),
    (escena_duplicada, "E4"),
    (opcion_duplicada, "activar_codigo"),
    (destino_inexistente, "E99"),
    (condicion_no_declarada, "fantasma"),
    (efecto_no_declarado, "fantasma"),
    (condicion_no_booleana, "conoce_origen"),
    (efecto_no_booleano, "conoce_origen"),
    (variable_inicial_no_booleana, "conoce_origen"),
    (final_con_opciones, "E4"),
    (no_final_sin_opciones, "E1"),
]


@pytest.mark.parametrize("mutar, referencia", CASOS)
def test_u4_contenido_invalido_se_rechaza_con_causa(datos, mutar, referencia):
    mutar(datos)
    with pytest.raises(HistoriaInvalida) as exc:
        construir(datos)
    assert exc.value.errores, "debe informar al menos una causa"
    assert any(referencia in m for m in exc.value.errores)


def test_historia_valida_no_produce_errores(datos):
    assert construir(datos).inicio == "E1"


def test_ca03_destino_e99_rechazado_con_mensaje(datos, tmp_path):
    destino_inexistente(datos)
    ruta = tmp_path / "mala.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    with pytest.raises(HistoriaInvalida) as exc:
        cargar_historia(str(ruta))
    assert "E99" in str(exc.value) and "E3" in str(exc.value)


@pytest.mark.parametrize("contenido", ["{ no es json", "", "[1, 2, 3]", '"texto"', "null"])
def test_u4_archivo_ilegible_o_estructura_incorrecta(tmp_path, contenido):
    ruta = tmp_path / "x.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(HistoriaInvalida):
        cargar_historia(str(ruta))


def test_u4_archivo_inexistente(tmp_path):
    with pytest.raises(HistoriaInvalida) as exc:
        cargar_historia(str(tmp_path / "nada.json"))
    assert "nada.json" in str(exc.value)


def test_se_informan_varios_errores_a_la_vez(datos):
    destino_inexistente(datos)
    condicion_no_declarada(datos)
    with pytest.raises(HistoriaInvalida) as exc:
        construir(datos)
    assert len(exc.value.errores) >= 2
