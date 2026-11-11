"""Paso 3. Resultados reales de Google para las consultas candidatas. Agrupa por solape y propone una acción por grupo."""
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, leer_csv, hoy, dominio, tabla
from sop.serp import Buscador
from sop.llm import pedir_json, disponible

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c, m, lim = caso["caso"], caso["mercado"], caso["limites"]
explicar("Paso 3 · Google por intención",
         "Pedimos la página de resultados de Google España para la consulta principal, sus variantes y las candidatas "
         "mejor puntuadas del paso 2, con preguntas relacionadas y respuesta de IA si la hay. Agrupamos las consultas "
         "que comparten resultados y miramos qué URL propia aparece en cada grupo.",
         "Dos consultas van a la misma página si Google les da los mismos resultados, no si se parecen por escrito. "
         f"El criterio es el solape de su top 10 (umbral {lim['umbral_solape_serp']}). El formato de la pieza sale de lo que "
         "Google muestra, no de lo que nos apetece escribir.",
         "Los grupos que salen, qué tipos de página dominan, si hay respuesta de IA y a quién enlaza, y los grupos "
         "donde aparecen varias URLs propias.")

google = Buscador(caso, exp, op["seco"], op["fresco"])
tabla_consultas = leer_csv(exp / "02-consultas.csv")
candidatas = [f["consulta"] for f in tabla_consultas if f["candidata_serp"] == "sí"]
volumen = {f["consulta"]: f["volumen_estimado"] for f in tabla_consultas}
consultas = list(dict.fromkeys([c["consulta_principal"].lower()] + [v.lower() for v in c["variantes"]] + candidatas))
resultados, preguntas, ia, top = [], [], [], {}

for i, q in enumerate(consultas):
    r = google.resultados(q, f"03-serp-{i}", profundidad=lim["profundidad_serp"])
    if not r:
        continue
    top[q] = [x["url"] for x in r["organicos"] if (x["posicion"] or 99) <= lim["top_organico"]]
    resultados += [{"consulta": q, "posicion": x["posicion"], "url": x["url"], "dominio": dominio(x["url"]),
                    "titulo": x["titulo"], "descripcion": x["descripcion"], "fecha_captura": hoy()} for x in r["organicos"]]
    preguntas += [{"consulta": q, "pregunta": x, "fuente": "Google, observada", "fecha": hoy()} for x in r["preguntas"]]
    ia += [{"consulta": q, "url": u, "dominio": dominio(u), "es_propia": "sí" if c["dominio"] in u else "no"} for u in r["ia"]]

if op["seco"]:
    raise SystemExit("\nModo --seco: no se ha enviado nada.")

# Agrupación determinista: dos consultas se unen si el Jaccard de sus top 10 alcanza el umbral.
jaccard = lambda a, b: len(set(a) & set(b)) / len(set(a) | set(b)) if set(a) | set(b) else 0
padre = {q: q for q in top}
def raiz(q):
    while padre[q] != q:
        q = padre[q]
    return q
qs = list(top)
for i, x in enumerate(qs):
    for y in qs[i + 1:]:
        if jaccard(top[x], top[y]) >= lim["umbral_solape_serp"]:
            padre[raiz(y)] = raiz(x)
grupos = {}
for q in qs:
    grupos.setdefault(raiz(q), []).append(q)
filas_grupo = []
for n, (cabeza, miembros) in enumerate(grupos.items(), 1):
    propias = sorted({(f["url"], f["posicion"]) for f in resultados if f["consulta"] in miembros and c["dominio"] in f["dominio"]},
                     key=lambda x: x[1] or 99)
    urls = list(dict.fromkeys(u for u, _ in propias))
    mayor = max(miembros, key=lambda q: int(float(volumen.get(q) or 0)))
    accion = ("crear: ninguna URL propia en los primeros resultados" if not urls
              else f"actualizar {urls[0]}" if len(urls) == 1
              else "revisar a mano: varias URLs propias aparecen; decidir si se consolidan")
    filas_grupo.append({"grupo": f"G{n}", "consultas": "; ".join(miembros), "consulta_mayor": mayor,
                        "volumen_consulta_mayor": volumen.get(mayor), "contiene_principal": "sí" if c["consulta_principal"].lower() in miembros else "",
                        "urls_propias": "; ".join(f"{u} (#{p})" for u, p in propias), "accion_candidata": accion})
    for f in resultados:
        if f["consulta"] in miembros:
            f["grupo"] = f"G{n}"

