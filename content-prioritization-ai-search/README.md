# content-prioritization-ai-search

Skill para decidir qué contenido de una web **crear, mantener, mejorar, rehacer o consolidar** pensando en la búsqueda con IA (AI Overviews, AI Mode, ChatGPT, Perplexity).

Se basa en el marco **«Content Prioritization in an AI Search Era»** de **Aleyda Solis** (Orainti y SEOFOMO):
- Guía: https://www.aleydasolis.com/en/ai-search/content-prioritization-ai-search/
- Hoja de cálculo: https://docs.google.com/spreadsheets/d/18myHCvxeylIyc6zGnE5HWLYw8nN7rQz-TfMQslAfiko/edit

Las instrucciones y las referencias de la skill están en español. El script (`evaluate.py`), la plantilla Excel y los ejemplos mantienen los nombres de columna en inglés, porque el script los lee así; el agente te traduce sus resultados.

## Instalación rápida

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/dvillarrubia/skills/main/install.ps1))) content-prioritization-ai-search all
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- content-prioritization-ai-search all
```

Cambia `all` por `claude` (solo Claude Code) o `antigravity` (solo Antigravity). Si vuelves a ejecutar el comando, actualiza la skill a la última versión.

Después instala la única dependencia de Python (solo hace falta si trabajas con Excel):
```bash
pip install openpyxl
```

¿Prefieres hacerlo a mano? Copia esta carpeta a tu directorio de skills; las rutas están en el [README principal](../README.md#cómo-instalar-una-skill).

## Lo que necesitas

1. **Python 3.10 o superior.** Compruébalo con `python --version` (en Windows también `py -3 --version`).
2. **openpyxl**, para leer y escribir Excel: `pip install openpyxl`. Si solo usas CSV, no hace falta.
3. **Claude Code o Google Antigravity** (o cualquier agente que lea carpetas y ejecute comandos).
4. **Tus datos** (opcional): el export de Search Console, pestaña **Páginas**, comparando con **el mismo periodo del año anterior**. Si no los tienes, usa `examples/test-ecommerce.csv`.

## Cómo usarla

Una vez instalada, pídeselo al agente con tus palabras:

- **Claude Code:** `/content-prioritization-ai-search` o «prioriza el contenido de este export de Search Console».
- **Antigravity:** «usa la skill content-prioritization-ai-search para evaluar mi inventario».

Encargo de ejemplo (cambia el contexto por el de tu web):

```
Evalúa examples/test-ecommerce.csv (o mi export de Search Console).
Contexto: ecommerce, objetivo conversión, España, comparación interanual,
inventario incompleto. Responde en español. Todo son borradores:
no cambies nada de la web.
```

Contesta la pregunta de contexto si te la hace. Luego abre la hoja que genera, `scored-inventory.xlsx`, y añade una columna **«Tu decisión»**: mantener, actualizar, consolidar o podar.

### Solo el script, sin agente

Desde dentro de la carpeta de la skill:

```bash
python scripts/evaluate.py examples/test-ecommerce.csv --out-dir resultados --setting site_model=ecommerce
```

Genera `resultados/scored-inventory.xlsx` (pestañas Results, Findings y Review) y `resultados/results.json`. Sin el agente no hay lectura de páginas ni clasificación: el script solo aplica los valores por defecto y las reglas.

Para comprobar que todo funciona: `python scripts/selftest.py`, que debe terminar con «All acceptance checks passed».

## Qué hay dentro

| Archivo o carpeta | Para qué sirve |
|---|---|
| `SKILL.md` | Las instrucciones que sigue el agente |
| `references/framework.md` | Los 21 tipos de contenido: 13 para priorizar (P1-P13) y 8 para despriorizar (D1-D8) |
| `references/inputs.md` | Qué columnas acepta y cómo se ejecuta el script |
| `references/examples-by-vertical.md` | Ejemplos del marco para ecommerce, SaaS y finanzas |
| `data/content-types.json` | Los tipos de contenido en formato de datos, para el script |
| `scripts/evaluate.py` | Hace las cuentas: puntuación, caídas de clics, filtro de revisión y hoja puntuada |
| `scripts/selftest.py` | Comprueba que las reglas siguen funcionando |
| `templates/content-inventory-template.xlsx` | Plantilla de inventario, por si no tienes uno |
| `examples/` | Inventarios **ficticios** para practicar: tienda de montaña, medio y banco, más un export de Search Console de ejemplo |

## Reglas y límites que debes conocer

- **El agente clasifica y tú decides.** Todo lo que sale es un borrador. La skill nunca aprueba una poda: como mucho, deja una URL como «candidata para revisión del propietario».
- **No inventa datos.** Lo que falta se queda como desconocido, no como cero.
- **Ninguna métrica cambia una puntuación por sí sola**, y la skill nunca atribuye a la IA una caída de tráfico: te dice qué comprobar (consultas, posiciones, estacionalidad, elementos de la SERP).
- **Sin datos de leads ni de citas en IA, el resultado es provisional.**
- **Las fichas transaccionales salen casi todas en prioridad alta:** entre ellas, prioriza con tu criterio.
- **Fallo conocido del script:** cuando las impresiones caen más que los clics, lo diagnostica como «impresiones estables». Revisa esos casos a mano.

## Privacidad

El export de Search Console de un cliente son datos suyos. Antes de pasárselo a un agente, comprueba que tienes permiso y que la herramienta y la cuenta que usas son adecuadas para esos datos. Para practicar, usa los inventarios ficticios de `examples/`.

## Autoría

Marco: **Aleyda Solis** (Orainti y SEOFOMO). Todos los derechos del marco y de su hoja de cálculo son suyos. Skill preparada para el curso «SEO para IA y con IA» por LIN3S, noviembre de 2026.
