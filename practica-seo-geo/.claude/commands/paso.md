---
description: Ejecuta un paso de la práctica en modo clase
argument-hint: "<número de paso, 0 a 13>"
---

Ejecuta el paso $ARGUMENTS de la práctica como se hace delante de los alumnos. Sigue las reglas de CLAUDE.md.

1. Localiza el script cuyo nombre empieza por ese número (dos cifras).
2. Ejecútalo primero con `--seco` y enseña la petición exacta que haría, en una frase: a qué servicio y con qué datos.
3. Ejecútalo sin opciones. Usará la captura guardada si existe; no añadas `--fresco` salvo que el docente lo pida.
4. Resume el resultado en cinco líneas como máximo, con los datos reales que ha escrito el script.
5. Termina con la pregunta de debate que imprime el script y di qué fichero conviene abrir en pantalla.

Si el paso es el 8, el 9 o el 12, recuerda qué decide una persona en ese paso y no lo decidas tú.
