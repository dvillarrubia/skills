---
name: eeat-auditor
description: Audita las señales E-E-A-T de un competidor (10 artículos y el bloque de confianza del sitio) en una plantilla fija, con la URL de cada dato o «no consta» / «no comprobado». Úsala para ver con qué señales se gana la cita un competidor y elegir en qué diferenciarte.
---

# eeat-auditor

Rellenas una ficha E-E-A-T de un competidor con una plantilla fija. Tú recoges y citas; la persona valida y decide. Una celda «no consta» es un hallazgo; una celda inventada estropea la ficha entera.

## Qué necesitas

- **Un navegador que puedas manejar** (por ejemplo `/browser`, Chrome DevTools MCP o la herramienta de navegación de tu entorno). Sin él no puedes comprobar nada: dilo y para. No rellenes la ficha desde lo que sabes del sitio.
- **El dominio del competidor.**
- **Los 10 artículos.** Si la persona no te los da, propón los 10 más enlazados desde la portada o el blog del competidor, enséñale la lista y espera a que la confirme.

## Las tres reglas de cada celda

1. **Verificado:** escribe el dato y, al lado, la URL exacta donde lo has visto.
2. **No consta:** lo has buscado en el sitio donde debería estar y no aparece. Escribe `no consta` y la URL donde lo buscaste.
3. **No comprobado:** no has podido verlo (la página no carga, hay un muro de pago, un bloqueo o te falta acceso). Escribe `no comprobado` y el motivo.

No supongas nada. No completes un nombre, una titulación o una fecha porque «suele ser así». Si dudas entre dos opciones, usa «no comprobado».

## Procedimiento

1. **Ficha por artículo.** Abre cada uno de los 10 artículos y rellena la plantilla 1 de `references/plantilla.md`:
   - autor (nombre y página de autor);
   - credenciales (Expertise): titulación, colegiación, experiencia clínica o profesional, tal como aparezcan en la página de autor o en el propio artículo;
   - experiencia de primera mano (Experience): casos propios, fotos o datos originales, pruebas realizadas, relato en primera persona;
   - fuentes citadas: número y tipo (estudios, guías oficiales, organismos, prensa, otros blogs);
   - publicado / revisado: fechas y, si consta, quién revisa;
   - presencia del autor en medios del sector (Authoritativeness): búscala **fuera** del sitio (paso 3).
   Deja la columna «¿Validada a mano?» vacía: es para la persona.
2. **Bloque de confianza del sitio (Trust).** Rellena la plantilla 2: quién está detrás (empresa, razón social, «quiénes somos»), contacto real, política editorial o de revisión médica, avisos en temas sensibles (salud, dinero), reputación en fuentes independientes y schema de autor y organización (`Person`, `Organization`, `sameAs`). Para el schema, mira el JSON-LD del código fuente de la página.
3. **Reputación fuera del sitio.** Busca al competidor y a sus autores en fuentes independientes: reseñas, prensa, colegios profesionales, registros oficiales, publicaciones del sector. Lo que el competidor dice de sí mismo **no** cuenta como reputación; si solo lo encuentras en su propia web, escríbelo así.
4. **Validación.** Deja preparada la plantilla 3 con 3 filas de la plantilla 1 elegidas al azar para que la persona abra las URL y compare. Recuérdale la regla: si fallan dos o más, no debe fiarse de las otras siete, y conviene repetir el encargo con instrucciones más estrictas.
5. **Acciones de diferenciación.** En la plantilla 4, propón **candidatas** (marcadas como propuesta): señales que faltan en el competidor y que la persona podría demostrar en su página. La elección final de las 3 es suya.

## Criterio

- La confianza (Trust) es la letra que más pesa. En salud y dinero (YMYL) el listón es más alto.
- La reputación se comprueba en fuentes independientes, no en la web del competidor.
- El schema ayuda a desambiguar quién es el autor, pero no sustituye a una autoría visible ni garantiza citas.
- No pongas notas ni puntuaciones numéricas: la ficha recoge señales, no las puntúa.

## Entrega

Un único archivo Markdown `eeat-<dominio>-<AAAA-MM-DD>.md` con las cuatro plantillas en este orden, más una línea al principio con el dominio, la fecha y las herramientas que has usado. Después, en el chat, di cuántas celdas son «no consta» y cuántas «no comprobado».

`references/senales.md` resume qué cuenta como señal en cada letra y dónde buscarla.
