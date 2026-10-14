"""Pruebas unitarias U1, U2, U3, U5 del motor (CA01 y CA02 incluidos)."""
import pytest

from motor import ErrorDeEleccion, Sesion, construir


def ids(sesion):
    return [o.id for o in sesion.opciones_disponibles()]


# U1: condiciones cumplidas / no cumplidas habilitan solo las opciones correspondientes
@pytest.mark.parametrize(
    "camino, esperadas",
    [
        (["revisar", "investigar"], ["activar_codigo", "cortar"]),   # conoce_origen = True
        (["revisar", "continuar"], ["activar_sin_verificar", "cortar"]),  # conoce_origen = False
    ],
)
def test_u1_condiciones_habilitan_opciones(sesion, camino, esperadas):
    for paso in camino:
        sesion.elegir(paso)
    assert sesion.escena.id == "E3"
    assert ids(sesion) == esperadas
    assert len(ids(sesion)) == 2


def test_u1_mapa_de_condiciones_vacio_habilita(sesion):
    assert ids(sesion) == ["revisar"]


# U2: elección válida aplica efectos y avanza al destino
@pytest.mark.parametrize(
    "camino, escena, conoce, confia",
    [
        (["revisar"], "E2", False, False),
        (["revisar", "investigar"], "E3", True, False),
        (["revisar", "investigar", "activar_codigo"], "E4", True, True),
        (["revisar", "continuar", "activar_sin_verificar"], "E5", False, True),
        (["revisar", "investigar", "cortar"], "E6", True, False),
    ],
)
def test_u2_eleccion_valida_aplica_efectos_y_avanza(sesion, camino, escena, conoce, confia):
    for paso in camino:
        sesion.elegir(paso)
    assert sesion.escena.id == escena
    assert sesion.variables == {"conoce_origen": conoce, "confia_en_la_voz": confia}


# U3: opción inexistente o no habilitada deja intacto el estado (CA02)
@pytest.mark.parametrize("intento", ["no_existe", "activar_codigo", "", "E4"])
def test_u3_opcion_invalida_no_altera_estado(sesion, intento):
    sesion.elegir("revisar")
    sesion.elegir("continuar")  # conoce_origen = False, escena E3
    antes = (sesion.escena.id, sesion.variables)
    with pytest.raises(ErrorDeEleccion):
        sesion.elegir(intento)
    assert (sesion.escena.id, sesion.variables) == antes


def test_ca02_activar_sin_verificar_lleva_a_e5(sesion):
    sesion.elegir("revisar")
    sesion.elegir("continuar")
    sesion.elegir("activar_sin_verificar")
    assert sesion.escena.id == "E5"


def test_u3_final_no_acepta_elecciones(sesion):
    for paso in ["revisar", "investigar", "cortar"]:
        sesion.elegir(paso)
    assert sesion.es_final
    with pytest.raises(ErrorDeEleccion):
        sesion.elegir("revisar")
    assert sesion.escena.id == "E6"


# U5: reiniciar restaura escena y variables iniciales
def test_u5_reiniciar_restaura_estado(sesion):
    for paso in ["revisar", "investigar", "activar_codigo"]:
        sesion.elegir(paso)
    assert sesion.variables["confia_en_la_voz"] is True
    sesion.reiniciar()
    assert sesion.escena.id == "E1"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}


def test_u5_estado_exterior_no_modifica_sesion(sesion):
    sesion.variables["conoce_origen"] = True  # modifica solo una copia
    assert sesion.variables["conoce_origen"] is False


# Bloqueo: escena no final sin opciones habilitadas
def test_escena_bloqueada_se_informa_y_permite_reiniciar(datos):
    datos["escenas"][0]["opciones"][0]["condiciones"] = {"conoce_origen": True}
    s = Sesion(construir(datos))
    assert s.bloqueada is True
    assert s.opciones_disponibles() == []
    with pytest.raises(ErrorDeEleccion):
        s.elegir("revisar")
    s.reiniciar()
    assert s.escena.id == "E1"
