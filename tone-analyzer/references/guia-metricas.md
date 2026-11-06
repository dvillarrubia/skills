# Como leer el JSON de metricas

El script mide; tu interpretas. Cada campo es una senal objetiva. Tradúcelas a rasgos de tono y crúzalas entre si (una sola metrica no define una voz).

## Resumen y cobertura

- `resumen` — cuantos documentos, palabras, frases y parrafos sostienen el analisis. Con menos de ~1.500 palabras totales, trata el perfil como provisional.
- `cobertura.fallidas` / `urls_fallidas` — URLs que no dieron texto util (404, bloqueo, JavaScript). Si son muchas, el retrato esta sesgado: pide mas URLs.

## Ritmo de la frase

- `frase.longitud_media_palabras` — **<12** telegrafico y directo · **12-20** estandar · **>20** denso, corporativo o academico.
- `frase.distribucion_pct` — si mezcla cortas, medias y largas, el ritmo es dinamico; si casi todo cae en una banda, es monotono. La variedad (ver `desviacion`) suele ser senal de voz trabajada.

## Persona y tratamiento

- `orientacion.dominante` — **`yo`** marca personal (alguien que firma) · **`nosotros`** empresa o equipo · **`tu/vosotros`** orientada al lector (copy, divulgacion).
- `tratamiento` — **tuteo** (cercano, directo) vs **usted** (formal, institucional). Es una de las decisiones mas visibles de una voz.
- `persona_gramatical_por_1000` — el detalle por pronombre, por si conviven varios registros.

## Riqueza del lexico

- `riqueza_lexica.type_token_ratio` — alto = vocabulario variado y rico; bajo = repetitivo o muy centrado en pocas ideas.
- `riqueza_lexica.hapax_pct` — proporcion de palabras que aparecen una sola vez; alto refuerza variedad.
- `riqueza_lexica.longitud_media_palabra` — palabras largas tiran hacia lo tecnico o formal.

## Legibilidad

- `legibilidad.fernandez_huerta` (adaptacion espanola de Flesch): **80+** muy facil · **65-80** facil · **50-65** normal · **30-50** algo dificil · **<30** tecnico. `interpretacion` ya trae la etiqueta.

## Puntuacion (por 1000 palabras)

- `interrogaciones` altas = estilo conversacional, interpela al lector.
- `exclamaciones` altas = enfatico, de marketing o entusiasta.
- `dos_puntos` y `guion_largo` = estilo que introduce, matiza o hace apartes.
- `parentesis` altos = voz que acota y puntualiza.

## Senales de tono

- `llamadas_a_accion_total` alto = copy comercial y directo ("descubre", "solicita", "reserva").
- `numeros_y_datos` y `simbolos_porcentaje_moneda` altos = voz anclada en datos y cifras concretas.
- `emojis` — su presencia (y cuantos) marca registro informal / redes.
- `conectores_formales_total` ("asimismo", "no obstante"...) = registro formal.
- `mayusculas_enfaticas` — palabras en MAYUSCULAS para enfatizar; informal o publicitario.

## Lexico caracteristico

- `palabras_top`, `bigramas_top`, `trigramas_top` — las muletillas, terminos ancla y jerga que hacen reconocible la voz. Filtra el ruido (restos de menus o enlaces) y quedate con lo que de verdad es de la marca. De aqui salen tanto las "palabras ancla" como las "palabras a evitar".

## Ejemplos reales

- `ejemplos_reales` (aperturas, frases cortas y largas, preguntas, exclamaciones) — **usa estas citas literales** en el perfil. Son la prueba de cada afirmacion y lo que hace util el documento. No parafrasees ni inventes.
