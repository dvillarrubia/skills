"""Paso 1. ICP, pains y journey (IPJ) con lenguaje real del público: foros, preguntas de Google y autocompletado."""
import pathlib
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, hoy, dominio, contiene
from sop.serp import Buscador
from sop.llm import pedir_json, SOLO_FUENTES
from sop import paginas
from sop.paginas import descargar, analizar

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c, p, m, icp, a = caso["caso"], caso["publico"], caso["mercado"], caso["icp"], caso["asistentes"]
explicar("Paso 1 · ICP, pains y journey",
         "Buscamos dónde habla el público con sus palabras: hilos de foros (una búsqueda con «site:»), preguntas "
         "que Google muestra y sugerencias de autocompletado. Si hay entrevistas, reseñas o tickets, se dejan como "
         ".txt en fuentes-cliente/ y entran igual. El modelo propone segmentos y problemas, cada uno con citas literales.",
         "Un perfil de cliente escrito de memoria es una opinión. Aquí cada problema necesita citas que Python "
         f"encuentra en la fuente, y solo se da por confirmado con {icp['umbral_fuentes_confirmado']} fuentes "
         "independientes o más. El resto queda como hipótesis o se descarta.",
         "Qué problemas pasan a «confirmado», con qué palabras los describe la gente y en qué etapa del recorrido "
         "aparecen. Compáralo con la hipótesis de partida de caso.toml.")

paginas.configurar(caso)
google = Buscador(caso, exp, op["seco"], op["fresco"])
fuentes = []


def anadir(tipo, url, texto, origen):
    if texto and len(texto.split()) >= 5:
        fuentes.append({"id": f"F{len(fuentes) + 1}", "tipo": tipo, "dominio": dominio(url) or tipo, "url": url,
                        "texto": texto, "origen_texto": origen, "palabras": len(texto.split()), "fecha": hoy()})


# 1) Hilos de foros: una búsqueda con «site:» localiza los hilos; después intentamos leer cada uno.
k, relacionadas = 0, []
for busqueda in icp["busquedas_dolor"]:
    for foro in icp["foros"]:
        r = google.resultados(f"site:{foro} {busqueda}", f"01-foro-{k}", profundidad=10)
        k += 1
        for item in ((r or {}).get("organicos") or [])[:icp["hilos_por_busqueda"]]:
            html, _ = descargar(item["url"])
            if html:
                anadir("hilo de foro", item["url"], analizar(html, item["url"])[1][:6000], "página del hilo")
            else:  # si el foro no permite la descarga, nos quedamos con lo que Google muestra
                anadir("hilo de foro", item["url"], f"{item.get('titulo') or ''}. {item.get('descripcion') or ''}",
                       "titular y fragmento de Google")

# 2) Preguntas y búsquedas relacionadas que Google muestra para la consulta principal.
r = google.resultados(c["consulta_principal"], "01-preguntas", profundidad=10, preguntas_extra=True)
preguntas = (r or {}).get("preguntas") or []
relacionadas = (r or {}).get("relacionadas") or []
anadir("preguntas de Google", "https://www.google.es/", "\n".join(preguntas), "preguntas relacionadas observadas")

# 3) Autocompletado: cómo termina la gente la frase.
sugerencias = []
for i, semilla in enumerate([c["consulta_principal"]] + icp["busquedas_dolor"]):
    sugerencias += google.autocompletar(semilla, f"01-autocompletar-{i}")
sugerencias = list(dict.fromkeys(sugerencias))
anadir("autocompletado de Google", "https://www.google.es/complete", "\n".join(sugerencias), "sugerencias observadas")

# 4) Material del negocio, si existe: entrevistas, reseñas, soporte. Un .txt por fuente, ya anonimizado.
for f in sorted((exp / "fuentes-cliente").glob("*.txt")) if (exp / "fuentes-cliente").exists() else []:
    anadir("material del negocio", f"fichero:{f.name}", f.read_text(encoding="utf-8")[:8000], "fichero propio")

if op["seco"]:
    raise SystemExit("\nModo --seco: no se ha enviado nada.")
(exp / "fuentes-cliente").mkdir(exist_ok=True)
escribir_csv(exp / "01-voz-cliente.csv", fuentes, ["id", "tipo", "dominio", "url", "origen_texto", "palabras", "fecha"])
escribir_csv(exp / "01-demanda-observada.csv",
             [{"tipo": "pregunta de Google", "texto": x} for x in preguntas if x]
             + [{"tipo": "autocompletado", "texto": x} for x in sugerencias]
             + [{"tipo": "búsqueda relacionada", "texto": x} for x in relacionadas], ["tipo", "texto"])
print(f"\n  {len(fuentes)} fuentes · {sum(f['origen_texto'] == 'página del hilo' for f in fuentes)} hilos leídos completos · "
      f"{len(preguntas)} preguntas · {len(sugerencias)} sugerencias")
if len(fuentes) < 3:
    raise SystemExit("  Menos de tres fuentes: amplía foros o búsquedas en caso.toml, o añade material a fuentes-cliente/.")

