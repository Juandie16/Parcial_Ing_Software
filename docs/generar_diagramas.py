"""Genera los diagramas del anexo (PNG) con Graphviz y matplotlib.
Uso: python docs/generar_diagramas.py   (requiere Graphviz instalado: comando `dot`)"""
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagramas")
BASE = 'graph [fontname="DejaVu Sans" dpi=130 pad=0.2]; node [fontname="DejaVu Sans" fontsize=11]; edge [fontname="DejaVu Sans" fontsize=10];'


def dot(nombre, cuerpo):
    fuente = f"digraph G {{ {BASE} {cuerpo} }}"
    subprocess.run(["dot", "-Tpng", "-o", os.path.join(SALIDA, nombre + ".png")],
                   input=fuente.encode("utf-8"), check=True)


# 1. Contexto
dot("01_contexto", '''
rankdir=LR;
esc [label="Escritora\\n(edita el JSON)" shape=box style=rounded];
lec [label="Lector\\n(juega en consola)" shape=box style=rounded];
coo [label="Coordinadora del festival\\n(corrige contenido)" shape=box style=rounded];
sis [label="Motor de historias\\ninteractivas" shape=box style="filled,bold" fillcolor="#dbeafe" width=2.2 height=1.2];
arc [label="Archivos de historia\\n(*.json)" shape=cylinder style=filled fillcolor="#fef9c3"];
esc -> arc [label="escribe"];
arc -> sis [label="lee"];
lec -> sis [label="elige opciones"];
sis -> lec [label="escena y opciones\\nhabilitadas"];
sis -> coo [label="errores de contenido\\n(causa + campo/ID)"];
coo -> esc [label="pide corrección" style=dashed];
''')

# 2. Casos de uso
dot("02_casos_de_uso", '''
rankdir=LR; compound=true;
lec [label="Lector" shape=box style=rounded];
esc [label="Escritora" shape=box style=rounded];
coo [label="Coordinadora" shape=box style=rounded];
subgraph cluster_s { label="Motor de historias"; style=dashed; fontname="DejaVu Sans";
  cargar [label="Cargar historia" shape=ellipse];
  validar [label="Validar contenido" shape=ellipse];
  leer [label="Leer escena y\\nopciones habilitadas" shape=ellipse];
  elegir [label="Elegir opción" shape=ellipse];
  cond [label="Evaluar condiciones" shape=ellipse];
  reiniciar [label="Reiniciar partida" shape=ellipse];
  deshacer [label="Deshacer última\\ndecisión (RF20)" shape=ellipse style=filled fillcolor="#fef3c7"];
  errores [label="Ver errores\\nde contenido" shape=ellipse];
}
lec -> cargar; lec -> leer; lec -> elegir; lec -> reiniciar; lec -> deshacer;
esc -> cargar [label="prueba su historia"]; esc -> errores; coo -> errores;
cargar -> validar [label="«include»" style=dashed];
leer -> cond [label="«include»" style=dashed];
elegir -> cond [label="«include»" style=dashed];
errores -> validar [label="«extend»" style=dashed];
''')

