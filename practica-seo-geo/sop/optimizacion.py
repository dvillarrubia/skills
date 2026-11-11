"""Controles de optimización para Google y para asistentes de IA. Son reglas legibles, no la opinión de un modelo."""
import re
import urllib.robotparser
import requests
from .texto import tokens, solape, secciones, primera_frase, sin_markdown, plano

ROBOTS_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Google-Extended", "CCBot"]
REFERENCIAL = ("esto ", "eso ", "esta ", "este ", "estos ", "estas ", "ello ", "como hemos visto", "como vimos",
               "como decíamos", "lo anterior", "por eso", "además,", "también ", "así que", "dicho esto", "en este sentido")
UNIDADES = r"(?:%|g\b|gr\b|gramos?|kg|ml|l\b|litros?|°c|ºc|grados|minutos?|min\b|segundos?|s\b|horas?|h\b|días?|semanas?|" \
           r"meses|años?|tazas?|cucharadas?|micras|mm|cm|euros?|€|puntos|bares?|veces|x\b)"


def _fila(bloque, control, ok, valor, detalle=""):
    return {"bloque": bloque, "control": control, "resultado": "sí" if ok else "NO", "valor": valor, "detalle": detalle}


def controles(md, titulo, descripcion, n_h1, ctx):
    """ctx: principal, consultas_grupo, preguntas_google, preguntas_asistentes, fan_out, entidades, dominio."""
    texto = sin_markdown(md)
    palabras = texto.split()
    secs = secciones(md)
    cabeceras = [h for h, _ in secs] + re.findall(r"^###\s+(.+)$", md, flags=re.M)
    aperturas = [(h, primera_frase(cuerpo)) for h, cuerpo in secs]
    f = []

    # --- Google ---
    f.append(_fila("Google", "Título de 60 caracteres o menos con la consulta principal",
                   0 < len(titulo) <= 60 and solape(ctx["principal"], titulo) >= 0.99, f"{len(titulo)} car.", titulo))
    f.append(_fila("Google", "Descripción de 135 a 145 caracteres", 135 <= len(descripcion) <= 145, f"{len(descripcion)} car."))
    f.append(_fila("Google", "Un único H1", n_h1 == 1, n_h1))
    f.append(_fila("Google", "Consulta principal en las primeras 100 palabras",
                   solape(ctx["principal"], " ".join(palabras[:100])) >= 0.99, f"{solape(ctx['principal'], ' '.join(palabras[:100])):.0%}"))
    cub = [q for q in ctx["consultas_grupo"] if solape(q, texto) >= 0.99]
    f.append(_fila("Google", "Consultas del grupo presentes en el texto", len(cub) == len(ctx["consultas_grupo"]),
                   f"{len(cub)} de {len(ctx['consultas_grupo'])}", "faltan: " + "; ".join(q for q in ctx["consultas_grupo"] if q not in cub)))
    pg = [q for q in ctx["preguntas_google"] if any(solape(q, h) >= 0.6 for h in cabeceras)]
    f.append(_fila("Google", "Preguntas que muestra Google con encabezado propio", len(pg) >= 0.6 * len(ctx["preguntas_google"]) if ctx["preguntas_google"] else True,
                   f"{len(pg)} de {len(ctx['preguntas_google'])}", "sin encabezado: " + "; ".join(q for q in ctx["preguntas_google"] if q not in pg)[:300]))
    internos = len(re.findall(r"\]\((?:https?://(?:www\.)?" + re.escape(ctx["dominio"]) + r"|/)[^)]*\)", md))
    f.append(_fila("Google", "Dos o más enlaces internos", internos >= 2, internos))
    f.append(_fila("Google", "Alguna tabla o lista que ordene la decisión", bool(re.search(r"^\s*(\||[-*] |\d+\. )", md, flags=re.M)), ""))

    # --- Asistentes de IA ---
    directas = [h for h, fr in aperturas if fr and len(fr.split()) <= 30 and not plano(fr).startswith(tuple(map(plano, REFERENCIAL)))]
    f.append(_fila("IA", "Secciones que abren con la respuesta (frase de 30 palabras o menos, sin remitir a lo anterior)",
                   bool(secs) and len(directas) >= 0.8 * len(secs), f"{len(directas)} de {len(secs)}",
                   "revisar: " + "; ".join(h for h, _ in aperturas if h not in directas)[:300]))
    con_sujeto = [h for h, fr in aperturas if any(plano(e) in plano(fr) for e in ctx["entidades"])]
    f.append(_fila("IA", "Primera frase de cada sección nombra la entidad de la que habla", bool(secs) and len(con_sujeto) >= 0.8 * len(secs),
                   f"{len(con_sujeto)} de {len(secs)}", "revisar: " + "; ".join(h for h, _ in aperturas if h not in con_sujeto)[:300]))
    pa = [q for q in ctx["preguntas_asistentes"] if any(solape(q, h + " " + fr) >= 0.5 for h, fr in aperturas)]
    f.append(_fila("IA", "Preguntas hechas a los asistentes con un pasaje que las responde", len(pa) == len(ctx["preguntas_asistentes"]),
                   f"{len(pa)} de {len(ctx['preguntas_asistentes'])}", "sin pasaje: " + "; ".join(q for q in ctx["preguntas_asistentes"] if q not in pa)))
    fo = [q for q in ctx["fan_out"] if solape(q, texto) >= 0.8]
    f.append(_fila("IA", "Búsquedas que lanza el asistente (fan-out) cubiertas por el texto", len(fo) >= 0.7 * len(ctx["fan_out"]) if ctx["fan_out"] else True,
                   f"{len(fo)} de {len(ctx['fan_out'])}", "sin cubrir: " + "; ".join(q for q in ctx["fan_out"] if q not in fo)[:300]))
    cifras = re.findall(r"(?<![\w.,])(\d+(?:[.,]\d+)?)(\s?(?:-|–|a)\s?\d+(?:[.,]\d+)?)?\s?(" + UNIDADES + r")?", plano(texto))
    cifras = [x for x in cifras if not (len(x[0]) == 4 and x[0][:2] in ("19", "20"))]          # los años no llevan unidad
    con_unidad = sum(1 for x in cifras if x[2])
    f.append(_fila("IA", "Cifras acompañadas de su unidad", not cifras or con_unidad >= 0.7 * len(cifras), f"{con_unidad} de {len(cifras)}"))
    medida = [h for h, cuerpo in secs if 40 <= len(sin_markdown(cuerpo).split()) <= 300]
    f.append(_fila("IA", "Secciones de 40 a 300 palabras, extraíbles como pasaje", bool(secs) and len(medida) >= 0.8 * len(secs),
                   f"{len(medida)} de {len(secs)}"))
    return f


