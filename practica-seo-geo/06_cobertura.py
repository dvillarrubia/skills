"""Paso 6. Matriz de cobertura por temas. El modelo propone y cita; Python verifica las citas y calcula los huecos."""
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, leer_csv, contiene
from sop.llm import pedir_json, SOLO_FUENTES

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c, p, lim = caso["caso"], caso["publico"], caso["limites"]
explicar("Paso 6 · Cobertura de temas",
         "El modelo lee el corpus y propone los temas que necesita el público, con una nota de 0 a 3 por página y el "
         "fragmento literal que la justifica. Después Python busca cada fragmento en la página.",
         "Un modelo puede atribuir a una página algo que no dice. Si el fragmento no aparece en el texto, la nota "
         "no cuenta: queda como «sin evidencia». El hueco tampoco lo decide el modelo, sino una regla con umbral.",
         "Cuántas notas caen por falta de evidencia, qué temas cubren bien los competidores y la página propia no, "
         "y qué temas no cubre nadie con prueba (ahí cabe la aportación original).")

paginas = [f for f in leer_csv(exp / "05-corpus" / "indice.csv") if f["fichero"]]
textos = {f["id"]: (exp / "05-corpus" / f["fichero"]).read_text(encoding="utf-8") for f in paginas}
propias = [f["id"] for f in paginas if f["origen"] == "propia"]
ajenas = [f["id"] for f in paginas if f["origen"] != "propia"]
material = "\n\n".join(f"=== {pid} ({next(f['dominio'] for f in paginas if f['id'] == pid)}) ===\n"
                       f"{t[:lim['caracteres_por_pagina']]}" for pid, t in textos.items())

datos = pedir_json(caso, exp, "06-cobertura",
    SOLO_FUENTES + "Devuelve solo JSON.",
    f"Público: {p['segmento']}. Problema: {p['problema']}. Consulta: {c['consulta_principal']}.\n\n"
    "Identifica entre 10 y 16 temas o relaciones (entidad–atributo, problema–causa, opción–limitación) que este público "
    "necesita para resolver su problema, a partir de lo que tratan las páginas. Para cada tema y cada página da una nota:\n"
    "0 = ausente; 1 = mencionado sin explicación; 2 = explicado y aplicable; 3 = explicado con prueba, ejemplo o criterio verificable.\n"
    "Toda nota de 1 a 3 lleva un fragmento LITERAL de esa página, copiado tal cual, de 8 a 30 palabras.\n\n"
    'Formato: {"temas": [{"tema": "...", "necesidad": "...", "paginas": {"P1": {"nota": 2, "fragmento": "..."}, "P2": {"nota": 0, "fragmento": ""}}}]}\n\n'
    f"PÁGINAS:\n{material}", max_tokens=8000, seco=op["seco"], fresco=op["fresco"])
if datos is None:
    raise SystemExit("\nModo --seco: prompt guardado en prompts/06-cobertura.md, sin llamar al modelo.")

filas, caidas = [], 0
for t in datos.get("temas", []):
    fila = {"tema": t.get("tema"), "necesidad": t.get("necesidad")}
    notas = {}
    for pid in textos:
        celda = (t.get("paginas") or {}).get(pid) or {}
        nota = celda.get("nota", 0) or 0
        if nota > 0 and not contiene(textos[pid], celda.get("fragmento", "")):
            fila[pid], caidas = "SE", caidas + 1                 # sin evidencia: el fragmento no está en la página
        else:
            fila[pid], notas[pid] = nota, nota
            fila[f"{pid}_fragmento"] = celda.get("fragmento", "")
    propia = max((notas.get(x, 0) for x in propias), default=0)
    evaluables = [notas[x] for x in ajenas if x in notas]
    bien = sum(1 for n in evaluables if n >= 2)
    fila["cubren_bien"] = f"{bien} de {len(evaluables)}"
    if propia < 2 and evaluables and bien / len(evaluables) >= lim["umbral_hueco"]:
        fila["decision"] = "hueco: lo cubren los competidores y la página propia no"
    elif not any(n >= 3 for n in evaluables) and propia < 3:
        fila["decision"] = "nadie lo prueba: candidato a aportación original"
    else:
        fila["decision"] = "cubierto"
    filas.append(fila)

campos = ["tema", "necesidad"] + list(textos) + ["cubren_bien", "decision"] + [f"{x}_fragmento" for x in textos]
escribir_csv(exp / "06-cobertura.csv", filas, campos)
print(f"\n  {len(filas)} temas · {caidas} notas anuladas porque el fragmento citado no está en la página\n")
for f in filas:
    print(f"  [{' '.join(str(f.get(x, '-')) for x in textos)}]  {f['decision'][:38].ljust(38)}  {f['tema']}")
print(f"\n  Columnas: {' '.join(textos)} · propias: {', '.join(propias)} · SE = sin evidencia")
print("  Para debatir: que cuatro competidores repitan un tema no prueba que Google ni un asistente lo exijan.")
