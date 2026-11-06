---
name: auditor-geo
description: Audita una web para la IA con el semáforo de 7 pilares. Úsala cuando pidan «audita esta web» o «¿la IA puede leer esta página?».
---

# Auditor GEO · semáforo de 7 pilares

## Pasos

1. Ejecuta `python scripts/semaforo.py URL --salida semaforo.md` (en Mac, `python3`). El script calcula seis pilares y deja la evidencia de cada uno.
2. Abre la URL con el navegador (`/browser` o Chrome DevTools MCP) y compara el texto con JavaScript y sin él. Así cierras el pilar 1: el script solo ve el HTML sin JavaScript.
3. Lee `semaforo.md` y revisa a mano cualquier pilar en rojo antes de darlo por bueno.
4. Lo que no puedas comprobar va como «no comprobado». Nunca lo supongas.

## Salida

Siempre la misma tabla, en `semaforo.md`, rellena con `plantilla.md`:

| Pilar | Color | Evidencia |
|---|---|---|

Una fila por pilar, en este orden: renderizado, schema, acceso de bots, densidad, encabezados, llms.txt y citabilidad. Debajo, el recuento de verdes, ámbar y rojos, y la lista de lo no comprobado.

## Reglas

- Evidencia antes que opinión: cada color lleva su dato (cifra, archivo, regla o código HTTP).
- No cambies un color sin una evidencia nueva.
- La ausencia de `llms.txt` no es un fallo: va en ámbar y con esa nota.
- La citabilidad es una heurística. Lee los pasajes antes de recomendar cambios.
- Solo lectura: no publiques, no envíes y no cambies nada en la web.
