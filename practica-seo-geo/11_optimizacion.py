"""Paso 11. Optimización para Google y para asistentes de IA: la página actual frente al borrador, control a control."""
import re
from sop.comun import cargar_caso, expediente, explicar, leer_csv, escribir_csv
from sop.contexto import de_optimizacion
from sop.optimizacion import controles, tecnico
from sop import paginas
from sop.paginas import descargar, analizar

caso = cargar_caso()
paginas.configurar(caso)
exp = expediente(caso)
c = caso["caso"]
explicar("Paso 11 · Optimización para Google y para asistentes de IA",
         "Pasamos los mismos controles a la página que la marca tiene publicada hoy y al borrador. Tres bloques: Google "
         "(título, consultas del grupo, preguntas observadas, enlaces), asistentes de IA (respuesta primero, entidad "
         "nombrada, preguntas y búsquedas fan-out cubiertas, cifras con unidad, pasajes extraíbles) y técnico (qué "
         "encuentra un rastreador de IA sin ejecutar JavaScript y si robots.txt le deja entrar).",
         "«Optimizado para IA» no significa nada si no se puede comprobar. Cada control es una regla que cualquiera "
         "puede leer y discutir, alimentada con datos del propio expediente: las preguntas que hicimos a los asistentes "
         "y las búsquedas que ellos lanzaron. Ninguno garantiza una cita; todos son condiciones razonables para optar a ella.",
         "Dónde mejora el borrador a la página actual, dónde empeora, y la lista de dominios que los asistentes citan: "
         "ahí es donde la marca tendría que aparecer además de en su propia web.")

ctx = de_optimizacion(caso, exp)
url = ctx["url_propia_del_grupo"] or caso["propias"]["urls"][0]
print(f"  Página actual evaluada: {url}")
html, ficha = descargar(url)
columnas = {}
if html:
    datos, md = analizar(html, url)
    n_h1 = len([h for h in datos["h1"].split(" | ") if h])
    actual = controles(md, datos["titulo"], datos["descripcion"], n_h1, ctx)
    for f in actual:                      # el texto limpio no conserva los enlaces: no se puede juzgar aquí
        if "enlaces internos" in f["control"]:
            f.update(resultado="n/e", valor="no evaluable en el texto limpio")
    columnas["página actual"] = actual + tecnico(url, ficha, datos, html)
else:
    print(f"  Página actual no evaluable: {ficha['incidencia']}")
borrador = exp / "10-borrador.md"
if borrador.exists():
    t = borrador.read_text(encoding="utf-8")
    titulo = (re.search(r"^TITULO:\s*(.+)$", t, flags=re.M) or [None, ""])[1].strip()
    descripcion = (re.search(r"^DESCRIPCION:\s*(.+)$", t, flags=re.M) or [None, ""])[1].strip()
    cuerpo = re.sub(r"^(TITULO|DESCRIPCION):.*$", "", t, flags=re.M).strip()
    columnas["borrador"] = controles(cuerpo, titulo, descripcion, len(re.findall(r"^# ", cuerpo, flags=re.M)), ctx)
else:
    print("  Todavía no hay borrador: se audita solo la página actual. Vuelve a ejecutar este paso después del 10.")
if not columnas:
    raise SystemExit("Nada que evaluar.")

base = next(iter(columnas.values()))
filas = []
for i, f in enumerate(base):
    fila = {"bloque": f["bloque"], "control": f["control"]}
    for nombre, lista in columnas.items():
        if i < len(lista):
            fila[nombre] = f"{lista[i]['resultado']} ({lista[i]['valor']})"
            fila[f"detalle {nombre}"] = lista[i]["detalle"]
    filas.append(fila)
campos = ["bloque", "control"] + list(columnas) + [f"detalle {n}" for n in columnas]
escribir_csv(exp / "11-optimizacion.csv", filas, campos)

fuentes = exp / "04-fuentes.csv"
citados = {}
if fuentes.exists():
    for f in leer_csv(fuentes):
        if f["es_propia"] == "no":
            citados[f["dominio"]] = citados.get(f["dominio"], 0) + int(f["ejecuciones"])
(exp / "11-optimizacion.md").write_text(
    f"# Optimización para Google y asistentes de IA · {c['id']}\n\nPágina actual: {url}\n\n"
    "| Bloque | Control | " + " | ".join(columnas) + " |\n| --- | --- | " + " | ".join("---" for _ in columnas) + " |\n"
    + "\n".join(f"| {f['bloque']} | {f['control']} | " + " | ".join(f.get(n, "—") for n in columnas) + " |" for f in filas)
    + "\n\n## Dónde citan los asistentes\n\nDominios ajenos que los asistentes enlazaron al responder las preguntas del caso, "
      "por número de ejecuciones. Son los sitios donde conviene que la marca aparezca mencionada.\n\n"
    + ("\n".join(f"- {d}: {n}" for d, n in sorted(citados.items(), key=lambda x: -x[1])[:12]) or "Sin datos: ejecuta antes el paso 4.")
    + "\n\nNingún control garantiza posiciones ni citas. Son condiciones comprobables, no causas demostradas.\n", encoding="utf-8")
print()
for f in filas:
    print(f"  {f['bloque'][:7].ljust(7)} " + " ".join(str(f.get(n, '—'))[:16].ljust(16) for n in columnas) + f" {f['control'][:78]}")
print(f"\n  Columnas: {' | '.join(columnas)}")
for nombre, lista in columnas.items():
    print(f"  {nombre}: {sum(x['resultado'] == 'sí' for x in lista)} de {len(lista)} controles superados")
print("  Para debatir: ¿qué control quitaríais o añadiríais, y con qué evidencia?")
