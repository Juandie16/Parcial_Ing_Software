import copy
import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from motor import Sesion, construir  # noqa: E402

RUTA_REFERENCIA = os.path.join(RAIZ, "historias", "la_ultima_transmision.json")
RUTA_FARO = os.path.join(RAIZ, "historias", "el_faro.json")


@pytest.fixture
def datos():
    """Copia fresca de los datos de la historia de referencia (dict)."""
    with open(RUTA_REFERENCIA, encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))


@pytest.fixture
def sesion(datos):
    return Sesion(construir(datos))
