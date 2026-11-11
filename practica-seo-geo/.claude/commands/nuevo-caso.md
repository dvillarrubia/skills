---
description: Prepara un caso.toml para otra web
argument-hint: "<dominio> <consulta principal>"
---

Prepara un caso nuevo para: $ARGUMENTS

1. Copia `caso.toml` a `casos/<id>.toml`, con un id corto en minúsculas y guiones. No sobrescribas `caso.toml`.
2. Rellena marca, dominio, consulta principal, variantes, semillas, términos de negocio y entidades clave.
   Pregunta al docente lo que no sepas: público, problema de partida, objetivo y conversión son suyos, no los supongas.
3. Para `[propias]` y `[voz]`, localiza en la web del caso las URLs reales que tocan la consulta y seis textos del
   blog de la marca. Comprueba que responden antes de anotarlas.
4. Propón foros y búsquedas de dolor para `[icp]` y tres preguntas a asistentes, y espera su visto bueno.
5. Explica cómo usarlo: `SOP_CASO=casos/<id>.toml python 00_conexiones.py`, y lo mismo para el resto de pasos.
