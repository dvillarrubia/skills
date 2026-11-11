"""Paso 9. Instrucciones editoriales: integra todo el expediente en un documento que el redactor puede seguir."""
from sop.comun import cargar_caso, expediente, explicar, opciones, leer_csv, exigir
from sop.llm import pedir, SOLO_FUENTES

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
c = caso["caso"]
explicar("Paso 9 · Instrucciones editoriales",
         "Juntamos encargo, problemas del público, consultas priorizadas, grupos, resultados, respuestas de asistentes, huecos de cobertura, guía de voz, "
         "afirmaciones verificadas y aportación original, y pedimos un esquema donde cada sección resuelve una pregunta.",
         "El script se niega a continuar si la aportación original sigue sin escribir. Sin algo propio y verificable, "
         "lo que saldría es un resumen de los competidores.",
         "Que cada sección tenga pregunta, evidencia y criterio de finalización, y que la acción propuesta "
         "(actualizar, ampliar, crear o consolidar) sea coherente con las URLs propias que ya existen.")

aportacion = exigir(exp / "aportacion.md")
if "[PENDIENTE" in aportacion:
    raise SystemExit("  CONTROL: aportacion.md sigue pendiente. Una persona debe describir la aportación original antes de seguir.")

consultas = [f for f in leer_csv(exp / "02-consultas.csv") if f["relacion_negocio"] == "sí"][:25]
diez = [f for f in leer_csv(exp / "03-resultados.csv") if f["consulta"] == c["consulta_principal"]][:10]
preguntas = leer_csv(exp / "03-preguntas-google.csv")
pains = [f for f in leer_csv(exp / "01-pains.csv") if not f["estado"].startswith("descartado")]
grupos = leer_csv(exp / "03-grupos.csv")
abanico = leer_csv(exp / "04-fan-out.csv")[:15]
asistentes = leer_csv(exp / "04-asistentes.csv")
fuentes = leer_csv(exp / "04-fuentes.csv")[:15]
cobertura = [f for f in leer_csv(exp / "06-cobertura.csv") if f["decision"] != "cubierto"]
verificadas = [f for f in leer_csv(exp / "08-evidencias.csv") if f["estado"].strip().lower() == "verificada"]
corpus = leer_csv(exp / "05-corpus" / "indice.csv")
print(f"  Entradas: {len(pains)} problemas, {len(consultas)} consultas, {len(grupos)} grupos, {len(diez)} resultados, {len(preguntas)} preguntas de Google, "
      f"{len(asistentes)} respuestas de asistentes, {len(cobertura)} temas con hueco, {len(verificadas)} afirmaciones verificadas")

usuario = f"""ENCARGO
{exigir(exp / '00-encargo.md')}

PROBLEMAS DEL PÚBLICO (con sus palabras)
{chr(10).join(f"- {f['id']} [{f['estado']}, {f['etapa']}] {f['problema']} → quiere: {f['resultado_deseado']}. Dice: {f['citas'][:300]}" for f in pains)}

CONSULTAS PRIORIZADAS (prioridad · volumen estimado · problema · posición propia)
{chr(10).join(f"- {f['consulta']} ({f['prioridad']} · {f['volumen_estimado'] or 'sin dato'} · {f['pain'] or 'sin problema asociado'} · {f['posicion_propia'] or 'no posiciona'})" for f in consultas)}

GRUPOS POR SOLAPE DE RESULTADOS
{chr(10).join(f"- {g['grupo']}: {g['consultas']} → {g['accion_candidata']} · URLs propias: {g['urls_propias'] or 'ninguna'}" for g in grupos)}

RESULTADOS DE GOOGLE PARA LA CONSULTA PRINCIPAL
{chr(10).join(f"{f['posicion']}. {f['dominio']} · {f.get('tipo_pagina_inferido', '')} · {f['titulo']}" for f in diez)}

PREGUNTAS OBSERVADAS EN GOOGLE
{chr(10).join('- ' + f['pregunta'] for f in preguntas) or 'ninguna observada'}

RESPUESTAS DE ASISTENTES (por ejecución)
{chr(10).join(f"- {f['pregunta']} | marca propia: {f['marca_propia']} | citan: {f['dominios_citados']}" for f in asistentes)}

BÚSQUEDAS QUE LANZAN LOS ASISTENTES (fan-out)
{chr(10).join(f"- {f['busqueda']} ({f['veces']})" for f in abanico) or 'ninguna observada'}

FUENTES MÁS REPETIDAS POR ASISTENTES
{chr(10).join(f"- {f['dominio']} ({f['ejecuciones']} de {f['de']}) {f['url']}" for f in fuentes)}

PÁGINAS PROPIAS EXISTENTES
{chr(10).join(f"- {f['id']} {f['url']} · {f['palabras']} palabras · H1: {f['h1']}" for f in corpus if f['origen'] == 'propia')}

TEMAS CON HUECO O SIN PRUEBA EN NINGUNA PÁGINA
{chr(10).join(f"- {f['tema']} → {f['decision']} (lo cubren bien {f['cubren_bien']})" for f in cobertura)}

AFIRMACIONES VERIFICADAS (las únicas cifras y hechos utilizables)
{chr(10).join(f"- {f['id']}: {f['afirmacion']} (fuente: {f['fuente_primaria']})" for f in verificadas) or 'ninguna todavía'}

APORTACIÓN ORIGINAL
{aportacion}

GUÍA DE VOZ
{exigir(exp / '07-voz.md')}
"""
texto = pedir(caso, exp, "09-instrucciones",
    SOLO_FUENTES + "Eres editor. Preparas instrucciones de redacción; no redactas el artículo.",
    "Con el expediente siguiente, escribe las instrucciones editoriales en Markdown con estos apartados:\n"
    "1. Decisión sobre la URL: actualizar, ampliar, crear o consolidar, justificada con los grupos y las páginas propias.\n"
    "2. Segmento y problemas a los que responde la pieza (ids), con las palabras del público que conviene recoger, y promesa concreta.\n"
    "3. Intención y formato, justificados con los resultados observados.\n"
    "4. Preguntas de asistentes y búsquedas fan-out que la pieza debe cubrir, cada una con el pasaje que la responderá.\n"
    "5. Esquema: una tabla con Encabezado | Pregunta que resuelve | Respuesta necesaria | Evidencia (id) | Recurso | Criterio de finalización.\n"
    "6. Dónde entra la aportación original.\n"
    "7. Afirmaciones permitidas y pendientes. Lo que no esté verificado se marca PENDIENTE.\n"
    "8. Exclusiones de alcance.\n\n" + usuario, max_tokens=5000, seco=op["seco"], fresco=op["fresco"])
if texto is None:
    raise SystemExit("\nModo --seco: prompt guardado en prompts/09-instrucciones.md, sin llamar al modelo.")
(exp / "09-instrucciones.md").write_text(texto, encoding="utf-8")
print(f"  -> 09-instrucciones.md ({len(texto.split())} palabras)")
print("  Tarea manual: leer la decisión sobre la URL y discutir si el grupo la aprueba antes de redactar.")
