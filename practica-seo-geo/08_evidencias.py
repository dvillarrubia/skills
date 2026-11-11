"""Paso 8. Registro de afirmaciones: qué dice hoy la marca que habría que poder demostrar antes de repetirlo."""
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, leer_csv, contiene, hoy
from sop.llm import pedir_json, SOLO_FUENTES

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
explicar("Paso 8 · Evidencias",
         "El modelo localiza en las páginas propias las afirmaciones comprobables (cifras, hechos, recomendaciones) "
         "con su fragmento literal. Todas entran como «pendiente». Una persona las verifica y cambia el estado.",
         "El borrador solo podrá usar afirmaciones en estado «verificada». Que una frase ya esté publicada, o que la "
         "repitan varios competidores o un asistente, no la convierte en un hecho.",
         "Las cifras: gramos, temperaturas, puntuaciones, años. Son las que un lector o un asistente copiará.")

destino = exp / "08-evidencias.csv"
if destino.exists() and not op["fresco"]:
    filas = leer_csv(destino)
    print(f"  Ya existe 08-evidencias.csv y no se sobrescribe (puede tener verificaciones hechas a mano).")
else:
    paginas = [f for f in leer_csv(exp / "05-corpus" / "indice.csv") if f["origen"] == "propia" and f["fichero"]]
    textos = {f["id"]: (exp / "05-corpus" / f["fichero"]).read_text(encoding="utf-8") for f in paginas}
    datos = pedir_json(caso, exp, "08-evidencias", SOLO_FUENTES + "Devuelve solo JSON.",
        "Extrae de estas páginas las afirmaciones que un lector podría comprobar: cifras, hechos sobre el producto o la "
        "empresa y recomendaciones técnicas concretas. Máximo 25. Cada una con el fragmento LITERAL que la contiene.\n"
        'Formato: [{"pagina": "P1", "afirmacion": "...", "fragmento": "...", "tipo": "cifra|hecho|recomendación"}]\n\n'
        + "\n\n".join(f"=== {pid} ===\n{t[:caso['limites']['caracteres_por_pagina']]}" for pid, t in textos.items()),
        max_tokens=4000, seco=op["seco"], fresco=op["fresco"])
    if datos is None:
        raise SystemExit("\nModo --seco: prompt guardado, sin llamar al modelo.")
    filas = [{"id": f"A{i + 1}", "afirmacion": d.get("afirmacion"), "tipo": d.get("tipo"), "pagina": d.get("pagina"),
              "fragmento": d.get("fragmento"), "fecha": hoy(), "fuente_primaria": "", "limites": "", "estado": "pendiente",
              "revisor": ""}
             for i, d in enumerate(d for d in datos if contiene(textos.get(d.get("pagina"), ""), d.get("fragmento", "")))]
    print(f"  {len(datos) - len(filas)} afirmaciones descartadas porque su fragmento no está en la página")
    escribir_csv(destino, filas, ["id", "afirmacion", "tipo", "pagina", "fragmento", "fecha", "fuente_primaria", "limites",
                                  "estado", "revisor"])
verificadas = sum(1 for f in filas if f["estado"].strip().lower() == "verificada")
print(f"\n  {len(filas)} afirmaciones · {verificadas} verificadas · {len(filas) - verificadas} pendientes o retiradas\n")
for f in filas[:12]:
    print(f"  {f['id']:>4} [{f['estado']}] {f['afirmacion'][:95]}")
print("\n  Tarea manual: abrir 08-evidencias.csv, buscar la fuente primaria de tres afirmaciones y cambiar su estado a "
      "«verificada» o «retirada». Después, escribir aportacion.md.")
