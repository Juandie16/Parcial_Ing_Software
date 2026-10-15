"""Exporta las evidencias que pide la guía:
  docs/resultados_pruebas.txt  (ejecución real de pytest)
  docs/historial_git.txt       (autores, fechas y mensajes; requiere haber hecho commits)
Uso desde la raíz del proyecto:  python scripts/exportar_evidencias.py"""
import datetime
import subprocess
import sys

def ejecutar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

ahora = datetime.datetime.now().isoformat(timespec="seconds")
r = ejecutar([sys.executable, "-m", "pytest", "-v"])
with open("docs/resultados_pruebas.txt", "w", encoding="utf-8") as f:
    f.write(f"Ejecución: {ahora}\nComando: python -m pytest -v\nCódigo de salida: {r.returncode}\n\n{r.stdout}{r.stderr}")
print("Escrito docs/resultados_pruebas.txt (código de salida", r.returncode, ")")

g = ejecutar(["git", "log", "--date=iso", "--pretty=format:%h | %an | %ad | %s%d"])
with open("docs/historial_git.txt", "w", encoding="utf-8") as f:
    if g.returncode == 0 and g.stdout.strip():
        f.write(g.stdout + "\n")
        print("Escrito docs/historial_git.txt")
    else:
        f.write("Sin commits todavía. Hagan commits con su usuario de Git y vuelvan a ejecutar este script.\n")
        print("AVISO: no hay commits; docs/historial_git.txt quedó con una nota.")
