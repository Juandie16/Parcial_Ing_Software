"""Interfaz de consola: entradas inválidas no alteran la partida y se informa el estado."""
from consola import jugar, main
from motor import cargar_historia
from tests.conftest import RUTA_REFERENCIA


def correr(respuestas):
    it = iter(respuestas)
    salida = []
    jugar(cargar_historia(RUTA_REFERENCIA), entrada=lambda _="": next(it), salida=salida.append)
    return "\n".join(salida)


def test_recorrido_completo_y_fin():
    texto = correr(["1", "1", "1", "n"])
    assert "equipo de rescate" in texto and "FIN" in texto


def test_entrada_invalida_no_avanza_y_no_se_cierra():
    texto = correr(["x", "9", "0", "1", "2", "2", "n"])  # tras errores, llega a E6
    assert texto.count("Entrada no válida") == 3
    assert "interrumpe la comunicación" in texto


def test_reinicio_desde_un_final():
    texto = correr(["1", "1", "1", "s", "1", "2", "1", "n"])
    assert "equipo de rescate" in texto and "mensaje automático antiguo" in texto  # dos partidas distintas


def test_deshacer_en_consola_y_segundo_intento_sin_efecto():
    # E1 -> E2 -> investigar (E3) -> d (E2) -> d (nada) -> continuar (E3) -> activar sin verificar (E5)
    texto = correr(["1", "1", "d", "d", "2", "1", "n"])
    assert texto.count("Se deshizo la última decisión.") == 1
    assert "No hay ninguna decisión para deshacer." in texto
    assert "mensaje automático antiguo" in texto


def test_al_iniciar_no_se_ofrece_deshacer():
    texto = correr(["d", "1", "1", "2", "n"])
    assert "No hay ninguna decisión para deshacer." in texto
    primera_escena = texto.split("La señal incluye")[0]
    assert "Deshacer la última decisión" not in primera_escena


def test_deshacer_desde_un_final_en_consola():
    # llega a E6, deshace (vuelve a E3) y elige activar con código (E4)
    texto = correr(["1", "1", "2", "d", "1", "n"])
    assert "interrumpe la comunicación" in texto
    assert "Se deshizo la última decisión." in texto
    assert "equipo de rescate" in texto


def test_main_con_archivo_invalido_devuelve_error(tmp_path, capsys):
    ruta = tmp_path / "x.json"
    ruta.write_text("{", encoding="utf-8")
    assert main([str(ruta)]) == 1
    assert "No se puede iniciar" in capsys.readouterr().out
