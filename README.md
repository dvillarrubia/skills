# skills

Skills de [Claude Code](https://claude.com/claude-code) listas para usar. Un sitio donde comparto, con fines de divulgación, herramientas que uso en mi trabajo de SEO y gestión de conocimiento.

> **¿Qué es una skill?** Una carpeta con un archivo `SKILL.md` (y, si hace falta, una carpeta `references/` con material de apoyo). Claude Code la detecta sola y te deja lanzarla por su nombre (`/nombre-skill`) o describiendo la tarea. La mayoría son Markdown puro y solo hay que copiar la carpeta; alguna incluye además un script (el propio `SKILL.md` indica al principio qué necesita).

## Catálogo

| Skill | Para qué sirve | Cómo se lanza |
|---|---|---|
| [`eeat-auditor`](eeat-auditor/) | Audita las señales **E-E-A-T** de un competidor (hasta 10 artículos + el bloque de confianza del sitio) en una plantilla fija, citando la URL de cada dato o marcándolo como «no consta» / «no comprobado». | `/eeat-auditor` |
| [`tone-analyzer`](tone-analyzer/) | Extrae el **tono de voz** de una persona o negocio a partir de 10-20 URLs: un script scrapea las páginas y mide señales objetivas (longitud de frase, tuteo/usted, léxico, legibilidad…), y el agente redacta un perfil de estilo reutilizable para «escribir como» esa marca. Lleva script Python (`pip install -r requirements.txt`). | `/tone-analyzer` |
| [`content-prioritization-ai-search`](content-prioritization-ai-search/) | Decide qué contenido **crear, mantener, mejorar, rehacer o consolidar** para la búsqueda con IA, con el marco de priorización de contenido de **Aleyda Solis**. Acepta una URL, un export de Search Console o un inventario y devuelve una hoja puntuada. Lleva script Python (`pip install -r requirements.txt`). | `/content-prioritization-ai-search` |
| [`auditor-geo`](auditor-geo/) | Audita si la IA puede **leer y citar una página** con un semáforo de 7 pilares (renderizado, schema, acceso de bots, densidad, encabezados, llms.txt y citabilidad), cada uno con su evidencia. Script Python sin dependencias. | `/auditor-geo` |
| [`medicion-menciones`](medicion-menciones/) | Mide cada semana si la IA **menciona y cita tu marca**, por ICP y fase, con una batería fija de preguntas; cuenta menciones, posición y citas y redacta un informe borrador. Puede lanzar la batería por OpenRouter (simula por defecto, con tope de gasto). Script Python sin dependencias. | `/medicion-menciones` |
| [`practica-seo-geo`](practica-seo-geo/) | **Práctica completa de clase**: el SOP de contenidos SEO/GEO de principio a fin sobre una web real (caso Café Barsel). Tono + ICP, keyword research con **minería de keywords de competidores**, visibilidad en Google y en IA, cobertura, briefing con el expertise del cliente y redacción auditada. Viene **resuelta y lista para proyectar** (carpeta `DEMO/` + informe visual). Motor Python (14 pasos); en clase se ejecuta sin claves reutilizando las capturas. | `/practica-seo-geo` |

## Instalación rápida (un comando)

Instala cualquier skill del catálogo en Claude Code y en Antigravity a la vez. Cambia `NOMBRE-SKILL` por el de la tabla.

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/dvillarrubia/skills/main/install.ps1))) NOMBRE-SKILL all
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- NOMBRE-SKILL all
```

El último parámetro elige dónde instalarla: `claude`, `antigravity` o `all` (las dos). Si vuelves a lanzar el comando, la skill se actualiza a la última versión. Si la skill trae un `requirements.txt`, el instalador te dice cómo instalar sus dependencias de Python.

Si prefieres no ejecutar scripts, sigue los pasos manuales de abajo.

## Cómo instalar una skill a mano

Cada skill es una carpeta con un `SKILL.md` (frontmatter `name` y `description`) y, si hace falta, una carpeta `references/` y un script. El mismo formato funciona en **Claude Code** y en **Google Antigravity**: solo cambia la carpeta donde copias la skill.

**Primero, descarga la carpeta de la skill.** Dos formas:
- Clona todo el repo:
  ```bash
  git clone https://github.com/dvillarrubia/skills.git
  ```
- O descarga el repo como ZIP desde GitHub (botón verde **Code → Download ZIP**) y descomprime.

Luego copia la carpeta de la skill (por ejemplo `eeat-auditor/`) al directorio que corresponda:

### En Claude Code

- **Global** (todas tus sesiones):
  - Windows: `C:\Users\TU-USUARIO\.claude\skills\`
  - macOS / Linux: `~/.claude/skills/`
- **Por proyecto** (y viaja con ese repo si usa Git): `<tu-proyecto>/.claude/skills/`

Debe quedar así: `.claude/skills/eeat-auditor/SKILL.md`

Abre o reinicia Claude Code y lánzala con `/eeat-auditor` o describiendo la tarea.

Cada skill tiene su propio `README.md` con qué hace, cómo se instala en Claude Code y en Antigravity y cómo se usa.

### En Google Antigravity

- **Antigravity CLI** (global): `~/.gemini/antigravity-cli/skills/`
- **Antigravity (app / IDE)** (global): `~/.gemini/config/skills/`
- **Por proyecto**: `<tu-proyecto>/.agents/skills/`

Debe quedar así, por ejemplo: `~/.gemini/antigravity-cli/skills/eeat-auditor/SKILL.md`

Comprueba que se ha cargado con `/skills` en la CLI (o preguntando «¿qué skills tienes disponibles?» en la app) y lánzala nombrándola: «audita las señales E-E-A-T de… con la skill eeat-auditor».

> Las rutas de Antigravity han cambiado rápido entre versiones. Si no aparece, revisa la sección **Customizations → Skills** y la [documentación oficial de skills](https://antigravity.google/docs/skills/).

## Requisitos

Algunas skills necesitan herramientas concretas; cada `SKILL.md` lo indica al principio.

- `eeat-auditor` necesita un navegador que el agente pueda manejar para verificar cada dato: si no lo tiene, se detiene y lo avisa en lugar de inventar.
- `tone-analyzer` necesita **Python 3** y sus dependencias. Dentro de su carpeta: `pip install -r requirements.txt` (en algunos equipos, `python3` / `pip3`).
- `content-prioritization-ai-search` necesita **Python 3.10+** y `openpyxl`. Dentro de su carpeta: `pip install -r requirements.txt` (solo hace falta si trabajas con Excel).
- `auditor-geo` necesita **Python 3.10+** (sin dependencias) y, para cerrar el pilar de renderizado, un navegador que el agente pueda manejar.
- `medicion-menciones` necesita **Python 3.10+** (sin dependencias). Para lanzar la batería de verdad, una clave de OpenRouter con tope de gasto.

## Autoría y uso

Creadas por **David Villarrubia** (Head Manager SEO). Puedes usarlas, copiarlas y adaptarlas libremente (licencia MIT, ver [`LICENSE`](LICENSE)). Si te resultan útiles, una mención se agradece.

`content-prioritization-ai-search` aplica el marco **«Content Prioritization in an AI Search Era»** de [Aleyda Solis](https://www.aleydasolis.com/en/ai-search/content-prioritization-ai-search/). El marco, sus textos y su hoja de cálculo son obra suya; la licencia MIT cubre solo el empaquetado como skill y el script.
