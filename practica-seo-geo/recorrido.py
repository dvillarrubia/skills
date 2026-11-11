"""Recorrido del expediente: qué pasos están hechos y el dato clave de cada uno. Genera RECORRIDO.md para la clase.

No llama a ninguna API ni al modelo: solo lee lo que hay en el expediente.
"""
import csv, json, re
from collections import Counter
from sop.comun import cargar_caso, expediente, hoy

caso = cargar_caso()
exp = expediente(caso)
c = caso["caso"]
lineas, hechos = [f"# Recorrido del caso · {c['marca']} · «{c['consulta_principal']}»", "",
                  f"Generado el {hoy()} a partir de `expedientes/{c['id']}/`. Solo resume lo que ya está en el expediente.", ""], 0


def leer(nombre):
    ruta = exp / nombre
    if not ruta.exists():
        return None
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def paso(n, titulo, comando, ficheros, resumen, debate):
    """resumen() devuelve una lista de líneas, o None si el paso no se ha ejecutado."""
    global hechos
    try:
        datos = resumen()
    except Exception as e:                       # un resumen que falla no debe tapar el resto del recorrido
        datos = [f"No se pudo resumir este paso ({type(e).__name__}: {e}). Abre los ficheros."]
    estado = "hecho" if datos is not None else "pendiente"
    hechos += datos is not None
    lineas.extend([f"## {n} · {titulo} — {estado}", "", f"`python {comando}`", ""])
    if datos is None:
        lineas.extend(["Todavía no se ha ejecutado.", ""])
        print(f"  [ ] {n:>2} {titulo}")
        return
    lineas.extend([f"- {d}" for d in datos])
    lineas.extend(["", "Abrir: " + ", ".join(f"`{f}`" for f in ficheros), "", f"Para debatir: {debate}", ""])
    print(f"  [x] {n:>2} {titulo}: {datos[0] if datos else ''}")


def r1():
    pains, fuentes = leer("01-pains.csv"), leer("01-voz-cliente.csv")
    if pains is None:
        return None
    est = Counter(p["estado"].split(":")[0] for p in pains)
    return [f"{len(fuentes or [])} fuentes analizadas · {est['confirmado']} problemas confirmados, {est['hipótesis']} hipótesis, {est['descartado']} descartados",
            f"{sum(int(p['citas_rechazadas'] or 0) for p in pains)} citas rechazadas porque no estaban literalmente en su fuente"] + \
           [f"{p['id']} ({p['estado']}, {p['fuentes_independientes']} fuentes): {p['problema']}" for p in pains[:3]]


def r2():
    f = leer("02-consultas.csv")
    if f is None:
        return None
    puesto = next((i + 1 for i, x in enumerate(f) if x["consulta"] == c["consulta_principal"].lower()), "fuera de la lista")
    return [f"{len(f)} consultas · {sum(x['relacion_negocio'] == 'sí' for x in f)} con relación con el negocio · "
            f"{sum(bool(x['pain']) for x in f)} asociadas a un problema",
            f"La consulta principal de partida queda en el puesto {puesto}",
            "Cinco primeras por prioridad: " + "; ".join(f"{x['consulta']} ({x['prioridad']})" for x in f[:5])]


def r3():
    g = leer("03-grupos.csv")
    if g is None:
        return None
    pr = next((x for x in g if x["contiene_principal"] == "sí"), None)
    ia = leer("03-respuesta-ia-google.csv") or []
    return [f"{len(g)} grupos de consultas por solape de resultados",
            f"Grupo de la consulta principal: {pr['consultas'] if pr else 'no encontrado'} → {pr['accion_candidata'] if pr else ''}",
            f"{len(leer('03-preguntas-google.csv') or [])} preguntas de Google observadas",
            f"Respuesta de IA en Google: {len(ia)} fuentes enlazadas, {sum(x['es_propia'] == 'sí' for x in ia)} propias"]


def r4():
    a = leer("04-asistentes.csv")
    if a is None:
        return None
    salida = [f"{len(a)} respuestas capturadas en {a[0]['superficie'] if a else ''}"]
    for q in caso["asistentes"]["preguntas"]:
        e = Counter(x["marca_propia"] for x in a if x["pregunta"] == q)
        salida.append(f"«{q}»: citada {e['citada']}, mencionada {e['mencionada']}, ausente {e['ausente']}")
    dom = Counter()
    for x in leer("04-fuentes.csv") or []:
        dom[x["dominio"]] += int(x["ejecuciones"])
    salida.append("Dominios más citados: " + ", ".join(f"{d} ({n})" for d, n in dom.most_common(5)))
    salida.append(f"{len(leer('04-fan-out.csv') or [])} búsquedas fan-out distintas")
    return salida


def r5():
    i = leer("05-corpus/indice.csv")
    if i is None:
        return None
    return [f"{sum(bool(x['fichero']) for x in i)} páginas evaluables y {sum(not x['fichero'] for x in i)} no evaluables",
            "Propias: " + "; ".join(f"{x['id']} {x['palabras']} palabras" for x in i if x["origen"] == "propia"),
            "Incidencias: " + ("; ".join(f"{x['id']} {x['incidencia']}" for x in i if x["incidencia"]) or "ninguna")]


def r6():
    f = leer("06-cobertura.csv")
    if f is None:
        return None
    d = Counter(x["decision"].split(":")[0] for x in f)
    anuladas = sum(v == "SE" for x in f for v in x.values())
    return [f"{len(f)} temas · " + ", ".join(f"{n} {k}" for k, n in d.items()),
            f"{anuladas} notas anuladas porque el fragmento citado no estaba en la página"]


