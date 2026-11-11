---
description: Prepara el caso completo antes de clase, de principio a fin, parando en los controles humanos
argument-hint: "[desde-paso]"
---

Vas a dejar preparado el ejemplo completo de la práctica para que el docente lo repase con sus alumnos.
El resultado es un expediente real en `expedientes/<id>/`, con capturas guardadas de todas las APIs, y un
`RECORRIDO.md` para ir por encima en clase. Sigue las reglas de CLAUDE.md.

Si `$ARGUMENTS` trae un número, empieza en ese paso y da por hechos los anteriores. Si no, empieza por el principio.

## 1. Entorno

1. Comprueba que existe `.env`. Si no, cópialo de `.env.example`, di al docente qué dos claves gratuitas necesita
   (SERPAPI_API_KEY en serpapi.com y GEMINI_API_KEY en aistudio.google.com) y para aquí. No leas ni muestres `.env`.
2. Crea el entorno si no existe (`python3 -m venv .venv`) e instala `requirements.txt`. Usa `.venv/bin/python` en adelante.
3. Ejecuta `00_conexiones.py`. Si alguna línea no termina en «correcto», explica cuál y cómo se arregla, y para.
   Si el modelo de Gemini configurado no está disponible, propón uno de la lista que imprime el script y espera el visto bueno antes de cambiar `caso.toml`.

## 2. Pasos 1 a 7, uno a uno

Ejecuta en orden `01_icp_pains.py`, `02_consultas.py`, `03_resultados.py`, `04_asistentes.py`, `05_corpus.py`,
`06_cobertura.py` y `07_voz.py`. Después de cada uno:

- Lee su salida y los ficheros que ha escrito. Comprueba que tienen contenido real, no cabeceras vacías.
- Si falla o sale vacío por la forma de la respuesta de una API, aplica el apartado «Si un script falla contra una API real» de CLAUDE.md.
- Da al docente un resumen de tres o cuatro líneas con los datos reales del paso. Sin adornos.

Comprobaciones mínimas, que no son para forzar sino para detectar un fallo técnico:

- Paso 1: hay al menos tres fuentes y algún problema que no esté descartado. Si todos salen descartados, revisa si los foros devolvieron hilos; si no, propón al docente otras búsquedas de dolor o foros en `[icp]` de `caso.toml`.
- Paso 2: hay consultas con relación con el negocio y candidatas marcadas.
- Paso 3: hay resultados orgánicos para la consulta principal y al menos una página comparable.
- Paso 4: hay respuestas con fuentes. Si Gemini responde sin fuentes en todas las ejecuciones, puede que la clave no tenga búsqueda de Google: díselo al docente.
- Paso 5: las páginas propias son evaluables. Enséñale lo que devuelven hoy las URLs antiguas.
- Paso 7: existe `07-prueba-ciega.md`.

## 3. Paso 8: aquí decide el docente

1. Ejecuta `08_evidencias.py` y enseña la lista de afirmaciones.
2. Verificación: para las tres o cuatro cifras más importantes, busca la fuente primaria si tienes acceso a la web
   y propón estado («verificada» o «retirada») y fuente. No toques `08-evidencias.csv` hasta que el docente confirme
   cada una; entonces actualiza solo esas filas, con su nombre como revisor.
3. Aportación original: enséñale los temas de `06-cobertura.csv` marcados «nadie lo prueba» y pregúntale qué puede
   aportar de verdad (una prueba, unos datos, unas fotos). Escribe `aportacion.md` solo con lo que él te diga, con
   qué se hizo, cuándo, con qué material y qué límites tiene. Si prefiere hacerlo más tarde, para aquí y dile cómo
   seguir con `/preparar-ejemplo 9`. No inventes una aportación.

## 4. Pasos 9 a 12

Ejecuta `09_instrucciones.py`, `10_borrador.py`, `11_optimizacion.py` y `12_revision.py`. Tras el 10, enséñale los
fallos que no se corrigieron solos y las cifras sin respaldo: son suyos, no los arregles tú. El paso 13
(seguimiento) no se ejecuta ahora: es para semanas después.

## 5. Recorrido y cierre

1. Ejecuta `recorrido.py`.
2. Escribe en `expedientes/<id>/MOMENTOS.md` de tres a cinco «momentos de clase»: hallazgos reales del expediente
   que merece la pena enseñar (una cita rechazada, una nota anulada, un grupo inesperado, la marca ausente en las
   respuestas, las URLs antiguas). Cada uno con el fichero y la línea donde se ve. Solo cosas que estén en el expediente.
3. Informe final al docente: pasos hechos, búsquedas de SerpApi que quedan (vuelve a ejecutar `00_conexiones.py`),
   cambios anotados en `CAMBIOS.md` y decisiones que siguen pendientes de él.

Recuerda que en clase bastará con ejecutar cada script sin `--fresco`: usará estas capturas.
