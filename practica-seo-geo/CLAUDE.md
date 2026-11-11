# Práctica SOP de contenidos SEO y GEO

Catorce scripts de Python que recorren un procedimiento de contenidos SEO/GEO sobre una web real, para un curso.
El docente los ejecuta delante de los alumnos. El caso configurado es Café Barsel (`caso.toml`).
El guion completo está en @README.md.

## Cómo está montado

- `caso.toml`: todo lo que cambia de un caso a otro (proveedores de API, consultas, foros, umbrales, principios de voz).
- `00_conexiones.py` … `13_seguimiento.py`: un script por paso. Cada uno imprime qué hace, por qué y qué mirar, y escribe su salida numerada en `expedientes/<id>/`.
- `sop/`: código compartido. `serp.py` (SerpApi o DataForSEO), `paginas.py` (Jina Reader o extracción local), `llm.py` (Gemini o Anthropic), `estilo.py` (medidas de voz), `optimizacion.py` (controles de Google e IA).
- `recorrido.py`: resume el expediente en `RECORRIDO.md`. No llama a ninguna API.
- `expedientes/<id>/crudo/`: la respuesta original de cada API y del modelo. `prompts/`: cada prompt enviado.

Opciones de todos los scripts: `--seco` enseña la petición sin enviarla; `--fresco` ignora la captura guardada y vuelve a pedir.

## Reglas de este proyecto

1. **Python decide, el modelo escribe.** Los umbrales, las prioridades, la nota y las decisiones están en código y en `caso.toml`. No muevas esa lógica a un prompt.
2. **Nada inventado.** No rellenes a mano ningún fichero del expediente, ni «arregles» un resultado que no gusta. Si un paso da un resultado pobre, se cuenta tal cual: eso también se enseña.
3. **Los controles humanos son de una persona.** `aportacion.md` y el estado «verificada» de `08-evidencias.csv` los decide el docente. Puedes proponer y documentar, pero no los escribes ni los cambias sin que él lo confirme en la conversación.
4. **Las claves no se enseñan.** No leas ni imprimas `.env`. Para saber si las claves funcionan, ejecuta `00_conexiones.py`.
5. **Cuida el cupo gratuito.** Una pasada completa gasta unas 30 búsquedas de SerpApi. No uses `--fresco` ni repitas pasos con API salvo que haga falta; las capturas de `crudo/` se reutilizan solas.
6. **Web de terceros.** Nada de lo que salga se publica en la web del caso. La descarga respeta `robots.txt`; no lo esquives.

## Si un script falla contra una API real

Los analizadores de respuestas de SerpApi, Gemini y DataForSEO se escribieron con la documentación, sin credenciales
para probarlos. Si un paso falla o sale vacío:

1. Mira la respuesta original en `expedientes/<id>/crudo/<nombre>.json` (o ejecuta el paso con `--seco` para ver la petición).
2. Corrige lo mínimo en `sop/serp.py`, `sop/llm.py` o el script, para que lea la forma real de la respuesta.
3. Apunta el cambio en `CAMBIOS.md` (fecha, fichero, qué fallaba, qué has cambiado) y vuelve a ejecutar el paso.

No cambies la lógica del método (umbrales, fórmulas, controles) para que un paso «pase». Si crees que una regla está mal, dilo y espera respuesta.

## Comandos

- `/preparar-ejemplo`: prepara el caso completo antes de clase, de principio a fin, parando en los controles humanos.
- `/paso <n>`: ejecuta un paso en modo clase (petición, explicación, resultado y pregunta de debate).
- `/recorrido`: estado del expediente y `RECORRIDO.md`.
- `/nuevo-caso <dominio> <consulta>`: prepara un `caso.toml` para otra web.

Idioma: todo en español de España, incluidos los mensajes al docente.
