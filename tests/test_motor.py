"""Pruebas unitarias U1, U2, U3, U5 y U6 del motor (CA01, CA02 y CA04 incluidos)."""
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


def test_u5_reiniciar_elimina_historial_de_retroceso(sesion):
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    assert sesion.puede_deshacer
    sesion.reiniciar()
    assert not sesion.puede_deshacer
    assert sesion.deshacer() is False  # no hay nada que deshacer: estado inicial intacto
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


# U6: deshacer restaura escena y variables y consume la posibilidad de retroceder (RF20)
def test_u6_al_iniciar_no_hay_retroceso(sesion):
    assert not sesion.puede_deshacer
    assert sesion.deshacer() is False
    assert sesion.escena.id == "E1"


def test_u6_deshacer_restaura_escena_y_variables_y_consume_retroceso(sesion):
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    assert (sesion.escena.id, sesion.variables["conoce_origen"]) == ("E3", True)
    assert sesion.deshacer() is True
    assert sesion.escena.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    assert not sesion.puede_deshacer
    assert sesion.deshacer() is False  # segundo intento: no cambia nada (un solo nivel)
    assert sesion.escena.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}


def test_ca04_ejemplo_del_cliente(sesion):
    """Desde E2, investigar -> E3 con origen; deshacer -> E2 sin origen; segundo deshacer no cambia;
    continuar sin investigar -> E3 muestra activar sin verificar y cortar comunicación."""
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.deshacer()
    assert (sesion.escena.id, sesion.variables["conoce_origen"]) == ("E2", False)
    antes = (sesion.escena.id, sesion.variables)
    sesion.deshacer()
    assert (sesion.escena.id, sesion.variables) == antes
    sesion.elegir("continuar")
    assert sesion.escena.id == "E3"
    assert ids(sesion) == ["activar_sin_verificar", "cortar"]


@pytest.mark.parametrize("intento", ["no_existe", "activar_codigo", "", "E4"])
def test_u6_entrada_invalida_preserva_historial(sesion, intento):
    sesion.elegir("revisar")
    sesion.elegir("continuar")  # E3, conoce_origen = False; última elección válida: continuar
    with pytest.raises(ErrorDeEleccion):
        sesion.elegir(intento)
    assert sesion.puede_deshacer
    sesion.deshacer()
    assert sesion.escena.id == "E2"  # deshace "continuar", no la entrada inválida
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}


def test_u6_entrada_invalida_tras_deshacer_no_habilita_retroceso(sesion):
    sesion.elegir("revisar")
    sesion.deshacer()
    with pytest.raises(ErrorDeEleccion):
        sesion.elegir("no_existe")
    assert not sesion.puede_deshacer
    assert sesion.escena.id == "E1"


@pytest.mark.parametrize("nueva", ["investigar", "continuar"])
def test_u6_nueva_eleccion_vuelve_a_habilitar_retroceso(sesion, nueva):
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.deshacer()
    assert not sesion.puede_deshacer
    sesion.elegir(nueva)
    assert sesion.puede_deshacer
    sesion.deshacer()
    assert sesion.escena.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}


def test_u6_deshacer_restaura_todas_las_variables(sesion):
    for paso in ["revisar", "investigar", "activar_codigo"]:
        sesion.elegir(paso)
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": True}
    sesion.deshacer()
    assert sesion.escena.id == "E3"
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": False}


def test_u6_deshacer_sale_de_un_bloqueo(datos):
    e2 = next(e for e in datos["escenas"] if e["id"] == "E2")
    e2["opciones"][0]["destino"] = "E3"
    for o in next(e for e in datos["escenas"] if e["id"] == "E3")["opciones"]:
        o["condiciones"] = {"confia_en_la_voz": True}
    s = Sesion(construir(datos))
    s.elegir("revisar")
    s.elegir("investigar")
    assert s.bloqueada
    assert s.deshacer() is True
    assert s.escena.id == "E2" and not s.bloqueada
