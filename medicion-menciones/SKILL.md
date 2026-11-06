---
name: medicion-menciones
description: Mide cada semana si la IA menciona y cita una marca, por ICP y por fase, a partir de una batería fija de preguntas. Úsala cuando pidan «mide las menciones», «línea base de menciones» o «informe semanal de visibilidad en IA».
---

# Medición de menciones por ICP y fase

El script cuenta, tú interpretas y una persona decide.

**Dónde está cada cosa.** Los scripts y los ejemplos están en la carpeta de esta skill (la que contiene este `SKILL.md`); en los comandos aparece como `<skill>`. Trabaja siempre en la carpeta de trabajo de la persona: ahí van su batería, su `marcas.json`, las ejecuciones y los resultados. No escribas nada dentro de la carpeta de la skill. En Windows usa `python` o `py -3`; en Mac, `python3`.

## Entradas

- **La batería** (`preguntas.csv` en la carpeta de trabajo): una pregunta por fila, etiquetada con ICP, pain, fase y redacción. Si no la tiene, cópiale `<skill>/bateria/plantilla-bateria.csv` para rellenarla, o usa el ejemplo `<skill>/preguntas.csv` para practicar. No cambies una batería sin el OK de una persona.
- **`marcas.json`** (en la carpeta de trabajo): la marca objetivo, la competencia con sus alias y los dominios conocidos. Si no lo tiene, cópiale `<skill>/marcas.json` como punto de partida: es un ejemplo con marcas ficticias.
- **Las respuestas en bruto**, de una de estas dos formas:
  - pegadas a mano en una carpeta, un archivo por respuesta, con la cabecera de los ejemplos de `<skill>/respuestas-demo/`;
  - lanzadas con `lanzar_bateria.py`, que SIMULA por defecto.

## Pasos

1. **Comprueba la batería:** cada pregunta tiene id único, ICP, fase y redacción. Si falta algo, para y dilo.
2. **Consigue las respuestas.**
   - Si son a mano, comprueba que la carpeta tiene todas las previstas.
   - Si son por API, primero simula:

     ```bash
     python <skill>/lanzar_bateria.py --bateria preguntas.csv --precios precios.json --modelos <modelos> --repeticiones 3 --tope-usd <tope> --salida ejecuciones
     ```

   - Solo con el OK expreso de la persona, y con la clave en `OPENROUTER_API_KEY`, repite con `--real`. Nunca subas el tope por tu cuenta. `precios.json` debe tener los precios reales: `<skill>/precios-ejemplo.json` solo sirve para simular.
3. **Consolida** en una carpeta de resultados nueva:

   ```bash
   python <skill>/consolidar_menciones.py <carpeta-respuestas> --bateria preguntas.csv --marcas marcas.json --salida resultados/<fecha>
   ```

4. **Lee en bruto al menos 10 respuestas antes de redactar:**
   - las de las celdas con el porcentaje más alto y más bajo;
   - todas las que salgan en «Avisos»;
   - alguna de cada modelo.
5. **Redacta el informe** con `<skill>/plantilla-informe.md`, en `resultados/<fecha>/informe-borrador.md`.
   - Da cada cifra con su n y su rango entre redacciones.
   - En descubrimiento cuenta la cita; en consideración y decisión, la mención y la posición.
   - Separa las preguntas con marca de las de sin marca.
6. **Ejecuta la alarma** si viene de una rutina: `python <skill>/alarma.py --carpeta ejecuciones`.

## Reglas

- Modo borradores: no publiques, no envíes y no borres nada. El informe es un borrador para que lo revise una persona.
- Una sola respuesta no es un dato. Una celda con menos de 6 respuestas se marca como poco fiable.
- No inventes marcas, dominios ni cifras. Lo que el script lista en «Avisos» se revisa, no se corrige a ojo.
- Las preguntas o los ICP nuevos que se te ocurran van a `resultados/<fecha>/propuestas.md`, no a la batería.
- No confundas tu medición con el dato de una herramienta de pago ni una mención con una recomendación: lee el contexto.
- Para una rutina programada, sigue `<skill>/RUTINA.md`.