# 3. Clases del dominio
dot("03_clases", '''
rankdir=TB; node [shape=record fontsize=10];
Historia [label="{Historia|titulo : str\\linicio : str\\lvariables : dict[str,bool]\\lescenas : dict[str,Escena]\\l}"];
Escena [label="{Escena|id : str\\ltexto : str\\lfinal : bool\\lopciones : tuple[Opcion]\\l}"];
Opcion [label="{Opcion|id : str\\ltexto : str\\ldestino : str\\lcondiciones : dict[str,bool]\\lefectos : dict[str,bool]\\l}"];
Sesion [label="{Sesion|- _historia : Historia\\l- _escena_id : str\\l- _variables : dict[str,bool]\\l- _anterior : (str, dict) \\| None\\l|+ escena : Escena\\l+ variables : dict\\l+ es_final : bool\\l+ bloqueada : bool\\l+ puede_deshacer : bool\\l+ opciones_disponibles() : list[Opcion]\\l+ elegir(opcion_id) : Escena\\l+ reiniciar()\\l+ deshacer() : bool\\l}"];
Cargador [label="{«módulo» cargador|+ cargar_historia(ruta) : Historia\\l+ construir(datos) : Historia\\l}"];
Validacion [label="{«módulo» validacion|+ validar(datos) : list[str]\\l}"];
HI [label="{HistoriaInvalida|errores : list[str]\\l}"];
EE [label="{ErrorDeEleccion|}"];
Consola [label="{«módulo» consola|+ jugar(historia)\\l+ main(argv)\\l}"];
Historia -> Escena [arrowtail=diamond dir=both arrowhead=none headlabel="1..*" taillabel="1" labeldistance=2];
Escena -> Opcion [arrowtail=diamond dir=both arrowhead=none headlabel="0..*" taillabel="1" labeldistance=2];
Sesion -> Historia [arrowhead=vee label="usa" headlabel="1"];
Sesion -> EE [style=dashed arrowhead=vee label="lanza"];
Cargador -> Historia [style=dashed arrowhead=vee label="crea"];
Cargador -> Validacion [style=dashed arrowhead=vee label="llama"];
Cargador -> HI [style=dashed arrowhead=vee label="lanza"];
Consola -> Sesion [arrowhead=vee label="usa"];
Consola -> Cargador [style=dashed arrowhead=vee label="llama"];
''')

# 5. Estados de la sesión
dot("05_estados_sesion", '''
rankdir=LR; nodesep=0.8; ranksep=1.3;
ini [shape=point width=0.2];
EnCurso [shape=box style="rounded,filled" fillcolor="#dcfce7" label="EnCurso\\n(escena no final con\\nopciones habilitadas)"];
Finalizada [shape=box style="rounded,filled" fillcolor="#dbeafe" label="Finalizada\\n(escena final)"];
Bloqueada [shape=box style="rounded,filled" fillcolor="#fee2e2" label="Bloqueada\\n(no final, sin opciones\\nhabilitadas)"];
ini -> EnCurso [label="abrir sesión\\n/ escena=inicio,\\nvariables iniciales"];
EnCurso -> EnCurso [label="elegir(opción habilitada)\\n[destino no final y con opciones]\\n/ aplicar efectos" tailport=n headport=n];
EnCurso -> EnCurso [label="elegir(opción inválida)\\n/ ErrorDeEleccion, sin cambios" style=dashed tailport=s headport=s];
EnCurso -> Finalizada [label="elegir(opción habilitada)\\n[destino final] / aplicar efectos"];
EnCurso -> Bloqueada [label="elegir(opción habilitada)\\n[destino sin opciones habilitadas]"];
Finalizada -> EnCurso [label="reiniciar()"];
Bloqueada -> EnCurso [label="reiniciar()"];
Finalizada -> EnCurso [label="deshacer() [hay retroceso]\\n/ restaurar escena y variables\\nprevias; consumir retroceso" color="#b45309" fontcolor="#b45309"];
Bloqueada -> EnCurso [label="deshacer() [hay retroceso]" color="#b45309" fontcolor="#b45309"];
EnCurso -> EnCurso [label="deshacer() [hay retroceso] / restaurar estado previo\\ndeshacer() [sin retroceso] / sin cambios" color="#b45309" fontcolor="#b45309" tailport=e headport=e];
''')

# 6. Componentes / capas
dot("06_componentes", '''
rankdir=TB; node [shape=box style="rounded,filled" fillcolor="#f8fafc"];
subgraph cluster_c { label="Contenido (datos)"; style=dashed; fontname="DejaVu Sans";
  json [label="historias/*.json\\nHistorias y reglas\\n(editable sin programar)" shape=cylinder fillcolor="#fef9c3"]; }
subgraph cluster_i { label="Interfaz"; style=dashed; fontname="DejaVu Sans";
  consola [label="consola.py\\nMuestra escenas y opciones,\\npide la elección, informa errores"]; }
subgraph cluster_m { label="Motor (reglas, sin interfaz ni contenido)"; style=dashed; fontname="DejaVu Sans";
  sesion [label="sesion.py\\nEstado de la partida, condiciones,\\nefectos, finales, reinicio,\\ndeshacer (historial de un nivel)"];
  cargador [label="cargador.py\\nLee JSON y construye el modelo"];
  validacion [label="validacion.py\\nReglas de validación del contenido"];
  modelo [label="modelo.py\\nHistoria, Escena, Opcion (datos)"];
  errores [label="errores.py\\nHistoriaInvalida, ErrorDeEleccion"]; }
consola -> sesion [label="usa"]; consola -> cargador [label="usa"];
cargador -> json [label="lee" style=dashed];
cargador -> validacion; cargador -> modelo; cargador -> errores;
sesion -> modelo; sesion -> errores;
''')


