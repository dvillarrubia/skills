---
name: practica-seo-geo
description: Práctica completa del SOP de contenidos SEO y GEO sobre una web real (caso Café Barsel, «molienda para cafetera italiana»). Recorre el método de principio a fin —tono e ICP, keyword research con minería de competidores, visibilidad en Google y en IA, cobertura, briefing con el expertise del cliente y redacción auditada— con el resultado ya preparado para enseñarlo. Úsala para dar o seguir la clase de contenidos para búsqueda e IA.
---

# Práctica SEO/GEO de contenidos

Catorce pasos de Python que recorren un procedimiento real de contenidos para SEO y GEO. **Python decide**
(umbrales, prioridades, agrupación, verificación de citas y la nota) y **el modelo redacta**; aquí el modelo
es **Claude Code**, así que no hace falta clave de LLM. El caso viene resuelto y listo para proyectar.

## Cómo lanzarla

El tutorial con los comandos exactos está en **[TUTORIAL.md](TUTORIAL.md)**. En resumen:

1. **Preparar una vez:**
   ```bash
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt     # Windows
   # .venv/bin/python -m pip install -r requirements.txt           # macOS / Linux
   ```
2. **Ver el resultado (demo):** abre `DEMO/informe-visual.html` y recorre `DEMO/` por bloques (empieza por `DEMO/00-LEEME.md`).
3. **Ejecutar el método paso a paso:**
   ```bash
   PYTHONUTF8=1 .venv\Scripts\python.exe 01_icp_pains.py
   # … 02, 03, 03b, 04, 05, 06, 07, 08, 09, 10, 11, 12
   ```
   Sin `--fresco` cada paso **reutiliza las capturas ya preparadas**: va rápido, no gasta API y no necesita claves.
4. **Desde Claude Code**, abierto dentro de la carpeta: `/paso 1`, `/recorrido`, `/preparar-ejemplo`, `/nuevo-caso`.

### Con tu propio caso, de una tirada
```
/caso-completo tudominio.com "tu tema o consulta"
```
Claude monta el `caso.toml`, ejecuta los 14 pasos (ICP y dolores → contenido) y deja el resultado en una
carpeta nueva. Necesita claves propias (`SERPAPI_API_KEY` y, para volumen/competencia, DataForSEO) y tu
conocimiento de primera mano en `fuentes-cliente/` para que no suene genérico. Detalles en `TUTORIAL.md`.

## Qué hay dentro

- **`DEMO/`** — el trabajo terminado, ordenado por 4 bloques (cliente y público · investigación · briefing · redacción) y un informe visual. Es lo que se enseña.
- **`00_…13_*.py` + `03b_…` + `sop/`** — el motor del método.
- **`caso.toml`** — todo lo que cambia de un caso a otro (consulta, foros, umbrales, principios de voz). Los scripts no se tocan.
- **`expedientes/barsel-cafetera-italiana/`** — el expediente completo, con las capturas que permiten re-ejecutar sin claves.
- **`fuentes-cliente/`** — el conocimiento de primera mano del cliente (en este caso, simulado para la demo).

## Requisitos
Python 3.11+. Claves (`.env`) **solo** si quieres regenerar desde cero con `--fresco`: `SERPAPI_API_KEY` y,
para volumen y keywords de competencia, `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`. Nunca se publican las claves.
