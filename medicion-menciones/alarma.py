"""Alarma de la rutina de medición: avisa si la última ejecución no existe, es antigua o salió incompleta.

Una rutina sin alarma falla en silencio. Este script mira la carpeta de ejecuciones de lanzar_bateria.py
(o la que hayas montado a mano con un ejecucion.json) y deja el resultado en estado-alarma.md.

Códigos de salida: 0 todo bien · 1 no hay ejecuciones · 2 la última es demasiado antigua ·
3 incompleta, con errores o parada por el tope · 4 la última fue una simulación.

Uso (en Mac, python3):
  python <carpeta-de-la-skill>/alarma.py --carpeta ejecuciones --max-dias 8
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path


def ultima_ejecucion(carpeta):
    ejecuciones = []
    for resumen in Path(carpeta).glob("*/ejecucion.json"):
        try:
            datos = json.loads(resumen.read_text(encoding="utf-8"))
            ejecuciones.append((datos.get("fin", ""), resumen.parent, datos))
        except (json.JSONDecodeError, OSError):
            continue
    return max(ejecuciones, key=lambda x: x[0]) if ejecuciones else None


def comprobar(carpeta, max_dias, hoy, permitir_simulada=False):
    """Devuelve (código, lista de problemas, carpeta revisada)."""
    ultima = ultima_ejecucion(carpeta)
    if not ultima:
        return 1, [f"No hay ninguna ejecución en {carpeta}: la rutina no ha llegado a correr."], None
    fin, ruta, datos = ultima
    problemas, codigo = [], 0
    dia = datetime.fromisoformat(fin).date() if fin else None
    if dia is None or (hoy - dia).days > max_dias:
        problemas.append(f"La última ejecución es del {dia or 'día desconocido'}: tiene más de {max_dias} días.")
        codigo = 2
    respuestas = len([p for p in ruta.glob("*.md")])
    if datos.get("hechas") != datos.get("esperadas") or respuestas != datos.get("hechas"):
        problemas.append(f"Incompleta: {datos.get('hechas')} de {datos.get('esperadas')} respuestas previstas ({respuestas} archivos en la carpeta).")
        codigo = codigo or 3
    if datos.get("errores"):
        problemas.append(f"{len(datos['errores'])} llamadas con error, por ejemplo: {datos['errores'][0]}")
        codigo = codigo or 3
    if datos.get("parado_por_tope"):
        problemas.append(f"Se paró al llegar al tope de {datos.get('tope_usd')} $: revisa el tope o la batería.")
        codigo = codigo or 3
    if datos.get("modo") == "simulado" and not permitir_simulada:
        problemas.append("La última ejecución fue una simulación: no mide nada.")
        codigo = codigo or 4
    return codigo, problemas, ruta


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # tildes en la terminal de Windows
    ap = argparse.ArgumentParser(description="Comprueba la última ejecución de la rutina de medición.")
    ap.add_argument("--carpeta", required=True, help="carpeta con una subcarpeta por ejecución")
    ap.add_argument("--max-dias", type=int, default=8)
    ap.add_argument("--hoy", help="fecha de referencia AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--permitir-simulada", action="store_true", help="no avisar si la última fue una simulación (para practicar)")
    a = ap.parse_args(argv)
    hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    codigo, problemas, ruta = comprobar(a.carpeta, a.max_dias, hoy, a.permitir_simulada)
    carpeta = Path(a.carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    if codigo == 0:
        texto = f"# Alarma de la medición: todo bien\n\nComprobado el {hoy}. Última ejecución: `{ruta.name}`.\n"
    else:
        texto = (f"# AVISO: la medición necesita revisión\n\nComprobado el {hoy}.\n\n" + "\n".join(f"- {p}" for p in problemas)
                 + "\n\nNo publiques ni envíes el informe de esta semana hasta revisarlo.\n")
    (carpeta / "estado-alarma.md").write_text(texto, encoding="utf-8", newline="\n")
    print(texto.strip())
    return codigo


if __name__ == "__main__":
    sys.exit(main())
