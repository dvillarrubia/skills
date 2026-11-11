"""Paso 4. Respuestas reales de asistentes de IA a las preguntas del público, repetidas, con fuentes y marcas."""
import sys
from collections import Counter, defaultdict
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, hoy, dominio
from sop.llm import asistente_gemini

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
etiqueta = (op["resto"] or ["referencia"])[0]          # «referencia» ahora; «seguimiento-AAAA-MM-DD» en el paso 13

c, m, a = caso["caso"], caso["mercado"], caso["asistentes"]
(exp / "04-respuestas").mkdir(exist_ok=True)
explicar("Paso 4 · Visibilidad en respuestas generativas",
         "Hacemos a un asistente con búsqueda en la web las preguntas del público, varias veces cada una, y guardamos "
         "la respuesta, las fuentes en que se apoya y las búsquedas que lanza. Por defecto es Gemini con búsqueda de "
         "Google (clave gratuita); con DataForSEO se captura ChatGPT tal como lo ve un usuario.",
         "Las respuestas cambian entre ejecuciones: una captura es una anécdota. Por eso contamos en cuántas "
         "ejecuciones aparece cada fuente, y lo cuenta Python buscando el dominio y el nombre de la marca.",
         "Si la marca aparece citada (enlazada), mencionada (nombrada) o ausente; qué dominios se repiten; y qué "
         "búsquedas lanza el asistente por debajo (fan-out): son las consultas para las que hay que estar presente.")

import json, requests
modo = caso["apis"]["asistente"]
if modo == "dataforseo" or a.get("llm_responses"):
    from sop.dfs import DataForSEO
    dfs = DataForSEO(exp, op["seco"], op["fresco"])


def url_real(u):
    """Gemini devuelve las fuentes tras una redirección de Google; la seguimos para guardar la URL de verdad."""
    try:
        return requests.head(u, allow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).url
    except requests.RequestException:
        return u


