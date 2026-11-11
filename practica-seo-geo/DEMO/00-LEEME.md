# DEMO · Café Barsel — «molienda para cafetera italiana»

Carpeta de **presentación** de la práctica, ordenada por los 4 bloques del proceso.
Empieza por **`informe-visual.html`** (ábrelo en el navegador: es el resumen con todo de un vistazo).

> Esta carpeta es la **foto limpia** del trabajo. El motor que lo genera (scripts, `caso.toml`,
> `sop/`) y el expediente de trabajo en bruto (`expedientes/…`, con capturas de API y logs) viven
> fuera de aquí. Si re-ejecutas un paso en clase, se actualiza el expediente; luego se vuelve a
> volcar aquí.

---

## El proceso, en 4 bloques

### 1 · Cliente y público — *¿a quién le hablamos y con qué voz?*
Antes de escribir nada, entendemos a la marca y a su gente.
- `tono-de-marca.md` — cómo escribe Barsel (sacado de sus propios textos): reglas, tics a evitar y reescrituras. `tono-medidas.json` son las 10 medidas de estilo; `tono-prueba-ciega.md`, un juego para clase.
- `icp-perfil.md` + `icp-pains.csv` — el cliente ideal y sus dolores, sacados de **fuentes externas** (foros, preguntas de Google), cada uno con cita verificada (confirmado / hipótesis).
- `voz-del-publico.csv` — las palabras reales con las que la gente describe el problema.

### 2 · Investigación — *¿qué se busca y quién manda en Google e IA?*
- `keywords.csv` — investigación de palabras clave (volumen, dificultad y posiciones, con DataForSEO).
- `demanda-observada.csv` — autocompletado y relacionadas de Google.
- `preguntas-google-paa.csv` — las *people also asked*.
- `serp-resultados.csv` + `serp-grupos.csv` — quién rankea y cómo se agrupan las consultas.
- `respuesta-ia-google.csv` — cuándo aparece la respuesta de IA de Google y a quién enlaza.
- `visibilidad-ia-*.csv` + `respuestas-de-ia/` — si la marca sale citada/mencionada/ausente en un asistente, sus fuentes y el *fan-out*.
- `competidores-corpus/` — el **texto completo** de las páginas que rankean (propias P1–P3 y competencia P4–P7).

### 3 · Briefing — *el encargo, cruzando datos + expertise del cliente*
- `cobertura-vs-competencia.csv` — matriz de qué temas cubre cada competidor y dónde están los huecos.
- `evidencias-verificadas.csv` — las afirmaciones comprobables que la pieza puede usar (verificadas por el docente).
- `aportacion-original.md` — lo que aporta la pieza que nadie más tiene.
- `expertise-del-cliente.md` — el conocimiento de primera mano de la marca (en real lo aporta el cliente; aquí simulado para la demo).
- `briefing.md` — el encargo editorial que junta todo lo anterior.

### 4 · Redacción — *del briefing al contenido, auditado*
- **`PIEZA-FINAL.md`** — la pieza buena: fluida, con voz de tostador y la cata del cliente. **Esta es la que se enseña.**
- `revision-final.md` — la revisión por rúbrica (nota y bloqueos).
- `auditoria-optimizacion.csv/.md` — los controles de Google e IA sobre la pieza y sobre la página actual.
- `anexos-del-proceso/` — el borrador automático «GEO» (el *antes* que suena a IA) y sus versiones intermedias. Útil para enseñar el contraste; no es la pieza final.

---

## Para la demo (orden sugerido)
1. Abre `informe-visual.html`.
2. Bloque 1 → 2 → 3 → 4, en ese orden.
3. Remata con `momentos-de-clase.md` (los hallazgos que más impactan) y el contraste
   `anexos-del-proceso/borrador-automatico-geo.md` **vs** `PIEZA-FINAL.md`.
