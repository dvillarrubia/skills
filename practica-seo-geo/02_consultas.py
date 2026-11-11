"""Paso 2. Investigación de palabras clave: ampliación, problema al que sirve cada consulta y prioridad por fórmula.

Dos modos, según [apis] volumenes en caso.toml:
  ninguno     gratis: demanda observada en Google (autocompletado, preguntas, búsquedas relacionadas), sin volumen
  dataforseo  de pago: además, volumen estimado, dificultad y posiciones del dominio con DataForSEO Labs
"""
import math
from collections import Counter
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, leer_csv, hoy, tabla
from sop.llm import pedir_json, disponible

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c, m, lim = caso["caso"], caso["mercado"], caso["limites"]
con_volumen = caso["apis"]["volumenes"] == "dataforseo"
explicar("Paso 2 · Palabras clave",
         ("Ampliamos con DataForSEO Labs (Keyword Suggestions, Related Keywords, Keyword Ideas) y pedimos las consultas "
          "por las que el dominio ya posiciona." if con_volumen else
          "Reunimos la demanda que Google enseña gratis: autocompletado de cada semilla, preguntas y búsquedas "
          "relacionadas. No tenemos volumen: contamos en cuántos sitios aparece cada consulta.")
         + " Después relacionamos cada consulta con un problema del público del paso 1.",
         "Una lista ordenada por volumen no es una estrategia, y sin volumen tampoco estamos a ciegas: una consulta que "
         "Google sugiere, pregunta y relaciona a la vez es demanda real. La prioridad sale de una fórmula a la vista. "
         "El modelo solo dice a qué problema responde cada consulta; el número lo calcula Python.",
         "Las consultas sin problema asociado, las que más se repiten entre fuentes y si la consulta principal de "
         "partida sobrevive al ranking." + ("" if con_volumen else " Con [apis] volumenes = \"dataforseo\" se añaden "
         "volumen, dificultad y posiciones propias."))

filas, vistas, posiciones = {}, Counter(), {}


def anotar(consulta, fuente, semilla="", info=None, prop=None, inten=None):
    k = (consulta or "").strip().lower().rstrip("?").lstrip("¿")
    if not k:
        return
    vistas[k] += 1
    info, prop, inten = info or {}, prop or {}, inten or {}
    filas.setdefault(k, {"consulta": k, "semilla": semilla, "fuente": fuente, "fecha_captura": hoy(),
                         "fecha_dato": (info.get("last_updated_time") or "")[:10], "volumen_estimado": info.get("search_volume"),
                         "cpc": info.get("cpc"), "competencia_publicitaria": info.get("competition_level"),
                         "dificultad_organica": prop.get("keyword_difficulty"), "intencion_estimada": inten.get("main_intent"),
                         "relacion_negocio": "sí" if any(t in k for t in c["terminos_negocio"]) else "no"})


# Demanda observada: sirve en los dos modos.
for q in [c["consulta_principal"]] + c["variantes"] + c["semillas"]:
    anotar(q, "caso.toml")
for f in leer_csv(exp / "01-demanda-observada.csv"):
    anotar(f["texto"], f"Google: {f['tipo']}")

if con_volumen:
    from sop.dfs import DataForSEO
    dfs = DataForSEO(exp, op["seco"], op["fresco"])
    base = {"location_code": m["location_code"], "language_code": m["language_code"]}
    items = lambda r: ((r or [{}])[0].get("items") or []) if r else []
    datos = lambda it: (it.get("keyword"), it.get("keyword_info"), it.get("keyword_properties"), it.get("search_intent_info"))
    for i, semilla in enumerate(c["semillas"]):
        for it in items(dfs.post("dataforseo_labs/google/keyword_suggestions/live",
                                 {**base, "keyword": semilla, "limit": lim["max_consultas_por_semilla"], "include_seed_keyword": True},
                                 f"02-sugerencias-{i}")):
            k, a, b, d = datos(it)
            anotar(k, "Labs Keyword Suggestions", semilla, a, b, d)
    for it in items(dfs.post("dataforseo_labs/google/related_keywords/live",
                             {**base, "keyword": c["consulta_principal"], "depth": 1, "limit": lim["max_consultas_por_semilla"]},
                             "02-relacionadas")):
        k, a, b, d = datos(it.get("keyword_data") or {})
        anotar(k, "Labs Related Keywords", c["consulta_principal"], a, b, d)
    for it in items(dfs.post("dataforseo_labs/google/keyword_ideas/live",
                             {**base, "keywords": list(filas)[:20], "limit": lim["max_consultas_por_semilla"]}, "02-ideas")):
        k, a, b, d = datos(it)
        anotar(k, "Labs Keyword Ideas", "demanda observada", a, b, d)
    for it in items(dfs.post("dataforseo_labs/google/ranked_keywords/live",
                             {**base, "target": c["dominio"], "limit": 500,
                              "order_by": ["keyword_data.keyword_info.search_volume,desc"]}, "02-posiciones-propias")):
        kd, el = it.get("keyword_data") or {}, (it.get("ranked_serp_element") or {}).get("serp_item") or {}
        if el.get("type") == "organic":
            posiciones[(kd.get("keyword") or "").lower()] = (el.get("rank_group"), el.get("url"))
            k, a, b, d = datos(kd)
            anotar(k, "Labs Ranked Keywords (dominio propio)", "", a, b, d)
    # Las consultas observadas gratis también reciben volumen cuando Labs las devuelve; si no, quedan en nulo.
