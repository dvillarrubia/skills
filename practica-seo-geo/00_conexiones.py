"""Paso 0. Comprueba las conexiones reales que usa el caso, según los proveedores elegidos en [apis] de caso.toml."""
import os
import requests
from sop.comun import cargar_caso, expediente, explicar
from sop import paginas

caso = cargar_caso()
exp = expediente(caso)
api, mod = caso["apis"], caso["modelo"]
explicar("Paso 0 · Conexiones",
         "Probamos cada servicio que el caso tiene configurado: de dónde salen los resultados de Google, quién lee las "
         "páginas, quién hace de asistente y qué modelo redacta.",
         "Una práctica en directo no puede descubrir a mitad de clase que falta una clave. Y conviene que todo el "
         "mundo vea de dónde sale cada dato antes de fiarse de él.",
         "Que cada línea termine en «correcto». Las claves gratuitas se crean en serpapi.com y aistudio.google.com; "
         "Jina Reader no necesita clave.")
print(f"  Configuración: serp={api['serp']} · lector={api['lector']} · volumenes={api['volumenes']} · "
      f"asistente={api['asistente']} · modelo={mod['proveedor']}\n")

if api["serp"] == "serpapi":
    r = requests.get("https://serpapi.com/account.json", params={"api_key": os.environ.get("SERPAPI_API_KEY", "")}, timeout=30)
    d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    print(f"  SerpApi: " + (f"correcto. Plan {d.get('plan_name')}, quedan {d.get('total_searches_left')} búsquedas este mes"
                            if r.ok and not d.get("error") else f"ERROR {r.status_code} {d.get('error', '')} (clave en serpapi.com)"))

if "dataforseo" in (api["serp"], api["volumenes"], api["asistente"]):
    from sop.dfs import DataForSEO
    dfs = DataForSEO(exp)
    u = dfs.get("appendix/user_data")
    try:
        print(f"  DataForSEO: correcto. Saldo: {u['tasks'][0]['result'][0]['money'].get('balance')} USD")
    except (KeyError, IndexError, TypeError):
        print(f"  DataForSEO: ERROR {u.get('status_code')} {u.get('status_message')}")
    if api["asistente"] == "dataforseo":
        loc = caso["mercado"]["location_code"]
        lugares = dfs.get("ai_optimization/chat_gpt/llm_scraper/locations")
        codigos = {x.get("location_code") for x in ((lugares.get("tasks") or [{}])[0].get("result") or [])}
        print(f"  ChatGPT LLM Scraper: {'cubre' if loc in codigos else 'NO lista'} la localización {loc}")

if "gemini" in (api["asistente"], mod["proveedor"]):
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                     params={"key": os.environ.get("GEMINI_API_KEY", ""), "pageSize": 200}, timeout=30)
    if r.ok:
        nombres = [x["name"].split("/")[-1] for x in r.json().get("models", [])
                   if "generateContent" in x.get("supportedGenerationMethods", [])]
        esta = mod["nombre_gemini"] in nombres
        print(f"  Gemini: correcto. {len(nombres)} modelos; «{mod['nombre_gemini']}» {'disponible' if esta else 'NO está: elige uno de la lista'}")
        if not esta:
            print("     " + ", ".join(n for n in nombres if "flash" in n or "pro" in n)[:400])
    else:
        print(f"  Gemini: ERROR {r.status_code} (clave en aistudio.google.com)")

if mod["proveedor"] == "anthropic":
    r = requests.post("https://api.anthropic.com/v1/messages", timeout=60,
                      headers={"x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01",
                               "content-type": "application/json"},
                      json={"model": mod["nombre_anthropic"], "max_tokens": 10, "messages": [{"role": "user", "content": "Responde solo: OK"}]})
    print(f"  Anthropic {mod['nombre_anthropic']}: " + ("correcto" if r.ok else f"ERROR {r.status_code} {r.text[:160]}"))

paginas.configurar(caso)
url = caso["propias"]["urls"][0]
html, ficha = paginas.descargar(url)
if html:
    datos, texto = paginas.analizar(html, url)
    print(f"  Lectura de páginas ({datos['metodo']}): correcto. {datos['palabras']} palabras de {url}")
else:
    print(f"  Lectura de páginas: {ficha['incidencia'] or ficha['estado']}  {url}")
