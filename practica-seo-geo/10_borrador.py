"""Paso 10. Borrador con ciclo de corrección: el modelo redacta, Python mide y devuelve los fallos, el modelo corrige."""
import json, re
from sop.comun import cargar_caso, expediente, explicar, opciones, leer_csv, exigir, normalizar
from sop.contexto import de_optimizacion
from sop.estilo import medir, desviaciones, cliches
from sop.llm import pedir, SOLO_FUENTES
from sop.optimizacion import controles

caso, op = cargar_caso(), opciones()
exp = expediente(caso)
voz = caso["voz"]
explicar("Paso 10 · Borrador",
         "El modelo redacta con las instrucciones, la guía de voz, las afirmaciones verificadas y la aportación. Después "
         "Python mide el texto: estilo frente al rango de la marca, fórmulas prohibidas, controles de Google y de "
         f"asistentes, y cifras sin respaldo. Los fallos vuelven al modelo como lista de correcciones, hasta {voz['max_revisiones']} veces.",
         "Pedirle a un modelo «escribe con la voz de la marca y optimizado para IA» produce un texto que dice cumplirlo. "
         "Aquí el crítico es código: los mismos números para cualquier borrador, y un presupuesto fijo de pasadas. "
         "Lo que no converge en ese presupuesto lo resuelve una persona.",
         "Cómo baja el número de fallos de una pasada a la siguiente, qué fallos no se corrigen solos y la lista "
         "final de cifras sin respaldo.")

instrucciones, aportacion, guia = exigir(exp / "09-instrucciones.md"), exigir(exp / "aportacion.md"), exigir(exp / "07-voz.md")
rango = json.loads(exigir(exp / "07-voz-medidas.json"))["rango"]
verificadas = [f for f in leer_csv(exp / "08-evidencias.csv") if f["estado"].strip().lower() == "verificada"]
ctx = de_optimizacion(caso, exp)
respaldo = normalizar(" ".join(f["afirmacion"] + " " + f["fragmento"] for f in verificadas) + " " + aportacion)
SISTEMA = (SOLO_FUENTES + "Redactas en español de España. Usa solo las cifras y hechos de las afirmaciones verificadas y de la "
           "aportación original. Lo que no puedas respaldar se escribe como PENDIENTE: [qué falta]. No inventes experiencias.")
FORMATO = ("La primera línea es «TITULO: …» (60 caracteres como máximo, con la consulta principal) y la segunda «DESCRIPCION: …» "
           "(entre 135 y 145 caracteres). Después el artículo en Markdown, con un único «# ». "
           "Escribe en PIRÁMIDE INVERTIDA: el párrafo de entrada responde la consulta principal en sus dos primeras frases "
           "(lo esencial arriba) y luego el texto va desglosando de lo más buscado a lo más específico. "
           "NO conviertas cada pregunta en una sección: agrupa y usa como mucho 5-7 secciones «## ». Cada sección abre con su "
           "respuesta en una frase clara de 30 palabras o menos que nombra el tema, sin remitir a lo anterior, y después "
           "desarrolla en prosa fluida y con voz, no en lista de preguntas sueltas.")
material = (f"CONSULTA PRINCIPAL: {ctx['principal']}\nCONSULTAS DEL GRUPO: {'; '.join(ctx['consultas_grupo'])}\n"
            f"PREGUNTAS DE GOOGLE: {'; '.join(ctx['preguntas_google'])}\nPREGUNTAS A ASISTENTES: {'; '.join(ctx['preguntas_asistentes'])}\n"
            f"BÚSQUEDAS QUE LANZAN LOS ASISTENTES: {'; '.join(ctx['fan_out'])}\n\nINSTRUCCIONES\n{instrucciones}\n\nAFIRMACIONES VERIFICADAS\n"
            + ("\n".join(f"- {f['id']}: {f['afirmacion']}" for f in verificadas) or "ninguna")
            + f"\n\nAPORTACIÓN ORIGINAL\n{aportacion}\n\nGUÍA DE VOZ\n{guia}")


def criticar(texto):
    titulo = (re.search(r"^TITULO:\s*(.+)$", texto, flags=re.M) or [None, ""])[1].strip()
    descripcion = (re.search(r"^DESCRIPCION:\s*(.+)$", texto, flags=re.M) or [None, ""])[1].strip()
    cuerpo = re.sub(r"^(TITULO|DESCRIPCION):.*$", "", texto, flags=re.M).strip()
    fallos = [f"Voz · {d}" for d in desviaciones(medir(cuerpo), rango, voz["medidas_a_ignorar"])]
    fallos += [f"Voz · fórmula prohibida: «{c}»" for c in cliches(cuerpo, voz["cliches_extra"])]
    fallos += [f"{f['bloque']} · {f['control']} ({f['valor']}). {f['detalle']}".strip()
               for f in controles(cuerpo, titulo, descripcion, len(re.findall(r"^# ", cuerpo, flags=re.M)), ctx) if f["resultado"] == "NO"]
    cifras = sorted({m for m in re.findall(r"\d+(?:[.,]\d+)?", cuerpo) if len(m) > 1})
    return fallos, [x for x in cifras if x not in respaldo]


texto = pedir(caso, exp, "10-borrador-v0", SISTEMA, f"Redacta la pieza siguiendo las instrucciones. {FORMATO}\n\n{material}",
              max_tokens=6000, seco=op["seco"], fresco=op["fresco"])
if texto is None:
    raise SystemExit("\nModo --seco: prompt guardado en prompts/10-borrador-v0.md, sin llamar al modelo.")
fallos, sin_respaldo = criticar(texto)
print(f"\n  Versión 0: {len(texto.split())} palabras · {len(fallos)} fallos medidos")
for n in range(1, voz["max_revisiones"] + 1):
    if not fallos:
        break
    (exp / f"10-borrador-v{n - 1}.md").write_text(texto, encoding="utf-8")
    for f in fallos:
        print(f"    - {f[:150]}")
    texto = pedir(caso, exp, f"10-borrador-v{n}", SISTEMA,
                  "Corrige el borrador para resolver SOLO los fallos de la lista, sin añadir datos nuevos ni cambiar lo que "
                  f"ya funciona. {FORMATO}\n\nFALLOS MEDIDOS\n" + "\n".join(f"- {f}" for f in fallos)
                  + f"\n\nBORRADOR\n{texto}\n\nMATERIAL DE REFERENCIA\n{material}", max_tokens=6000, fresco=op["fresco"])
    anteriores = len(fallos)
    fallos, sin_respaldo = criticar(texto)
    print(f"\n  Versión {n}: {len(texto.split())} palabras · {len(fallos)} fallos medidos (antes {anteriores})")
(exp / "10-borrador.md").write_text(texto, encoding="utf-8")
print(f"\n  -> 10-borrador.md\n  Fallos que quedan para una persona: {len(fallos)}")
for f in fallos:
    print(f"    - {f[:150]}")
print(f"  Marcas PENDIENTE: {texto.count('PENDIENTE')}")
print(f"  Cifras que no están en las evidencias verificadas ni en la aportación: {', '.join(sin_respaldo) or 'ninguna'}")
print("\n  Tarea manual: resolver cada cifra sin respaldo y cada fallo restante antes de pasar a revisión.")
