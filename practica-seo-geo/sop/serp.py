"""Resultados de Google y autocompletado con el proveedor elegido en caso.toml: SerpApi (plan gratuito) o DataForSEO.

Los dos devuelven lo mismo, ya normalizado, para que el resto de la práctica no dependa del proveedor:
  resultados() -> {"organicos": [{posicion, url, titulo, descripcion}], "preguntas": [...], "ia": [urls], "relacionadas": [...]}
  autocompletar() -> [sugerencias]
"""
import json, os, sys
import requests
from .comun import ahora


class Buscador:
    def __init__(self, caso, exp, seco=False, fresco=False):
        self.caso, self.exp, self.seco, self.fresco = caso, exp, seco, fresco
        self.proveedor = caso["apis"]["serp"]
        m = caso["mercado"]
        self.pais, self.idioma = m["pais_iso"].lower(), m["language_code"]
        if self.proveedor == "dataforseo":
            from .dfs import DataForSEO
            self.dfs = DataForSEO(exp, seco, fresco)
        elif self.proveedor == "serpapi":
            self.clave = os.environ.get("SERPAPI_API_KEY", "")
            if not seco and not self.clave:
                sys.exit("Falta SERPAPI_API_KEY en .env. La clave gratuita se crea en serpapi.com (o usa --seco).")
        else:
            sys.exit(f"[apis] serp = «{self.proveedor}» no existe. Opciones: serpapi, dataforseo.")

    # --- SerpApi: una petición GET y una respuesta JSON ---
    def _serpapi(self, parametros, nombre):
        fichero = self.exp / "crudo" / f"{nombre}.json"
        if fichero.exists() and not self.fresco:
            g = json.loads(fichero.read_text(encoding="utf-8"))
            print(f"  [captura del {g['capturado']}] {nombre}  (usa --fresco para volver a pedir)")
            return g["respuesta"]
        print(f"  GET https://serpapi.com/search.json  {json.dumps(parametros, ensure_ascii=False)}")
        if self.seco:
            return None
        r = requests.get("https://serpapi.com/search.json", params={**parametros, "api_key": self.clave}, timeout=120)
        datos = r.json()
        if r.status_code != 200 or datos.get("error"):
            sys.exit(f"SerpApi devolvió un error: {r.status_code} {datos.get('error')}")
        fichero.write_text(json.dumps({"capturado": ahora(), "proveedor": "serpapi", "carga": parametros, "respuesta": datos},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
        return datos

    def resultados(self, consulta, nombre, profundidad=20, preguntas_extra=False):
        if self.proveedor == "serpapi":
            d = self._serpapi({"engine": "google", "q": consulta, "google_domain": f"google.{self.pais}", "gl": self.pais,
                               "hl": self.idioma, "device": self.caso["mercado"]["dispositivo"]}, nombre)
            if d is None:
                return None
            return {"organicos": [{"posicion": x.get("position"), "url": x.get("link"), "titulo": x.get("title"),
                                   "descripcion": x.get("snippet")} for x in d.get("organic_results") or []],
                    "preguntas": [x.get("question") for x in d.get("related_questions") or [] if x.get("question")],
                    "ia": list(dict.fromkeys(x.get("link") for x in (d.get("ai_overview") or {}).get("references") or [] if x.get("link"))),
                    "relacionadas": [x.get("query") for x in d.get("related_searches") or [] if x.get("query")]}
        m = self.caso["mercado"]
        carga = {"keyword": consulta, "location_code": m["location_code"], "language_code": m["language_code"],
                 "device": m["dispositivo"], "depth": profundidad, "load_async_ai_overview": True}
        if preguntas_extra:
            carga["people_also_ask_click_depth"] = 2
        r = self.dfs.post("serp/google/organic/live/advanced", carga, nombre)
        if not r:
            return None
        salida = {"organicos": [], "preguntas": [], "ia": [], "relacionadas": []}
        for item in r[0].get("items") or []:
            t = item.get("type")
            if t == "organic":
                salida["organicos"].append({"posicion": item.get("rank_group"), "url": item.get("url"),
                                            "titulo": item.get("title"), "descripcion": item.get("description")})
            elif t == "people_also_ask":
                salida["preguntas"] += [x.get("title") for x in item.get("items") or [] if x.get("title")]
            elif t == "ai_overview":
                refs = []
                _referencias(item, refs)
                salida["ia"] += list(dict.fromkeys(refs))
            elif t == "related_searches":
                salida["relacionadas"] += [x for x in item.get("items") or [] if isinstance(x, str)]
        return salida

    def autocompletar(self, consulta, nombre):
        if self.proveedor == "serpapi":
            d = self._serpapi({"engine": "google_autocomplete", "q": consulta, "gl": self.pais, "hl": self.idioma}, nombre)
            return [x.get("value") for x in (d or {}).get("suggestions") or [] if x.get("value")]
        m = self.caso["mercado"]
        r = self.dfs.post("serp/google/autocomplete/live/advanced",
                          {"keyword": consulta, "location_code": m["location_code"], "language_code": m["language_code"]}, nombre)
        return [x.get("suggestion") for x in ((r or [{}])[0].get("items") or []) if x.get("suggestion")]


def _referencias(nodo, salida):
    if isinstance(nodo, dict):
        salida += [r["url"] for r in nodo.get("references") or [] if isinstance(r, dict) and r.get("url")]
        for v in nodo.values():
            _referencias(v, salida)
    elif isinstance(nodo, list):
        for v in nodo:
            _referencias(v, salida)