# Comparables: primeros resultados de la principal que no son propios ni de dominios excluidos.
principal = c["consulta_principal"].lower()
elegidas = []
for f in resultados:
    f["seleccionada"] = ""
    if f["consulta"] == principal and (f["posicion"] or 99) <= lim["top_organico"]:
        if c["dominio"] in f["dominio"]:
            f["seleccionada"] = "propia"
        elif not any(d in f["dominio"] for d in lim["excluir_dominios"]) and len(elegidas) < lim["paginas_comparables"]:
            f["seleccionada"] = "comparable"
            elegidas.append(f["url"])

# El modelo solo etiqueta, sin haber leído las páginas: es una inferencia y así se rotula.
diez = [f for f in resultados if f["consulta"] == principal and (f["posicion"] or 99) <= lim["top_organico"]]
etiquetas = pedir_json(caso, exp, "03-clasificar-resultados",
    "Clasificas resultados de búsqueda a partir de su título, descripción y URL. Es una inferencia: no has leído las páginas. "
    "Devuelve solo JSON.",
    f"Consulta: {principal}\n\nResultados:\n" + "\n".join(f"{f['posicion']}. {f['titulo']} | {f['url']} | {f['descripcion']}" for f in diez)
    + '\n\nLista JSON, un objeto por resultado: {"posicion": n, "tipo_pagina": "tienda|blog de marca|medio|foro|vídeo|comparador|otro", '
      '"tarea": "qué quiere resolver quien llega", "formato": "guía|lista|ficha|respuesta breve|otro"}',
    max_tokens=1500, fresco=op["fresco"]) if diez and disponible(caso) else []
por_pos = {e.get("posicion"): e for e in etiquetas or [] if isinstance(e, dict)}
for f in diez:
    e = por_pos.get(f["posicion"], {})
    f.update(tipo_pagina_inferido=e.get("tipo_pagina"), tarea_inferida=e.get("tarea"), formato_inferido=e.get("formato"))

escribir_csv(exp / "03-resultados.csv", resultados,
             ["consulta", "grupo", "posicion", "dominio", "titulo", "url", "seleccionada", "tipo_pagina_inferido",
              "tarea_inferida", "formato_inferido", "descripcion", "fecha_captura"])
escribir_csv(exp / "03-grupos.csv", filas_grupo, ["grupo", "consultas", "consulta_mayor", "volumen_consulta_mayor",
                                                  "contiene_principal", "urls_propias", "accion_candidata"])
escribir_csv(exp / "03-preguntas-google.csv", [dict(t) for t in {tuple(p.items()) for p in preguntas}],
             ["consulta", "pregunta", "fuente", "fecha"])
escribir_csv(exp / "03-respuesta-ia-google.csv", ia, ["consulta", "dominio", "url", "es_propia"])
print(f"\n  {len(consultas)} consultas -> {len(filas_grupo)} grupos por solape de resultados\n")
for g in filas_grupo:
    print(f"  {g['grupo']} {'[principal] ' if g['contiene_principal'] else ''}{g['consultas'][:90]}\n      {g['accion_candidata']}")
print()
tabla(diez, ["posicion", "dominio", "tipo_pagina_inferido", "formato_inferido", "seleccionada"])
con_ia = sorted({x["consulta"] for x in ia})
print(f"\n  Respuesta de IA en Google: " + (f"observada en {len(con_ia)} de {len(consultas)} consultas; "
      f"{c['dominio']} enlazado en {sum(x['es_propia'] == 'sí' for x in ia)} ocasiones" if ia else "no observada en estas capturas"))
print("  No sumamos el volumen de las consultas de un grupo: son la misma demanda dicha de varias formas.")
print("  Para debatir: que dos URLs propias aparezcan en un grupo, ¿basta para hablar de canibalización?")