# 4. Secuencia: elegir una opción (dibujo manual, con bloque alternativo)
def secuencia():
    partes = ["Lector", "Consola", "Sesion", "Historia"]
    x = {p: i * 3.2 for i, p in enumerate(partes)}
    # (origen, destino, texto, retorno, marca_alt)
    msgs = [
        ("Lector", "Consola", "1: escribe número de opción", False, None),
        ("Consola", "Sesion", "2: opciones_disponibles()", False, None),
        ("Sesion", "Consola", "3: opciones habilitadas", True, None),
        ("Consola", "Sesion", "4: elegir(opcion_id)", False, None),
        ("Sesion", "Sesion", "5: buscar opción entre las habilitadas", False, None),
        ("Sesion", "Sesion", "6: guardar escena y variables previas (retroceso)", False, "alt1"),
        ("Sesion", "Sesion", "6b: aplicar efectos a las variables", False, "alt1"),
        ("Sesion", "Historia", "7: escenas[destino]", False, "alt1"),
        ("Historia", "Sesion", "8: escena destino", True, "alt1"),
        ("Sesion", "Consola", "9: escena nueva", True, "alt1"),
        ("Sesion", "Consola", "10: ErrorDeEleccion (estado e historial sin cambios)", True, "alt2"),
        ("Consola", "Lector", "11: muestra la escena o el aviso", True, None),
    ]
    fig, ax = plt.subplots(figsize=(10, 9.2), dpi=130)
    paso = 0.78
    for p in partes:
        ax.text(x[p], 0.4, p, ha="center", va="bottom", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round", fc="#dbeafe", ec="#334155"))
        ax.plot([x[p], x[p]], [0, -paso * (len(msgs) + 1) - 3.4], color="#64748b", lw=1, ls="--")
    ys = {}
    extra, previo = 0.0, None
    for i, (a, b, t, ret, alt) in enumerate(msgs):
        if alt != previo:
            extra += 0.75
            previo = alt
        y = -paso * (i + 1) - extra
        ys.setdefault(alt, []).append(y)
        if a == b:
            ax.annotate("", xy=(x[a] + 0.05, y - 0.3), xytext=(x[a] + 0.05, y),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-1.6", color="#0f172a"))
            ax.text(x[a] + 0.45, y - 0.15, t, fontsize=8.5, va="center")
        else:
            ax.annotate("", xy=(x[b], y), xytext=(x[a], y),
                        arrowprops=dict(arrowstyle="->", color="#0f172a", ls="--" if ret else "-"))
            ax.text((x[a] + x[b]) / 2, y + 0.08, t, fontsize=8.5, ha="center", va="bottom")
    # marcos alt
    x0, x1 = x["Lector"] + 1.2, x["Historia"] + 1.4
    for clave, etiqueta, color in (("alt1", "alt  [opción habilitada]", "#16a34a"),
                                   ("alt2", "[opción inexistente o no habilitada]", "#dc2626")):
        y_top, y_bot = max(ys[clave]) + (0.5 if len(ys[clave]) > 1 else 0.95), min(ys[clave]) - 0.45
        ax.add_patch(plt.Rectangle((x0, y_bot), x1 - x0, y_top - y_bot, fill=False, ec=color, lw=1.2))
        ax.text(x0 + 0.1, y_top - 0.08, etiqueta, fontsize=8.5, color=color, va="top", fontweight="bold")
    ax.set_xlim(-1.5, x["Historia"] + 2.2)
    ax.set_ylim(-paso * (len(msgs) + 1.3) - 3.4, 1.3)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "04_secuencia_elegir.png"))


secuencia()
print("Diagramas generados en", SALIDA)
