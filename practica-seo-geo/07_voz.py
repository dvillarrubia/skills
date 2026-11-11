"""Paso 7. Guía de voz: estilo medido con números, reglas con ejemplos verificados, listón editorial y prueba ciega."""
import json, random, re
from sop.comun import cargar_caso, expediente, explicar, opciones, contiene
from sop.estilo import MEDIDAS, CLICHES, medir, rangos, desviaciones, cliches
from sop.llm import pedir_json, SOLO_FUENTES
from sop import paginas
from sop.paginas import descargar, analizar

caso, op = cargar_caso(), opciones()
paginas.LECTOR = "local"      # para medir estilo usamos siempre la extracción local, que deja solo el cuerpo del artículo
exp = expediente(caso)
voz = caso["voz"]
explicar("Paso 7 · Guía de voz",
         "Hacemos tres cosas con textos reales de la marca. Una: medir su estilo con números (largo de frase, tuteo, "
         "preguntas, negritas). Dos: pedir al modelo reglas observables, cada una con un ejemplo literal que Python "
         "busca en los textos. Tres: separar lo que se conserva de lo que no, con el listón editorial de caso.toml.",
         "Imitar a la marca no basta si la marca escribe regular. La guía tiene dos capas: lo que la hace reconocible "
         "(medido) y lo que queremos que cumpla aunque hoy no lo haga (principios escritos por una persona). El último "
         "texto se reserva sin enseñárselo al modelo y sirve para comprobar que los rangos describen de verdad a la marca.",
         "Si el texto reservado cae dentro de los rangos, qué tics de la marca decidimos no imitar, y la prueba ciega: "
         "¿distingue el grupo el párrafo real de los generados?")

textos, titulos = {}, {}
for u in voz["textos"]:
    html, ficha = descargar(u)
    if html:
        datos, textos[u] = analizar(html, u)
        titulos[u] = datos["h1"].split(" | ")[0] or datos["titulo"]
        print(f"  {datos['palabras']:>5} palabras  {u}")
    else:
        print(f"  no evaluable ({ficha['incidencia'] or ficha['estado']})  {u}")
if len(textos) < 4:
    raise SystemExit("Hacen falta al menos cuatro textos evaluables: tres para la guía y uno reservado.")
*entrenamiento, reservado = list(textos)

# 1) Estilo medido. Sin modelo.
medidas = {u: medir(textos[u]) for u in textos}
rango = rangos([medidas[u] for u in entrenamiento], voz["tolerancia"])
fuera_reservado = desviaciones(medidas[reservado], rango)
print(f"\n  {'Medida'.ljust(62)} {'rango de la marca'.ljust(18)} reservado")
for k, nombre in MEDIDAS.items():
    lo, hi = rango[k]
    v = medidas[reservado][k]
    print(f"  {nombre[:62].ljust(62)} {f'{lo} – {hi}'.ljust(18)} {v} {'' if lo <= v <= hi else '<- fuera'}")
print(f"\n  El texto reservado cae dentro del rango en {len(MEDIDAS) - len(fuera_reservado)} de {len(MEDIDAS)} medidas.")
if op["seco"]:
    raise SystemExit("\nModo --seco: medidas calculadas; no se llama al modelo.")

# 2) Reglas cualitativas con ejemplo literal, tics, reescrituras y párrafos para la prueba ciega.
material = "\n\n".join(f"=== TEXTO {i + 1} ===\n{textos[u][:7000]}" for i, u in enumerate(entrenamiento))
datos = pedir_json(caso, exp, "07-voz", SOLO_FUENTES + "Devuelve solo JSON.",
    "Analiza cómo escribe esta marca.\n\n"
    "A) «reglas»: de 8 a 12 reglas observables sobre tratamiento al lector, persona gramatical, ritmo, vocabulario propio "
    "del oficio, tipo de ejemplos, transiciones y llamadas a la acción. Cada una con un ejemplo LITERAL de 6 a 25 palabras.\n"
    "B) «tics»: de 3 a 6 hábitos de estos textos que restan (relleno, elogios sin dato, fórmulas repetidas, mayúsculas "
    "en cada palabra del encabezado…), cada uno con un ejemplo LITERAL.\n"
    "C) «reescrituras»: 3 frases LITERALES de los textos que incumplen los principios de abajo y, para cada una, la "
    "versión que sí los cumple, sin añadir datos que no estén en la frase original.\n"
    "D) «muestra»: de 200 a 300 palabras sobre «cómo guardar el café en casa» con la voz de la marca y los principios. "
    "Sin inventar datos ni experiencias.\n"
    f"E) «parrafos_ciegos»: dos párrafos distintos de 60 a 90 palabras para un artículo titulado «{titulos[reservado]}».\n\n"
    "PRINCIPIOS (listón editorial fijado por el equipo):\n" + "\n".join(f"- {x}" for x in voz["principios"]) + "\n\n"
    'Formato: {"reglas": [{"rasgo": "", "regla": "", "ejemplo": "", "aplicacion": ""}], "tics": [{"tic": "", "ejemplo": "", '
    '"en_su_lugar": ""}], "reescrituras": [{"antes": "", "despues": "", "principio": ""}], "muestra": "", "parrafos_ciegos": ["", ""]}\n\n'
    + material, max_tokens=5000, fresco=op["fresco"])

