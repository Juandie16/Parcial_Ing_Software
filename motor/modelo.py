"""Modelo de dominio: Historia, Escena y Opcion (solo datos, sin lógica de juego)."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Opcion:
    id: str
    texto: str
    destino: str
    condiciones: dict = field(default_factory=dict)
    efectos: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Escena:
    id: str
    texto: str
    final: bool
    opciones: tuple = ()


@dataclass(frozen=True)
class Historia:
    titulo: str
    inicio: str
    variables: dict
    escenas: dict  # id de escena -> Escena
