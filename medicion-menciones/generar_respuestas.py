"""Genera las respuestas en bruto de demostración (datos sintéticos) de los laboratorios 2, 4 y 8.

Atlas Gym, sus competidores, los medios y todos los dominios son ficticios. Las respuestas imitan lo
que pegaría un alumno desde un chat de IA, pero las escribe este script con una semilla fija:
volver a ejecutarlo da exactamente los mismos archivos.

Uso: python generar_respuestas.py   (en Mac: python3)
"""
import csv
import random
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "respuestas-demo"
SEMILLA = 20261114
MODELOS = ["modelo-a", "modelo-b", "modelo-c"]
AVISO = "> Datos sintéticos del curso: respuesta inventada para practicar. Marcas y dominios ficticios."

# ---------------------------------------------------------------- textos base

INTRO = {
    "mantenimiento": "Con un uso intensivo, lo que más desgasta una cinta es la banda, el motor y la falta de lubricación.",
    "financiacion": "Para un centro pequeño, la decisión entre comprar y financiar depende sobre todo de la tesorería y del ritmo de renovación.",
    "plazos": "En maquinaria profesional, el plazo real suele depender del stock en almacén y de si la instalación la hace la propia tienda.",
    "ruido": "En un piso, el ruido de una cinta llega sobre todo por el impacto y las vibraciones que se transmiten al forjado.",
    "espacio": "En espacios pequeños conviene medir también la altura y el hueco de uso, no solo la huella de la máquina.",
    "presupuesto": "Con unos 800 €, lo importante es la garantía, el peso máximo admitido y que haya repuestos.",
    "inf": "Para un gimnasio pequeño conviene fijarse en la potencia continua del motor, la superficie de carrera y el servicio técnico.",
    "com": "Depende de lo que pese más para ti: catálogo profesional, plazos o precio.",
    "sit": "En un bajo con vecinos encima el problema es el impacto, así que importa tanto la cinta como la base.",
}

CONSEJOS = {
    "mantenimiento": ["Lubrica la banda según el uso real, no por calendario.", "Revisa la tensión y el centrado cada semana.",
                      "Aspira bajo el motor: el polvo acorta su vida.", "Lleva un registro de averías por máquina."],
    "financiacion": ["El renting incluye a menudo el mantenimiento.", "Comprar sale más barato si la máquina dura más de cinco años.",
                     "Compara el coste total, no la cuota.", "Pregunta qué pasa al final del contrato."],
    "plazos": ["Pide el plazo por escrito antes de pagar.", "Comprueba si la instalación está incluida.",
               "Pregunta por el stock real, no por el catálogo.", "Ten prevista la entrada: algunas cintas no caben por puertas estándar."],
    "ruido": ["Usa una base de caucho de al menos 15 mm.", "Evita correr a última hora.",
              "Coloca la cinta lejos de las paredes medianeras.", "Una cinta con amortiguación reduce el impacto."],
    "espacio": ["Las plegables ganan espacio, pero pierden estabilidad.", "Deja medio metro libre detrás de la cinta.",
                "Una bici estática ocupa la mitad que una elíptica.", "Mide la altura del techo si eres alto."],
    "presupuesto": ["Por debajo de 800 € la garantía suele ser de dos años.", "Mira el peso del volante de inercia.",
                    "Desconfía de las ofertas sin servicio técnico en España.", "Pregunta por los repuestos."],
    "inf": ["Motor de uso continuo, no de pico.", "Superficie de al menos 150 × 55 cm.", "Servicio técnico propio.", "Consumo eléctrico."],
    "com": ["Pide referencias de otros gimnasios.", "Compara plazos de entrega.", "Mira las condiciones de garantía."],
    "sit": ["Base antivibración profesional.", "Cinta con amortiguación regulable.", "Pide una visita técnica antes de comprar."],
}

