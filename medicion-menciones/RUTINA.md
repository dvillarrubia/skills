# Rutina semanal de medición de menciones

Una skill que se ejecuta sola cada semana, con una persona en el circuito. Antes de programarla, pruébala dos veces a mano y compara los resultados: si cambian mucho, revisa las instrucciones primero.

## 1 · Instalar la skill

Sigue la instalación del [README](README.md). Después prepara una **carpeta de trabajo** propia (por ejemplo `medicion-mimarca/`) con tu `preguntas.csv`, tu `marcas.json` y tu `precios.json`. Abre el agente en esa carpeta: ahí se guardan las ejecuciones y los resultados.

En los comandos de abajo, `<skill>` es la carpeta donde está instalada la skill, por ejemplo `~/.claude/skills/medicion-menciones`.

## 2 · Programarla

**Con Antigravity:** usa `/schedule` dentro de `agy` y pide algo así:

> «Cada lunes a las 8:00, ejecuta la skill medicion-menciones en modo borradores con un tope de [X] $ por ejecución. Al terminar, ejecuta la alarma y, si sale distinta de 0, déjame el aviso arriba del informe.»

**Con Claude Code:** programa una tarea recurrente (por ejemplo con `/schedule`) con el mismo encargo, abierta en tu carpeta de trabajo.

**Sin agente, solo los scripts:**
- **Windows**, en el Programador de tareas: crea una tarea semanal que ejecute `py -3 <skill>\lanzar_bateria.py … --salida ejecuciones` y después `py -3 <skill>\alarma.py --carpeta ejecuciones`, con tu carpeta de trabajo como directorio de inicio.
- **Mac o Linux**, con cron (`crontab -e`):

  ```
  0 8 * * 1 cd /ruta/a/mi-carpeta && python3 <skill>/lanzar_bateria.py ... --salida ejecuciones && python3 <skill>/alarma.py --carpeta ejecuciones
  ```

## 3 · Las cuatro reglas de la rutina

| Regla | Cómo se cumple aquí |
|---|---|
| **Modo borradores** | La skill solo escribe informes en `resultados/`. No publica, no envía y no borra. |
| **Tope de gasto** | `--tope-usd` es obligatorio. Pon también un tope en la cuenta de OpenRouter. |
| **Alarma** | `alarma.py` avisa si no se ha ejecutado, si es antigua, si está incompleta o si fue una simulación. Escribe `estado-alarma.md` y sale con un código distinto de 0. |
| **Punto de control humano** | Una persona lee el borrador y 10 respuestas en bruto antes de que el informe salga. Las preguntas nuevas que proponga el agente las aprueba esa persona. |

## 4 · Ficha de la rutina

Apunta: nombre de la skill, qué hace, entradas, salida, frecuencia, modo de permiso, tope por ejecución, alarma, punto de control humano y si las dos pruebas coinciden.
