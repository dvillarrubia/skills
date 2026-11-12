"""Estilometría: convierte «cómo escribe la marca» en números que se pueden comparar con un borrador."""
import re, statistics
from .texto import frases, sin_markdown, plano

MEDIDAS = {
    "palabras_por_frase": "media de palabras por frase",
    "frases_cortas_pct": "% de frases de 8 palabras o menos",
    "frases_largas_pct": "% de frases de 30 palabras o más",
    "palabras_por_parrafo": "media de palabras por párrafo",
    "segunda_persona_por_100": "tuteo (tú, te, ti, tu, tus) por cada 100 palabras",
    "nosotros_por_100": "primera persona del plural (nosotros, nuestro, nos) por cada 100 palabras",
    "preguntas_pct": "% de frases que son preguntas",
    "exclamaciones_pct": "% de frases con exclamación",
    "negritas_por_100": "negritas por cada 100 palabras",
    "encabezados_mayusculas_pct": "% de encabezados con Mayúscula En Cada Palabra",
}

# Fórmulas que delatan texto genérico. La lista es editable: es una decisión editorial, no del modelo.
CLICHES = ["en el mundo de", "en la actualidad", "hoy en día", "sin lugar a dudas", "sin duda alguna", "no es solo",
           "no se trata solo de", "sumérgete", "sumergirnos", "descubre el fascinante", "en resumen", "en conclusión",
           "en definitiva", "cabe destacar", "es importante destacar", "es importante tener en cuenta", "a la hora de",
           "juega un papel", "marca la diferencia", "lleva tu", "al siguiente nivel", "un viaje", "todo lo que necesitas saber",
           "la clave está en", "ni más ni menos", "como ya sabrás", "amante del café", "experiencia única", "auténtica experiencia"]


def medir(md):
    fs = frases(md)
    largos = [len(f.split()) for f in fs] or [0]
    texto = sin_markdown(md)
    palabras = max(1, len(texto.split()))
    parrafos = [p for p in re.split(r"\n\s*\n", md) if len(p.split()) >= 8 and not p.lstrip().startswith(("#", "|", "-"))]
    cabeceras = re.findall(r"^#{2,3}\s+(.+)$", md, flags=re.M)

    def titulo(h):
        ps = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{4,}", h)]
        return len(ps) >= 3 and sum(w[0].isupper() for w in ps) / len(ps) >= 0.7

    bajo = " " + plano(texto) + " "
    cuenta = lambda patron: len(re.findall(patron, bajo))
    return {
        "palabras_por_frase": round(statistics.mean(largos), 1),
        "frases_cortas_pct": round(100 * sum(n <= 8 for n in largos) / len(largos), 1),
        "frases_largas_pct": round(100 * sum(n >= 30 for n in largos) / len(largos), 1),
        "palabras_por_parrafo": round(statistics.mean(len(p.split()) for p in parrafos), 1) if parrafos else 0,
        "segunda_persona_por_100": round(100 * cuenta(r"\b(tu|tus|te|ti|contigo)\b") / palabras, 2),
        "nosotros_por_100": round(100 * cuenta(r"\b(nosotros|nuestr[oa]s?|nos)\b") / palabras, 2),
        "preguntas_pct": round(100 * sum("?" in f for f in fs) / max(1, len(fs)), 1),
        "exclamaciones_pct": round(100 * sum("!" in f for f in fs) / max(1, len(fs)), 1),
        "negritas_por_100": round(100 * len(re.findall(r"\*\*[^*]+\*\*", md)) / palabras, 2),
        "encabezados_mayusculas_pct": round(100 * sum(map(titulo, cabeceras)) / len(cabeceras), 1) if cabeceras else 0,
    }


def rangos(lista_medidas, tolerancia):
    """Rango de la marca por medida: del mínimo al máximo entre sus textos, ensanchado por una tolerancia."""
    r = {}
    for k in MEDIDAS:
        vs = [m[k] for m in lista_medidas]
        margen = max((max(vs) - min(vs)) * tolerancia, abs(statistics.mean(vs)) * tolerancia, 0.5)
        r[k] = (round(max(0, min(vs) - margen), 2), round(max(vs) + margen, 2))
    return r


def desviaciones(medidas, rango, ignorar=()):
    fuera = []
    for k, (lo, hi) in rango.items():
        if k not in ignorar and not lo <= medidas[k] <= hi:
            fuera.append(f"{MEDIDAS[k]}: el texto tiene {medidas[k]} y la marca escribe entre {lo} y {hi}")
    return fuera


# Abreviaturas tras las que una minúscula es correcta («etc. y», «p. ej. el»).
ABREVIATURAS = {"etc", "ej", "p", "aprox", "pág", "págs", "núm", "art", "vs", "cf", "máx", "mín", "tel", "nº", "n"}


def ortografia(md, nombres_propios=()):
    """Mayúsculas según la ortografía del español: inicial de encabezado, de párrafo y tras punto, y nombres propios.
    Devuelve la lista de fallos, cada uno con el fragmento literal."""
    fallos = []
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    inicial = lambda s: re.match(r"[\s¿¡«\"'(*_\[]*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", s)
    for h in re.findall(r"^#{1,6}\s+(.+)$", md, flags=re.M):
        m = inicial(h)
        if m and m.group(1).islower():
            fallos.append(f"el encabezado «{h.strip()}» empieza en minúscula; lleva mayúscula inicial")
    anterior = ""
    for linea in md.splitlines():
        abre_parrafo, anterior = not anterior.strip(), linea     # una línea que sigue a otra es el mismo párrafo
        if not linea.strip() or linea.lstrip().startswith(("#", "|", "-", "*", ">")) or re.match(r"\s*\d+[.)]\s", linea):
            continue
        limpia = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", linea)
        m = inicial(limpia)
        if abre_parrafo and m and m.group(1).islower() and not re.match(r"\s*https?://", limpia):
            fallos.append(f"el párrafo «{limpia.strip()[:50]}…» empieza en minúscula")
        for m in re.finditer(r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñº]+)([.!?…])[»\"')*_]*\s+(?=[¿¡«\"'(*_]*[a-záéíóúüñ])", limpia):
            if m.group(2) == "." and m.group(1).lower() in ABREVIATURAS:
                continue
            trozo = limpia[m.start():m.end() + 25].strip()
            fallos.append(f"minúscula tras «{m.group(2)}» en «{trozo}»; la frase siguiente empieza con mayúscula")
    for nombre in nombres_propios:
        if nombre and nombre[0].isupper():
            for m in re.finditer(rf"(?<![\w./@-]){re.escape(nombre.lower())}(?![\w.-]*\.[a-z]{{2,}})(?![\w-])", md):
                fallos.append(f"el nombre propio «{nombre}» aparece en minúscula («{md[max(0, m.start() - 15):m.end() + 10].strip()}»)")
    return list(dict.fromkeys(fallos))


def cliches(md, extra=()):
    bajo = plano(md)
    return [c for c in list(CLICHES) + list(extra) if plano(c) in bajo]
