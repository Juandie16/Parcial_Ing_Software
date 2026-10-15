"""Genera docs/Anexo.pdf: diagramas A1-A6, matriz de trazabilidad B y capturas del tablero C."""
import os
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

d = os.path.dirname(os.path.abspath(__file__))
ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=14)
CAP = ParagraphStyle("cap", parent=ss["Normal"], fontSize=9, textColor=colors.HexColor("#334155"))
CEL = ParagraphStyle("cel", parent=ss["Normal"], fontSize=7.5, leading=9)
CELB = ParagraphStyle("celb", parent=CEL, fontName="Helvetica-Bold")

FIGURAS = [
    ("A1", "01_contexto", "Diagrama de contexto: actores y archivos de historia alrededor del motor."),
    ("A2", "02_casos_de_uso", "Casos de uso del motor de historias (incluye deshacer, RF20)."),
    ("A3", "03_clases", "Clases del dominio y módulos principales (nombres idénticos al código)."),
    ("A4", "04_secuencia_elegir", "Secuencia de elegir una opción, con la rama de error."),
    ("A5", "05_estados_sesion", "Estados de una sesión de juego, con las transiciones de deshacer (RF20)."),
    ("A6", "06_componentes", "Componentes y capas: contenido, motor e interfaz."),
]


def figura(codigo, nombre, texto, ancho=17 * cm, alto=19 * cm):
    ruta = os.path.join(d, "diagramas", nombre + ".png")
    w, h = PILImage.open(ruta).size
    esc = min(ancho / w, alto / h)
    return KeepTogether([Image(ruta, w * esc, h * esc), Spacer(1, 4), Paragraph(f"<b>Figura {codigo}.</b> {texto}", CAP), Spacer(1, 14)])


MATRIZ = [
    ("RF01", "A2, A3", "motor/cargador.py", "test_integracion.py::test_i1_*; test_validacion.py::test_ca03_*"),
    ("RF02, RF12", "A5", "motor/sesion.py (reiniciar)", "test_motor.py::test_u5_*; test_consola.py::test_reinicio_desde_un_final"),
    ("RF03", "A6", "motor/ sin cambios; historias/el_faro.json", "test_integracion.py::test_segunda_historia_*; test_rnf.py::test_rnf01_*"),
    ("RF04, RF09", "A4", "consola.py (jugar)", "test_consola.py"),
    ("RF05, RF06", "A2, A3, A4", "motor/sesion.py (opciones_disponibles)", "test_motor.py::test_u1_*"),
    ("RF07, RF10", "A4, A5", "motor/sesion.py (elegir)", "test_motor.py::test_u2_*"),
    ("RF08", "A4, A5", "motor/sesion.py (elegir)", "test_motor.py::test_u3_*, test_ca02_*"),
    ("RF11", "A5", "motor/sesion.py (es_final)", "test_integracion.py::test_i1_*"),
    ("RF13–RF17", "A2, A3", "motor/validacion.py, motor/errores.py", "test_validacion.py::test_u4_*"),
    ("RF18", "A5", "motor/sesion.py (bloqueada)", "test_motor.py::test_escena_bloqueada_*"),
    ("RF19 (reemplazado)", "—", "Reemplazado por RF20 en la hora 6; vigente solo en v1-antes-del-cambio", "Informe, secciones 4 y 9"),
    ("RNF01", "A6", "motor/, historias/", "test_rnf.py::test_rnf01_*; salida de git diff --stat"),
    ("RNF02", "A3", "motor/validacion.py, motor/errores.py", "test_rnf.py::test_rnf02_*"),
    ("RNF03", "A5", "motor/sesion.py, motor/cargador.py", "test_rnf.py::test_rnf03_*"),
    ("RF20 Deshacer (cambio hora 6)", "A2, A3, A4, A5, A6", "motor/sesion.py (elegir, deshacer, puede_deshacer, reiniciar); consola.py (comando d)",
     "test_motor.py::test_u6_*, test_ca04_ejemplo_del_cliente, test_u5_reiniciar_elimina_historial_de_retroceso; "
     "test_integracion.py::test_i1_deshacer_desde_un_final_vuelve_a_e3; test_consola.py::test_deshacer_*, test_al_iniciar_no_se_ofrece_deshacer"),
]


def tabla_matriz():
    datos = [[Paragraph(t, CELB) for t in ("Requisito", "Modelo", "Componente o archivo", "Evidencia (tests/ ...)")]]
    datos += [[Paragraph(c, CEL) for c in fila] for fila in MATRIZ]
    t = Table(datos, colWidths=[2.4 * cm, 2.8 * cm, 5.4 * cm, 6.4 * cm], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


historia = [Paragraph("Anexo — La última transmisión", H1),
            Paragraph("Contenido: <b>A</b> diagramas (A1–A6), <b>B</b> matriz de trazabilidad, <b>C</b> capturas del tablero. "
                      "Integrantes: (nombre completo 1) y (nombre completo 2).", ss["Normal"]), Spacer(1, 10)]
for cod, nom, txt in FIGURAS[:2]:
    historia.append(figura(cod, nom, txt, alto=9 * cm))
historia.append(PageBreak())
historia.append(figura(*FIGURAS[2], alto=21 * cm)); historia.append(PageBreak())
historia.append(figura(*FIGURAS[3], alto=21 * cm)); historia.append(PageBreak())
for cod, nom, txt in FIGURAS[4:]:
    historia.append(figura(cod, nom, txt, alto=9 * cm))
historia += [PageBreak(), Paragraph("B. Matriz de trazabilidad", H1),
             Paragraph("Rutas relativas a la raíz del proyecto; las pruebas están en <b>tests/</b>.", ss["Normal"]), Spacer(1, 8), tabla_matriz(),
             PageBreak(), Paragraph("C. Capturas del tablero", H1),
             Paragraph("<b>C1. Tablero inicial</b> — (insertar captura con tareas y responsables)<br/><br/><br/><br/><br/><br/><br/><br/>"
                       "<b>C2. Tablero final</b> — (insertar captura con tareas y responsables)", ss["Normal"])]
SimpleDocTemplate(os.path.join(d, "Anexo.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="Anexo - La última transmisión").build(historia)
print("Anexo.pdf generado")
