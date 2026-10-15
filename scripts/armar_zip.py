"""Arma el ZIP de entrega sin .venv, .git, cachés ni archivos temporales de la demostración.
Uso (desde la raíz del proyecto):
    python scripts/armar_zip.py Parcial_ApellidoNombre_ApellidoNombre.zip
El ZIP se crea en la carpeta superior a la del proyecto."""
import os
import sys
import zipfile

if len(sys.argv) != 2 or not sys.argv[1].endswith(".zip"):
    sys.exit("Uso: python scripts/armar_zip.py Parcial_ApellidoNombre_ApellidoNombre.zip")

raiz = os.getcwd()
destino = os.path.abspath(os.path.join(raiz, "..", sys.argv[1]))
EXCLUIR_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".idea"}
EXCLUIR_ARCH = {"_demo_error.json", ".DS_Store"}

n = 0
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
    for carpeta, dirs, archivos in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in EXCLUIR_DIRS]
        for a in archivos:
            if a in EXCLUIR_ARCH or a.endswith((".pyc", ".zip")):
                continue
            ruta = os.path.join(carpeta, a)
            z.write(ruta, os.path.relpath(ruta, raiz).replace(os.sep, "/"))
            n += 1
print(f"{n} archivos en {destino}")
for nombre in ("README.md", "docs/Informe.pdf", "docs/Anexo.pdf", "docs/historial_git.txt", "docs/resultados_pruebas.txt"):
    if not os.path.exists(nombre):
        print("AVISO: falta", nombre)
if not any(f.lower().endswith(".mp4") for _, _, fs in os.walk("video") for f in fs) if os.path.isdir("video") else True:
    print("AVISO: no hay un .mp4 en la carpeta video/ (si lo enlazan desde el README, ignoren este aviso)")