"""Tratamiento de texto sin modelo: tokens, frases, secciones. Todo lo que aquí se mide es reproducible."""
import re, unicodedata

VACIAS = set("a al algo como con cual cuando de del desde donde el ella ellos en entre era es esa ese eso esta este esto "
             "ha hay la las le lo los mas me mi muy no nos o para pero por que qué se si sin sobre su sus te tu tus un una "
             "uno unas unos y ya yo cómo cuál cuánto cuándo dónde quién puedo debo hago estoy".split())


def plano(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def tokens(s):
    return [t for t in re.findall(r"[a-z0-9ñ]+", plano(s)) if t not in {plano(v) for v in VACIAS} and len(t) > 1]


def solape(pregunta, texto):
    """Proporción de los términos con significado de «pregunta» que aparecen en «texto»."""
    a, b = set(tokens(pregunta)), set(tokens(texto))
    return len(a & b) / len(a) if a else 0.0


def sin_markdown(md):
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    return re.sub(r"[*_`>#|]", " ", md)


def frases(texto):
    trozos = re.split(r"(?<=[.!?…])\s+|\n+", sin_markdown(texto))
    return [f.strip() for f in trozos if len(f.split()) >= 3]


def secciones(md):
    """Lista de (encabezado, cuerpo) por cada H2 del Markdown."""
    partes = re.split(r"^##\s+(.+)$", md, flags=re.M)
    return [(partes[i].strip(), partes[i + 1].strip()) for i in range(1, len(partes) - 1, 2)]


def primera_frase(cuerpo):
    f = frases(re.sub(r"^#+\s.*$", "", cuerpo, flags=re.M))
    return f[0] if f else ""