RAZON = {
    "Hierro Norte": ["catálogo profesional amplio y servicio técnico propio", "es la referencia para gimnasios y centros de entrenamiento",
                     "muy valorada por su instalación"],
    "Atlas Gym": ["especializada en maquinaria profesional con instalación incluida", "buena relación entre precio y garantía en cintas profesionales",
                  "tiene guías de mantenimiento útiles"],
    "FitMarket": ["mucha variedad para casa y precios bajos", "envío rápido de máquinas plegables", "financiación sin intereses en compras pequeñas"],
    "Pesas y Más": ["opción económica para empezar", "buenas ofertas en elípticas de gama media", "tienda física y online"],
}

FUENTES = {
    "mantenimiento": ["https://fitnesshoy.example/mantenimiento-cintas-gimnasio", "https://comunidadgym.example/hilo/cintas-que-se-averian"],
    "financiacion": ["https://fitnesshoy.example/renting-o-compra", "https://hierronorte.example/financiacion"],
    "plazos": ["https://comunidadgym.example/hilo/plazos-de-entrega", "https://hierronorte.example/envios"],
    "ruido": ["https://comunidadgym.example/hilo/cinta-en-un-piso", "https://fitnesshoy.example/aislar-ruido-cinta"],
    "espacio": ["https://fitnesshoy.example/maquinas-plegables", "https://fitmarket.example/plegables"],
    "presupuesto": ["https://fitmarket.example/elipticas", "https://pesasymas.example/elipticas-ofertas"],
    "inf": ["https://fitnesshoy.example/elegir-cinta-profesional", "https://hierronorte.example/cintas-profesionales"],
    "com": ["https://fitnesshoy.example/tiendas-maquinaria", "https://comunidadgym.example/hilo/donde-comprar"],
    "sit": ["https://comunidadgym.example/hilo/gimnasio-en-un-bajo", "https://fitnesshoy.example/bases-antivibracion"],
}
FUENTE_ATLAS = {
    "mantenimiento": "https://atlasgym.example/guias/mantenimiento-cintas-profesionales",
    "financiacion": "https://atlasgym.example/financiacion",
    "plazos": "https://atlasgym.example/envios-e-instalacion",
    "inf": "https://atlasgym.example/cintas-correr-profesionales",
    "com": "https://atlasgym.example/",
    "sit": "https://atlasgym.example/cintas-correr-profesionales",
}

# Probabilidad de que la respuesta nombre tiendas o marcas, según el verbo de la pregunta.
P_LISTA = {1: 0.04, 2: 0.45, 3: 0.92}
# Probabilidad de que salga Atlas Gym en una lista, por ICP y fase.
P_ATLAS = {("ICP1", "descubrimiento"): 0.2, ("ICP1", "consideración"): 0.5, ("ICP1", "decisión"): 0.8,
           ("ICP2", "descubrimiento"): 0.0, ("ICP2", "consideración"): 0.15, ("ICP2", "decisión"): 0.1}
ORDEN = {"ICP1": ["Hierro Norte", "Atlas Gym", "FitMarket", "Pesas y Más"],
         "ICP2": ["FitMarket", "Pesas y Más", "Hierro Norte", "Atlas Gym"]}

TEMA = {"P5": "mantenimiento", "P4": "financiacion", "P6": "plazos", "P2": "ruido", "P3": "espacio"}


def tema_de(fila):
    if fila["id"].startswith("L2-"):
        return fila["id"][3:].lower()
    clave = fila["pain"].split(" ")[0]
    if fila["icp"] == "ICP2" and clave == "P4":
        return "presupuesto"
    return TEMA.get(clave, "mantenimiento")


# ---------------------------------------------------------------- composición

def cabecera(id_pregunta, modelo, busqueda, rep, fecha):
    return "\n".join(["---", f"id_pregunta: {id_pregunta}", f"modelo: {modelo}", f"busqueda: {busqueda}",
                      f"repeticion: {rep}", f"fecha: {fecha}", "datos: sintéticos", "---", ""])


