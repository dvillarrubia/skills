# medicion-menciones

Skill para **medir cada semana si la IA menciona y cita tu marca**, separando por ICP (perfil de cliente), pain y fase del recorrido (descubrimiento, consideración y decisión). Lanza una batería fija de preguntas a varios modelos (o usa respuestas que pegues a mano), cuenta menciones, posición y citas, y redacta un informe borrador para que lo revise una persona.

El reparto es siempre el mismo: **el script cuenta, el agente interpreta y una persona decide.**

## Qué hace

1. **Comprueba la batería de preguntas**: cada una con id, ICP, pain, fase y redacción. Hay tres redacciones por celda para ver cuánto depende la cifra de cómo se pregunta.
2. **Consigue las respuestas** de una de dos formas:
   - las pegas a mano desde ChatGPT, Perplexity, etc., un archivo por respuesta;
   - las lanza `lanzar_bateria.py` por la API de OpenRouter. **Por defecto simula** y no gasta nada; solo llama de verdad con `--real`, con la clave en una variable de entorno y con un tope de gasto obligatorio.
3. **Consolida** con `consolidar_menciones.py`: qué marcas salen y en qué orden, qué dominios se citan y avisos de lo que hay que revisar a mano. Genera un CSV por ICP y fase y un informe en Markdown.
4. **Lee en bruto** al menos 10 respuestas (las extremas, las de los avisos y alguna de cada modelo) antes de redactar.
5. **Redacta el informe** con `plantilla-informe.md`: cifras con su n y su rango, preguntas con marca separadas de las sin marca, quién se lleva las citas y propuestas para que las apruebe una persona.
6. **Alarma** (`alarma.py`): si la rutina semanal no se ha ejecutado, es antigua, ha salido incompleta o fue una simulación, lo avisa en `estado-alarma.md`.

Además puede comprobar **qué sabe la IA de tu marca** (modo `--modo entidad`): separa las respuestas coherentes, las que no saben y las que confunden tu marca con otra de nombre parecido.

## Instalación

### Rápida (un comando)

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/dvillarrubia/skills/main/install.ps1))) medicion-menciones all
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- medicion-menciones all
```

Cambia `all` por `claude` (solo Claude Code) o `antigravity` (solo Antigravity). Si vuelves a lanzarlo, se actualiza. Solo necesita **Python 3.10 o superior**; no hay dependencias que instalar.

### A mano

Descarga el repo (`git clone https://github.com/dvillarrubia/skills.git` o **Code → Download ZIP**) y copia la carpeta `medicion-menciones/`:

| Herramienta | Carpeta global | Carpeta por proyecto |
|---|---|---|
| **Claude Code** | Windows: `C:\Users\TU-USUARIO\.claude\skills\` · Mac/Linux: `~/.claude/skills/` | `<tu-proyecto>/.claude/skills/` |
| **Antigravity CLI** | `~/.gemini/antigravity-cli/skills/` | `<tu-proyecto>/.agents/skills/` |
| **Antigravity (app / IDE)** | `~/.gemini/config/skills/` | `<tu-proyecto>/.agents/skills/` |

Debe quedar así: `.../skills/medicion-menciones/SKILL.md`. Reinicia la herramienta.

### Comprobar que funciona

Desde la carpeta de la skill: `python -m unittest discover -s tests` (en Mac, `python3`). Debe terminar en `OK`.

## Cómo usarla

1. **Crea una carpeta de trabajo** para tu marca (por ejemplo `medicion-mimarca/`) y abre ahí Claude Code o Antigravity. Las ejecuciones y los informes se guardan en esa carpeta, no dentro de la skill.
2. Pídeselo al agente:
   - **Claude Code:** `/medicion-menciones` o «mide las menciones de mi marca con esta batería».
   - **Antigravity:** «usa la skill medicion-menciones para sacar la línea base de menciones».
3. Si aún no tienes batería ni lista de marcas, el agente parte de las plantillas de la skill:
   - `bateria/plantilla-bateria.csv`: una batería vacía (2 ICP × 3 fases × 3 redacciones, más preguntas con marca);
   - `marcas.json`: tu marca, la competencia con sus alias y los dominios conocidos.
4. Para practicar sin gastar nada, pide que use el ejemplo: la batería `preguntas.csv` y las respuestas de `respuestas-demo/lab8/`.

### Formato de una respuesta pegada a mano

Un archivo `.md` o `.txt` por respuesta, con esta cabecera y el texto de la IA debajo:

```
---
id_pregunta: ICP1-DEC-R1
modelo: modelo-a
busqueda: si
repeticion: 1
fecha: 2026-11-14
---
(texto de la respuesta, pegado tal cual, con sus enlaces)
```

Nombre recomendado: `ICP1-DEC-R1__modelo-a__busq-si__r1.md`. Copia también los enlaces: sin ellos no se pueden contar las citas.

### Lanzarla por API (opcional)

1. Crea una clave en OpenRouter **con tope de gasto**.
2. Guárdala en la variable de entorno `OPENROUTER_API_KEY`: en PowerShell, `$env:OPENROUTER_API_KEY = "…"`; en Mac o Linux, `export OPENROUTER_API_KEY=…`. El script nunca acepta la clave como argumento ni la escribe en ningún archivo.
3. Copia `precios-ejemplo.json` a tu carpeta como `precios.json` y pon los precios reales de tus modelos. Con los de ejemplo, `--real` se niega a arrancar.
4. Simula primero, revisa el coste previsto y solo entonces añade `--real`.

Para dejarla como **rutina semanal** con alarma y punto de control humano, sigue [`RUTINA.md`](RUTINA.md).

## Qué hay dentro

| Archivo o carpeta | Para qué sirve |
|---|---|
| `SKILL.md` | Las instrucciones que sigue el agente |
| `consolidar_menciones.py` | Cuenta menciones, posición y citas; saca un CSV y un informe en Markdown |
| `lanzar_bateria.py` | Lanza la batería por la API de OpenRouter. Simula por defecto |
| `alarma.py` | Avisa si la rutina no se ha ejecutado, es antigua, está incompleta o fue una simulación |
| `plantilla-informe.md` | El formato fijo del informe semanal |
| `RUTINA.md` | Cómo programarla cada semana con sus cuatro reglas |
| `preguntas.csv` | Batería de ejemplo (marca ficticia Atlas Gym) |
| `bateria/` | La plantilla vacía y otras baterías de ejemplo |
| `marcas.json` | Ejemplo de marcas, alias y dominios (todo ficticio) |
| `precios-ejemplo.json` | Precios ilustrativos, solo para simular |
| `respuestas-demo/` | Respuestas **ficticias** para practicar |
| `generar_respuestas.py` | Regenera las respuestas de ejemplo (lo usan las pruebas) |
| `tests/` | Pruebas automáticas |

## Reglas y límites

- **Modo borradores:** no publica, no envía y no borra nada. El informe lo revisa una persona.
- **Una respuesta no es un dato.** Las celdas con menos de 6 respuestas se marcan como poco fiables.
- **No inventa** marcas, dominios ni cifras. Lo que sale en «Avisos» se revisa, no se corrige a ojo.
- **Las preguntas nuevas** que proponga el agente van a un archivo de propuestas, no a la batería.
- **Una mención no es una recomendación**, y esta medición no equivale al dato de una herramienta de pago: lee el contexto.
- Todas las marcas y dominios de los ejemplos son **ficticios**.
