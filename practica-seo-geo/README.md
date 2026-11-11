# Práctica real del SOP de contenidos SEO y GEO

Catorce scripts que recorren el SOP de principio a fin sobre una web real, con peticiones reales a APIs
sencillas y gratuitas (SerpApi, Jina Reader y Gemini), y DataForSEO como opción de pago para lo que no tiene
alternativa gratuita. Cada script explica en pantalla qué
hace, por qué y qué hay que mirar antes de ejecutar nada, para leerlo en voz alta en clase.

El caso configurado es **Café Barsel** (cafebarsel.com) y la consulta de partida «molienda para cafetera
italiana». Para cambiar de caso se edita `caso.toml`; los scripts no se tocan.

Para prepararlo todo en una sesión de Claude Code, empieza por `ARRANQUE.md`.

## Principio de diseño

Python decide; el modelo solo escribe. Los umbrales, los filtros, las agrupaciones, la prioridad de cada
consulta, la nota final y la decisión de publicar están en código y en `caso.toml`. El modelo etiqueta,
extrae y redacta, y todo fragmento que cita se busca después en la fuente original. Si no está, no cuenta.

## De dónde salen los datos

Con dos claves gratuitas funciona toda la práctica. Cada servicio se elige en `[apis]` de `caso.toml`.

| Para qué | Por defecto (gratis) | Dónde se consigue | Alternativa de pago |
| --- | --- | --- | --- |
| Resultados de Google, preguntas relacionadas y autocompletado | SerpApi, plan gratuito con un cupo mensual de búsquedas | serpapi.com → registrarse → Your Private API Key | DataForSEO SERP API |
| Leer una página como texto limpio | Jina Reader: se antepone `r.jina.ai/` a la URL; no necesita clave | jina.ai/reader (la clave es opcional y sube el límite) | Extracción local con `lector = "local"`, también gratis |
| Asistente de IA con fuentes y búsquedas | Gemini con búsqueda de Google | aistudio.google.com → Get API key | DataForSEO LLM Scraper: ChatGPT tal como lo ve un usuario |
| Modelo que etiqueta y redacta | Gemini, con la misma clave | aistudio.google.com | Anthropic (`proveedor = "anthropic"`) |
| Volumen, dificultad y posiciones del dominio | No hay opción gratuita: se trabaja con demanda observada, sin volumen | — | DataForSEO Labs (`volumenes = "dataforseo"`) |

Una pasada completa del caso gasta unas 30 búsquedas de SerpApi y unas 25 llamadas a Gemini. Los cupos gratuitos
cambian: compruébalos en la página de precios de cada servicio antes de clase. `00_conexiones.py` enseña cuántas
búsquedas de SerpApi quedan en el mes.

Lo que cambia sin DataForSEO: el paso 2 prioriza por veces que Google muestra cada consulta en lugar de por
volumen, y el paso 4 mide Gemini, no ChatGPT. El método y los controles son los mismos.

## Los cuatro pilares

| Pilar | Paso | Datos reales | Qué decide Python |
| --- | --- | --- | --- |
| ICP, pains y journey | 1 | Hilos de foros localizados con una búsqueda `site:`, preguntas de Google, autocompletado y, si existen, entrevistas o reseñas en `fuentes-cliente/` | Cada cita se busca en su fuente; un problema es «confirmado» con 2 fuentes independientes, «hipótesis» con 1 y se descarta con 0 |
| Investigación de palabras clave | 2 y 3 | Autocompletado, preguntas y búsquedas relacionadas de Google; resultados de las candidatas. Con DataForSEO Labs, además volumen, dificultad y posiciones | Prioridad por fórmula visible (veces observada o volumen, evidencia del problema); grupos por solape del top 10; acción por grupo |
| Optimización para Google y para IA | 4, 10 y 11 | Respuestas de un asistente con búsqueda (Gemini por defecto) con sus fuentes y búsquedas fan-out; página publicada de la marca | 19 controles legibles en tres bloques (Google, asistentes, técnico), aplicados a la página actual y al borrador |
| Tono y voz | 7 y 10 | Seis textos publicados por la marca, uno de ellos reservado | Diez medidas de estilo con su rango; ejemplos verificados; fórmulas prohibidas; el borrador se corrige contra esas medidas |

## Preparación (una vez)

```bash
python -m venv .venv && source .venv/bin/activate      # Python 3.11 o superior
pip install -r requirements.txt
cp .env.example .env                                   # y rellenar SERPAPI_API_KEY y GEMINI_API_KEY
python 00_conexiones.py
```

## Dos opciones en todos los scripts

- `--seco`: enseña la petición exacta que se enviaría, sin gastar nada. Sirve para explicar la API antes de llamarla.
- `--fresco`: ignora la captura guardada y vuelve a pedir. Sin esta opción, una captura ya guardada se reutiliza.

Ese comportamiento es el respaldo de la clase: se ejecuta todo el día anterior y, si en directo falla la
red o una API, el script sigue con la captura fechada. Para hacerlo en vivo de verdad, se añade `--fresco`.

## Guion de la sesión

