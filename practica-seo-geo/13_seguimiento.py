"""Paso 13. Seguimiento: repite las mismas preguntas a los asistentes y compara con la captura de referencia."""
import subprocess, sys
from collections import Counter
from sop.comun import cargar_caso, expediente, explicar, escribir_csv, leer_csv, hoy

caso = cargar_caso()
exp = expediente(caso)
etiqueta = f"seguimiento-{hoy()}"
explicar("Paso 13 · Seguimiento",
         "Lanzamos otra vez el paso 4 con las mismas preguntas, superficie, país e idioma, y comparamos la presencia "
         "de la marca con la captura de referencia.",
         "Solo se puede comparar lo que se midió igual. Y una cita nueva después de publicar no prueba que la "
         "publicación la causara: las respuestas ya variaban entre ejecuciones antes de tocar nada.",
         "La diferencia entre referencia y seguimiento, leída junto a la variación que ya había dentro de la referencia.")

subprocess.run([sys.executable, "04_asistentes.py", etiqueta] + [a for a in sys.argv[1:] if a.startswith("--")], check=True)
antes, ahora_ = leer_csv(exp / "04-asistentes.csv"), leer_csv(exp / f"04-asistentes-{etiqueta}.csv")
filas = []
for pregunta in caso["asistentes"]["preguntas"]:
    a = Counter(f["marca_propia"] for f in antes if f["pregunta"] == pregunta)
    b = Counter(f["marca_propia"] for f in ahora_ if f["pregunta"] == pregunta)
    filas.append({"pregunta": pregunta, "fecha": hoy(),
                  "referencia_citada": f"{a['citada']}/{sum(a.values())}", "seguimiento_citada": f"{b['citada']}/{sum(b.values())}",
                  "referencia_mencionada": f"{a['mencionada']}/{sum(a.values())}",
                  "seguimiento_mencionada": f"{b['mencionada']}/{sum(b.values())}"})
escribir_csv(exp / "13-seguimiento.csv", filas, list(filas[0]))
for f in filas:
    print(f"  «{f['pregunta']}»\n     citada {f['referencia_citada']} -> {f['seguimiento_citada']} · "
          f"mencionada {f['referencia_mencionada']} -> {f['seguimiento_mencionada']}")
