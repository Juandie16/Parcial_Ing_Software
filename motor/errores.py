"""Errores controlados del motor."""


class HistoriaInvalida(Exception):
    """El contenido no es válido. `errores` lista cada causa encontrada."""

    def __init__(self, errores):
        self.errores = list(errores)
        super().__init__("; ".join(self.errores))


class ErrorDeEleccion(Exception):
    """La opción pedida no existe o no está habilitada. No altera la partida."""