def lista_marcas(rnd, icp, fase, forzar_atlas=None):
    orden = list(ORDEN[icp])
    p_atlas = P_ATLAS[(icp, fase)] if forzar_atlas is None else (1.0 if forzar_atlas else 0.0)
    elegidas = [orden[0]]  # la primera de la lista casi nunca cambia
    for marca in orden[1:]:
        p = p_atlas if marca == "Atlas Gym" else 0.6
        if rnd.random() < p:
            elegidas.append(marca)
    if len(elegidas) > 2 and rnd.random() < 0.35:  # la cola baila
        i = rnd.randrange(1, len(elegidas) - 1)
        elegidas[i], elegidas[i + 1] = elegidas[i + 1], elegidas[i]
    return elegidas


def componer(rnd, tema, marcas, busqueda, citar_atlas=False, estilo_fuentes=None):
    lineas = [AVISO, "", INTRO[tema], ""]
    if marcas:
        lineas.append("Estas son las opciones que más se recomiendan:")
        for n, marca in enumerate(marcas, 1):
            lineas.append(f"{n}. **{marca}**: {rnd.choice(RAZON[marca])}.")
        lineas.append("")
        lineas.append(f"Consejo: {rnd.choice(CONSEJOS[tema]).lower()}")
    else:
        consejos = rnd.sample(CONSEJOS[tema], k=min(3, len(CONSEJOS[tema])))
        for n, c in enumerate(consejos, 1):
            lineas.append(f"{n}. {c}")
        lineas.append("")
        lineas.append("Si me das más datos de tu caso, te ayudo a afinar.")
    if busqueda == "si":
        urls = rnd.sample(FUENTES[tema], k=rnd.choice([1, 2]))
        if citar_atlas and tema in FUENTE_ATLAS:
            urls.insert(rnd.randrange(0, len(urls) + 1), FUENTE_ATLAS[tema])
        estilo = estilo_fuentes or rnd.choice(["lista", "corchetes", "suelto"])
        lineas.append("")
        if estilo == "lista":
            lineas.append("Fuentes:")
            lineas += [f"- {u}" for u in urls]
        elif estilo == "corchetes":
            lineas.append("Fuentes: " + " ".join(f"[{i}] {u}" for i, u in enumerate(urls, 1)))
        else:
            lineas.append("Más información en " + ", ".join(u.split("//")[1].split("/")[0] for u in urls) + ".")
    return "\n".join(lineas) + "\n"


def escribir(carpeta, nombre, texto):
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / nombre).write_text(texto, encoding="utf-8", newline="\n")


def nombre_archivo(id_pregunta, modelo, busqueda, rep):
    return f"{id_pregunta}__{modelo}__busq-{busqueda}__r{rep}.md"