def r7():
    if not (exp / "07-voz-medidas.json").exists():
        return None
    from sop.estilo import MEDIDAS, desviaciones
    m = json.loads((exp / "07-voz-medidas.json").read_text(encoding="utf-8"))
    fuera = desviaciones(m["medidas"][m["reservado"]], {k: tuple(v) for k, v in m["rango"].items()})
    return [f"El texto reservado cae dentro del rango de la marca en {len(MEDIDAS) - len(fuera)} de {len(MEDIDAS)} medidas",
            "Prueba ciega lista: `07-prueba-ciega.md` (la solución está en un fichero aparte)"
            if (exp / "07-prueba-ciega.md").exists() else "Sin prueba ciega"]


def r8():
    f = leer("08-evidencias.csv")
    if f is None:
        return None
    e = Counter(x["estado"].strip().lower() for x in f)
    ap = (exp / "aportacion.md").read_text(encoding="utf-8") if (exp / "aportacion.md").exists() else "[PENDIENTE"
    return [f"{len(f)} afirmaciones: " + ", ".join(f"{n} {k}" for k, n in e.items()),
            "Aportación original: " + ("PENDIENTE, la escribe una persona" if "[PENDIENTE" in ap else "escrita")]


def texto(nombre):
    return (exp / nombre).read_text(encoding="utf-8") if (exp / nombre).exists() else None


def r9():
    t = texto("09-instrucciones.md")
    return None if t is None else [f"Instrucciones editoriales de {len(t.split())} palabras"]


def r10():
    t = texto("10-borrador.md")
    if t is None:
        return None
    return [f"Borrador de {len(t.split())} palabras tras {len(list(exp.glob('10-borrador-v*.md')))} pasadas de corrección",
            f"Marcas PENDIENTE sin resolver: {t.count('PENDIENTE')}"]


def r11():
    f = leer("11-optimizacion.csv")
    if f is None:
        return None
    cols = [k for k in f[0] if k not in ("bloque", "control") and not k.startswith("detalle")]
    return [f"{col}: {sum(x[col].startswith('sí') for x in f if x.get(col))} de {sum(bool(x.get(col)) for x in f)} controles superados" for col in cols]


def r12():
    t = texto("12-revision.md")
    if t is None:
        return None
    m = re.search(r"\*\*(Puntuación.+?)\*\*", t)
    return [m.group(1) if m else "Revisión hecha"]


def r13():
    f = leer("13-seguimiento.csv")
    return None if f is None else [f"{x['pregunta']}: citada {x['referencia_citada']} → {x['seguimiento_citada']}" for x in f]


print(f"\nExpediente: expedientes/{c['id']}/\n")
paso(1, "ICP, pains y journey", "01_icp_pains.py", ["01-cliente.md", "01-pains.csv"], r1, "¿la hipótesis de partida sale confirmada, matizada o desmentida?")
paso(2, "Palabras clave", "02_consultas.py", ["02-consultas.csv"], r2, "¿cambiamos de consulta principal?")
paso(3, "Google por intención", "03_resultados.py", ["03-grupos.csv", "03-resultados.csv"], r3, "¿basta que dos URLs propias aparezcan en un grupo para hablar de canibalización?")
paso(4, "Asistentes de IA", "04_asistentes.py", ["04-asistentes.csv", "04-fuentes.csv", "04-respuestas/"], r4, "¿qué diferencia hay entre citada, mencionada y recomendada?")
paso(5, "Corpus", "05_corpus.py", ["05-corpus/indice.csv"], r5, "¿qué se ha perdido al limpiar una página?")
paso(6, "Cobertura", "06_cobertura.py", ["06-cobertura.csv"], r6, "¿que todos los competidores repitan un tema prueba que haga falta?")
paso(7, "Voz", "07_voz.py", ["07-voz.md", "07-prueba-ciega.md"], r7, "¿qué hábitos de la marca decidimos no imitar y por qué?")
paso(8, "Evidencias y aportación", "08_evidencias.py", ["08-evidencias.csv", "aportacion.md"], r8, "¿qué afirmación publicada no hemos podido verificar?")
paso(9, "Instrucciones editoriales", "09_instrucciones.py", ["09-instrucciones.md"], r9, "¿aprobamos la decisión sobre la URL?")
paso(10, "Borrador", "10_borrador.py", ["10-borrador.md", "prompts/10-borrador-v0.md"], r10, "¿qué fallos no se corrigieron solos?")
paso(11, "Optimización para Google e IA", "11_optimizacion.py", ["11-optimizacion.md"], r11, "¿qué control quitaríais o añadiríais, y con qué evidencia?")
paso(12, "Revisión", "12_revision.py", ["12-revision.md"], r12, "¿quién firma y por qué no puede ser quien redactó?")
paso(13, "Seguimiento", "13_seguimiento.py", ["13-seguimiento.csv"], r13, "¿la diferencia es mayor que la variación que ya había entre ejecuciones?")

capturas = Counter(json.loads(f.read_text(encoding="utf-8")).get("proveedor", "modelo" if f.name.startswith("llm-") else "dataforseo")
                   for f in (exp / "crudo").glob("*.json"))
lineas.extend(["## Capturas guardadas", "", ", ".join(f"{n} de {k}" for k, n in capturas.items()) or "Ninguna todavía.", "",
               "Sin `--fresco`, cada script reutiliza estas capturas: la clase funciona aunque falle la red.", ""])
(exp / "RECORRIDO.md").write_text("\n".join(lineas), encoding="utf-8")
print(f"\n  {hechos} de 13 pasos hechos · -> expedientes/{c['id']}/RECORRIDO.md")
