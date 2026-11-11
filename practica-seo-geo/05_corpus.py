"""Paso 5. Descarga y extrae las páginas que vamos a comparar: propias, comparables de Google y fuentes de asistentes."""
from sop.comun import cargar_caso, expediente, explicar, opciones, escribir_csv, leer_csv, hoy, slug, dominio, tabla
from sop import paginas
from sop.paginas import descargar, analizar

caso, op = cargar_caso(), opciones()
paginas.configurar(caso)
exp = expediente(caso)
c, lim = caso["caso"], caso["limites"]
explicar("Paso 5 · Corpus",
         "Descargamos el HTML de las páginas propias, las comparables del paso 3 y las fuentes que más repiten los "
         "asistentes en el paso 4. Guardamos el HTML original y, aparte, el texto principal limpio.",
         "El texto limpio sirve para analizar contenido; el HTML, para comprobar la implementación. Un error de "
         "acceso se anota como «no evaluable»: nunca se convierte en «el competidor no habla de esto».",
         "El estado HTTP, la URL final tras redirecciones, la canonical, cuántas palabras y tablas sobreviven a la "
         "limpieza y qué páginas quedan como no evaluables.")

urls = [(u, "propia") for u in caso["propias"]["urls"]]
urls += [(f["url"], "comparable Google") for f in leer_csv(exp / "03-resultados.csv") if f["seleccionada"] == "comparable"]
ruta_fuentes = exp / "04-fuentes.csv"
if ruta_fuentes.exists():
    repetidas = [f for f in leer_csv(ruta_fuentes) if f["es_propia"] == "no" and int(f["ejecuciones"]) >= 2
                 and not any(d in f["dominio"] for d in lim["excluir_dominios"])]
    urls += [(f["url"], "fuente de asistente") for f in repetidas[:3]]

indice, vistos = [], set()
for url, origen in urls:
    if url in vistos:
        continue
    vistos.add(url)
    pid = f"P{len(indice) + 1}"
    print(f"  {pid} {origen}: {url}")
    if op["seco"]:
        continue
    html, ficha = descargar(url)
    ficha.update(id=pid, origen=origen, dominio=dominio(url), fecha=hoy(), fichero="")
    if html:
        datos, texto = analizar(html, url)
        nombre = f"{pid}-{slug(url)}"
        (exp / "05-corpus" / f"{nombre}.html").write_text(html, encoding="utf-8")
        (exp / "05-corpus" / f"{nombre}.md").write_text(texto, encoding="utf-8")
        ficha.update(datos, fichero=f"{nombre}.md")
        if datos["palabras"] < 150:
            ficha["incidencia"] = "revisar a mano: menos de 150 palabras extraídas (¿contenido cargado con JavaScript?)"
    indice.append(ficha)

if op["seco"]:
    raise SystemExit("\nModo --seco: no se ha descargado nada.")
escribir_csv(exp / "05-corpus" / "indice.csv", indice,
             ["id", "origen", "dominio", "url", "url_final", "estado", "palabras", "tablas", "titulo", "descripcion", "h1",
              "canonical", "robots", "datos_estructurados", "h2_h3", "metodo", "fecha", "incidencia", "fichero"])
print()
if caso["propias"].get("urls_antiguas"):
    import requests
    print("  URLs de la estructura anterior (¿redirigen a la nueva?):")
    for u in caso["propias"]["urls_antiguas"]:
        try:
            r = requests.get(u, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            salto = f" -> {r.url}" if r.url.rstrip("/") != u.rstrip("/") else ""
            print(f"    HTTP {r.status_code}{salto}  {u}")
        except requests.RequestException as e:
            print(f"    no evaluable ({type(e).__name__})  {u}")
    print()
tabla(indice, ["id", "origen", "dominio", "estado", "palabras", "tablas", "incidencia"])
print("\n  Tarea manual antes de seguir: abrir dos .md del corpus junto a su página y comprobar que no se ha perdido "
      "ninguna tabla o sección importante.")
