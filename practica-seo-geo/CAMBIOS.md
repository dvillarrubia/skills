# Cambios durante la preparación

## 2026-11-11 · El modelo que etiqueta y redacta pasa a ser Claude Code

**Qué fallaba.** El modelo configurado era el alias `gemini-flash-latest`. En la preparación devolvió
errores repetidos en los pasos 1 y 3: cuatro intentos seguidos con `503 "high demand"` y un `ReadTimeout`
a los 600 s. El alias enruta al modelo más nuevo, hoy saturado. Inservible para una clase en directo.

**Qué se ha cambiado (a petición del docente).**

- `sop/llm.py`: nuevo proveedor `claudecode`. No llama a ninguna API; Claude Code (la sesión del docente)
  hace de modelo. Las respuestas se guardan en `crudo/llm-*.json` igual que las de Gemini, así que en clase
  se reutilizan sin ninguna llamada externa. Si falta una respuesta, el script se detiene con instrucciones
  en vez de llamar a Gemini. `disponible()` devuelve `True` para este proveedor.
- `caso.toml` `[modelo]`: `proveedor = "claudecode"`. `nombre_gemini` se fija en `gemini-2.5-flash`
  (modelo estable) **solo** para el asistente del paso 4, que mide un asistente de IA real con búsqueda de
  Google y por eso sí sigue siendo Gemini.

**Qué NO se ha tocado.** La lógica del método: umbrales, fórmulas de prioridad, agrupaciones, notas,
controles de optimización y la verificación de cada cita contra su fuente siguen en Python y en `caso.toml`.
Solo cambia quién redacta y etiqueta. Los pasos 1 y 2 ya se habían completado con Gemini antes del cambio;
sus capturas se conservan.
CAMBIOS: bug paso 3b (nombre de captura por competidor) corregido 2026-11-11

## 2026-11-11 · Los 4 cambios de proceso (flujo corregido)
1. Orden: el tono (paso 7) se presenta en el Bloque 1 junto a ICP/pains (ver carpeta DEMO/).
2. Nuevo paso `03b_keywords_competidores.py`: mina con DataForSEO las keywords por las que rankean
   los competidores de la SERP y marca las relevantes que no teníamos. Nuevo límite
   `competidores_keywords` en caso.toml.
3. Expertise del cliente (`fuentes-cliente/barsel-contexto.md`) integrado en el pipeline como
   afirmaciones verificadas C1–C4 en 08-evidencias.csv, para que el borrador pueda usarlo.
4. Plantilla del paso 10 cambiada a PIRÁMIDE INVERTIDA (respuesta arriba, profundizar hacia abajo,
   5–7 secciones, prosa fluida) en vez de una sección-pregunta por cada PAA.
