# La última transmisión — motor de historias interactivas

**Integrantes:** Juan Diego Rosales (T00081640) y Daniel Alejandro Castro (T00080238)

## Requisitos
- Python 3.9 o superior
- pytest (solo para las pruebas): `pip install -r requirements.txt`
- El motor solo usa la biblioteca estándar de Python.

## Ejecución
```
python consola.py                                   # historia de referencia
python consola.py historias/el_faro.json            # segunda historia, mismo motor
python consola.py historias/otra.json               # cualquier historia válida
```
Se elige una opción escribiendo su número. Escribiendo `d` se deshace la última decisión (solo un nivel; la opción aparece cuando hay algo que deshacer). Al llegar a un final se puede jugar de nuevo o deshacer.

## Pruebas
```
python -m pytest -v
```

## Formato de contenido (JSON)
| Elemento | Campos |
|---|---|
| Historia | `titulo`, `inicio` (id de escena), `variables` (mapa nombre → booleano inicial), `escenas` (lista) |
| Escena | `id` (único), `texto`, `final` (booleano), `opciones` (lista; vacía si es final) |
| Opción | `id` (único en la escena), `texto`, `destino` (id existente), `condiciones` (mapa variable → booleano), `efectos` (mapa variable → booleano) |

- Una opción se muestra solo si **todas** sus condiciones se cumplen. `condiciones` vacío o ausente = siempre disponible.
- `efectos` asigna verdadero/falso al elegir. Vacío o ausente = no cambia nada.
- Esta es la equivalencia exacta del contrato de la guía; `condiciones` y `efectos` son opcionales.

## Rutas para demostrar cada final (historia de referencia)
| Final | Opciones a elegir |
|---|---|
| E4 Rescate | Revisar señal → Investigar archivo → Activar con código |
| E5 El eco | Revisar señal → Continuar sin investigar → Activar sin verificar |
| E6 Silencio | Revisar señal → (cualquiera) → Cortar comunicación |

## Versiones (Git)
- `v1-antes-del-cambio` — versión disponible al recibir la solicitud de la hora 6.
- `v2-con-cambio` — con RF20 (deshacer la última decisión).

## Estructura
- `motor/modelo.py` — datos (Historia, Escena, Opción)
- `motor/validacion.py` — reglas de validación del contenido
- `motor/cargador.py` — lectura de JSON y construcción del modelo
- `motor/sesion.py` — estado de la partida, reglas de juego y deshacer
- `consola.py` — interfaz de consola (sin reglas de negocio)
- `historias/` — contenido; `tests/` — pruebas automatizadas

## Limitaciones conocidas
- Retroceso de un solo nivel (RF20, solicitud del cliente en la hora 6); no hay rehacer ni guardado entre ejecuciones.
- No se analizan automáticamente todos los caminos posibles; un bloqueo en juego se informa y permite reiniciar.

## Trabajar en Visual Studio Code
1. Instala Python 3.9+ y VS Code con la extensión **Python** (Microsoft). Abre la carpeta del proyecto (`Archivo > Abrir carpeta`).
2. Terminal integrada (`Ctrl+ñ` o `Ctrl+\``): `python -m venv .venv`, activa el entorno
   (Windows: `.venv\Scripts\activate`; macOS/Linux: `source .venv/bin/activate`) y ejecuta `pip install -r requirements.txt`.
3. Elige el intérprete: `Ctrl+Shift+P` > *Python: Select Interpreter* > el de `.venv`.
4. Jugar o depurar: panel *Ejecutar y depurar* (`Ctrl+Shift+D`) > «Jugar: La última transmisión» o «Jugar: El faro» > F5.
5. Pruebas: icono del matraz (*Testing*) o `python -m pytest -v` en la terminal.

## Enlace a video explicativo

https://tecnoutb-my.sharepoint.com/:v:/g/personal/daniecastro_utb_edu_co/IQCg-_s4ZYhHS56Nu0n_FUYQAagLUJh3OBm2v5KD1uDpF64?e=wm7IOB&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D

## Documentación y evidencias (`docs/`)
- `informe.md` → `Informe.pdf` (`python docs/build_informe.py`; requiere pandoc, python-docx y LibreOffice) y `Anexo.pdf` (`python docs/build_anexo.py`, requiere reportlab y pillow).
- `diagramas/` se regenera con `python docs/generar_diagramas.py` (requiere Graphviz y matplotlib).
- `backlog.md`: tareas para el tablero. `resultados_pruebas.txt` e `historial_git.txt`: `python scripts/exportar_evidencias.py`.
