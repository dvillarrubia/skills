# Cómo lanzar la práctica

Práctica del curso **MIDE · SEO/GEO de contenidos** sobre una web real (Café Barsel).
Caso ya preparado: *«molienda para cafetera italiana»*. Sigue uno de los tres modos de abajo.

---

## Lo que necesitas
- **Python 3.11 o superior** (probado con 3.13).
- **En clase NO hacen falta claves de API**: cada paso reutiliza las capturas ya preparadas en
  `expedientes/barsel-cafetera-italiana/crudo/`. Va rápido y funciona aunque falle la red.
- El modelo que etiqueta y redacta es **Claude Code** (no necesita clave).
- Claves **solo si quieres regenerar desde cero** (opción `--fresco`): `SERPAPI_API_KEY` y, para volumen
  y keywords de competencia, `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` en el fichero `.env`.

## Preparación (una sola vez)
Desde una terminal, dentro de esta carpeta:

```bash
# 1) Entorno virtual
python -m venv .venv

# 2) Dependencias
#    Windows:
.venv\Scripts\python.exe -m pip install -r requirements.txt
#    macOS / Linux:
.venv/bin/python -m pip install -r requirements.txt

# 3) (Solo si vas a regenerar) copia la plantilla de claves y rellénala en tu editor
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

---

## Modo A · Ver el resultado (lo más rápido para enseñar)
No ejecuta nada. Abre en el navegador:

```
DEMO/informe-visual.html
```

y recorre las carpetas por bloques empezando por **`DEMO/00-LEEME.md`**:

```
DEMO/1-cliente-y-publico/   → tono, ICP y dolores
DEMO/2-investigacion/       → keywords, competidores, SERP, visibilidad en IA
DEMO/3-briefing/            → cobertura, aportación, expertise del cliente, briefing
DEMO/4-redaccion/           → PIEZA-FINAL.md y la auditoría
```

## Modo B · Ejecutar el método paso a paso (en clase)
Ejecuta los scripts **en orden**. En Windows antepón `PYTHONUTF8=1` para que los acentos salgan bien:

```bash
# Windows (una línea por paso)
set PYTHONUTF8=1
.venv\Scripts\python.exe 00_conexiones.py
.venv\Scripts\python.exe 01_icp_pains.py
.venv\Scripts\python.exe 02_consultas.py
.venv\Scripts\python.exe 03_resultados.py
.venv\Scripts\python.exe 03b_keywords_competidores.py
.venv\Scripts\python.exe 04_asistentes.py
.venv\Scripts\python.exe 05_corpus.py
.venv\Scripts\python.exe 06_cobertura.py
.venv\Scripts\python.exe 07_voz.py
.venv\Scripts\python.exe 08_evidencias.py
.venv\Scripts\python.exe 09_instrucciones.py
.venv\Scripts\python.exe 10_borrador.py
.venv\Scripts\python.exe 11_optimizacion.py
.venv\Scripts\python.exe 12_revision.py
.venv\Scripts\python.exe recorrido.py
```

En macOS/Linux es igual pero con `PYTHONUTF8=1 .venv/bin/python 01_icp_pains.py`.

- **Sin `--fresco`** cada paso **reutiliza la captura guardada**: no gasta API ni necesita claves.
- **Con `--fresco`** vuelve a pedir a las APIs (necesita claves y gasta cupo/saldo).
- **`--seco`** enseña la petición exacta que se haría, sin enviarla (útil para explicar la API).
- El paso **13** (seguimiento) es para semanas *después* de publicar; no se ejecuta en la preparación.

## Modo C · Desde Claude Code
Abre Claude Code **dentro de esta carpeta** y usa los comandos:

```
/paso 1        · ejecuta un paso en modo clase (petición, explicación, resultado y debate)
/recorrido     · estado del expediente
/preparar-ejemplo   · deja el caso completo listo, parando en los controles humanos
/nuevo-caso <dominio> <consulta>   · prepara otro caso
```

---

## Úsalo con tu propio caso (de cero)
Para generar un caso nuevo —otra marca, otro tema— con Claude de motor, desde Claude Code dentro de la carpeta:

```
/caso-completo tudominio.com "tu tema o consulta principal"
```

Claude monta el `caso.toml` (investigando la web), ejecuta los 14 pasos (ICP y dolores → keywords y
competencia → visibilidad → cobertura → briefing → contenido) y deja el resultado en una carpeta nueva,
sin tocar el caso de ejemplo. Qué saber:

- **Necesitas claves propias** en `.env`: `SERPAPI_API_KEY` (gratis) y, para volumen y keywords de
  competencia, `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (de pago). Si lo quieres solo gratis, pon
  `volumenes = "ninguno"` y omite el paso `03b`.
- **Aporta tu conocimiento de primera mano** en `fuentes-cliente/` (una cata, un dato, una prueba real).
  Es lo que evita que el contenido suene a IA; sin ello saldrá más genérico, y Claude te lo advertirá.
- **Los controles humanos** (qué se da por verificado y la aportación original) Claude los deja en
  **borrador marcados «revisar»**: míralos antes de publicar.
- Si prefieres solo preparar la config y decidir tú cada control: usa `/nuevo-caso tudominio.com "tema"`
  y luego `/preparar-ejemplo`.

## Detalles útiles
- **La pieza final** está en `DEMO/4-redaccion/PIEZA-FINAL.md` (y el borrador automático «antes», en `anexos-del-proceso/`).
- **El modelo es Claude Code**: si borras una captura de `crudo/` o usas `--fresco`, el script se detiene y
  pide que Claude escriba esa respuesta. Para clase, deja las capturas como están. (Ver `CAMBIOS.md`.)
- **Para otro cliente/tema**: edita `caso.toml` (consulta, foros, umbrales, principios de voz) y vuelve a
  ejecutar. Los scripts no se tocan.
- **Guion detallado del método**: `README.md`. **Reglas del proyecto**: `CLAUDE.md`.
