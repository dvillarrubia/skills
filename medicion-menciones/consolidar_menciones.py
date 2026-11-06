"""Consolida una carpeta de respuestas de IA en bruto: qué marcas salen, en qué orden y qué dominios se citan.

El script cuenta; no interpreta. Lo que no sabe clasificar no lo adivina: lo lista en «Avisos» para que
lo revise una persona. Sirve para los laboratorios 2 y 8 (modo «menciones») y para el 4 (modo «entidad»).

Uso:
  python consolidar_menciones.py respuestas-demo/lab8 --bateria bateria/bateria-atlas.csv --salida resultados/lab8
  python consolidar_menciones.py respuestas-demo/lab4 --bateria bateria/bateria-lab4.csv --modo entidad --salida resultados/lab4
(En Mac, python3. Las rutas son relativas a esta carpeta.)
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TLD = r"(?:example|com|es|org|net|io|eu|info|cat|ai)"
RE_URL = re.compile(r"https?://[^\s<>\]\)\"']+", re.I)
RE_DOMINIO = re.compile(r"(?<![\w@/.-])((?:[a-z0-9-]+\.)+" + TLD + r")(?![\w-])", re.I)
RE_ITEM = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+\*\*([^*]+)\*\*", re.M)
MIN_FIABLE = 6  # menos respuestas que esto en una celda: se marca como poco fiable


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


# ---------------------------------------------------------------- lectura

def leer_respuesta(ruta):
    texto = ruta.read_text(encoding="utf-8")
    meta = {}
    cuerpo = texto
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) == 3:
            for linea in partes[1].strip().splitlines():
                if ":" in linea:
                    k, v = linea.split(":", 1)
                    meta[k.strip()] = v.strip()
            cuerpo = partes[2]
    return meta, cuerpo


def leer_bateria(ruta):
    if not ruta:
        return {}
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    ids = [f["id"] for f in filas]
    repes = [i for i, n in Counter(ids).items() if n > 1]
    if repes:
        raise ValueError(f"Identificadores repetidos en la batería: {', '.join(repes)}")
    return {f["id"]: f for f in filas}


def normalizar_dominio(d):
    d = d.lower().strip(".,;:")
    return d[4:] if d.startswith("www.") else d


# ---------------------------------------------------------------- detección

def patron_alias(alias):
    return re.compile(r"(?<![\w])" + re.escape(sin_tildes(alias)) + r"(?![\w])")


def detectar_marcas(cuerpo, marcas):
    """Devuelve las marcas en el orden en que aparecen por primera vez."""
    # las URL y los dominios sueltos cuentan como cita, no como mención
    plano = sin_tildes(RE_DOMINIO.sub(" ", RE_URL.sub(" ", cuerpo)))
    primeras = {}
    for marca, alias in marcas.items():
        posiciones = [m.start() for a in alias for m in patron_alias(a).finditer(plano)]
        if posiciones:
            primeras[marca] = min(posiciones)
    return [m for m, _ in sorted(primeras.items(), key=lambda x: x[1])]


def detectar_dominios(cuerpo):
    dominios = [normalizar_dominio(u.split("//", 1)[1].split("/")[0].split("?")[0]) for u in RE_URL.findall(cuerpo)]
    sin_urls = RE_URL.sub(" ", cuerpo)
    dominios += [normalizar_dominio(d) for d in RE_DOMINIO.findall(sin_urls)]
    vistos = []
    for d in dominios:
        if d not in vistos:
            vistos.append(d)
    return vistos


def candidatos_sin_clasificar(cuerpo, marcas, ignorados):
    conocidos = {sin_tildes(a) for alias in marcas.values() for a in alias}
    ignorados = {sin_tildes(t) for t in ignorados}
    salida = []
    for nombre in RE_ITEM.findall(cuerpo):
        n = sin_tildes(nombre.strip())
        if n not in conocidos and n not in ignorados and not any(k in n for k in conocidos):
            salida.append(nombre.strip())
    return salida


# ---------------------------------------------------------------- análisis

def analizar(carpeta, bateria, config):
    marcas, objetivo = config["marcas"], config["objetivo"]
    dom_obj = config.get("dominio_objetivo", "")
    conocidos = set(config.get("dominios_conocidos", []))
    filas, avisos = [], defaultdict(list)
    archivos = sorted(p for p in Path(carpeta).rglob("*") if p.suffix.lower() in (".md", ".txt") and p.is_file())
    if not archivos:
        raise ValueError(f"No hay respuestas (.md o .txt) en {carpeta}")
    for ruta in archivos:
        meta, cuerpo = leer_respuesta(ruta)
        nombre = ruta.relative_to(carpeta).as_posix()
        orden = detectar_marcas(cuerpo, marcas)
        dominios = detectar_dominios(cuerpo)
        for d in dominios:
            if d not in conocidos:
                avisos["dominio no listado: comprueba que existe y que no es una invención"].append(f"{d} ({nombre})")
        for c in candidatos_sin_clasificar(cuerpo, marcas, config.get("terminos_ignorados", [])):
            avisos["nombre destacado que no está en marcas.json: ¿marca nueva, error o invención?"].append(f"{c} ({nombre})")
        fila = {"archivo": nombre, "id_pregunta": meta.get("id_pregunta", ""), "modelo": meta.get("modelo", ""),
                "busqueda": meta.get("busqueda", ""), "repeticion": meta.get("repeticion", ""),
                "marcas": " > ".join(orden), "aparece_objetivo": objetivo in orden,
                "posicion_objetivo": orden.index(objetivo) + 1 if objetivo in orden else "",
                "cita_objetivo": dom_obj in dominios, "dominios": " ".join(dominios), "cuerpo": cuerpo}
        if not meta:
            avisos["respuesta sin cabecera: se cuenta aparte, no entra en los porcentajes"].append(nombre)
            fila["sin_cabecera"] = True
        else:
            datos = bateria.get(fila["id_pregunta"]) if bateria else None
            if bateria and not datos:
                avisos["id_pregunta que no está en la batería: no entra en los porcentajes"].append(f"{fila['id_pregunta']} ({nombre})")
                fila["sin_cabecera"] = True
            datos = datos or {}
            fila.update({k: datos.get(k, "") for k in ("icp", "pain", "fase", "redaccion", "con_marca")})
        filas.append(fila)
    return filas, avisos


def resumir(filas, claves):
    grupos = defaultdict(list)
    for f in filas:
        grupos[tuple(f.get(k, "") for k in claves)].append(f)
    salida = []
    for clave, g in sorted(grupos.items()):
        pos = [f["posicion_objetivo"] for f in g if f["posicion_objetivo"] != ""]
        salida.append({**dict(zip(claves, clave)), "n": len(g),
                       "pct_aparece": round(100 * sum(f["aparece_objetivo"] for f in g) / len(g), 1),
                       "posicion_media": round(sum(pos) / len(pos), 2) if pos else "",
                       "pct_citada": round(100 * sum(f["cita_objetivo"] for f in g) / len(g), 1),
                       "pct_con_alguna_marca": round(100 * sum(bool(f["marcas"]) for f in g) / len(g), 1)})
    return salida


def rango_redacciones(filas):
    """Por ICP y fase: % de aparición mínimo y máximo entre redacciones."""
    por_red = resumir(filas, ["icp", "fase", "redaccion"])
    rangos = defaultdict(list)
    for r in por_red:
        rangos[(r["icp"], r["fase"])].append(r["pct_aparece"])
    return {k: (min(v), max(v)) for k, v in rangos.items()}


def presencia_por_marca(filas, marcas):
    n = len(filas)
    return [{"marca": m, "pct_respuestas": round(100 * sum(m in f["marcas"].split(" > ") for f in filas) / n, 1),
             "veces_primera": sum(f["marcas"].split(" > ")[0] == m for f in filas if f["marcas"])} for m in marcas]


# ---------------------------------------------------------------- modo entidad

def analizar_entidad(filas, config):
    ent = config.get("entidad", {})
    objetivo = config["objetivo"]
    salida = []
    for f in filas:
        plano = sin_tildes(f["cuerpo"])
        tipo = "sin clasificar: léela"
        for nombre, pistas in ent.get("confusiones", {}).items():
            if any(sin_tildes(p) in plano for p in pistas):
                if any(sin_tildes(p) in plano for p in ent.get("distingue", [])):
                    tipo = f"distingue de: {nombre}"
                else:
                    tipo = f"confunde con: {nombre}"
                break
        else:
            if any(sin_tildes(p) in plano for p in ent.get("no_sabe", [])):
                tipo = "no sabe o no lo confirma"
            elif any(sin_tildes(p) in plano for p in ent.get("descripcion_correcta", [])):
                tipo = "descripción coherente con la entidad"
        frases = [s.strip() for s in re.split(r"(?<=[.!?])\s+", f["cuerpo"].replace("\n", " "))
                  if sin_tildes(objetivo) in sin_tildes(s) or "atlas" in sin_tildes(s)]
        salida.append({**f, "tipo": tipo, "frases": frases})
    return salida


# ---------------------------------------------------------------- salida

def celda(valor):
    # el informe es para leerlo en español: coma decimal y sin «,0» (el CSV conserva el punto)
    if isinstance(valor, float):
        valor = f"{valor:g}"
    return re.sub(r"(\d)\.(\d)", r"\1,\2", str(valor))


def tabla_md(filas, columnas, titulos=None):
    titulos = titulos or columnas
    lineas = ["| " + " | ".join(titulos) + " |", "|" + "---|" * len(columnas)]
    for f in filas:
        lineas.append("| " + " | ".join(celda(f.get(c, "")) for c in columnas) + " |")
    return "\n".join(lineas)


def escribir_csv(ruta, filas, columnas):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def informe_menciones(validas, todas, avisos, config, carpeta):
    obj = config["objetivo"]
    con_marca = [f for f in validas if f.get("con_marca") == "si"]
    validas = [f for f in validas if f.get("con_marca") != "si"]  # sin marca: miden si te recomiendan
    rangos = rango_redacciones(validas)
    icp_fase = resumir(validas, ["icp", "fase"])
    for r in icp_fase:
        lo, hi = rangos.get((r["icp"], r["fase"]), ("", ""))
        r["rango_redacciones"] = f"{lo}-{hi} %" if lo != "" else ""
        r["fiable"] = "sí" if r["n"] >= MIN_FIABLE else f"no (n < {MIN_FIABLE})"
    dominios = Counter(d for f in validas + con_marca for d in f["dominios"].split())
    md = [f"# Menciones de {obj}", "",
          f"Carpeta: `{carpeta}` · respuestas leídas: {len(todas)} · sin marca: {len(validas)} · con marca: {len(con_marca)}.", "",
          "> El script cuenta; no interpreta. Antes de creerte la tabla, lee unas 10 respuestas en bruto. "
          "Una sola respuesta no es un dato: mira la columna n.", "",
          "## Por ICP y fase (preguntas sin marca)", "",
          tabla_md(icp_fase, ["icp", "fase", "n", "pct_aparece", "rango_redacciones", "posicion_media", "pct_citada", "fiable"],
                   ["ICP", "Fase", "n", f"% aparece {obj}", "Rango entre redacciones", "Posición media", f"% cita {config.get('dominio_objetivo', '')}", "¿Fiable?"]),
          "", "## Por pregunta (sin marca)", "",
          tabla_md(resumir(validas, ["id_pregunta"]), ["id_pregunta", "n", "pct_aparece", "posicion_media", "pct_citada", "pct_con_alguna_marca"],
                   ["Pregunta", "n", f"% aparece {obj}", "Posición media", "% citada", "% con alguna marca"]),
          "", "## Por modelo y modo (sin marca)", "",
          tabla_md(resumir(validas, ["modelo", "busqueda"]), ["modelo", "busqueda", "n", "pct_aparece", "posicion_media", "pct_citada", "pct_con_alguna_marca"],
                   ["Modelo", "Búsqueda", "n", f"% aparece {obj}", "Posición media", "% citada", "% con alguna marca"]),
          "", "## Todas las marcas (sin marca)", "",
          tabla_md(presencia_por_marca(validas, config["marcas"]), ["marca", "pct_respuestas", "veces_primera"],
                   ["Marca", "% de respuestas", "Veces en primer lugar"]),
          "", "## Preguntas con marca: qué dice la IA de ti", "",
          (tabla_md(resumir(con_marca, ["id_pregunta"]), ["id_pregunta", "n", "pct_aparece", "posicion_media", "pct_citada"],
                    ["Pregunta", "n", f"% aparece {obj}", "Posición media", "% citada"]) if con_marca else "No hay preguntas con marca."),
          "", "Aparecer cuando te nombran es lo esperado: lo que importa es qué dicen. Lee estas respuestas en bruto.",
          "", "## Dominios más citados (todas las respuestas)", "",
          tabla_md([{"dominio": d, "veces": n} for d, n in dominios.most_common(10)], ["dominio", "veces"], ["Dominio", "Veces"]),
          "", "## Avisos (revísalos a mano)", ""]
    if not avisos:
        md.append("Sin avisos.")
    for tipo, items in avisos.items():
        md.append(f"- **{tipo}** ({len(items)}):")
        md += [f"  - {i}" for i in items]
    return "\n".join(md) + "\n", icp_fase


def informe_entidad(ent, avisos, config):
    md = [f"# Cómo describen las IA a {config['objetivo']}", "",
          "> Agrupa las descripciones; no decide cuál es la verdad. Contrástalo con Wikidata, el Knowledge Panel y el schema de tu web.", ""]
    grupos = defaultdict(list)
    for f in ent:
        grupos[f["tipo"]].append(f)
    md.append(tabla_md([{"tipo": t, "n": len(g)} for t, g in grupos.items()], ["tipo", "n"], ["Tipo de descripción", "Respuestas"]))
    for t, g in grupos.items():
        md += ["", f"## {t}", ""]
        for f in g:
            md.append(f"- `{f['archivo']}` ({f['modelo']}, búsqueda {f['busqueda']}): " + " ".join(f["frases"])[:400])
    md += ["", "## Avisos (revísalos a mano)", ""]
    if not avisos:
        md.append("Sin avisos.")
    for tipo, items in avisos.items():
        md.append(f"- **{tipo}** ({len(items)}):")
        md += [f"  - {i}" for i in items]
    return "\n".join(md) + "\n"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # tildes en la terminal de Windows
    ap = argparse.ArgumentParser(description="Consolida respuestas de IA en bruto (datos del curso).")
    ap.add_argument("carpeta", help="carpeta con las respuestas (.md o .txt)")
    ap.add_argument("--bateria", help="CSV de la batería con id, icp, pain, fase, redaccion…")
    ap.add_argument("--marcas", default=str(AQUI / "marcas.json"))
    ap.add_argument("--modo", choices=["menciones", "entidad"], default="menciones")
    ap.add_argument("--salida", required=True, help="carpeta donde se escriben el CSV y el Markdown (debe ser nueva o estar vacía)")
    a = ap.parse_args(argv)
    carpeta, salida = Path(a.carpeta), Path(a.salida)
    if salida.exists() and any(salida.iterdir()):
        sys.exit(f"La carpeta de salida {salida} ya tiene archivos: usa otra para no pisar resultados anteriores.")
    salida.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(a.marcas).read_text(encoding="utf-8"))
    bateria = leer_bateria(a.bateria)
    filas, avisos = analizar(carpeta, bateria, config)
    validas = [f for f in filas if not f.get("sin_cabecera")]
    cols = ["archivo", "id_pregunta", "icp", "pain", "fase", "redaccion", "con_marca", "modelo", "busqueda", "repeticion",
            "marcas", "aparece_objetivo", "posicion_objetivo", "cita_objetivo", "dominios"]
    escribir_csv(salida / "por-respuesta.csv", filas, cols)
    if a.modo == "entidad":
        ent = analizar_entidad(filas, config)
        (salida / "entidad.md").write_text(informe_entidad(ent, avisos, config), encoding="utf-8", newline="\n")
        print(f"{len(filas)} respuestas · informe en {salida / 'entidad.md'}")
        return 0
    md, icp_fase = informe_menciones(validas, filas, avisos, config, carpeta.as_posix())
    escribir_csv(salida / "por-icp-y-fase.csv", icp_fase,
                 ["icp", "fase", "n", "pct_aparece", "rango_redacciones", "posicion_media", "pct_citada", "fiable"])
    (salida / "menciones.md").write_text(md, encoding="utf-8", newline="\n")
    print(f"{len(filas)} respuestas ({len(validas)} en los porcentajes) · {sum(len(v) for v in avisos.values())} avisos · informe en {salida / 'menciones.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
