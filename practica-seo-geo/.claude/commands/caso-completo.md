---
description: De un dominio y un tema a un caso completo (ICP y pains → contenido) en una sola tirada, con Claude de motor
argument-hint: "<dominio> <tema o consulta principal>"
---

Vas a montar y ejecutar un caso NUEVO de principio a fin para: **$ARGUMENTS**. Claude es el modelo y usas las
conexiones configuradas (SerpApi, DataForSEO, web). Todo en español de España. Sigue las reglas de CLAUDE.md.

Reglas de este flujo:
- **Modo datos completo**: `serp="serpapi"`, `lector="jina"`, `volumenes="dataforseo"`, `asistente="claudecode"`, `[modelo] proveedor="claudecode"`.
- **Una sola tirada**: no te detienes en los controles humanos; los dejas en **BORRADOR marcados «revisar»**.
- **Nada inventado**: lo que propongas tú (público, foros, preguntas) se marca como *propuesta*, no como dato del cliente. Las citas que pida un paso van literales. Si algo no está en el material, se dice.

## 0 · Entorno y claves
1. Comprueba `.env`: hacen falta `SERPAPI_API_KEY` y `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD`. Si falta alguna, dilo y para (indica dónde se crean: serpapi.com y app.dataforseo.com). No leas ni muestres `.env`.
2. Crea el `.venv` e instala `requirements.txt` si no existe. Usa `.venv/Scripts/python.exe` (Windows) o `.venv/bin/python` (mac/Linux). En Windows antepón `PYTHONUTF8=1`.

## 1 · Montar el caso (en `casos/<id>.toml`, sin tocar el de ejemplo)
1. Elige un `<id>` corto en minúsculas-con-guiones a partir del dominio y el tema.
2. Copia `caso.toml` a `casos/<id>.toml` y rellénalo. Para `[propias]` y `[voz]`, **visita la web real** y localiza las URLs que tocan el tema y seis textos del blog de la marca (comprueba que responden). Para `[publico]`, `[icp]` y `[asistentes]`, **propón** segmento/problema/objetivo/conversión, foros, búsquedas de dolor y tres preguntas reales de ese público; déjalo marcado como hipótesis.
3. **Expertise del cliente** → crea `fuentes-cliente/<id>-contexto.md`:
   - Si el alumno te ha dado material de primera mano (entrevista, cata, datos), vuélcalo ahí.
   - Si NO, **díselo con claridad**: sin aportación propia el contenido saldrá más genérico. Deja solo lo que la web ya afirma, marcado como «sin aportación de primera mano».
4. A partir de aquí, ejecuta cada paso apuntando a ese caso con la variable `SOP_CASO`, p. ej.:
   `SOP_CASO=casos/<id>.toml PYTHONUTF8=1 .venv/Scripts/python.exe 00_conexiones.py`
   (en PowerShell: `$env:SOP_CASO="casos/<id>.toml"` antes de cada comando).

## 2 · Ejecutar el método (0 → 12, con 3b)
Ejecuta en orden: `00, 01, 02, 03, 03b, 04, 05, 06, 07, 08, 09, 10, 11, 12`.
- Cuando un paso de modelo se detenga pidiendo una captura: **lee `prompts/<paso>.md`**, produce la respuesta **siguiendo exactamente el formato que pide el prompt** (solo con el material dado; citas literales donde se exijan) y escríbela en `crudo/llm-<paso>.json` con la forma `{"capturado","modelo":"claude-code","uso":null,"texto":"…"}`. Re-ejecuta el paso. Igual con el asistente del paso 4: responde a cada pregunta con **búsqueda web real** y guarda `crudo/04-…-claude-…json`.
- Revisa que cada salida tiene contenido real (no cabeceras vacías). Si un script falla por la forma de una respuesta de API, aplica «Si un script falla contra una API real» de CLAUDE.md y anótalo en `CAMBIOS.md`.

## 3 · Paso 8 en modo borrador
1. **Verificadas**: marca «verificada» solo las afirmaciones claramente factuales o de consenso, cada una con una nota de fuente; el resto «pendiente». Revisor: `Claude (BORRADOR · revisar)`.
2. **Aportación**: escribe `aportacion.md` a partir de un tema que **nadie prueba** (paso 6), construido solo con material verificado y las palabras del público. Empieza con «BORRADOR PARA REVISAR» y deja claros sus límites.

## 4 · Redacción
Ejecuta `09, 10, 11, 12`. El borrador sale en **pirámide invertida** (respuesta arriba, 5–7 secciones, prosa fluida). Escribe además `10-borrador-humano.md`: la versión con voz de marca, siguiendo el briefing y el expertise del cliente (o avisando de que, sin expertise propia, será más genérica).

## 5 · Cierre y entrega
1. Ejecuta `recorrido.py`.
2. Replica la **estructura de presentación** por bloques como en el caso de ejemplo (ver `DEMO/00-LEEME.md`) para este `<id>`: una carpeta limpia con la pieza final, el briefing, la cobertura, la visibilidad en IA y el tono.
3. (Opcional) genera un `informe-visual.html` como el del ejemplo.
4. Informe final al alumno: qué está hecho, qué quedó **«para revisar»** (verificadas + aportación), si faltó expertise de primera mano y cómo afecta al resultado, y el coste de DataForSEO.
