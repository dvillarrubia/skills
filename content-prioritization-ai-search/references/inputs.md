# Entradas, definiciones y cómo se ejecuta el script

## Qué puede aportar la persona usuaria
Solo es obligatoria **page o url**. Cualquier otra columna es opcional y convierte un valor por defecto en evidencia.
- **Una URL o unas pocas URL:** lee las páginas y valóralas; no hace falta el script.
- **Un export de Rendimiento de Search Console** (pestaña Páginas, .csv o .xlsx), idealmente comparando el mismo periodo con un año de diferencia. El script reconoce las cabeceras estándar del export: «Top pages», «Clicks», «Impressions» y, en los exports comparativos, «Last 3 months Clicks» y «Previous 3 months Clicks» (vale cualquier redacción del periodo). Si el export está en español («Páginas principales», «Clics», «Impresiones»), renombra las columnas a `url`, `clicks`, `clicks_previous`, `impressions` e `impressions_previous` antes de ejecutarlo.
- **Un inventario completo**, con `templates/content-inventory-template.xlsx` o con las columnas de la propia persona.

## Columnas (los nombres se reconocen de forma flexible; alias entre corchetes)

Los nombres de columna se quedan en inglés porque el script los lee así.

| Columna | Significado |
|---|---|
| page [name, title, page_group] | Nombre de la página o del grupo de páginas |
| url [address, top pages, path, url_pattern] | URL o patrón como /blog/* |
| content_type [type, format, page_type, type_id] | Nombre del tipo, nombre corto en inglés o ID (P1–P13, D1–D8, X). Vacío significa sin clasificar: léela, clasifícala y rellénalo. Lo más seguro es usar el ID |
| classification [classification_status] | Confirmed (página o brief leído) o Inferred (solo URL o título) |
| status | Live (publicada), Planned (planificada) o N/A (N/A excluye la fila). Vacío significa Live |
| pages [url_count, count] | URL del grupo; vacío significa 1 |
| topic [category, product_line, cluster] | Para la cobertura por tema |
| clicks [organic_clicks, gsc_clicks, current clicks] | Clics de **Search Console** en el periodo actual. Nunca sesiones de analítica |
| clicks_previous [previous clicks, prior clicks] | Clics de Search Console en el periodo de comparación. Mejor que un porcentaje |
| clicks_change_pct [click_change, yoy, change_pct] | Solo si no hay recuentos. Unidad: ver change_unit más abajo |
| impressions, impressions_previous, impressions_change_pct | Lo mismo, para impresiones. Solo se usan para orientar investigaciones |
| sessions [analytics_sessions] | Sesiones de analítica; se muestran, nunca se mezclan con los clics |
| conversions [leads, transactions, goal_completions] | Número de conversiones directas. No son ingresos ni conversiones asistidas (esas van en notes) |
| revenue, currency | Ingresos atribuidos a la página, con su moneda. Una columna llamada solo «value» no se lee como ingresos |
| tracking_verified | Y si la medición de conversiones e ingresos está verificada para el periodo; si no, las conversiones se muestran pero no bajan el valor de negocio |
| ai_cited_groups [ai_citations, cited_prompt_groups] | Grupos de prompts seguidos, distintos entre sí, en los que se citó la página |
| ai_tracked_groups [tracked_prompt_groups] | Grupos de prompts relevantes seguidos con el mismo protocolo (el denominador) |
| ai_scope [ai_platforms] | Plataforma, mercado, idioma y fechas del seguimiento. Los alcances distintos van en ejecuciones separadas |
| ai_cited (Y/N) [cited] | Se acepta en inventarios antiguos: aparece en las notas de la fila como señal, nunca como tasa, y nunca se usa para cambiar una puntuación |
| gsc_ai_impressions | Impresiones en las funciones de IA de Google según Search Console. Una métrica aparte: no son grupos de prompts ni citas |
| first_party_data (Y/N) [distinctive_value, proprietary_data] | Y si la página aporta algo difícil de reproducir: datos propios, pruebas, acceso, experiencia o funcionalidad. Una pista que hay que confirmar en la página; nunca cambia una puntuación |
| last_verified [last_updated, last_modified] | Fecha en que se comprobaron o actualizaron a fondo los datos de la página por última vez |
| referring_domains [backlinks, ref_domains] | Dominios de referencia únicos hacia la URL |
| required (Y/N) | Y si la página tiene una función legal, regulatoria, contractual, de soporte o de accesibilidad. Vacío significa desconocido, y un vacío no es un no |
| value_reviewed (Y/N) | Y cuando una persona ha valorado el valor asistido, de soporte y de audiencia de la página. Un cero en la columna de conversiones no es esa revisión |
| same_intent_confirmed (Y/N) | Y cuando una persona ha confirmado que el destino de consolidate_into cubre la misma necesidad. Que un destino aparezca en el inventario no lo demuestra |
| consolidate_into [canonical, merge_into, redirect_to] | Destino propuesto para una fusión |
| owner [team] | Equipo o persona responsable |
| notes | Cualquier cosa relevante, incluido lo que se ha leído en la página |
| cr, cp, bm, bv, pa, ef | Puntuaciones (resiliencia de clics, potencial de cita, mención de marca, valor de negocio, ventaja propia y esfuerzo). Escribe un nivel, opcionalmente seguido de su base: `H`, `M page`, `L measured`, `H set`. Un nivel solo cuenta como User set (fijada por la persona). Vacío usa el valor por defecto del marco. El script nunca deriva una puntuación de una métrica |
| score_notes | Motivos de una línea para las valoraciones de página |

Los valores Y/N se escriben así (Y = sí, N = no).

## Ajustes
En la pestaña Settings de la plantilla, en un objeto JSON «settings» o con opciones de línea de comandos. Todos son opcionales. El mínimo de 100 clics, la proporción de tráfico relevante, la alerta del −35 %, las ventanas de vigencia de 6 y 12 meses y la regla de prioridad (compartida con el evaluador complementario) son **ajustes de la skill, no parte del marco**.

| Ajuste | Por defecto | Significado |
|---|---|---|
| brand, site_model, objective, market, vertical | unknown | Contexto (marca, modelo de sitio, objetivo, mercado, sector), que se muestra en los resultados |
| current_period, previous_period | unknown | Fechas de la comparación |
| same_period_last_year | unknown | Y si la comparación es interanual; N lanza un aviso de estacionalidad |
| inventory_complete | N | Y solo si el inventario cubre todo el contenido relevante; si no, las proporciones y los huecos se dan solo para la muestra |
| change_unit | points | Cómo se leen los números sin formato de las columnas *_change_pct: points (-22 = -22 %) o fraction (-0,22 = -22 %). Los valores escritos con % y las celdas de porcentaje de Excel siempre se leen bien |
| min_comparison_clicks | 100 | Por debajo de estos clics en el periodo anterior, un cambio es demasiado pequeño para sacar conclusiones |
| material_share | 0.5 | Tráfico relevante: al menos este porcentaje de todos los clics de las filas aportadas en un periodo, y al menos min_comparison_clicks. Adapta el umbral al sitio |
| decline_threshold | -35 | Cambio de clics (%) que lanza «Investigar la pérdida de clics» |
| review_months, review_months_current_facts | 12, 6 | Ciclos de revisión de vigencia |

## Cómo se ejecuta
```bash
python scripts/evaluate.py ENTRADA.(xlsx|csv|json) --out-dir CARPETA_SALIDA [--setting clave=valor ...]
```
Escribe `scored-inventory.xlsx` (las columnas de la persona más las columnas `result_`, una pestaña Findings y una pestaña Review) y `results.json`. Sus columnas y textos están en inglés: tradúcelos al presentarlos. Sus acciones son borradores: cuando enumera varias opciones de reconversión, elige la que encaja con la función de la página y explica por qué. Leer o escribir .xlsx necesita openpyxl (`pip install openpyxl`); CSV y JSON no necesitan nada más.

Flujo de trabajo: ejecútalo una vez para obtener los valores por defecto y las alertas de datos. Lee y clasifica las páginas sin clasificar o de la muestra, escribe los tipos y las valoraciones de página (con sus motivos) en el inventario, y ejecútalo otra vez para los resultados finales. El script hace las cuentas y aplica las reglas documentadas; la clasificación, las valoraciones de página y las recomendaciones escritas son tuyas, y la persona decide.
