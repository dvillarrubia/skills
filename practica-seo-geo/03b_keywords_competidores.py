"""Paso 3b. Keywords de los competidores. Lee quién rankea en la SERP (paso 3), pide a DataForSEO Labs
las consultas por las que posiciona cada competidor y se queda con las relevantes que nosotros aún no atacamos.
Solo con [apis] volumenes = "dataforseo". Objetivo: ampliar el research con lo que ya le funciona a la competencia."""
import sys
from collections import defaultdict
from sop.comun import cargar_caso, expediente, explicar, opciones, leer_csv, escribir_csv, hoy, dominio

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c, m, lim = caso["caso"], caso["mercado"], caso["limites"]

explicar("Paso 3b · Keywords de los competidores",
         "Cogemos los dominios que rankean en la SERP de nuestras consultas y preguntamos a DataForSEO Labs por qué "
         "palabras posicionan ellos. Nos quedamos con las que tienen que ver con el negocio y que nosotros todavía no "
         "trabajamos: son candidatas para ampliar el contenido y el research.",
         "Lo que ya le funciona a la competencia es la mejor pista de demanda real. No para copiarles, sino para no "
         "dejarnos temas que Google premia en este nicho.",
         "Qué keywords relevantes aparecen que no teníamos, con su volumen y la posición del competidor.")

if caso["apis"]["volumenes"] != "dataforseo":
    sys.exit("Este paso necesita [apis] volumenes = \"dataforseo\" en caso.toml.")

from sop.dfs import DataForSEO
dfs = DataForSEO(exp, op["seco"], op["fresco"])

# 1) Dominios competidores reales de la SERP (fuera redes, foros, buscadores, diccionarios, agregados).
FUERA = {"reddit.com", "youtube.com", "tiktok.com", "instagram.com", "facebook.com", "google.es",
         "es.wikipedia.org", "dle.rae.es", "usc.gal", "ugr.es", "forocafe.es"}
FUERA |= set(caso["limites"].get("excluir_dominios", []))
vistos, competidores = set(), []
for r in leer_csv(exp / "03-resultados.csv"):
    d = (r.get("dominio") or dominio(r.get("url", ""))).lower()
    if d and d != c["dominio"] and d not in FUERA and d not in vistos:
        vistos.add(d)
        competidores.append(d)
competidores = competidores[:lim.get("competidores_keywords", 4)]
print(f"  Competidores a analizar: {', '.join(competidores)}\n")

# 2) Consultas que ya tenemos (para marcar lo que es nuevo).
ya_tenemos = {f["consulta"].strip().lower() for f in leer_csv(exp / "02-consultas.csv")}
RELEVANTE = ("molienda", "moler", "molido", "moka", "cafetera italiana")

filas = []
for dom in competidores:
    r = dfs.post("dataforseo_labs/google/ranked_keywords/live",
                 {"location_code": m["location_code"], "language_code": m["language_code"], "target": dom,
                  "limit": 200, "order_by": ["keyword_data.keyword_info.search_volume,desc"]},
                 f"03b-keywords-{dom.replace('.', '-').replace('/', '-')}")
    for it in ((r or [{}])[0].get("items") or []) if r else []:
        kd = it.get("keyword_data") or {}
        el = (it.get("ranked_serp_element") or {}).get("serp_item") or {}
        kw = (kd.get("keyword") or "").strip().lower()
        info = kd.get("keyword_info") or {}
        if not kw or el.get("type") != "organic":
            continue
        rel_negocio = any(t in kw for t in c["terminos_negocio"])
        rel_tema = any(t in kw for t in RELEVANTE)
        if not rel_negocio:
            continue
        filas.append({"competidor": dom, "keyword": kw, "volumen": info.get("search_volume"),
                      "posicion_competidor": el.get("rank_group"), "relevante_para_el_tema": "sí" if rel_tema else "",
                      "nueva_para_nosotros": "sí" if kw not in ya_tenemos else "", "fecha": hoy()})

# Dedup por keyword quedándonos con la mejor posición.
mejor = {}
for f in filas:
    k = f["keyword"]
    if k not in mejor or (f["posicion_competidor"] or 999) < (mejor[k]["posicion_competidor"] or 999):
        mejor[k] = f
orden = sorted(mejor.values(), key=lambda f: (-(f["volumen"] or 0)))
escribir_csv(exp / "03b-keywords-competidores.csv", orden,
             ["keyword", "volumen", "competidor", "posicion_competidor", "relevante_para_el_tema", "nueva_para_nosotros", "fecha"])

gemas = [f for f in orden if f["relevante_para_el_tema"] and f["nueva_para_nosotros"]]
print(f"\n  {len(orden)} keywords de negocio de la competencia · {sum(1 for f in orden if f['nueva_para_nosotros'])} nuevas para nosotros "
      f"· {len(gemas)} relevantes para el tema y nuevas\n")
print("  Relevantes para el tema que NO teníamos (candidatas a encabezado/subtema):")
for f in gemas[:15]:
    print(f"    {str(f['volumen'] or '—').rjust(6)}  {f['keyword']}  (· {f['competidor']} pos. {f['posicion_competidor']})")
print("\n  Para el briefing: añade las que encajen con el tema y con el expertise del cliente; no metas todas por volumen.")
