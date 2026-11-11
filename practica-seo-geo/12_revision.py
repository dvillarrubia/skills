"""Paso 12. Revisión con rúbrica. El modelo puntúa con evidencia; la nota final y la decisión las calcula Python."""
from sop.comun import cargar_caso, expediente, explicar, opciones, exigir
from sop.llm import pedir_json, SOLO_FUENTES

PESOS = {"Adecuación al público y la tarea": 20, "Rigor y trazabilidad": 20, "Aportación propia": 20,
         "Cobertura pertinente": 10, "Utilidad y facilidad de lectura": 10, "Voz editorial": 10,
         "Pasajes citables y claridad de entidades": 5, "Preparación técnica": 5}
BLOQUEOS = ["Intención principal mal resuelta", "Afirmación central inventada, no verificada o contradictoria",
            "Aportación prometida inexistente", "Copia sustancial de otro contenido",
            "Experiencias atribuidas al autor que no ocurrieron"]
UMBRAL = 80

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
explicar("Paso 12 · Revisión",
         "El modelo puntúa de 0 a 4 cada dimensión de la rúbrica citando el pasaje que justifica la nota, y señala "
         "posibles bloqueos. Python pondera, suma, compara con el umbral y añade los bloqueos mecánicos.",
         f"Publicar exige {UMBRAL} puntos y ningún bloqueo. Un modelo que revisa su propio texto tiende a aprobarlo: "
         "por eso la decisión no es suya y por eso la firma una persona distinta de quien redactó.",
         "Las notas bajas con su evidencia, y si algún bloqueo mecánico (pendientes sin resolver) está activo.")

borrador = exigir(exp / "10-borrador.md")
datos = pedir_json(caso, exp, "12-revision",
    SOLO_FUENTES + "Eres un editor exigente. No apruebas afirmaciones porque suenen plausibles. Devuelve solo JSON.",
    "Revisa el borrador contra las instrucciones, la guía de voz y la aportación original.\n"
    f"Dimensiones (nota de 0 a 4 cada una; 0 ausente, 1 deficiente, 2 suficiente con carencias, 3 sólido, 4 excelente con evidencias): {list(PESOS)}\n"
    f"Bloqueos posibles: {BLOQUEOS}\n"
    'Formato: {"dimensiones": {"<nombre>": {"nota": n, "evidencia": "pasaje o problema concreto", "correccion": "..."}}, '
    '"bloqueos": {"<nombre>": {"activo": true|false, "motivo": "..."}}}\n\n'
    f"INSTRUCCIONES\n{exigir(exp / '09-instrucciones.md')}\n\nAPORTACIÓN ORIGINAL\n{exigir(exp / 'aportacion.md')}\n\n"
    f"GUÍA DE VOZ\n{exigir(exp / '07-voz.md')}\n\nBORRADOR\n{borrador}", max_tokens=4000, seco=op["seco"], fresco=op["fresco"])
if datos is None:
    raise SystemExit("\nModo --seco: prompt guardado en prompts/12-revision.md, sin llamar al modelo.")

total, lineas = 0.0, []
for nombre, peso in PESOS.items():
    d = (datos.get("dimensiones") or {}).get(nombre) or {}
    nota = max(0, min(4, int(d.get("nota", 0) or 0)))
    total += peso * nota / 4
    lineas.append(f"| {nombre} | {peso} | {nota} | {peso * nota / 4:.1f} | {d.get('evidencia', '')} | {d.get('correccion', '')} |")
activos = [f"{n}: {b.get('motivo', '')}" for n, b in (datos.get("bloqueos") or {}).items() if b.get("activo")]
if "PENDIENTE" in borrador:
    activos.append(f"Pendientes sin resolver: {borrador.count('PENDIENTE')} (comprobación mecánica)")
if "[PENDIENTE" in exigir(exp / "aportacion.md"):
    activos.append("Aportación original sin describir (comprobación mecánica)")
decision = "APTO para revisión humana final" if total >= UMBRAL and not activos else "NO APTO: vuelve a redacción"
(exp / "12-revision.md").write_text(
    f"# Revisión · {caso['caso']['id']}\n\n**Puntuación: {total:.1f} / 100 · umbral {UMBRAL} · {decision}**\n\n"
    "| Dimensión | Peso | Nota (0–4) | Puntos | Evidencia | Corrección |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(lineas)
    + "\n\n## Bloqueos activos\n\n" + ("\n".join(f"- {a}" for a in activos) or "Ninguno.")
    + "\n\n## Pendiente de una persona\n\n- [ ] Revisión experta si el tema la requiere\n- [ ] Datos privados no autorizados\n"
      "- [ ] Comprobación de la URL publicada (acceso, canonical, renderizado, enlaces, medición)\n- [ ] Firma de quien aprueba\n",
    encoding="utf-8")
print(f"\n  Puntuación: {total:.1f} / 100 (umbral {UMBRAL})\n  Bloqueos activos: {len(activos)}")
for a in activos:
    print(f"    - {a}")
print(f"  Decisión: {decision}\n  -> 12-revision.md")
