"""Sesión de juego: estado de una partida sobre una Historia ya validada."""
from .errores import ErrorDeEleccion


class Sesion:
    def __init__(self, historia):
        self._historia = historia
        self.reiniciar()

    def reiniciar(self):
        """Restaura escena y variables iniciales; no conserva nada de la partida anterior."""
        self._escena_id = self._historia.inicio
        self._variables = dict(self._historia.variables)

    @property
    def escena(self):
        return self._historia.escenas[self._escena_id]

    @property
    def variables(self):
        return dict(self._variables)  # copia: el exterior no puede mutar el estado

    @property
    def es_final(self):
        return self.escena.final

    def _habilitada(self, opcion):
        # Todas las condiciones deben cumplirse; mapa vacío => habilitada.
        return all(self._variables[k] == v for k, v in opcion.condiciones.items())

    def opciones_disponibles(self):
        return [o for o in self.escena.opciones if self._habilitada(o)]

    @property
    def bloqueada(self):
        """Escena no final sin ninguna opción habilitada."""
        return (not self.es_final) and not self.opciones_disponibles()

    def elegir(self, opcion_id):
        """Aplica una opción habilitada. Si no existe o no está habilitada, no cambia nada."""
        for o in self.opciones_disponibles():
            if o.id == opcion_id:
                self._variables.update(o.efectos)
                self._escena_id = o.destino
                return self.escena
        raise ErrorDeEleccion(f"La opción '{opcion_id}' no existe o no está disponible en la escena '{self._escena_id}'.")
