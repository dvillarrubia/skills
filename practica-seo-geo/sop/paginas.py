"""Descarga y extracción de páginas con trazabilidad. Respeta robots.txt y nunca trata un error como ausencia."""
import json, re
import urllib.robotparser
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

AGENTE = "Mozilla/5.0 (compatible; practica-sop-seo-geo/1.0; uso docente)"
_robots = {}
LECTOR = "local"            # «jina» usa r.jina.ai para el texto principal; lo fija configurar()


def configurar(caso):
    global LECTOR
    LECTOR = caso.get("apis", {}).get("lector", "local")


def leer_con_jina(url):
    """Jina Reader: se antepone r.jina.ai/ a la URL y devuelve la página en Markdown. Sin clave funciona con límite."""
    import os, time
    cab = {"Accept": "application/json", "X-Return-Format": "markdown", "X-Retain-Images": "none",
           "X-Remove-Selector": "header, footer, nav, aside, form, script, style"}   # fuera menús, pie e imágenes
    if os.environ.get("JINA_API_KEY"):
        cab["Authorization"] = "Bearer " + os.environ["JINA_API_KEY"]
    else:
        time.sleep(3.2)     # sin clave el límite ronda las 20 peticiones por minuto
    try:
        r = requests.get("https://r.jina.ai/" + url, headers=cab, timeout=90)
        return ((r.json().get("data") or {}).get("content") or "").strip() if r.status_code == 200 else ""
    except (requests.RequestException, ValueError):
        return ""


def permitido(url):
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(base + "/robots.txt", headers={"User-Agent": AGENTE}, timeout=15)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except requests.RequestException:
            rp.parse([])
        _robots[base] = rp
    return _robots[base].can_fetch(AGENTE, url)


def descargar(url):
    """Devuelve (html, ficha). La ficha siempre existe; html es None si la página no es evaluable."""
    ficha = {"url": url, "url_final": "", "estado": "", "incidencia": ""}
    if not permitido(url):
        ficha["incidencia"] = "no evaluable: robots.txt no permite el acceso"
        return None, ficha
    try:
        r = requests.get(url, headers={"User-Agent": AGENTE, "Accept-Language": "es-ES,es;q=0.9"}, timeout=30)
    except requests.RequestException as e:
        ficha["incidencia"] = f"no evaluable: {type(e).__name__}"
        return None, ficha
    ficha.update(url_final=r.url, estado=r.status_code)
    if r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
        ficha["incidencia"] = f"no evaluable: HTTP {r.status_code} {r.headers.get('content-type', '')}"
        return None, ficha
    r.encoding = r.encoding if r.encoding and r.encoding.lower() != "iso-8859-1" else r.apparent_encoding
    return r.text, ficha


def analizar(html, url=None):
    """Metadatos de implementación (del HTML) y texto principal (para analizar el contenido)."""
    sopa = BeautifulSoup(html, "lxml")
    meta = lambda **k: (sopa.find("meta", attrs=k) or {}).get("content", "")
    enlace = sopa.find("link", rel="canonical")
    tipos = []
    for s in sopa.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(s.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for nodo in (d if isinstance(d, list) else d.get("@graph", [d]) if isinstance(d, dict) else []):
            t = nodo.get("@type") if isinstance(nodo, dict) else None
            tipos += t if isinstance(t, list) else [t] if t else []
    datos = {
        "titulo": (sopa.title.string or "").strip() if sopa.title else "",
        "descripcion": meta(name="description"),
        "canonical": enlace.get("href", "") if enlace else "",
        "robots": meta(name="robots"),
        "h1": " | ".join(h.get_text(" ", strip=True) for h in sopa.find_all("h1")),
        "h2_h3": " | ".join(h.get_text(" ", strip=True) for h in sopa.find_all(["h2", "h3"]))[:1500],
        "tablas": len(sopa.find_all("table")),
        "datos_estructurados": ", ".join(sorted(set(map(str, tipos)))),
    }
    texto = None
    if LECTOR == "jina" and url:
        texto = leer_con_jina(url)
        if texto:
            datos["metodo"] = "Jina Reader"
            datos["palabras"] = len(texto.split())
            return datos, texto
    try:
        import trafilatura
        texto = trafilatura.extract(html, output_format="markdown", include_tables=True, include_links=False,
                                    favor_recall=True)
    except ImportError:
        pass
    if not texto:  # respaldo: cuerpo sin navegación ni pie
        for t in sopa(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            t.decompose()
        texto = re.sub(r"\n\s*\n+", "\n\n", (sopa.find("main") or sopa.body or sopa).get_text("\n", strip=True))
        datos["metodo"] = "respaldo bs4"
    else:
        datos["metodo"] = "trafilatura"
    datos["palabras"] = len(texto.split())
    return datos, texto