def tecnico(url, ficha, datos, html):
    """Controles sobre la página publicada: lo que un rastreador de IA encuentra sin ejecutar JavaScript."""
    f = []
    base = re.match(r"https?://[^/]+", url).group(0)
    try:
        r = requests.get(base + "/robots.txt", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        bloqueados = [b for b in ROBOTS_IA if not rp.can_fetch(b, url)]
        f.append(_fila("Técnico", "robots.txt permite el acceso a los rastreadores de IA", not bloqueados,
                       f"{len(ROBOTS_IA) - len(bloqueados)} de {len(ROBOTS_IA)}", "bloqueados: " + ", ".join(bloqueados) if bloqueados else "; ".join(ROBOTS_IA)))
    except requests.RequestException as e:
        f.append(_fila("Técnico", "robots.txt permite el acceso a los rastreadores de IA", False, "no evaluable", type(e).__name__))
    f.append(_fila("Técnico", "Contenido principal presente en el HTML sin ejecutar JavaScript (300 palabras o más)",
                   int(datos.get("palabras") or 0) >= 300, f"{datos.get('palabras')} palabras"))
    f.append(_fila("Técnico", "Datos estructurados en el HTML inicial", bool(datos.get("datos_estructurados")), datos.get("datos_estructurados") or "ninguno"))
    canon = (datos.get("canonical") or "").rstrip("/")
    f.append(_fila("Técnico", "Canonical apunta a la propia URL", canon in (url.rstrip("/"), (ficha.get("url_final") or "").rstrip("/")), canon or "sin canonical"))
    f.append(_fila("Técnico", "Sin noindex", "noindex" not in (datos.get("robots") or "").lower(), datos.get("robots") or "sin meta robots"))
    return f