def leer_bateria(nombre):
    with open(AQUI / "bateria" / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- respuestas especiales (para leer en bruto)

ESPECIALES = {
    # lab 2 · una marca que no existe en ninguna lista
    ("L2-COM", "modelo-c", "no", 2): AVISO + "\n\nDepende de lo que pese más para ti: catálogo profesional, plazos o precio.\n\n"
        "1. **Hierro Norte**: es la referencia para gimnasios y centros de entrenamiento.\n"
        "2. **TitanPro Equipos**: líder en maquinaria de alta gama con más de 30 años en el sector.\n"
        "3. **FitMarket**: mucha variedad para casa y precios bajos.\n\n"
        "Consejo: pide referencias de otros gimnasios.\n",
    # lab 2 · la única tirada en la que Atlas Gym sale primera
    ("L2-SIT", "modelo-b", "si", 1): AVISO + "\n\nEn un bajo con vecinos encima el problema es el impacto, así que importa tanto la cinta como la base.\n\n"
        "1. **Atlas Gym**: especializada en maquinaria profesional con instalación incluida, y su guía de bases antivibración es muy completa.\n"
        "2. **Hierro Norte**: catálogo profesional amplio y servicio técnico propio.\n\n"
        "Consejo: pide una visita técnica antes de comprar.\n\nFuentes:\n- https://atlasgym.example/guias/bases-antivibracion\n"
        "- https://comunidadgym.example/hilo/gimnasio-en-un-bajo\n",
    # lab 2 · un dominio que no está en la lista (y que no existe)
    ("L2-COM", "modelo-a", "si", 3): AVISO + "\n\nDepende de lo que pese más para ti: catálogo profesional, plazos o precio.\n\n"
        "1. **Hierro Norte**: catálogo profesional amplio y servicio técnico propio.\n"
        "2. **FitMarket**: envío rápido de máquinas plegables.\n"
        "3. **Atlas Gym**: buena relación entre precio y garantía en cintas profesionales.\n\n"
        "Según el ranking de guiadelgimnasio.example, las tres tienen buenas opiniones.\n\n"
        "Fuentes: [1] https://guiadelgimnasio.example/ranking-tiendas-2026 [2] https://fitnesshoy.example/tiendas-maquinaria\n",
    # lab 8 · Atlas Gym aparece, pero para desaconsejarla
    ("ICP1-DEC-R3", "modelo-b", "si", 2): AVISO + "\n\nEn maquinaria profesional, el plazo real suele depender del stock en almacén.\n\n"
        "1. **Hierro Norte**: muy valorada por su instalación y con stock de cintas profesionales.\n"
        "2. **FitMarket**: envío rápido, aunque su gama profesional es corta.\n\n"
        "Yo evitaría **Atlas Gym** si necesitas el equipo ya: en comunidadgym.example varios usuarios se quejan de retrasos en la reposición de elípticas.\n\n"
        "Fuentes:\n- https://comunidadgym.example/hilo/plazos-de-entrega\n- https://hierronorte.example/envios\n",
    # lab 8 · «Atlas» suelto no es Atlas Gym
    ("ICP2-CON-R3", "modelo-a", "no", 1): AVISO + "\n\nEn espacios pequeños conviene medir también la altura y el hueco de uso.\n\n"
        "1. **FitMarket**: mucha variedad para casa; su elíptica plegable Atlas 500 cabe en 2 m².\n"
        "2. **Pesas y Más**: opción económica para empezar.\n\n"
        "Consejo: deja medio metro libre detrás de la cinta.\n",
    # lab 8 · te citan como fuente sin nombrarte
    ("ICP1-DES-R3", "modelo-a", "si", 1): AVISO + "\n\nCon un uso intensivo, lo que más desgasta una cinta es la banda, el motor y la falta de lubricación.\n\n"
        "1. Lubrica la banda según las horas de uso.\n2. Revisa tensión y centrado cada semana.\n3. Lleva un registro de averías por máquina.\n\n"
        "Una guía muy completa y gratuita es esta: https://atlasgym.example/guias/mantenimiento-cintas-profesionales\n\n"
        "Fuentes:\n- https://fitnesshoy.example/mantenimiento-cintas-gimnasio\n",
    # lab 8 · el modelo que contesta con pasos aunque le pidas una recomendación
    ("ICP1-DEC-R3", "modelo-c", "si", 1): AVISO + "\n\nPara llegar a tiempo a la apertura, te propongo este orden:\n\n"
        "1. Define el número de cintas y el uso diario previsto.\n2. Pide tres presupuestos con plazo de entrega por escrito.\n"
        "3. Confirma que la instalación está incluida.\n4. Reserva la fecha de montaje antes de pagar.\n\n"
        "Fuentes:\n- https://comunidadgym.example/hilo/plazos-de-entrega\n",
    # lab 8 · sin búsqueda, se inventa un dato de la marca
    ("MARCA-1", "modelo-b", "no", 1): AVISO + "\n\nSí. **Atlas Gym** ofrece instalación gratuita en 48 horas en toda España para cualquier pedido profesional, "
        "y si no cumple te devuelve el importe del envío.\n",
    # lab 8 · con búsqueda, el dato que sí publica la marca
    ("MARCA-1", "modelo-b", "si", 1): AVISO + "\n\nSegún su web, **Atlas Gym** entrega la maquinaria profesional en un plazo de 7 a 15 días laborables, "
        "con instalación incluida en la península. Hay quejas puntuales por retrasos en elípticas sin stock.\n\n"
        "Fuentes:\n- https://atlasgym.example/envios-e-instalacion\n- https://comunidadgym.example/hilo/plazos-de-entrega\n",
    # lab 8 · alias sin espacio y URL con parámetros de seguimiento
    ("ICP2-DEC-R3", "modelo-a", "si", 2): AVISO + "\n\nCon unos 800 €, lo importante es la garantía y que haya repuestos.\n\n"
        "1. **FitMarket**: financiación sin intereses en compras pequeñas.\n2. **Pesas y Más**: buenas ofertas en elípticas de gama media.\n"
        "3. **AtlasGym**: tiene alguna elíptica doméstica, aunque su fuerte es lo profesional.\n\n"
        "Fuentes:\n- https://www.fitmarket.example/elipticas?utm_source=chat&utm_medium=ia\n- https://pesasymas.example/elipticas-ofertas\n",
}

LAB4 = {
    ("L4-QUE", "modelo-a", "no"): "**Atlas Gym** es una tienda online española de maquinaria y equipamiento de gimnasio, centrada en cintas y elípticas profesionales.",
    ("L4-QUE", "modelo-a", "si"): "**Atlas Gym** es una tienda online de maquinaria de gimnasio profesional que vende a gimnasios y centros de entrenamiento, con instalación incluida.\n\nFuentes:\n- https://atlasgym.example/quienes-somos",
    ("L4-QUE", "modelo-b", "no"): "No tengo información fiable sobre Atlas Gym. Puede tratarse de una tienda pequeña o de un nombre comercial reciente.",
    ("L4-QUE", "modelo-b", "si"): "**Atlas Gym** es un comercio de venta online de equipamiento de gimnasio (cintas, elípticas y fuerza).\n\nFuentes:\n- https://atlasgym.example/\n- https://comunidadgym.example/hilo/donde-comprar",
    ("L4-QUE", "modelo-c", "no"): "**Atlas Gym** es una cadena de gimnasios con centros en varias ciudades, conocida por su cuota mensual sin permanencia y sus clases dirigidas.",
    ("L4-QUE", "modelo-c", "si"): "Hay dos entidades con nombre parecido: **Atlas Gym**, una tienda de maquinaria (atlasgym.example), y Atlas Fitness, una cadena de gimnasios (atlasfitness.example). Si buscas maquinaria, es la primera.\n\nFuentes:\n- https://atlasgym.example/\n- https://atlasfitness.example/centros",
    ("L4-QUIEN", "modelo-a", "no"): "No dispongo de datos sobre quién dirige **Atlas Gym**. Por su web, parece una empresa pequeña de venta de maquinaria.",
    ("L4-QUIEN", "modelo-a", "si"): "Según su página «Quiénes somos», **Atlas Gym** es una empresa de equipamiento fundada por un equipo con experiencia en gimnasios, aunque no publica los nombres de sus directivos.\n\nFuentes:\n- https://atlasgym.example/quienes-somos",
    ("L4-QUIEN", "modelo-b", "no"): "No puedo confirmar quién está detrás de **Atlas Gym**: no encuentro información pública sobre su propiedad.",
    ("L4-QUIEN", "modelo-b", "si"): "La web de **Atlas Gym** no indica quién la dirige. En comunidadgym.example algunos usuarios la relacionan con un distribuidor del norte, pero no hay confirmación.\n\nFuentes:\n- https://comunidadgym.example/hilo/quien-esta-detras",
    ("L4-QUIEN", "modelo-c", "no"): "**Atlas Gym** pertenece al grupo de Atlas Fitness, que gestiona sus gimnasios y cobra una cuota mensual a sus socios.",
    ("L4-QUIEN", "modelo-c", "si"): "No hay datos públicos sobre los propietarios de **Atlas Gym**. Ojo: no es la cadena Atlas Fitness, que tiene otro dominio.\n\nFuentes:\n- https://atlasgym.example/quienes-somos\n- https://atlasfitness.example/",
}

SIN_CABECERA = ("Te respondo: para un gimnasio pequeño yo miraría Hierro Norte y Atlas Gym. Las dos instalan, "
                "aunque Hierro Norte tiene más stock. FitMarket es más para casa.\n")


# ---------------------------------------------------------------- laboratorios

def lab2(rnd):
    carpeta = SALIDA / "lab2"
    for fila in leer_bateria("bateria-lab2.csv"):
        tema = tema_de(fila)
        p_lista = {"inf": 0.3, "com": 1.0, "sit": 0.85}[tema]
        for modelo in MODELOS:
            for busqueda in ("si", "no"):
                for rep in (1, 2, 3):
                    clave = (fila["id"], modelo, busqueda, rep)
                    if clave in ESPECIALES:
                        cuerpo = ESPECIALES[clave]
                    else:
                        marcas = lista_marcas(rnd, "ICP1", "consideración") if rnd.random() < p_lista else []
                        cuerpo = componer(rnd, tema, marcas, busqueda, citar_atlas=("Atlas Gym" in marcas and rnd.random() < 0.4))
                    escribir(carpeta, nombre_archivo(*clave), cabecera(*clave, "2026-11-06") + cuerpo)
    escribir(carpeta, "pegado-sin-cabecera.md", SIN_CABECERA)


def lab4():
    carpeta = SALIDA / "lab4"
    for (id_pregunta, modelo, busqueda), texto in LAB4.items():
        clave = (id_pregunta, modelo, busqueda, 1)
        escribir(carpeta, nombre_archivo(*clave), cabecera(*clave, "2026-11-07") + AVISO + "\n\n" + texto + "\n")


def lab8(rnd):
    carpeta = SALIDA / "lab8"
    for fila in leer_bateria("bateria-atlas.csv"):
        tema = tema_de(fila)
        marca = fila["con_marca"] == "si"
        redaccion = int(fila["redaccion"])
        for modelo in MODELOS:
            for busqueda in ("si", "no"):
                for rep in (1, 2):
                    clave = (fila["id"], modelo, busqueda, rep)
                    if clave in ESPECIALES:
                        cuerpo = ESPECIALES[clave]
                    elif marca:
                        marcas = ["Atlas Gym"] if rnd.random() < 0.8 else [ORDEN[fila["icp"]][0], "Atlas Gym"]
                        cuerpo = componer(rnd, tema, marcas, busqueda, citar_atlas=True)
                    else:
                        lista = modelo != "modelo-c" and rnd.random() < P_LISTA[redaccion]
                        marcas = lista_marcas(rnd, fila["icp"], fila["fase"]) if lista else []
                        cita = busqueda == "si" and tema in FUENTE_ATLAS and (
                            ("Atlas Gym" in marcas and rnd.random() < 0.5)
                            or (fila["icp"] == "ICP1" and fila["fase"] == "descubrimiento" and rnd.random() < 0.45))
                        cuerpo = componer(rnd, tema, marcas, busqueda, citar_atlas=cita)
                    escribir(carpeta, nombre_archivo(*clave), cabecera(*clave, "2026-11-14") + cuerpo)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # tildes en la terminal de Windows
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    rnd = random.Random(SEMILLA)
    lab2(rnd)
    lab4()
    lab8(rnd)
    for sub in ("lab2", "lab4", "lab8"):
        print(f"{sub}: {len(list((SALIDA / sub).glob('*.md')))} respuestas")


if __name__ == "__main__":
    main()