todo = "\n".join(textos[u] for u in entrenamiento)
marca = lambda frag: "literal" if contiene(todo, frag) else "NO ENCONTRADO"
reglas = [f"| {r.get('rasgo')} | {r.get('regla')} | «{r.get('ejemplo')}» | {marca(r.get('ejemplo', ''))} | {r.get('aplicacion')} |"
          for r in datos.get("reglas", [])]
tics = [f"| {t.get('tic')} | «{t.get('ejemplo')}» | {marca(t.get('ejemplo', ''))} | {t.get('en_su_lugar')} |" for t in datos.get("tics", [])]
pares = [f"| «{x.get('antes')}» | {marca(x.get('antes', ''))} | «{x.get('despues')}» | {x.get('principio')} |" for x in datos.get("reescrituras", [])]
muestra = datos.get("muestra", "")
desv_muestra = desviaciones(medir(muestra), rango, voz["medidas_a_ignorar"])
vistos = cliches(muestra, voz["cliches_extra"])

# 3) Prueba ciega: un párrafo real del texto reservado entre dos generados.
reales = [p.strip() for p in re.split(r"\n\s*\n", textos[reservado]) if 50 <= len(p.split()) <= 110 and "\n" not in p.strip() and not p.lstrip().startswith(("#", "|", "-", "*"))
          and not p.lstrip()[0].isdigit()]
if reales and len(datos.get("parrafos_ciegos") or []) >= 2:
    opciones_ciegas = [("real", reales[0])] + [("generado", x) for x in datos["parrafos_ciegos"][:2]]
    random.Random(len(reales[0])).shuffle(opciones_ciegas)
    (exp / "07-prueba-ciega.md").write_text(
        f"# Prueba ciega · ¿cuál lo escribió la marca?\n\nArtículo: «{titulos[reservado]}»\n\n"
        + "\n\n".join(f"## Párrafo {chr(65 + i)}\n\n{t}" for i, (_, t) in enumerate(opciones_ciegas)) + "\n", encoding="utf-8")
    (exp / "07-prueba-ciega-solucion.md").write_text(
        "\n".join(f"Párrafo {chr(65 + i)}: {o}" for i, (o, _) in enumerate(opciones_ciegas)) + f"\n\nFuente del real: {reservado}\n", encoding="utf-8")

(exp / "07-voz-medidas.json").write_text(json.dumps({"rango": rango, "medidas": medidas, "reservado": reservado}, ensure_ascii=False, indent=1), encoding="utf-8")
(exp / "07-voz.md").write_text(
    f"# Guía de voz · {caso['caso']['marca']}\n\nExtraída de {len(entrenamiento)} textos. Reservado para contraste: {reservado}\n\n"
    "## Voz objetivo: principios\n\nLo que la voz debe cumplir aunque los textos actuales no siempre lo hagan.\n\n"
    + "\n".join(f"- {x}" for x in voz["principios"])
    + "\n\n## Estilo medido\n\n| Medida | Rango de la marca | Texto reservado | Se imita |\n| --- | --- | --- | --- |\n"
    + "\n".join(f"| {MEDIDAS[k]} | {rango[k][0]} – {rango[k][1]} | {medidas[reservado][k]} | {'no: choca con los principios' if k in voz['medidas_a_ignorar'] else 'sí'} |" for k in MEDIDAS)
    + "\n\n## Reglas observables\n\n| Rasgo | Regla | Ejemplo de referencia | Verificación | Aplicación |\n| --- | --- | --- | --- | --- |\n" + "\n".join(reglas)
    + "\n\n## Tics que no se imitan\n\n| Tic | Ejemplo | Verificación | En su lugar |\n| --- | --- | --- | --- |\n" + "\n".join(tics)
    + "\n\n## Antes y después\n\n| Frase de la marca | Verificación | Reescrita con los principios | Principio |\n| --- | --- | --- | --- |\n" + "\n".join(pares)
    + "\n\n## Fórmulas prohibidas\n\n" + ", ".join(f"«{x}»" for x in CLICHES + voz["cliches_extra"])
    + f"\n\n## Muestra para validar ({len(muestra.split())} palabras)\n\n{muestra}\n\n"
    + "Desviaciones de la muestra respecto al estilo medido: " + ("; ".join(desv_muestra) or "ninguna") + ".\n"
    + "Fórmulas prohibidas en la muestra: " + (", ".join(vistos) or "ninguna") + ".\n\n"
    "## Validación\n\n- [ ] El responsable editorial aprueba la muestra\n- [ ] Prueba ciega hecha con el grupo\n", encoding="utf-8")
literales = sum("| literal |" in x for x in reglas + tics + pares)
print(f"\n  -> 07-voz.md, 07-voz-medidas.json, 07-prueba-ciega.md")
print(f"  {len(reglas)} reglas, {len(tics)} tics, {len(pares)} reescrituras · {literales} de {len(reglas + tics + pares)} ejemplos son literales")
print(f"  Muestra de {len(muestra.split())} palabras · fuera de rango en {len(desv_muestra)} medidas · fórmulas prohibidas: {len(vistos)}")
print("  En clase: proyectar 07-prueba-ciega.md, votar y abrir después la solución.")
