# auditor-geo

Skill que **audita si la IA puede leer, entender y citar una página**, con un semáforo de 7 pilares. Cada pilar sale en verde, ámbar o rojo **con su evidencia** (una cifra, un archivo, una regla o un código HTTP), y lo que no se ha podido comprobar se marca como «no comprobado» en lugar de suponerlo.

La salida es siempre la misma tabla, así que puedes comparar webs entre sí o la misma web de un mes a otro.

## Qué hace

1. **Ejecuta `scripts/semaforo.py`** sobre la URL. Descarga el HTML sin JavaScript, `robots.txt` y `llms.txt`, y pide la página haciéndose pasar por 8 bots de IA. Calcula seis de los siete pilares.
2. **Abre la página en el navegador** y compara el texto con JavaScript y sin él para cerrar el pilar 1, que el script no puede ver.
3. **Revisa a mano** cualquier pilar en rojo antes de darlo por bueno.
4. **Devuelve la tabla** en `semaforo.md` (y los mismos datos en `semaforo.json`), con el recuento de colores y la lista de lo no comprobado.

| Pilar | Lo mide el script | Lo tiene que mirar el agente o tú |
|---|---|---|
| 1. Renderizado | Cuánto texto hay en el HTML sin JavaScript y si hay señales de una aplicación JavaScript | El texto con JavaScript, en el navegador |
| 2. Schema | Los tipos de JSON-LD y los campos clave de Organization y Product | La validez formal, en el validador de schema.org |
| 3. Acceso de bots | `robots.txt` bot por bot y la respuesta HTTP con el user-agent de 8 bots (GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot…) | Qué bots vinieron de verdad: eso lo dicen los logs |
| 4. Densidad | Palabras, proporción de texto e imágenes sin alt | Si la respuesta está en una imagen |
| 5. Encabezados | H1, H2 y saltos de nivel | Si los encabezados describen bien el contenido |
| 6. llms.txt | Si existe | Si aporta algo. Su ausencia no es un fallo: sale en ámbar |
| 7. Citabilidad | Párrafos de 40 a 150 palabras que responden primero, con cifra y fecha | Todo: es una heurística, lee los pasajes |

**Solo lee.** No cambia nada en la web y hace unas 12 peticiones por auditoría.

## Instalación

### Rápida (un comando)

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/dvillarrubia/skills/main/install.ps1))) auditor-geo all
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- auditor-geo all
```

Cambia `all` por `claude` (solo Claude Code) o `antigravity` (solo Antigravity). Si vuelves a lanzarlo, se actualiza. Solo necesita **Python 3.10 o superior**, sin dependencias: usa la biblioteca estándar.

### A mano

Descarga el repo (`git clone https://github.com/dvillarrubia/skills.git` o **Code → Download ZIP**) y copia la carpeta `auditor-geo/`:

| Herramienta | Carpeta global | Carpeta por proyecto |
|---|---|---|
| **Claude Code** | Windows: `C:\Users\TU-USUARIO\.claude\skills\` · Mac/Linux: `~/.claude/skills/` | `<tu-proyecto>/.claude/skills/` |
| **Antigravity CLI** | `~/.gemini/antigravity-cli/skills/` | `<tu-proyecto>/.agents/skills/` |
| **Antigravity (app / IDE)** | `~/.gemini/config/skills/` | `<tu-proyecto>/.agents/skills/` |

Debe quedar así: `.../skills/auditor-geo/SKILL.md`. Reinicia la herramienta.

### Comprobar que funciona

Desde la carpeta de la skill: `python -m unittest discover -s tests -v` (en Mac, `python3`). Las pruebas levantan dos webs de mentira, una buena y otra mala, sin conexión a internet.

## Cómo usarla

- **Claude Code:** `/auditor-geo https://tu-web.com/` o «audita esta web: https://tu-web.com/».
- **Antigravity:** «usa la skill auditor-geo para auditar https://tu-web.com/».

Para cerrar el pilar 1, el agente necesita un navegador que pueda manejar: en Claude Code, Chrome DevTools MCP o Claude in Chrome; en Antigravity, su navegador integrado (`/browser`). Sin navegador, ese pilar queda como «no comprobado».

### Solo el script, sin agente

Desde la carpeta de la skill:

```bash
python scripts/semaforo.py https://tu-web.com/ --salida semaforo.md
```

En Windows también vale `py -3`; en Mac, `python3`. Crea `semaforo.md` (la tabla) y `semaforo.json` (los mismos datos, para otro programa).

## Qué hay dentro

| Archivo | Para qué |
|---|---|
| `SKILL.md` | Las instrucciones que lee el agente: cuándo se usa, pasos, salida y reglas |
| `plantilla.md` | La tabla de salida, siempre con el mismo formato |
| `scripts/semaforo.py` | Mide seis de los siete pilares y deja la evidencia |
| `tests/` | Pruebas con dos webs de mentira, sin conexión |

## Límites

- El script se hace pasar por cada bot, pero no lo es: un servidor que verifica la IP tratará distinto al bot de verdad.
- La citabilidad es una heurística (longitud, cifra, fecha y respuesta en la primera frase). Sirve para encontrar candidatos, no para puntuar.
- Es una auditoría de una página, sin rastreo de la web entera ni comparativas.
