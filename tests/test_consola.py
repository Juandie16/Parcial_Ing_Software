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


def test_main_con_archivo_invalido_devuelve_error(tmp_path, capsys):
    ruta = tmp_path / "x.json"
    ruta.write_text("{", encoding="utf-8")
    assert main([str(ruta)]) == 1
    assert "No se puede iniciar" in capsys.readouterr().out
