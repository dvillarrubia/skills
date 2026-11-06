---
name: tone-analyzer
description: Extrae el tono de voz de una persona o negocio a partir de 10-20 URLs y produce un perfil de estilo reutilizable para escribir imitandolo. Un script scrapea las paginas y mide senales objetivas (longitud de frase, persona, tuteo/usted, lexico, legibilidad); tu interpretas y redactas el perfil. Usala cuando alguien quiera "escribir como" una web o clonar la voz de una marca.
---

# tone-analyzer

Sacas el tono de voz de una persona o negocio analizando su propia web. El script `tono.py` scrapea 10-20 URLs, limpia la prosa y **mide senales objetivas**; nunca adivina el tono. La parte cualitativa —interpretar esas senales y redactar el perfil— la haces tu con los datos delante, citando ejemplos reales del texto, no inventados.

Flujo en una linea: reunir URLs → `python tono.py full` → leer el JSON → redactar el perfil con la plantilla.

## Que necesitas

- **Python 3** y las dependencias del `requirements.txt`. Instalalas una vez:
  ```bash
  pip install -r requirements.txt
  ```
  (En algunos equipos el comando es `python3` y `pip3` en vez de `python`/`pip`.)
- **10-20 URLs del mismo autor o marca.** Si la persona no las da, pideselas. Cuanta mas prosa real, mejor: pagina "sobre mi", 3-6 articulos de blog, fichas de servicio, notas de prensa. Evita paginas sin prosa (login, carrito, avisos legales) y la portada si es solo tarjetas y enlaces.

Si no puedes ejecutar Python en tu entorno, dilo y para: el perfil necesita el texto real, no lo que creas saber de la marca.

## Como se usa

1. **Reunir las URLs.** Si la persona no las tiene claras, propon una lista variada a partir de su web, ensenasela y espera a que la confirme. Puedes guardarlas en un `urls.txt` (una por linea, `#` para comentar).

2. **Scrapear y medir:**
   ```bash
   python tono.py full urls.txt --out ./salida --name marca
   ```
   o pasando las URLs sueltas:
   ```bash
   python tono.py full https://marca.com/sobre https://marca.com/blog/post-1 --out ./salida --name marca
   ```
   Genera dos ficheros en `--out`:
   - `marca-corpus.json` — el texto limpio de cada pagina.
   - `marca-metricas.json` — las senales de estilo (esto es lo que lees).

3. **Revisar la cobertura.** Mira `cobertura` en el JSON. Si han fallado muchas URLs o `ok` es menor que 8, avisa y pide mas antes de concluir: un perfil con poco texto no es fiable. Si fallan por JavaScript (webs que cargan todo con JS), pide URLs de articulos con contenido en el HTML.

4. **Interpretar y redactar.** Lee `references/guia-metricas.md` para traducir cada metrica a rasgos de tono. Luego redacta el perfil con `references/plantilla-perfil.md`. **Cita siempre ejemplos reales** del bloque `ejemplos_reales` del JSON; nunca te inventes frases de la marca.

5. **Guardar el perfil** donde la persona lleve sus notas, con un nombre claro tipo `tono-de-marca.md`.

## Reglas

- **Gramatica y ortografia impecables** en el perfil y en cualquier texto que generes con el, aunque la fuente escriba descuidada: mayusculas, tildes y puntuacion sin excepciones.
- El script **no ejecuta JavaScript**: en webs 100% dinamicas puede sacar poco texto. No es un fallo del script; pide otras URLs.
- Rate limiting por defecto 1s entre peticiones (`--delay`). Subelo si el dominio responde lento.
- Esto **deriva el tono de textos que ya existen**. Para definir una voz desde cero por conversacion (una marca que aun no escribe), esta no es la skill adecuada.

## Modos del script

| Comando | Que hace |
|---|---|
| `python tono.py full <urls>` | Scrapea y mide en una pasada (lo habitual). |
| `python tono.py scrape <urls>` | Solo descarga y limpia el texto (genera el corpus). |
| `python tono.py metrics <corpus.json>` | Recalcula metricas sobre un corpus ya scrapeado. |

Opciones: `--out` carpeta de salida, `--name` nombre base de los ficheros, `--delay` segundos entre peticiones, `--timeout` por peticion.
