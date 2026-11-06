# Plantilla del perfil de tono

Rellena esta plantilla con los datos del JSON de metricas. Cada afirmacion debe apoyarse en una metrica o en una cita real del corpus. Si algo no se puede sostener con los datos, dejalo fuera o marcalo como no concluyente.

```markdown
---
tipo: tono-de-voz
fuente: tone-analyzer
marca: [nombre]
urls_analizadas: [n]
fecha: [YYYY-MM-DD]
---

# Tono de voz — [nombre]

## En una frase
[La voz en 1-2 lineas. Ej.: "Cercana, directa y orientada al lector, anclada en datos concretos."]

## Registro y persona
- Formalidad: [tuteo / usted], [cercano / corporativo / institucional]
- Persona: [yo (marca personal) / nosotros (equipo) / orientada al tu]
- Legibilidad: [etiqueta] (Fernandez-Huerta [n])

## Ritmo y estructura
- Frase: [media] palabras de media, [distribucion: ej. "mezcla frases cortas de impacto con otras medias"]
- Parrafo: [corto / medio / largo]
- Puntuacion caracteristica: [preguntas / exclamaciones / dos puntos / guiones / parentesis...]

## Lexico
- Palabras ancla: [de palabras_top y n-gramas, ya filtrado el ruido]
- Jerga o terminos propios: [...]
- Palabras a evitar (chirrian con esta voz): [...]

## Senas de identidad
[2-4 patrones reconocibles: aperturas en forma de pregunta, cierres con llamada a la accion, datos siempre con cifra, frases cortas para rematar una idea...]

## Ejemplos reales
> [cita textual del corpus]
> [cita textual del corpus]
> [cita textual del corpus]

## Prompt de estilo (reutilizable)
Escribe como [nombre]: [instrucciones operativas en imperativo, destiladas de todo lo anterior —
registro, persona, longitud de frase, lexico, puntuacion, que hacer y que evitar—, pensadas para
pegar como instruccion de estilo al generar textos nuevos con esta voz].
```

## Consejos

- El **prompt de estilo** del final es lo mas util del documento: debe poder copiarse y pegarse como instruccion para que cualquier agente (o tu mismo) escriba con esa voz. Hazlo concreto y accionable, no descriptivo.
- Separa lo que es **voz de marca** de lo que es **tema**: que una web hable mucho de "precios" es tema; como lo dice (con cifras, con preguntas, tuteando) es voz.
- Si analizas a un competidor, el perfil sirve para decidir **en que diferenciarte**, no solo para imitar.
