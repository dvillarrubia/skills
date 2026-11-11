"""Utilidades compartidas: configuración, expediente, CSV y la explicación que se lee en clase."""
import csv, datetime, os, pathlib, re, sys, textwrap, tomllib

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def cargar_env():
    ruta = RAIZ / ".env"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.strip().startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def cargar_caso():
    cargar_env()
    ruta = pathlib.Path(os.environ.get("SOP_CASO", RAIZ / "caso.toml"))
    with open(ruta, "rb") as f:
        return tomllib.load(f)


def expediente(caso):
    p = RAIZ / "expedientes" / caso["caso"]["id"]
    for sub in ("", "crudo", "prompts", "05-corpus"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def opciones():
    """--seco enseña la petición sin gastar; --fresco ignora las capturas guardadas y vuelve a pedir."""
    a = sys.argv[1:]
    return {"seco": "--seco" in a, "fresco": "--fresco" in a, "resto": [x for x in a if not x.startswith("--")]}


def hoy():
    return datetime.date.today().isoformat()


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def explicar(paso, que, por_que, mirar):
    """Lo que el docente lee en voz alta antes de que el script haga nada."""
    ancho = 96
    print("\n" + "=" * ancho)
    print(paso.upper())
    print("=" * ancho)
    for etiqueta, texto in (("QUÉ HACEMOS", que), ("POR QUÉ", por_que), ("QUÉ MIRAR", mirar)):
        print(f"\n{etiqueta}")
        print(textwrap.fill(texto, ancho, initial_indent="  ", subsequent_indent="  "))
    print("\n" + "-" * ancho)


def escribir_csv(ruta, filas, campos):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({k: ("" if fila.get(k) is None else fila.get(k)) for k in campos})
    print(f"  -> {ruta.relative_to(RAIZ)} ({len(filas)} filas)")


def leer_csv(ruta):
    if not ruta.exists():
        sys.exit(f"Falta {ruta.relative_to(RAIZ)}. Ejecuta antes el script que lo genera.")
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def exigir(ruta):
    if not ruta.exists():
        sys.exit(f"Falta {ruta.relative_to(RAIZ)}. Ejecuta antes el script que lo genera.")
    return ruta.read_text(encoding="utf-8")


def dominio(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1).lower() if m else ""


def slug(url):
    s = re.sub(r"https?://(www\.)?", "", url).strip("/")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:90]


def normalizar(texto):
    return re.sub(r"[\s*_#>|`\-]+", " ", (texto or "").lower()).strip()


def contiene(texto, fragmento):
    """Comprobación determinista: ¿el fragmento que cita el modelo está de verdad en la página?"""
    f = normalizar(fragmento)
    return len(f) >= 12 and f in normalizar(texto)


def tabla(filas, campos, ancho=38):
    for fila in filas:
        print("  " + " | ".join(str("" if fila.get(c) is None else fila.get(c))[:ancho].ljust(min(ancho, 22)) for c in campos))
