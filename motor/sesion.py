"""Sesión de juego: estado de una partida sobre una Historia ya validada."""
from .errores import ErrorDeEleccion


class Sesion:
    def __init__(self, historia):
        self._historia = historia
        self.reiniciar()

    def reiniciar(self):
        """Restaura escena y variables iniciales y elimina el historial de retroceso (RF12, RF20)."""
        self._escena_id = self._historia.inicio
        self._variables = dict(self._historia.variables)
        self._anterior = None  # (escena_id, variables) previos a la última elección válida

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

    @property
    def puede_deshacer(self):
        """Hay una última elección válida que todavía no se ha deshecho (RF20)."""
        return self._anterior is not None

    def elegir(self, opcion_id):
        """Aplica una opción habilitada. Si no existe o no está habilitada, no cambia nada
        (tampoco el historial de retroceso)."""
        for o in self.opciones_disponibles():
            if o.id == opcion_id:
                self._anterior = (self._escena_id, dict(self._variables))
                self._variables.update(o.efectos)
                self._escena_id = o.destino
                return self.escena
        raise ErrorDeEleccion(f"La opción '{opcion_id}' no existe o no está disponible en la escena '{self._escena_id}'.")

    def deshacer(self):
        """Revierte la última elección válida: restaura la escena y todas las variables previas.
        Solo un nivel: después de deshacer no hay retroceso hasta una nueva elección válida.
        Devuelve True si deshizo algo y False si no había nada que deshacer (sin cambios)."""
        if self._anterior is None:
            return False
        self._escena_id, variables = self._anterior
        self._variables = dict(variables)
        self._anterior = None
        return True