def gemini(pregunta, nombre):
    fichero = exp / "crudo" / f"{nombre}.json"
    if fichero.exists() and not op["fresco"]:
        g = json.loads(fichero.read_text(encoding="utf-8"))
        print(f"  [captura del {g['capturado']}] {nombre}  (usa --fresco para volver a pedir)")
        return g["respuesta"]
    if caso["apis"]["asistente"] == "claudecode":
        # El asistente es Claude Code (esta sesión) con búsqueda web. No se llama a ninguna API:
        # Claude responde a la pregunta, guarda la respuesta y sus fuentes, y al re-ejecutar se reutiliza.
        sys.exit(f"[Claude Code es el asistente] No hay respuesta guardada para «{nombre}». "
                 f"Claude: responde a «{pregunta}» con búsqueda web y escribe crudo/{nombre}.json con la forma "
                 '{"capturado": "<fecha ISO>", "proveedor": "claudecode", "carga": {"pregunta": "..."}, '
                 '"respuesta": {"texto": "...", "fuentes": [{"url": "...", "titulo": "..."}], "busquedas": ["..."]}}. '
                 f"Después vuelve a ejecutar el paso.")
    print(f"  Gemini con búsqueda de Google <- «{pregunta}»")
    if op["seco"]:
        return None
    r = asistente_gemini(caso, pregunta)
    for f in r["fuentes"]:
        f["url"] = url_real(f["url"])
    from sop.comun import ahora
    fichero.write_text(json.dumps({"capturado": ahora(), "proveedor": "gemini", "carga": {"pregunta": pregunta}, "respuesta": r},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return r


def recoger(nodo, tipo, salida):
    if isinstance(nodo, dict):
        if nodo.get("type") == tipo:
            salida.append(nodo)
        for v in nodo.values():
            recoger(v, tipo, salida)
    elif isinstance(nodo, list):
        for v in nodo:
            recoger(v, tipo, salida)


def estado_marca(texto, urls):
    if any(c["dominio"] in (u or "") for u in urls):
        return "citada"
    return "mencionada" if c["marca"].lower() in (texto or "").lower() else "ausente"


filas, fuentes = [], defaultdict(set)
for i, pregunta in enumerate(a["preguntas"]):
    for n in range(1, a["ejecuciones"] + 1):
        if modo in ("gemini", "claudecode"):
            prov = "claude" if modo == "claudecode" else "gemini"
            sup = "Claude Code con búsqueda web" if modo == "claudecode" else "Gemini con búsqueda de Google"
            r = gemini(pregunta, f"04-{etiqueta}-{prov}-p{i}-e{n}")
            if not r:
                continue
            texto, urls = r["texto"], list(dict.fromkeys(f["url"] for f in r["fuentes"]))
            superficie, marcas, abanico_, cabecera = sup, "", r["busquedas"], f"{sup} · ejecución {n} · {hoy()}"
        else:
            r = dfs.post("ai_optimization/chat_gpt/llm_scraper/live/advanced",
                         {"keyword": pregunta, "location_code": m["location_code"], "language_code": m["language_code"]},
                         f"04-{etiqueta}-chatgpt-p{i}-e{n}")
            if not r:
                continue
            citas, entidades = [], []
            recoger(r, "chat_gpt_source", citas)
            recoger(r, "chat_gpt_brand_entity", entidades)
            texto = r[0].get("markdown") or "\n\n".join(x.get("markdown", "") for x in r[0].get("items") or [] if isinstance(x, dict))
            urls = list(dict.fromkeys(x.get("url") for x in citas if x.get("url")))
            superficie, abanico_ = "ChatGPT (LLM Scraper)", r[0].get("fan_out_queries") or []
            marcas = "; ".join(dict.fromkeys(x.get("title", "") for x in entidades))
            cabecera = f"ChatGPT · ejecución {n} · {r[0].get('datetime', hoy())} · modelo {r[0].get('model', '')}"
        (exp / "04-respuestas" / f"{etiqueta}-p{i}-e{n}.md").write_text(f"# {pregunta}\n\n{cabecera}\n\n{texto}\n", encoding="utf-8")
        for u in urls:
            fuentes[(i, dominio(u), u)].add(n)
        filas.append({"etiqueta": etiqueta, "pregunta": pregunta, "superficie": superficie, "ejecucion": n,
                      "fecha": hoy(), "marca_propia": estado_marca(texto, urls), "n_fuentes": len(urls),
                      "dominios_citados": "; ".join(dict.fromkeys(dominio(u) for u in urls)),
                      "marcas_mencionadas": marcas, "busquedas_fan_out": "; ".join(map(str, abanico_))})

# Superficies extra por API. La respuesta por API puede diferir de la que ve un usuario en la aplicación.
for spec in a.get("llm_responses", []):
    plataforma, modelo = spec.split(":", 1)
    for i, pregunta in enumerate(a["preguntas"]):
        for n in range(1, a["ejecuciones"] + 1):
            carga = {"user_prompt": pregunta, "model_name": modelo, "web_search": True}
            if plataforma == "chat_gpt":
                carga["web_search_country_iso_code"] = m["pais_iso"]
            r = dfs.post(f"ai_optimization/{plataforma}/llm_responses/live", carga, f"04-{etiqueta}-{plataforma}-p{i}-e{n}")
            if not r:
                continue
            texto, urls = "", []
            for item in r[0].get("items") or []:
                for s in (item.get("sections") or []) if item.get("type") == "message" else []:
                    texto += s.get("text") or ""
                    urls += [x.get("url") for x in s.get("annotations") or [] if x.get("url")]
            urls = list(dict.fromkeys(urls))
            for u in urls:
                fuentes[(i, dominio(u), u)].add(n)
            filas.append({"etiqueta": etiqueta, "pregunta": pregunta, "superficie": f"{plataforma} {modelo} (API)", "ejecucion": n,
                          "fecha": hoy(), "marca_propia": estado_marca(texto, urls), "n_fuentes": len(urls),
                          "dominios_citados": "; ".join(dict.fromkeys(dominio(u) for u in urls))})

if op["seco"]:
    sys.exit("\nModo --seco: no se ha enviado nada.")

sufijo = "" if etiqueta == "referencia" else f"-{etiqueta}"
escribir_csv(exp / f"04-asistentes{sufijo}.csv", filas,
             ["etiqueta", "pregunta", "superficie", "ejecucion", "fecha", "marca_propia", "n_fuentes", "dominios_citados",
              "marcas_mencionadas", "busquedas_fan_out"])
escribir_csv(exp / f"04-fuentes{sufijo}.csv",
             sorted(({"pregunta": a["preguntas"][i], "dominio": d, "url": u, "ejecuciones": len(ns),
                      "de": a["ejecuciones"], "es_propia": "sí" if c["dominio"] in d else "no"}
                     for (i, d, u), ns in fuentes.items()), key=lambda f: (f["pregunta"], -f["ejecuciones"])),
             ["pregunta", "dominio", "url", "ejecuciones", "de", "es_propia"])
abanico = Counter(q.strip().lower() for f in filas for q in (f.get("busquedas_fan_out") or "").split(";") if q.strip())
escribir_csv(exp / f"04-fan-out{sufijo}.csv", [{"busqueda": q, "veces": n} for q, n in abanico.most_common()], ["busqueda", "veces"])
print()
for pregunta in a["preguntas"]:
    estados = Counter(f["marca_propia"] for f in filas if f["pregunta"] == pregunta)
    total = sum(estados.values())
    print(f"  «{pregunta}»\n     {c['marca']}: citada {estados['citada']}/{total} · mencionada {estados['mencionada']}/{total} "
          f"· ausente {estados['ausente']}/{total}")
print("\n  Para debatir: una mención no es una recomendación, y «ausente en 3 ejecuciones» no es «ausente siempre».")