else:
    from sop.serp import Buscador
    google = Buscador(caso, exp, op["seco"], op["fresco"])
    for i, semilla in enumerate(dict.fromkeys(c["semillas"] + c["variantes"])):
        for s in google.autocompletar(semilla, f"02-autocompletar-{i}"):
            anotar(s, "Google: autocompletado", semilla)

if op["seco"]:
    raise SystemExit("\nModo --seco: no se ha enviado nada. Quita --seco para hacer las peticiones.")

# A qué problema responde cada consulta: etiqueta del modelo, validada contra los ids reales del paso 1.
pains = {f["id"]: f for f in leer_csv(exp / "01-pains.csv") if not f["estado"].startswith("descartado")}
negocio = sorted((f for f in filas.values() if f["relacion_negocio"] == "sí"),
                 key=lambda f: (-(f["volumen_estimado"] or 0), -vistas[f["consulta"]]))
asignadas = {}
if pains and disponible(caso):
    datos_llm = pedir_json(caso, exp, "02-consulta-a-pain",
        "Relacionas consultas de búsqueda con problemas de cliente. Si una consulta no responde con claridad a ninguno, "
        "pon null. No fuerces relaciones. Devuelve solo JSON.",
        "PROBLEMAS\n" + "\n".join(f"{i}: {f['problema']} (resultado deseado: {f['resultado_deseado']})" for i, f in pains.items())
        + "\n\nCONSULTAS\n" + "\n".join(f["consulta"] for f in negocio[:lim["consultas_a_asignar"]])
        + '\n\nFormato: {"consulta exacta": "D1" o null, ...}', max_tokens=4000, fresco=op["fresco"])
    asignadas = {k.lower(): v for k, v in (datos_llm or {}).items() if v in pains}

for f in filas.values():
    pos, url = posiciones.get(f["consulta"], (None, None))
    pain = pains.get(asignadas.get(f["consulta"]))
    f.update(posicion_propia=pos, url_propia=url, veces_observada=vistas[f["consulta"]], pain=pain["id"] if pain else "",
             etapa=pain["etapa"] if pain else "", pain_estado=pain["estado"] if pain else "")
    # Fórmula de prioridad. Cada factor es discutible en clase; por eso está a la vista y no dentro de un modelo.
    evidencia = 1 + 0.5 * int(pain["fuentes_independientes"]) if pain else 0.5
    if con_volumen:
        demanda = math.log10((f["volumen_estimado"] or 0) + 1)
        facilidad = 1 - (f["dificultad_organica"] if f["dificultad_organica"] is not None else 50) / 100
        a_tiro = 1.5 if pos and 4 <= pos <= 20 else 1.0
        valor = demanda * facilidad * evidencia * a_tiro
    else:
        valor = vistas[f["consulta"]] * evidencia
    f["prioridad"] = round(valor, 2) if f["relacion_negocio"] == "sí" else 0

orden = sorted(filas.values(), key=lambda f: -f["prioridad"])
for i, f in enumerate(orden):
    f["candidata_serp"] = "sí" if i < lim["candidatas_serp"] and f["prioridad"] > 0 else ""
escribir_csv(exp / "02-consultas.csv", orden,
             ["consulta", "prioridad", "candidata_serp", "veces_observada", "volumen_estimado", "dificultad_organica", "pain", "etapa",
              "pain_estado", "posicion_propia", "url_propia", "intencion_estimada", "cpc", "competencia_publicitaria",
              "relacion_negocio", "semilla", "fuente", "fecha_captura", "fecha_dato"])
print(f"\n  {len(orden)} consultas únicas · {len(negocio)} con relación con el negocio · {len(asignadas)} asociadas a un problema"
      + (f" · {sum(1 for f in orden if f['posicion_propia'])} en las que {c['dominio']} ya posiciona · "
         f"{sum(1 for f in orden if f['volumen_estimado'] is None)} sin volumen (nulo, no cero)" if con_volumen else " · sin volumen (modo gratuito)") + "\n")
tabla(orden[:15], ["consulta", "prioridad", "veces_observada", "pain"] + (["volumen_estimado", "dificultad_organica", "posicion_propia"] if con_volumen else []))
puesto = next((i + 1 for i, f in enumerate(orden) if f["consulta"] == c["consulta_principal"].lower()), None)
print("\n  Prioridad = " + ("log10(volumen+1) × (1 − dificultad/100) × (1 + 0,5 × fuentes del problema) × 1,5 si posición 4–20"
                           if con_volumen else "veces observada × (1 + 0,5 × fuentes del problema); 0,5 si no responde a ningún problema"))
print(f"  La consulta principal de partida queda en el puesto {puesto or 'fuera de la lista'}.")
print("  Para debatir: ¿cambiamos de consulta principal? Si es así, se edita caso.toml y se dice por qué.")
