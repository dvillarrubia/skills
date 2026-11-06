# skills

Skills de [Claude Code](https://claude.com/claude-code) listas para usar. Un sitio donde comparto, con fines de divulgación, herramientas que uso en mi trabajo de SEO y gestión de conocimiento.

> **¿Qué es una skill?** Una carpeta con un archivo `SKILL.md` (y, si hace falta, una carpeta `references/` con material de apoyo). Claude Code la detecta sola y te deja lanzarla por su nombre (`/nombre-skill`) o describiendo la tarea. No hay que compilar ni instalar nada: solo copiar la carpeta a tu directorio de skills.

## Catálogo

| Skill | Para qué sirve | Cómo se lanza |
|---|---|---|
| [`eeat-auditor`](eeat-auditor/) | Audita las señales **E-E-A-T** de un competidor (hasta 10 artículos + el bloque de confianza del sitio) en una plantilla fija, citando la URL de cada dato o marcándolo como «no consta» / «no comprobado». | `/eeat-auditor` |

## Cómo instalar una skill

1. **Descarga la carpeta de la skill** que te interese. Dos formas:
   - Clona todo el repo:
     ```bash
     git clone https://github.com/dvillarrubia/skills.git
     ```
   - O descarga el repo como ZIP desde GitHub (botón verde **Code → Download ZIP**) y descomprime.

2. **Copia la carpeta de la skill** (por ejemplo `eeat-auditor/`) a tu directorio de skills:

   - **Global** — disponible en todas tus sesiones de Claude Code:
     - Windows: `C:\Users\TU-USUARIO\.claude\skills\`
     - macOS / Linux: `~/.claude/skills/`

   - **Por proyecto** — solo dentro de una carpeta concreta (y viaja con ese repo si usa Git):
     - `<tu-proyecto>/.claude/skills/`

   Debe quedar así:
   ```
   .claude/skills/eeat-auditor/SKILL.md
   .claude/skills/eeat-auditor/references/...
   ```

3. **Abre (o reinicia) Claude Code.** La skill ya aparece disponible. Lánzala con `/eeat-auditor` o describiendo la tarea.

## Requisitos

Algunas skills necesitan herramientas concretas; cada `SKILL.md` lo indica al principio. Por ejemplo, `eeat-auditor` necesita un navegador que el agente pueda manejar para verificar cada dato: si no lo tiene, se detiene y lo avisa en lugar de inventar.

## Autoría y uso

Creadas por **David Villarrubia** (Head Manager SEO). Puedes usarlas, copiarlas y adaptarlas libremente (licencia MIT, ver [`LICENSE`](LICENSE)). Si te resultan útiles, una mención se agradece.