| Paso | Comando | Qué explicar | Trabajo del grupo | Min |
| --- | --- | --- | --- | --- |
| 0 | `python 00_conexiones.py` | Qué servicios usamos y qué cubre cada uno en España | — | 5 |
| 1 | `python 01_icp_pains.py` | Un perfil de cliente sin citas es una opinión; confirmado frente a hipótesis | Comparar con la hipótesis de `caso.toml`; decidir qué fuente falta | 30 |
| 2 | `python 02_consultas.py` | Volumen estimado, nulo no es cero; la fórmula de prioridad y sus factores | ¿Cambiamos de consulta principal? | 25 |
| 3 | `python 03_resultados.py` | Agrupar por resultados, no por parecido; formato desde la SERP; respuesta de IA | Discutir la acción por grupo y la canibalización | 20 |
| 4 | `python 04_asistentes.py` | Citada, mencionada o ausente; por qué se repite; qué es el fan-out | Leer dos respuestas en `04-respuestas/` | 25 |
| 5 | `python 05_corpus.py` | HTML frente a texto limpio; «no evaluable» no es «ausente»; URLs antiguas | Cotejar una extracción con su página | 10 |
| 6 | `python 06_cobertura.py` | Notas con fragmento verificado; hueco por regla con umbral | Revisar los huecos prioritarios | 15 |
| 7 | `python 07_voz.py` | Voz medida más listón editorial; qué se imita y qué no | Prueba ciega con `07-prueba-ciega.md` | 30 |
| 8 | `python 08_evidencias.py` | Publicado no significa verificado | Verificar tres afirmaciones y escribir `aportacion.md` | 15 |
| 9 | `python 09_instrucciones.py` | Control: sin aportación original, el script se detiene | Aprobar la decisión sobre la URL | 10 |
| 10 | `python 10_borrador.py` | El crítico es código: fallos medidos, presupuesto fijo de pasadas | Resolver cifras sin respaldo y fallos que no convergen | 25 |
| 11 | `python 11_optimizacion.py` | Qué significa de forma comprobable «optimizado para Google y para IA» | Página actual frente a borrador; qué control sobra o falta | 15 |
| 12 | `python 12_revision.py` | La nota la calcula Python; la decisión la firma una persona | Leer bloqueos y decidir | 10 |
| 13 | `python 13_seguimiento.py` | Solo se compara lo que se midió igual; correlación no es causa | — | 5 |

Total: 240 minutos, en cuatro sesiones de una hora (pasos 0–2, 3–6, 7–9 y 10–13). Los minutos son una
estimación de planificación; conviene cronometrar la primera edición. El paso 11 también se puede ejecutar
justo después del 5 para auditar la página actual antes de tener borrador.

## Qué se puede tocar en clase sin programar

Todo esto está en `caso.toml` y cambia el resultado al volver a ejecutar:

- `[icp]`: foros, búsquedas de dolor y cuántas fuentes hacen falta para confirmar un problema.
- `[caso] terminos_negocio`: la regla que decide si una consulta tiene relación con el negocio.
- `[limites] umbral_solape_serp`: cuándo dos consultas van a la misma página.
- `[voz] principios`: el listón editorial. `medidas_a_ignorar`: qué hábitos de la marca no se imitan.
- `[voz] max_revisiones`: cuántas pasadas de corrección tiene el borrador.

La fórmula de prioridad está en `02_consultas.py`, los controles de optimización en `sop/optimizacion.py`
y la lista de fórmulas prohibidas en `sop/estilo.py`. Son cortos a propósito, para proyectarlos y discutirlos.

## Qué queda en el expediente

Todo se escribe en `expedientes/<id del caso>/`:

- `00-encargo.md`, `01-cliente.md`, `01-pains.csv`, `01-voz-cliente.csv`, `01-demanda-observada.csv`, `aportacion.md`
- `02-consultas.csv`
- `03-resultados.csv`, `03-grupos.csv`, `03-preguntas-google.csv`, `03-respuesta-ia-google.csv`
- `04-asistentes.csv`, `04-fuentes.csv`, `04-fan-out.csv`, `04-respuestas/`
- `05-corpus/` (HTML original, texto limpio e `indice.csv`)
- `06-cobertura.csv`
- `07-voz.md`, `07-voz-medidas.json`, `07-prueba-ciega.md` y su solución
- `08-evidencias.csv`, `09-instrucciones.md`
- `10-borrador.md` y sus versiones intermedias
- `11-optimizacion.md`, `11-optimizacion.csv`, `12-revision.md`, `13-seguimiento.csv`
- `crudo/`: cada respuesta original de DataForSEO y del modelo, con fecha y petición
- `prompts/`: cada prompt enviado, para proyectarlo y discutirlo
- `costes.csv`: el coste de cada llamada a DataForSEO, si se usa

## Límites del caso

Es una web de terceros. No hay Search Console, analítica ni experto del negocio, y el expediente lo dice.
Por eso «confirmado» en el paso 1 significa que varias fuentes públicas describen el problema, no que sea
el del cliente de esta marca. Con un cliente propio, las entrevistas, reseñas y tickets se dejan como `.txt`
anonimizados en `fuentes-cliente/` y entran en el mismo análisis.

Los rangos de estilo salen de cinco textos: describen esos textos, no toda la marca. Los controles de
optimización son condiciones comprobables, no causas demostradas de posicionar o de ser citado.

Nada de lo que salga de la práctica se publica en esa web. La descarga de páginas respeta `robots.txt`;
si un foro no permite leer el hilo, se usa solo el titular y el fragmento que muestra Google.

## Estado de las pruebas

Probado con datos reales: Jina Reader y la extracción local sobre cafebarsel.com y otras webs, la estilometría
sobre los seis textos de Barsel, los controles de optimización y técnicos sobre su página publicada, y los
controles que detienen el flujo. Las peticiones a SerpApi, Gemini y DataForSEO siguen su documentación, pero no
se han ejecutado con credenciales: el análisis de sus respuestas se ha probado solo con capturas de ejemplo con
la forma documentada. La primera ejecución completa hay que hacerla antes de clase, no en clase. A vigilar en
esa primera ejecución: el nombre del modelo de Gemini (el paso 0 lista los disponibles), si la clave gratuita
de Gemini admite la búsqueda de Google en vuestra cuenta, y el cupo de SerpApi.
