"""Lanza la batería de preguntas contra varios modelos por la API de OpenRouter (opcional en el curso).

Seguridad, por diseño:
- Por defecto SIMULA: no llama a nada y escribe respuestas marcadas como simuladas. Para llamar de verdad hay
  que pasar --real a propósito.
- La clave solo se lee de la variable de entorno OPENROUTER_API_KEY. No se acepta por argumento, no se imprime
  y no se escribe en ningún archivo.
- --tope-usd es obligatorio. Antes de cada llamada se suma una estimación conservadora (precios.json) y, si se
  pasaría del tope, se para.
- Cada respuesta es una conversación nueva, sin mensaje de sistema y con la temperatura por defecto, para que se
  parezca a lo que ve un usuario.

Uso (en Mac, python3):
  python lanzar_bateria.py --bateria bateria/bateria-atlas.csv --precios precios-ejemplo.json \\
      --modelos proveedor-a/modelo-x,proveedor-b/modelo-y --modos si,no --repeticiones 3 --tope-usd 5
  Añade --real solo cuando hayas revisado la simulación y tengas la clave con tope de gasto en OpenRouter.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
URL_API = "https://openrouter.ai/api/v1/chat/completions"
REINTENTABLES = {429, 500, 502, 503, 504}
AVISO_SIM = "> Respuesta SIMULADA: no se ha llamado a ninguna IA. Sirve para probar el circuito y el coste previsto."


class TopeAlcanzado(Exception):
    pass


def leer_bateria(ruta, ids=None):
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    if ids:
        filas = [f for f in filas if f["id"] in ids]
    if not filas:
        raise ValueError("La batería está vacía o el filtro de ids no deja ninguna pregunta.")
    vacias = [f["id"] for f in filas if not f.get("pregunta", "").strip()]
    if vacias:
        raise ValueError(f"Preguntas sin texto en la batería: {', '.join(vacias)}")
    return filas


def leer_precios(ruta, modelos, real):
    precios = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if real and precios.get("ilustrativo"):
        raise ValueError("precios.json está marcado como ilustrativo: pon los precios reales de tus modelos antes de usar --real.")
    faltan = [m for m in modelos if m not in precios.get("modelos", {})]
    if faltan:
        raise ValueError(f"Faltan precios para: {', '.join(faltan)}. Añádelos a {ruta}.")
    for m in modelos:
        p = precios["modelos"][m]
        if not all(isinstance(p.get(k), (int, float)) and p[k] > 0 for k in ("entrada_usd_por_millon", "salida_usd_por_millon")):
            raise ValueError(f"Precios incompletos o a cero para {m}: el tope no se puede calcular.")
    return precios


def coste_estimado(precios, modelo, pregunta, max_tokens, busqueda):
    """Estimación conservadora: 1 token cada 3 caracteres de entrada y la salida máxima completa."""
    p = precios["modelos"][modelo]
    entrada = (len(pregunta) / 3 + 20) * p["entrada_usd_por_millon"] / 1e6
    salida = max_tokens * p["salida_usd_por_millon"] / 1e6
    extra = p.get("busqueda_usd_por_llamada", 0) if busqueda == "si" else 0
    return entrada + salida + extra


def coste_real(precios, modelo, uso, busqueda, estimado):
    p = precios["modelos"][modelo]
    if not uso:
        return estimado
    c = (uso.get("prompt_tokens", 0) * p["entrada_usd_por_millon"] + uso.get("completion_tokens", 0) * p["salida_usd_por_millon"]) / 1e6
    return c + (p.get("busqueda_usd_por_llamada", 0) if busqueda == "si" else 0)


def llamar_api(modelo, pregunta, busqueda, max_tokens, clave, espera_base=2.0, reintentos=3, abrir=urllib.request.urlopen, dormir=time.sleep):
    # En OpenRouter, «:online» activa la búsqueda web y se cobra aparte (docs de OpenRouter, Web Search, 02/11/2026).
    cuerpo = json.dumps({"model": modelo + (":online" if busqueda == "si" else ""), "max_tokens": max_tokens,
                         "messages": [{"role": "user", "content": pregunta}]}).encode("utf-8")
    peticion = urllib.request.Request(URL_API, data=cuerpo, method="POST",
                                      headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"})
    ultimo = None
    for intento in range(reintentos + 1):
        try:
            with abrir(peticion, timeout=120) as r:
                datos = json.loads(r.read().decode("utf-8"))
            return datos["choices"][0]["message"]["content"], datos.get("usage")
        except urllib.error.HTTPError as e:
            ultimo = f"HTTP {e.code}"
            if e.code not in REINTENTABLES:
                break
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
            ultimo = type(e).__name__
        if intento < reintentos:
            dormir(espera_base * 2 ** intento)
    raise RuntimeError(f"La llamada falló tras {reintentos + 1} intentos ({ultimo}).")


def cabecera(fila, modelo, busqueda, rep, simulado):
    return "\n".join(["---", f"id_pregunta: {fila['id']}", f"modelo: {modelo}", f"busqueda: {busqueda}", f"repeticion: {rep}",
                      f"fecha: {datetime.now().date().isoformat()}", f"simulado: {'si' if simulado else 'no'}", "---", ""])


def nombre_archivo(id_pregunta, modelo, busqueda, rep):
    return f"{id_pregunta}__{modelo.replace('/', '_').replace(':', '_')}__busq-{busqueda}__r{rep}.md"


def ejecutar(args, clave=None, llamar=llamar_api, ahora=datetime.now):
    real = args.real
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    modos = [m.strip() for m in args.modos.split(",") if m.strip()]
    if not set(modos) <= {"si", "no"}:
        raise ValueError("--modos solo admite si y no (con búsqueda y sin ella).")
    if args.tope_usd <= 0:
        raise ValueError("--tope-usd tiene que ser mayor que 0.")
    if real and not clave:
        raise ValueError("Falta la variable de entorno OPENROUTER_API_KEY. La clave no se acepta por argumento.")
    filas = leer_bateria(args.bateria, set(args.ids.split(",")) if args.ids else None)
    precios = leer_precios(args.precios, modelos, real)
    plan = [(f, m, b, r) for f in filas for m in modelos for b in modos for r in range(1, args.repeticiones + 1)]
    inicio = ahora()
    base = Path(args.salida)
    carpeta = base / inicio.strftime("%Y-%m-%d_%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=False)
    gastado, hechas, errores, parado = 0.0, 0, [], False
    previsto = sum(coste_estimado(precios, m, f["pregunta"], args.max_tokens, b) for f, m, b, _ in plan)
    print(f"{'REAL' if real else 'SIMULACIÓN'}: {len(plan)} llamadas previstas · coste máximo estimado {previsto:.2f} $ · tope {args.tope_usd:.2f} $")
    for fila, modelo, busqueda, rep in plan:
        est = coste_estimado(precios, modelo, fila["pregunta"], args.max_tokens, busqueda)
        if gastado + est > args.tope_usd:
            parado = True
            print(f"Parado antes de pasarse del tope: llevas {gastado:.2f} $ y la siguiente llamada podría costar {est:.4f} $.")
            break
        try:
            if real:
                texto, uso = llamar(modelo, fila["pregunta"], busqueda, args.max_tokens, clave, args.espera_base)
                gastado += coste_real(precios, modelo, uso, busqueda, est)
            else:
                texto = f"{AVISO_SIM}\n\nPregunta: {fila['pregunta']}\n"
                gastado += est
            (carpeta / nombre_archivo(fila["id"], modelo, busqueda, rep)).write_text(
                cabecera(fila, modelo, busqueda, rep, not real) + texto.strip() + "\n", encoding="utf-8", newline="\n")
            hechas += 1
        except RuntimeError as e:
            errores.append(f"{fila['id']} · {modelo} · búsqueda {busqueda} · r{rep}: {e}")
    fin = ahora()
    resumen = {"inicio": inicio.isoformat(timespec="seconds"), "fin": fin.isoformat(timespec="seconds"),
               "modo": "real" if real else "simulado", "bateria": Path(args.bateria).name, "modelos": modelos, "modos": modos,
               "repeticiones": args.repeticiones, "esperadas": len(plan), "hechas": hechas, "errores": errores,
               "parado_por_tope": parado, "coste_usd": round(gastado, 4), "tope_usd": args.tope_usd}
    (carpeta / "ejecucion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    registro = base / "registro-ejecuciones.csv"
    nuevo = not registro.exists()
    with open(registro, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if nuevo:
            w.writerow(["inicio", "carpeta", "modo", "esperadas", "hechas", "errores", "parado_por_tope", "coste_usd", "tope_usd"])
        w.writerow([resumen["inicio"], carpeta.name, resumen["modo"], len(plan), hechas, len(errores), parado, resumen["coste_usd"], args.tope_usd])
    print(f"Hechas {hechas} de {len(plan)} · errores {len(errores)} · coste {gastado:.2f} $ · carpeta {carpeta}")
    return resumen, carpeta


def parser():
    ap = argparse.ArgumentParser(description="Lanza la batería por API (simula por defecto).")
    ap.add_argument("--bateria", required=True)
    ap.add_argument("--precios", required=True, help="JSON con el precio por millón de tokens de cada modelo")
    ap.add_argument("--modelos", required=True, help="identificadores de OpenRouter separados por comas")
    ap.add_argument("--modos", default="si,no", help="si (con búsqueda), no (sin ella) o los dos")
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--tope-usd", type=float, required=True)
    ap.add_argument("--max-tokens", type=int, default=800)
    ap.add_argument("--ids", help="solo estas preguntas (ids separados por comas)")
    ap.add_argument("--salida", default=str(AQUI / "ejecuciones"))
    ap.add_argument("--espera-base", type=float, default=2.0, help="segundos de la primera espera entre reintentos")
    ap.add_argument("--real", action="store_true", help="llamar de verdad a la API (sin esto, simula)")
    return ap


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # tildes en la terminal de Windows
    args = parser().parse_args(argv)
    try:
        resumen, _ = ejecutar(args, clave=os.environ.get("OPENROUTER_API_KEY") if args.real else None)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 0 if resumen["hechas"] == resumen["esperadas"] and not resumen["errores"] else 1


if __name__ == "__main__":
    sys.exit(main())
