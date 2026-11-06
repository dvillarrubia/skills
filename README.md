# skills

Skills de [Claude Code](https://claude.com/claude-code) listas para usar. Un sitio donde comparto, con fines de divulgación, herramientas que uso en mi trabajo de SEO y gestión de conocimiento.

> **¿Qué es una skill?** Una carpeta con un archivo `SKILL.md` (y, si hace falta, una carpeta `references/` con material de apoyo). Claude Code la detecta sola y te deja lanzarla por su nombre (`/nombre-skill`) o describiendo la tarea. No hay que compilar ni instalar nada: solo copiar la carpeta a tu directorio de skills.

## Catálogo

| Skill | Para qué sirve | Cómo se lanza |
|---|---|---|
| [`eeat-auditor`](eeat-auditor/) | Audita las señales **E-E-A-T** de un competidor (hasta 10 artículos + el bloque de confianza del sitio) en una plantilla fija, citando la URL de cada dato o marcándolo como «no consta» / «no comprobado». | `/eeat-auditor` |

## Cómo instalar una skill

Estas skills son **Markdown puro** (un `SKILL.md` con frontmatter `name` y `description`, más una carpeta `references/`). El mismo formato funciona en **Claude Code** y en **Google Antigravity**: solo cambia la carpeta donde copias la skill.

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

### En Google Antigravity

- **Antigravity CLI** (global): `~/.gemini/antigravity-cli/skills/`
- **Antigravity (app / IDE)** (global): `~/.gemini/config/skills/`
- **Por proyecto**: `<tu-proyecto>/.agents/skills/`

Debe quedar así, por ejemplo: `~/.gemini/antigravity-cli/skills/eeat-auditor/SKILL.md`

Comprueba que se ha cargado con `/skills` en la CLI (o preguntando «¿qué skills tienes disponibles?» en la app) y lánzala nombrándola: «audita las señales E-E-A-T de… con la skill eeat-auditor».

> Las rutas de Antigravity han cambiado rápido entre versiones. Si no aparece, revisa la sección **Customizations → Skills** y la [documentación oficial de skills](https://antigravity.google/docs/skills/).

## Requisitos

Algunas skills necesitan herramientas concretas; cada `SKILL.md` lo indica al principio. Por ejemplo, `eeat-auditor` necesita un navegador que el agente pueda manejar para verificar cada dato: si no lo tiene, se detiene y lo avisa en lugar de inventar.

## Autoría y uso

Creadas por **David Villarrubia** (Head Manager SEO). Puedes usarlas, copiarlas y adaptarlas libremente (licencia MIT, ver [`LICENSE`](LICENSE)). Si te resultan útiles, una mención se agradece.