datos = pedir_json(caso, exp, "01-icp-pains", SOLO_FUENTES + "Devuelve solo JSON.",
    f"Negocio: {c['marca']} ({c['dominio']}). Objetivo: {p['objetivo_negocio']}.\n"
    f"Hipótesis de partida, que puedes confirmar, matizar o contradecir: {p['segmento']}. {p['problema']}.\n\n"
    "Con las fuentes siguientes, identifica de 2 a 4 segmentos de cliente y de 6 a 12 problemas. Para cada problema: "
    "situación desencadenante, problema, consecuencia, objeción o freno, resultado deseado y etapa del recorrido "
    "(descubrimiento, consideración, decisión o uso). Cada problema lleva de 1 a 4 citas LITERALES, copiadas tal cual "
    "de una fuente, de 5 a 30 palabras, con el id de la fuente. Conserva las palabras de la gente, con sus faltas.\n\n"
    'Formato: {"segmentos": [{"id": "S1", "nombre": "...", "descripcion": "...", "como_se_reconoce": "..."}], '
    '"pains": [{"id": "D1", "segmento": "S1", "situacion": "...", "problema": "...", "consecuencia": "...", '
    '"objecion": "...", "resultado_deseado": "...", "etapa": "...", "citas": [{"fuente": "F3", "cita": "..."}]}]}\n\n'
    + "\n\n".join(f"=== {f['id']} · {f['tipo']} · {f['dominio']} ===\n{f['texto']}" for f in fuentes),
    max_tokens=6000, fresco=op["fresco"])

por_id = {f["id"]: f for f in fuentes}
filas = []
for d in datos.get("pains", []):
    buenas = [x for x in d.get("citas") or [] if x.get("fuente") in por_id and contiene(por_id[x["fuente"]]["texto"], x.get("cita", ""))]
    independientes = {x["fuente"] for x in buenas}
    estado = ("confirmado" if len(independientes) >= icp["umbral_fuentes_confirmado"]
              else "hipótesis" if independientes else "descartado: ninguna cita encontrada en las fuentes")
    filas.append({**{k: d.get(k) for k in ("id", "segmento", "etapa", "situacion", "problema", "consecuencia", "objecion",
                                           "resultado_deseado")},
                  "fuentes_independientes": len(independientes), "estado": estado,
                  "citas": " ¦ ".join(f"«{x['cita']}» ({x['fuente']})" for x in buenas),
                  "citas_rechazadas": len(d.get("citas") or []) - len(buenas)})
filas.sort(key=lambda f: -f["fuentes_independientes"])
escribir_csv(exp / "01-pains.csv", filas, ["id", "segmento", "etapa", "estado", "fuentes_independientes", "problema",
                                           "situacion", "consecuencia", "objecion", "resultado_deseado", "citas",
                                           "citas_rechazadas"])

(exp / "01-cliente.md").write_text(
    f"# ICP, pains y journey · {c['id']}\n\n{hoy()} · {len(fuentes)} fuentes analizadas\n\n## Segmentos\n\n"
    "| Id | Segmento | Descripción | Cómo se reconoce |\n| --- | --- | --- | --- |\n"
    + "\n".join(f"| {s.get('id')} | {s.get('nombre')} | {s.get('descripcion')} | {s.get('como_se_reconoce')} |" for s in datos.get("segmentos", []))
    + "\n\n## Problemas por etapa\n\n| Id | Etapa | Estado | Fuentes | Problema | Resultado deseado | En sus palabras |\n| --- | --- | --- | --- | --- | --- | --- |\n"
    + "\n".join(f"| {f['id']} | {f['etapa']} | {f['estado']} | {f['fuentes_independientes']} | {f['problema']} | "
                f"{f['resultado_deseado']} | {f['citas']} |" for f in filas)
    + f"\n\n## Hipótesis de partida\n\n{p['segmento']}. {p['problema']}.\n\nSin entrevistas ni datos del negocio, "
      "«confirmado» significa que varias fuentes públicas describen el problema, no que sea el del cliente de esta marca.\n",
    encoding="utf-8")

(exp / "00-encargo.md").write_text(f"""# Encargo · {c['id']}

Versión 1 · {hoy()}

| Campo | Contenido |
| --- | --- |
| Marca y dominio | {c['marca']} · {c['dominio']} |
| Objetivo de negocio | {p['objetivo_negocio']} |
| Consulta principal de partida | {c['consulta_principal']} |
| Preguntas a asistentes | {' / '.join(a['preguntas'])} |
| Mercado | localización {m['location_code']}, idioma {m['language_code']}, {m['dispositivo']} |
| URLs propias relacionadas | {'; '.join(caso['propias']['urls'])} |
| Conversión | {p['conversion']} |
| Search Console, analítica y experto del negocio | no disponible |
""", encoding="utf-8")
ap = exp / "aportacion.md"
if not ap.exists():
    ap.write_text("# Aportación original\n\n[PENDIENTE: describe aquí la aportación propia y verificable de la pieza. "
                  "La escribe una persona, no el modelo.]\n\nIndica qué se hizo, cuándo, con qué material y qué límites tiene.\n",
                  encoding="utf-8")
print()
for f in filas:
    print(f"  {f['id']:>3} {str(f['etapa'])[:14].ljust(14)} {f['estado'][:11].ljust(11)} {f['fuentes_independientes']} fuentes  {str(f['problema'])[:70]}")
print(f"\n  {sum(f['citas_rechazadas'] for f in filas)} citas rechazadas porque no aparecen literalmente en su fuente")
print("  Para debatir: ¿la hipótesis de caso.toml sale confirmada, matizada o desmentida? ¿Qué fuente falta?")
