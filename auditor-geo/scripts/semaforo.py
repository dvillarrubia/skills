"""Semáforo GEO de 7 pilares para una URL (versión didáctica del curso «SEO para IA y con IA»).

Descarga el HTML sin ejecutar JavaScript, robots.txt y llms.txt, y pide la página con el
user-agent de cada bot de IA. Cada pilar sale en verde, ámbar o rojo, con su evidencia.
Lo que el script no puede ver (el texto con JavaScript) queda como «no comprobado».

Uso:
    python semaforo.py URL                      # Markdown por pantalla
    python semaforo.py URL --salida semaforo.md # escribe semaforo.md y semaforo.json
    python semaforo.py URL --formato json       # JSON por pantalla
Solo biblioteca estándar. Python 3.10 o superior.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

NAVEGADOR = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

# token de robots.txt, tipo de bot y user-agent con el que se pide la página (None: solo es un token)
BOTS = [
    ("GPTBot", "entrenamiento", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.1; +https://openai.com/gptbot"),
    ("ClaudeBot", "entrenamiento", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"),
    ("Google-Extended", "entrenamiento", None),
    ("OAI-SearchBot", "búsqueda", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot"),
    ("Claude-SearchBot", "búsqueda", "Mozilla/5.0 (compatible; Claude-SearchBot/1.0; +https://www.anthropic.com)"),
    ("PerplexityBot", "búsqueda", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"),
    ("ChatGPT-User", "acción del usuario", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"),
    ("Claude-User", "acción del usuario", "Mozilla/5.0 (compatible; Claude-User/1.0; +https://www.anthropic.com)"),
    ("Perplexity-User", "acción del usuario", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)"),
]

VERDE, AMBAR, ROJO, NC = "verde", "ámbar", "rojo", "no comprobado"
ICONO = {VERDE: "🟢 verde", AMBAR: "🟡 ámbar", ROJO: "🔴 rojo", NC: "⚪ no comprobado"}
MAX_BYTES = 5_000_000

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"
RE_FECHA = re.compile(rf"\b(19|20)\d{{2}}\b|\b\d{{1,2}}/\d{{1,2}}/\d{{2,4}}\b|\b({MESES})\b", re.I)
RE_CIFRA_UNIDAD = re.compile(r"\d+(?:[.,]\d+)?\s?(%|€|\$|kg|km|cm|mm|kw|w|min|h|años|meses|días|horas|euros|usuarios|clientes|veces)(?!\w)", re.I)
RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
RE_FUENTE = re.compile(r"\b(según|fuente|datos de|estudio|informe|encuesta)\b", re.I)
RELLENO = ("en este artículo", "en este post", "hoy vamos", "hoy te", "bienvenid", "como todos sabemos", "a continuación")
RAIZ_SPA = re.compile(r"<div[^>]+id=[\"'](root|app|__next|__nuxt)[\"'][^>]*>\s*</div>", re.I)
MARCAS_SPA = ("__NEXT_DATA__", "ng-version", "data-reactroot", "window.__NUXT__")


# --- descarga ---------------------------------------------------------------------

def pedir(url, ua=NAVEGADOR, timeout=10):
    """Devuelve (código, cabeceras, texto). Código None si no hay respuesta."""
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,text/plain,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cuerpo = r.read(MAX_BYTES)
            return r.status, dict(r.headers), decodificar(cuerpo, r.headers.get_content_charset())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), ""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, {}, str(getattr(e, "reason", e))


def decodificar(cuerpo, charset):
    for c in (charset, "utf-8", "latin-1"):
        if not c:
            continue
        try:
            return cuerpo.decode(c)
        except (LookupError, UnicodeDecodeError):
            pass
    return cuerpo.decode("utf-8", "replace")


# --- robots.txt (RFC 9309, simplificado) -------------------------------------------

def parsear_robots(texto):
    grupos, actual = [], None
    for linea in texto.splitlines():
        linea = linea.split("#", 1)[0].strip()
        if ":" not in linea:
            continue
        clave, valor = (x.strip() for x in linea.split(":", 1))
        clave = clave.lower()
        if clave == "user-agent":
            if actual is None or actual["reglas"]:
                actual = {"agentes": [], "reglas": []}
                grupos.append(actual)
            actual["agentes"].append(valor)
        elif clave in ("allow", "disallow") and actual is not None:
            actual["reglas"].append((clave, valor))
    return grupos


def _patron(ruta):
    fin = ruta.endswith("$")
    cuerpo = re.escape(ruta[:-1] if fin else ruta).replace(r"\*", ".*")
    return re.compile(cuerpo + ("$" if fin else ""))


def evaluar_robots(grupos, token, ruta):
    """Decide si `token` puede rastrear `ruta`. Regla más larga gana; en empate, Allow."""
    propios = [g for g in grupos if any(a.split("/")[0].strip().lower() == token.lower() for a in g["agentes"])]
    usados = propios or [g for g in grupos if "*" in g["agentes"]]
    reglas = [r for g in usados for r in g["reglas"] if r[1]]  # Disallow vacío = todo permitido
    coincidencias = [(len(v), t == "allow", t, v) for t, v in reglas if _patron(v).match(ruta)]
    contradicciones = []
    if len(propios) > 1:
        contradicciones.append(f"{token} aparece en {len(propios)} grupos")
    rutas = {}
    for t, v in reglas:
        rutas.setdefault(v, set()).add(t)
    contradicciones += [f"Allow y Disallow a la vez para «{v}»" for v, ts in rutas.items() if len(ts) == 2]
    if not coincidencias:
        return {"permitido": True, "regla": None, "grupo": "propio" if propios else ("*" if usados else "ninguno"),
                "contradicciones": contradicciones}
    _, _, tipo, valor = max(coincidencias)
    return {"permitido": tipo == "allow", "regla": f"{tipo.capitalize()}: {valor}",
            "grupo": "propio" if propios else "*", "contradicciones": contradicciones}


# --- lectura del HTML --------------------------------------------------------------

class Lector(HTMLParser):
    OCULTOS = {"script", "style", "noscript", "template", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila, self.texto, self.encabezados, self.parrafos, self.jsonld = [], [], [], [], []
        self.scripts = self.imagenes = self.imagenes_sin_alt = 0
        self._h = self._p = self._ld = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("img",):
            self.imagenes += 1
            self.imagenes_sin_alt += not (a.get("alt") or "").strip()
            return
        if tag in ("br", "hr", "meta", "link", "input", "source"):
            return
        self.pila.append(tag)
        if tag == "script":
            self.scripts += 1
            if (a.get("type") or "").lower() == "application/ld+json":
                self._ld = []
        elif re.fullmatch(r"h[1-6]", tag):
            self._h = [int(tag[1]), []]
        elif tag == "p":
            self._p = [[], False]
        elif tag == "a" and self._p is not None and a.get("href"):
            self._p[1] = True

    def handle_endtag(self, tag):
        if tag not in self.pila:
            return
        while self.pila and self.pila.pop() != tag:
            pass
        if tag == "script" and self._ld is not None:
            self.jsonld.append("".join(self._ld)); self._ld = None
        elif re.fullmatch(r"h[1-6]", tag) and self._h:
            self.encabezados.append((self._h[0], " ".join("".join(self._h[1]).split()))); self._h = None
        elif tag == "p" and self._p is not None:
            self.parrafos.append({"texto": " ".join("".join(self._p[0]).split()), "enlace": self._p[1]}); self._p = None

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data); return
        if any(t in self.OCULTOS for t in self.pila):
            return
        self.texto.append(data)
        if self._h:
            self._h[1].append(data)
        if self._p is not None:
            self._p[0].append(data)


def plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


def palabras(texto):
    return re.findall(r"\w+", texto)


# --- pilares -----------------------------------------------------------------------

def pilar_renderizado(html, lector):
    n = len(palabras(" ".join(lector.texto)))
    spa = bool(RAIZ_SPA.search(html)) or any(m in html for m in MARCAS_SPA)
    base = f"Sin JavaScript se leen {plural(n, 'palabra', 'palabras')} y hay {plural(lector.scripts, 'script', 'scripts')}"
    if n < 150 and (spa or lector.scripts >= 3):
        color, ev = ROJO, base + (": contenedor vacío de aplicación JavaScript" if spa else ": casi todo llega con JavaScript")
    elif n < 300 or spa:
        color, ev = AMBAR, base + (" y señales de aplicación JavaScript" if spa else "")
    else:
        color, ev = VERDE, base
    return color, ev + ". Falta comparar con JavaScript en el navegador"


def tipos_jsonld(nodo, salida):
    if isinstance(nodo, list):
        for x in nodo:
            tipos_jsonld(x, salida)
    elif isinstance(nodo, dict):
        t = nodo.get("@type")
        for tipo in (t if isinstance(t, list) else [t] if t else []):
            salida.append((str(tipo), nodo))
        for v in nodo.values():
            if isinstance(v, (dict, list)):
                tipos_jsonld(v, salida)


def pilar_schema(lector):
    nodos, invalidos = [], 0
    for bloque in lector.jsonld:
        try:
            tipos_jsonld(json.loads(bloque), nodos)
        except json.JSONDecodeError:
            invalidos += 1
    tipos = sorted({t for t, _ in nodos})
    if not nodos:
        return ROJO, ("JSON-LD no válido" if invalidos else "Sin JSON-LD") + " en la página", tipos
    faltan = []
    for t, n in nodos:
        if t == "Organization":
            faltan += [f"Organization.{c}" for c in ("name", "url", "logo", "sameAs") if not n.get(c)]
        if t == "Product":
            ofertas = n.get("offers") or {}
            ofertas = ofertas[0] if isinstance(ofertas, list) and ofertas else ofertas
            if not ofertas:
                faltan.append("Product.offers")
            else:
                faltan += [f"offers.{c}" for c in ("price", "priceCurrency", "availability") if not ofertas.get(c)]
    ev = "Tipos: " + ", ".join(tipos)
    if invalidos:
        ev += f"; {invalidos} bloque(s) JSON-LD no válidos"
    if faltan:
        ev += "; faltan " + ", ".join(sorted(set(faltan)))
    color = VERDE if not faltan and not invalidos and "Organization" in tipos else AMBAR
    if color == AMBAR and "Organization" not in tipos:
        ev += "; sin Organization"
    return color, ev, tipos


def pilar_bots(url, robots_codigo, robots_texto, timeout):
    ruta = urllib.parse.urlsplit(url).path or "/"
    grupos = parsear_robots(robots_texto) if robots_codigo == 200 else []
    base, _, _ = pedir(url, NAVEGADOR, timeout)
    filas, avisos = [], []
    for token, tipo, ua in BOTS:
        r = evaluar_robots(grupos, token, ruta)
        codigo = pedir(url, ua, timeout)[0] if ua else None
        bloqueo_http = ua is not None and base == 200 and (codigo is None or codigo >= 400)
        filas.append({"bot": token, "tipo": tipo, "robots": "permitido" if r["permitido"] else "bloqueado",
                      "regla": r["regla"], "http": codigo if ua else "solo token", "bloqueo_http": bloqueo_http,
                      "contradicciones": r["contradicciones"]})
        if not r["permitido"]:
            avisos.append(f"{token} bloqueado en robots.txt")
        if bloqueo_http:
            avisos.append(f"{token} recibe un {codigo}" if codigo else f"{token} no recibe respuesta")
        avisos += [f"robots.txt contradictorio para {token}: {c}" for c in r["contradicciones"]]
    busqueda = [f for f in filas if f["tipo"] == "búsqueda"]
    if robots_codigo not in (200, 404):
        avisos.insert(0, f"robots.txt responde {robots_codigo}")
    if all(f["robots"] == "bloqueado" or f["bloqueo_http"] for f in busqueda):
        color = ROJO
    elif avisos:
        color = AMBAR
    else:
        color = VERDE
    if not avisos:
        ev = "Los 9 bots de IA pueden entrar" + ("" if robots_codigo == 200 else " (no hay robots.txt)")
    else:
        ev = "; ".join(dict.fromkeys(avisos[:4])) + (f" y {plural(len(avisos) - 4, 'aviso', 'avisos')} más" if len(avisos) > 4 else "")
    return color, ev, filas


def pilar_densidad(html, lector):
    texto = " ".join(lector.texto)
    n = len(palabras(texto))
    ratio = len(texto.strip()) / max(len(html), 1)
    ev = f"{plural(n, 'palabra', 'palabras')}; el texto es el {ratio:.0%} del HTML; {plural(lector.imagenes, 'imagen', 'imágenes')}"
    if lector.imagenes_sin_alt:
        ev += f", {lector.imagenes_sin_alt} sin alt"
    if n >= 300 and ratio >= 0.10:
        return VERDE, ev
    if n >= 150 or ratio >= 0.05:
        return AMBAR, ev
    return ROJO, ev


def pilar_encabezados(lector):
    hs = lector.encabezados
    h1 = [t for n, t in hs if n == 1]
    saltos = [f"H{a}→H{b}" for (a, _), (b, _) in zip(hs, hs[1:]) if b > a + 1]
    vacios = sum(1 for _, t in hs if not t)
    h2 = sum(1 for n, _ in hs if n == 2)
    ev = f"{len(h1)} H1, {h2} H2"
    if saltos:
        ev += "; saltos de nivel: " + ", ".join(dict.fromkeys(saltos))
    if vacios:
        ev += f"; {plural(vacios, 'encabezado vacío', 'encabezados vacíos')}"
    if not h1:
        return ROJO, ev
    if len(h1) > 1 or saltos or vacios or h2 == 0:
        return AMBAR, ev
    return VERDE, ev + f"; H1: «{h1[0][:60]}»"


def pilar_llms(url, timeout):
    p = urllib.parse.urlsplit(url)
    codigo, cab, texto = pedir(f"{p.scheme}://{p.netloc}/llms.txt", NAVEGADOR, timeout)
    tipo = (cab.get("Content-Type") or cab.get("content-type") or "").lower()
    if codigo == 200 and "html" not in tipo and texto.lstrip().startswith("#"):
        return VERDE, f"Existe /llms.txt ({len(texto.splitlines())} líneas). Revisa si aporta algo"
    if codigo == 200:
        return AMBAR, "/llms.txt responde 200 pero no es un llms.txt (parece HTML)"
    return AMBAR, "No existe; su ausencia no es un fallo"


def es_citable(p):
    t = p["texto"]
    n = len(palabras(t))
    if not 40 <= n <= 150:
        return None
    primera = re.split(r"(?<=[.!?])\s", t, maxsplit=1)[0]
    responde = len(palabras(primera)) <= 35 and not primera.rstrip().endswith("?") \
        and not t.lower().startswith(RELLENO)
    cifra = bool(RE_CIFRA_UNIDAD.search(t)) or len(RE_NUMERO.findall(t)) >= 2
    fecha = bool(RE_FECHA.search(t))
    fuente = p["enlace"] or bool(RE_FUENTE.search(t))
    return {"palabras": n, "responde_primero": responde, "cifra": cifra, "fecha": fecha, "fuente": fuente,
            "citable": responde and cifra and fecha, "inicio": t[:80]}


def pilar_citabilidad(lector):
    evaluados = [e for e in (es_citable(p) for p in lector.parrafos) if e]
    citables = [e for e in evaluados if e["citable"]]
    con_fuente = sum(1 for e in citables if e["fuente"])
    casi = [e for e in evaluados if e["cifra"] and not e["citable"]]
    ev = (f"{len(citables)} de {len(lector.parrafos)} párrafos responden primero con cifra y fecha "
          f"({con_fuente} con fuente)")
    if casi:
        ev += f"; {len(casi)} tienen cifra pero les falta fecha o respuesta directa"
    ev += ". Heurística: lee los pasajes"
    color = VERDE if len(citables) >= 2 else AMBAR if citables or casi else ROJO
    return color, ev, evaluados


# --- informe -----------------------------------------------------------------------

def auditar(url, timeout=10):
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise ValueError("La URL tiene que empezar por http:// o https://")
    codigo, _, html = pedir(url, NAVEGADOR, timeout)
    p = urllib.parse.urlsplit(url)
    informe = {"url": url, "web": p.netloc, "fecha": date.today().isoformat(), "codigo": codigo,
               "pilares": [], "no_comprobado": [], "detalle": {}}
    if codigo != 200:
        informe["no_comprobado"].append(f"La página responde {codigo or 'sin respuesta'}: no se puede auditar")
        informe["pilares"] = [{"pilar": n, "color": NC, "evidencia": f"La página responde {codigo}"} for n in NOMBRES]
        return informe
    lector = Lector()
    lector.feed(html)
    r_codigo, _, r_texto = pedir(f"{p.scheme}://{p.netloc}/robots.txt", NAVEGADOR, timeout)

    c1, e1 = pilar_renderizado(html, lector)
    c2, e2, tipos = pilar_schema(lector)
    c3, e3, bots = pilar_bots(url, r_codigo, r_texto, timeout)
    c4, e4 = pilar_densidad(html, lector)
    c5, e5 = pilar_encabezados(lector)
    c6, e6 = pilar_llms(url, timeout)
    c7, e7, pasajes = pilar_citabilidad(lector)
    for nombre, c, e in zip(NOMBRES, (c1, c2, c3, c4, c5, c6, c7), (e1, e2, e3, e4, e5, e6, e7)):
        informe["pilares"].append({"pilar": nombre, "color": c, "evidencia": e})
    informe["no_comprobado"] += [
        "Texto con JavaScript: compáralo en el navegador (pilar 1)",
        "Validez del schema en el validador de schema.org y en la prueba de resultados enriquecidos (pilar 2)",
        "Bots reales: el script se hace pasar por ellos; los logs dicen quién vino de verdad (pilar 3)",
    ]
    if r_codigo != 200:
        informe["no_comprobado"].append(f"robots.txt responde {r_codigo}: se asume que todo está permitido")
    informe["detalle"] = {"robots_txt": r_codigo, "bots": bots, "schema": tipos,
                          "encabezados": lector.encabezados[:30], "pasajes": pasajes[:30]}
    return informe


NOMBRES = ["1. Renderizado", "2. Schema", "3. Acceso de bots", "4. Densidad", "5. Encabezados",
           "6. llms.txt", "7. Citabilidad"]


def a_markdown(inf):
    cuenta = {c: sum(1 for p in inf["pilares"] if p["color"] == c) for c in (VERDE, AMBAR, ROJO)}
    lineas = [f"# Semáforo GEO · {inf['web']}", "", f"7 pilares · {inf['fecha']} · {inf['url']}", "",
              "| Pilar | Color | Evidencia |", "|---|---|---|"]
    lineas += [f"| {p['pilar']} | {ICONO[p['color']]} | {p['evidencia'].replace('|', '/')} |" for p in inf["pilares"]]
    lineas += ["", f"**Recuento:** {cuenta[VERDE]} {'verde' if cuenta[VERDE] == 1 else 'verdes'} · "
               f"{cuenta[AMBAR]} ámbar · {cuenta[ROJO]} {'rojo' if cuenta[ROJO] == 1 else 'rojos'}", "",
               "## No comprobado", ""]
    lineas += [f"- {x}" for x in inf["no_comprobado"]]
    bots = inf["detalle"].get("bots")
    if bots:
        lineas += ["", "## Bots, uno a uno", "", "| Bot | Tipo | robots.txt | Regla | HTTP |", "|---|---|---|---|---|"]
        lineas += [f"| {b['bot']} | {b['tipo']} | {b['robots']} | {b['regla'] or '—'} | {b['http']} |" for b in bots]
    return "\n".join(lineas) + "\n"


def main(argv=None):
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Semáforo GEO de 7 pilares para una URL")
    ap.add_argument("url")
    ap.add_argument("--salida", help="archivo .md; al lado se guarda el .json con el mismo nombre")
    ap.add_argument("--formato", choices=["md", "json"], default="md", help="formato por pantalla")
    ap.add_argument("--timeout", type=float, default=10)
    a = ap.parse_args(argv)
    try:
        inf = auditar(a.url, a.timeout)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    md, js = a_markdown(inf), json.dumps(inf, ensure_ascii=False, indent=2)
    if a.salida:
        destino = Path(a.salida)
        destino.write_text(md, encoding="utf-8", newline="\n")
        destino.with_suffix(".json").write_text(js + "\n", encoding="utf-8", newline="\n")
        print(f"Escrito {destino} y {destino.with_suffix('.json')}")
    else:
        print(js if a.formato == "json" else md)
    return 0 if inf["codigo"] == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
