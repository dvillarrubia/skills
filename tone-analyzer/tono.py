#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tono.py — Analizador de tono a partir de 10-20 URLs.

Scrapea el contenido de un bloque de URLs, lo limpia a prosa y calcula
metricas estilometricas DETERMINISTAS (longitud de frase, persona gramatical,
tratamiento tu/usted, riqueza lexica, puntuacion, legibilidad, lexico
caracteristico...). No "adivina" el tono: mide senales objetivas y recoge
ejemplos reales. La interpretacion cualitativa la hace Claude leyendo el JSON.

Modos:
  scrape   descarga y limpia el texto de las URLs -> corpus
  metrics  calcula metricas sobre un corpus ya scrapeado
  full     scrape + metrics en una sola pasada (lo habitual)

Uso:
  python tono.py full urls.txt --out ./salida --name cliente-x
  python tono.py full https://a.com https://a.com/sobre-mi --out ./salida
  python tono.py scrape urls.txt --out ./salida --delay 1.0
  python tono.py metrics ./salida/corpus.json

Dependencias: requests, beautifulsoup4, lxml (ya usadas por geo-auditor).
"""

import sys
import os
import re
import json
import time
import math
import argparse
from collections import Counter
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: faltan paquetes. Instala con: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

# Etiquetas que casi nunca contienen prosa de marca
STRIP_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form",
              "noscript", "svg", "button", "iframe"]

# Contenedores de contenido principal, por orden de preferencia
MAIN_SELECTORS = ["article", "main", '[role="main"]', ".post-content",
                  ".entry-content", ".article-body", "#content", ".content"]


def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Elimina lineas muy cortas tipo menu (1-2 palabras) sueltas
    lineas = []
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            lineas.append("")
            continue
        lineas.append(ln)
    return "\n".join(lineas).strip()


def fetch_one(url: str, timeout: int = 30) -> dict:
    """Descarga una URL y extrae el texto de prosa principal."""
    out = {"url": url, "ok": False, "title": None, "text": "",
           "word_count": 0, "status": None, "error": None}
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        out["status"] = r.status_code
        if r.status_code != 200:
            out["error"] = f"HTTP {r.status_code}"
            return out

        r.encoding = r.apparent_encoding or r.encoding
        soup = BeautifulSoup(r.text, "lxml")

        t = soup.find("title")
        out["title"] = t.get_text(strip=True) if t else None

        for tag in soup(STRIP_TAGS):
            tag.decompose()

        # Busca el contenedor principal; si no, usa el body
        container = None
        for sel in MAIN_SELECTORS:
            try:
                found = soup.select_one(sel)
            except Exception:
                found = None
            if found and len(found.get_text(strip=True)) > 200:
                container = found
                break
        if container is None:
            container = soup.body or soup

        # Reconstruye parrafos a partir de bloques de prosa
        bloques = []
        for el in container.find_all(["p", "li", "h1", "h2", "h3", "h4",
                                      "blockquote", "figcaption"]):
            txt = el.get_text(" ", strip=True)
            # Descarta migas, menus y textos sin prosa real
            if len(txt) < 25:
                continue
            if txt.count("|") >= 3 or txt.count("·") >= 3:
                continue
            bloques.append(txt)

        texto = "\n\n".join(bloques)
        if len(texto) < 200:
            # Fallback: todo el texto del contenedor
            texto = container.get_text(" ", strip=True)

        texto = _clean_text(texto)
        out["text"] = texto
        out["word_count"] = len(texto.split())
        out["ok"] = out["word_count"] >= 20
        if not out["ok"]:
            out["error"] = "contenido insuficiente"
    except requests.exceptions.Timeout:
        out["error"] = f"timeout tras {timeout}s"
    except requests.exceptions.RequestException as e:
        out["error"] = f"error de red: {e}"
    except Exception as e:  # noqa: BLE001
        out["error"] = f"error inesperado: {e}"
    return out


def read_urls(source: list) -> list:
    """Admite un .txt (una URL por linea, # comentario) o URLs sueltas."""
    urls = []
    if len(source) == 1 and os.path.isfile(source[0]):
        with open(source[0], "r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    urls.append(ln)
    else:
        urls = list(source)
    # Dedup conservando orden
    seen, clean = set(), []
    for u in urls:
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        if u not in seen:
            seen.add(u)
            clean.append(u)
    return clean


def scrape(urls: list, delay: float = 1.0, timeout: int = 30) -> dict:
    docs = []
    for i, u in enumerate(urls, 1):
        if i > 1 and delay > 0:
            time.sleep(delay)
        print(f"  [{i}/{len(urls)}] {u}", file=sys.stderr)
        doc = fetch_one(u, timeout=timeout)
        docs.append(doc)
    ok = [d for d in docs if d["ok"]]
    return {
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "requested": len(urls),
        "ok": len(ok),
        "failed": len(urls) - len(ok),
        "domains": sorted({urlparse(d["url"]).netloc for d in ok}),
        "docs": docs,
    }


# ---------------------------------------------------------------------------
# Metricas estilometricas
# ---------------------------------------------------------------------------

STOPWORDS = set("""
a al algo algunas algunos ante antes como con contra cual cuando de del desde donde dos e el
ella ellas ellos en entre era erais eramos eran eres es esa esas ese eso esos esta estaba
estaban estamos estan estar este esto estos estoy ha habia han hasta hay la las le les lo los
mas me mi mientras muy nada ni no nos o os para pero poco por porque que quien se sea sean si
sin sobre solo son su sus tambien tan tanto te tu tus un una uno unas unos vosotras vosotros y
ya the a an and or but of to in on for with at by from is are was were be been this that it its
""".split())

PRON = {
    "yo_sg": r"\b(yo|me|mi|mis|conmigo|m[ií]a?s?)\b",
    "nos_pl": r"\b(nosotros|nosotras|nos|nuestro|nuestra|nuestros|nuestras)\b",
    "tu_2s": r"\b(t[uú]|te|tus|ti|contigo|tuyos?|tuyas?)\b",
    "usted_2": r"\b(usted|ustedes|le|les|su|sus|suyo|suya)\b",
    "vos_2p": r"\b(vosotros|vosotras|os|vuestro|vuestra|vuestros|vuestras)\b",
}

FORMAL_CONNECTORS = [
    "asimismo", "no obstante", "por consiguiente", "en consecuencia",
    "cabe destacar", "en relacion", "en relación", "dicho esto",
    "por tanto", "por lo tanto", "sin embargo", "en definitiva",
]
CTA_VERBS = [
    "descubre", "descarga", "solicita", "contacta", "reserva", "apuntate",
    "apúntate", "empieza", "prueba", "compra", "registrate", "regístrate",
    "consigue", "unete", "únete", "pide", "llama", "escribenos", "escríbenos",
    "agenda", "suscribete", "suscríbete",
]

EMOJI_RE = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF" "\U0001F1E6-\U0001F1FF" "←-⇿" "]",
    flags=re.UNICODE,
)
WORD_RE = re.compile(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", re.UNICODE)


def split_sentences(text: str) -> list:
    text = text.replace("\n", " ")
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def count_syllables_es(word: str) -> int:
    w = word.lower()
    groups = re.findall(r"[aeiouáéíóúü]+", w)
    return max(1, len(groups))


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _stdev(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def ngrams(tokens, n):
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def metrics(corpus: dict) -> dict:
    docs = [d for d in corpus.get("docs", []) if d.get("ok")]
    full = "\n\n".join(d["text"] for d in docs)
    low = full.lower()

    sentences = split_sentences(full)
    sent_lens = [len(s.split()) for s in sentences]
    tokens_all = WORD_RE.findall(low)
    content = [t for t in tokens_all if t not in STOPWORDS and len(t) > 2]
    total_words = len(tokens_all)

    # Parrafos
    paras = [p for p in re.split(r"\n{2,}", full) if p.strip()]
    para_lens = [len(p.split()) for p in paras]

    # Persona gramatical (conteo por 1000 palabras)
    def per_1k(pat):
        c = len(re.findall(pat, low))
        return round(c / max(total_words, 1) * 1000, 2)

    persona = {k: per_1k(v) for k, v in PRON.items()}

    # Puntuacion / 1000 palabras
    def punct_1k(ch):
        return round(full.count(ch) / max(total_words, 1) * 1000, 2)

    # Legibilidad Fernandez-Huerta (adaptacion espanola de Flesch)
    syll = sum(count_syllables_es(t) for t in tokens_all)
    n_sent = max(len(sentences), 1)
    fh = 206.84 - 60 * (syll / max(total_words, 1)) - 1.02 * (total_words / n_sent)

    # Lexico
    freq = Counter(content)
    bi = Counter(ngrams([t for t in tokens_all if t not in STOPWORDS], 2))
    tri = Counter(ngrams([t for t in tokens_all if t not in STOPWORDS], 3))

    short = sum(1 for l in sent_lens if l < 10)
    medium = sum(1 for l in sent_lens if 10 <= l <= 25)
    long = sum(1 for l in sent_lens if l > 25)

    # Ejemplos reales (para que Claude cite texto autentico, no inventado)
    by_len = sorted(sentences, key=lambda s: len(s.split()))
    questions = [s for s in sentences if s.rstrip().endswith("?")]
    exclam = [s for s in sentences if s.rstrip().endswith("!")]
    openers = [d["text"].split("\n")[0][:300] for d in docs if d["text"]]

    formal_hits = sum(low.count(c) for c in FORMAL_CONNECTORS)
    cta_hits = sum(len(re.findall(r"\b" + re.escape(v) + r"\b", low)) for v in CTA_VERBS)

    return {
        "resumen": {
            "documentos": len(docs),
            "dominios": corpus.get("domains", []),
            "palabras_totales": total_words,
            "frases_totales": len(sentences),
            "parrafos_totales": len(paras),
        },
        "frase": {
            "longitud_media_palabras": round(_mean(sent_lens), 1),
            "desviacion": round(_stdev(sent_lens), 1),
            "mas_corta": min(sent_lens) if sent_lens else 0,
            "mas_larga": max(sent_lens) if sent_lens else 0,
            "distribucion_pct": {
                "cortas_<10": round(short / n_sent * 100, 1),
                "medias_10_25": round(medium / n_sent * 100, 1),
                "largas_>25": round(long / n_sent * 100, 1),
            },
        },
        "parrafo": {
            "longitud_media_palabras": round(_mean(para_lens), 1),
            "frases_por_parrafo_aprox": round(len(sentences) / max(len(paras), 1), 1),
        },
        "persona_gramatical_por_1000": persona,
        "orientacion": _orientacion(persona),
        "tratamiento": _tratamiento(persona),
        "riqueza_lexica": {
            "type_token_ratio": round(len(set(tokens_all)) / max(total_words, 1), 3),
            "palabras_unicas": len(set(tokens_all)),
            "hapax_pct": round(sum(1 for w, c in Counter(tokens_all).items() if c == 1)
                               / max(len(set(tokens_all)), 1) * 100, 1),
            "longitud_media_palabra": round(_mean([len(t) for t in tokens_all]), 2),
        },
        "puntuacion_por_1000": {
            "interrogaciones": punct_1k("?"),
            "exclamaciones": punct_1k("!"),
            "puntos_suspensivos": round(full.count("...") + full.count("…"), 0),
            "dos_puntos": punct_1k(":"),
            "punto_y_coma": punct_1k(";"),
            "parentesis": punct_1k("("),
            "guion_largo": full.count("—") + full.count("–"),
        },
        "senales_tono": {
            "emojis": len(EMOJI_RE.findall(full)),
            "conectores_formales_total": formal_hits,
            "llamadas_a_accion_total": cta_hits,
            "mayusculas_enfaticas": len(re.findall(r"\b[A-ZÁÉÍÓÚÑ]{3,}\b", full)),
            "numeros_y_datos": len(re.findall(r"\d", full)),
            "simbolos_porcentaje_moneda": len(re.findall(r"[%€$]", full)),
        },
        "legibilidad": {
            "fernandez_huerta": round(fh, 1),
            "interpretacion": _fh_label(fh),
            "silabas_por_palabra": round(syll / max(total_words, 1), 2),
        },
        "lexico_caracteristico": {
            "palabras_top": freq.most_common(30),
            "bigramas_top": bi.most_common(15),
            "trigramas_top": tri.most_common(10),
        },
        "ejemplos_reales": {
            "aperturas": openers[:8],
            "frases_cortas": by_len[:6],
            "frases_largas": by_len[-6:],
            "preguntas": questions[:6],
            "exclamaciones": exclam[:6],
        },
        "cobertura": {
            "ok": corpus.get("ok"),
            "fallidas": corpus.get("failed"),
            "urls_fallidas": [{"url": d["url"], "motivo": d.get("error")}
                              for d in corpus.get("docs", []) if not d.get("ok")],
        },
    }


def _orientacion(p):
    yo = p["yo_sg"]
    nos = p["nos_pl"]
    tu = p["tu_2s"] + p["usted_2"] + p["vos_2p"]
    dom = max(("yo", yo), ("nosotros", nos), ("tu/vosotros", tu), key=lambda x: x[1])
    return {"dominante": dom[0],
            "nota": "yo=marca personal, nosotros=empresa/equipo, tu=orientado al lector"}


def _tratamiento(p):
    tu = p["tu_2s"] + p["vos_2p"]
    ud = p["usted_2"]
    if tu == 0 and ud == 0:
        return "no determinado (poca 2a persona)"
    return "tuteo" if tu >= ud else "trato de usted (formal)"


def _fh_label(fh):
    if fh >= 80:
        return "muy facil"
    if fh >= 65:
        return "facil"
    if fh >= 50:
        return "normal"
    if fh >= 30:
        return "algo dificil"
    return "dificil / tecnico"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Analizador de tono desde URLs")
    ap.add_argument("mode", choices=["scrape", "metrics", "full"])
    ap.add_argument("source", nargs="+",
                    help="URLs, un .txt con URLs, o (en modo metrics) ruta a corpus.json")
    ap.add_argument("--out", default=".", help="Carpeta de salida (def: actual)")
    ap.add_argument("--name", default=None, help="Nombre base de los ficheros de salida")
    ap.add_argument("--delay", type=float, default=1.0, help="Segundos entre peticiones")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    base = args.name or "tono"

    if args.mode == "metrics":
        with open(args.source[0], "r", encoding="utf-8") as f:
            corpus = json.load(f)
        result = metrics(corpus)
        out_path = os.path.join(args.out, f"{base}-metricas.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"\nMetricas -> {out_path}", file=sys.stderr)
        return

    urls = read_urls(args.source)
    if not urls:
        print("ERROR: no se encontraron URLs validas.", file=sys.stderr)
        sys.exit(1)
    if len(urls) < 10:
        print(f"AVISO: solo {len(urls)} URLs. Lo ideal son 10-20 para un perfil fiable.",
              file=sys.stderr)
    if len(urls) > 30:
        print(f"AVISO: {len(urls)} URLs es mucho; se usaran las 30 primeras.", file=sys.stderr)
        urls = urls[:30]

    print(f"Scrapeando {len(urls)} URLs...", file=sys.stderr)
    corpus = scrape(urls, delay=args.delay, timeout=args.timeout)
    corpus_path = os.path.join(args.out, f"{base}-corpus.json")
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print(f"Corpus -> {corpus_path}  ({corpus['ok']}/{corpus['requested']} OK)", file=sys.stderr)

    if args.mode == "scrape":
        return

    if corpus["ok"] == 0:
        print("ERROR: ninguna URL devolvio contenido util. Revisa las URLs.", file=sys.stderr)
        sys.exit(2)

    result = metrics(corpus)
    out_path = os.path.join(args.out, f"{base}-metricas.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nCorpus    -> {corpus_path}", file=sys.stderr)
    print(f"Metricas  -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
