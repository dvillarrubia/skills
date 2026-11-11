# Recorrido del caso · Barsel · «molienda para cafetera italiana»

Generado el 2026-11-11 a partir de `expedientes/barsel-cafetera-italiana/`. Solo resume lo que ya está en el expediente.

## 1 · ICP, pains y journey — hecho

`python 01_icp_pains.py`

- 32 fuentes analizadas · 7 problemas confirmados, 2 hipótesis, 0 descartados
- 0 citas rechazadas porque no estaban literalmente en su fuente
- D6 (confirmado, 3 fuentes): La temperatura del agua mal ajustada estropea la extracción
- D1 (confirmado, 2 fuentes): La molienda demasiado fina sobreextrae en la cafetera italiana
- D2 (confirmado, 2 fuentes): La infusión queda infraextraída en la moka

Abrir: `01-cliente.md`, `01-pains.csv`

Para debatir: ¿la hipótesis de partida sale confirmada, matizada o desmentida?

## 2 · Palabras clave — hecho

`python 02_consultas.py`

- 90 consultas · 90 con relación con el negocio · 43 asociadas a un problema
- La consulta principal de partida queda en el puesto 2
- Cinco primeras por prioridad: mejor molienda para cafetera italiana (6.0); molienda para cafetera italiana (4.0); molienda cafetera italiana (4.0); molienda para cafetera italiana numero (4.0); molienda recomendada para cafetera italiana (4.0)

Abrir: `02-consultas.csv`

Para debatir: ¿cambiamos de consulta principal?

## 3 · Google por intención — hecho

`python 03_resultados.py`

- 9 grupos de consultas por solape de resultados
- Grupo de la consulta principal: molienda para cafetera italiana; molienda para cafetera italiana numero → crear: ninguna URL propia en los primeros resultados
- 40 preguntas de Google observadas
- Respuesta de IA en Google: 18 fuentes enlazadas, 0 propias

Abrir: `03-grupos.csv`, `03-resultados.csv`

Para debatir: ¿basta que dos URLs propias aparezcan en un grupo para hablar de canibalización?

## 4 · Asistentes de IA — hecho

`python 04_asistentes.py`

- 3 respuestas capturadas en Claude Code con búsqueda web
- «Mi café de cafetera italiana sale amargo, ¿qué estoy haciendo mal?»: citada 0, mencionada 0, ausente 1
- «¿Qué molienda necesito para una cafetera italiana si compro café en grano?»: citada 0, mencionada 0, ausente 1
- «¿Qué café de especialidad me recomiendas comprar online en España para cafetera italiana?»: citada 0, mencionada 0, ausente 1
- Dominios más citados: cafeselcriollo.com (2), sanjorge.cafe (2), vitaleco.com.uy (1), blackdrop.cl (1), mejorcafetera.com (1)
- 3 búsquedas fan-out distintas

Abrir: `04-asistentes.csv`, `04-fuentes.csv`, `04-respuestas/`

Para debatir: ¿qué diferencia hay entre citada, mencionada y recomendada?

## 5 · Corpus — hecho

`python 05_corpus.py`

- 7 páginas evaluables y 0 no evaluables
- Propias: P1 1441 palabras; P2 1439 palabras; P3 571 palabras
- Incidencias: ninguna

Abrir: `05-corpus/indice.csv`

Para debatir: ¿qué se ha perdido al limpiar una página?

## 6 · Cobertura — hecho

`python 06_cobertura.py`

- 13 temas · 11 cubierto, 2 nadie lo prueba
- 2 notas anuladas porque el fragmento citado no estaba en la página

Abrir: `06-cobertura.csv`

Para debatir: ¿que todos los competidores repitan un tema prueba que haga falta?

## 7 · Voz — hecho

`python 07_voz.py`

- El texto reservado cae dentro del rango de la marca en 9 de 10 medidas
- Prueba ciega lista: `07-prueba-ciega.md` (la solución está en un fichero aparte)

Abrir: `07-voz.md`, `07-prueba-ciega.md`

Para debatir: ¿qué hábitos de la marca decidimos no imitar y por qué?

## 8 · Evidencias y aportación — hecho

`python 08_evidencias.py`

- 9 afirmaciones: 9 verificada
- Aportación original: escrita

Abrir: `08-evidencias.csv`, `aportacion.md`

Para debatir: ¿qué afirmación publicada no hemos podido verificar?

## 9 · Instrucciones editoriales — hecho

`python 09_instrucciones.py`

- Instrucciones editoriales de 870 palabras

Abrir: `09-instrucciones.md`

Para debatir: ¿aprobamos la decisión sobre la URL?

## 10 · Borrador — hecho

`python 10_borrador.py`

- Borrador de 948 palabras tras 2 pasadas de corrección
- Marcas PENDIENTE sin resolver: 0

Abrir: `10-borrador.md`, `prompts/10-borrador-v0.md`

Para debatir: ¿qué fallos no se corrigieron solos?

## 11 · Optimización para Google e IA — hecho

`python 11_optimizacion.py`

- página actual: 10 de 19 controles superados
- borrador: 14 de 14 controles superados

Abrir: `11-optimizacion.md`

Para debatir: ¿qué control quitaríais o añadiríais, y con qué evidencia?

## 12 · Revisión — hecho

`python 12_revision.py`

- Puntuación: 83.8 / 100 · umbral 80 · APTO para revisión humana final

Abrir: `12-revision.md`

Para debatir: ¿quién firma y por qué no puede ser quien redactó?

## 13 · Seguimiento — pendiente

`python 13_seguimiento.py`

Todavía no se ha ejecutado.

## Capturas guardadas

26 de serpapi, 3 de claudecode, 11 de modelo

Sin `--fresco`, cada script reutiliza estas capturas: la clase funciona aunque falle la red.
