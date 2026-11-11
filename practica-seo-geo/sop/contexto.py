"""Reúne del expediente lo que los controles de optimización necesitan saber del caso."""
from .comun import leer_csv


def de_optimizacion(caso, exp):
    c = caso["caso"]
    principal = c["consulta_principal"].lower()
    leer = lambda nombre: leer_csv(exp / nombre) if (exp / nombre).exists() else []
    grupo = next((g for g in leer("03-grupos.csv") if g["contiene_principal"] == "sí"), None)
    return {
        "principal": principal,
        "consultas_grupo": [q.strip() for q in grupo["consultas"].split(";")] if grupo else [principal],
        "preguntas_google": list(dict.fromkeys(f["pregunta"] for f in leer("03-preguntas-google.csv") if f["pregunta"]))[:12],
        "preguntas_asistentes": caso["asistentes"]["preguntas"],
        "fan_out": [f["busqueda"] for f in leer("04-fan-out.csv")][:15],
        "entidades": c["entidades_clave"],
        "dominio": c["dominio"],
        "url_propia_del_grupo": (grupo["urls_propias"].split(" (#")[0] if grupo and grupo["urls_propias"] else ""),
    }
