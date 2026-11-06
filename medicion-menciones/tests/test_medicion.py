"""Pruebas de la skill medicion-menciones. Ejecuta desde la carpeta de la skill: python -m unittest discover -s tests -v"""
import argparse
import contextlib
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import alarma  # noqa: E402
import consolidar_menciones as cm  # noqa: E402
import lanzar_bateria as lb  # noqa: E402

CONFIG = json.loads((RAIZ / "marcas.json").read_text(encoding="utf-8"))
CABECERA = "---\nid_pregunta: {id}\nmodelo: modelo-a\nbusqueda: si\nrepeticion: 1\nfecha: 2026-11-14\n---\n"


def escribir(carpeta, nombre, texto):
    (carpeta / nombre).write_text(texto, encoding="utf-8", newline="\n")


class Consolidacion(unittest.TestCase):
    def test_orden_y_alias(self):
        texto = "1. **FitMarket**: barato.\n2. **AtlasGym**: profesional.\n3. **Pesas y Mas**: económico."
        self.assertEqual(cm.detectar_marcas(texto, CONFIG["marcas"]), ["FitMarket", "Atlas Gym", "Pesas y Más"])

    def test_atlas_suelto_no_es_la_marca(self):
        self.assertEqual(cm.detectar_marcas("La elíptica Atlas 500 de FitMarket.", CONFIG["marcas"]), ["FitMarket"])

    def test_url_cuenta_como_cita_no_como_mencion(self):
        texto = "Guía: https://atlasgym.example/guias/mantenimiento"
        self.assertEqual(cm.detectar_marcas(texto, CONFIG["marcas"]), [])
        self.assertEqual(cm.detectar_dominios(texto), ["atlasgym.example"])

    def test_dominios_normalizados(self):
        texto = "Ver https://www.FitMarket.example/elipticas?utm_source=chat y también comunidadgym.example, y de nuevo fitmarket.example."
        self.assertEqual(cm.detectar_dominios(texto), ["fitmarket.example", "comunidadgym.example"])

    def test_no_confunde_archivos_con_dominios(self):
        self.assertEqual(cm.detectar_dominios("Lee CLAUDE.md y datos.csv"), [])

    def test_carpeta_con_y_sin_cabecera(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            escribir(d, "a.md", CABECERA.format(id="ICP1-DEC-R3") + "1. **Hierro Norte**: x.\n2. **Atlas Gym**: y.\nFuentes: https://atlasgym.example/envios")
            escribir(d, "b.md", "Sin cabecera: Atlas Gym y FitMarket.")
            escribir(d, "c.md", CABECERA.format(id="NO-EXISTE") + "Nada.")
            escribir(d, "d.md", CABECERA.format(id="ICP1-DEC-R3") + "1. **TitanPro**: inventada.\nVer guiadelgimnasio.example")
            bateria = cm.leer_bateria(RAIZ / "bateria" / "bateria-atlas.csv")
            filas, avisos = cm.analizar(d, bateria, CONFIG)
            validas = [f for f in filas if not f.get("sin_cabecera")]
            self.assertEqual(len(filas), 4)
            self.assertEqual(len(validas), 2)
            a = next(f for f in filas if f["archivo"] == "a.md")
            self.assertEqual((a["posicion_objetivo"], a["cita_objetivo"], a["fase"]), (2, True, "decisión"))
            textos = " ".join(avisos)
            self.assertIn("sin cabecera", textos)
            self.assertIn("no está en la batería", textos)
            self.assertIn("TitanPro (d.md)", avisos["nombre destacado que no está en marcas.json: ¿marca nueva, error o invención?"])
            self.assertTrue(any("guiadelgimnasio.example" in x for x in avisos["dominio no listado: comprueba que existe y que no es una invención"]))

    def test_resumen_y_rango(self):
        filas = [{"icp": "ICP1", "fase": "decisión", "redaccion": r, "aparece_objetivo": ap, "posicion_objetivo": p,
                  "cita_objetivo": False, "marcas": "x"} for r, ap, p in [("1", False, ""), ("1", False, ""), ("3", True, 2), ("3", True, 4)]]
        r = cm.resumir(filas, ["icp", "fase"])[0]
        self.assertEqual((r["n"], r["pct_aparece"], r["posicion_media"]), (4, 50.0, 3.0))
        self.assertEqual(cm.rango_redacciones(filas)[("ICP1", "decisión")], (0.0, 100.0))

    def test_bateria_con_ids_repetidos(self):
        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "b.csv"
            ruta.write_text("id,icp,pain,fase,redaccion,pregunta,con_marca\nX,ICP1,,descubrimiento,1,¿a?,no\nX,ICP1,,descubrimiento,2,¿b?,no\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                cm.leer_bateria(ruta)

    def test_modo_entidad(self):
        filas = [{"cuerpo": t, "archivo": n, "modelo": "m", "busqueda": "no"} for n, t in [
            ("1", "Atlas Gym es una cadena de gimnasios con cuota mensual."),
            ("2", "Atlas Gym es una tienda de maquinaria; no es la cadena Atlas Fitness."),
            ("3", "No tengo información sobre Atlas Gym."),
            ("4", "Atlas Gym es una tienda online de equipamiento.")]]
        tipos = [f["tipo"] for f in cm.analizar_entidad(filas, CONFIG)]
        self.assertTrue(tipos[0].startswith("confunde"))
        self.assertTrue(tipos[1].startswith("distingue"))
        self.assertEqual(tipos[2], "no sabe o no lo confirma")
        self.assertEqual(tipos[3], "descripción coherente con la entidad")

    def test_salida_no_pisa_resultados(self):
        with tempfile.TemporaryDirectory() as td:
            salida = Path(td) / "res"
            salida.mkdir()
            (salida / "previo.md").write_text("x", encoding="utf-8")
            with self.assertRaises(SystemExit):
                cm.main([str(RAIZ / "respuestas-demo" / "lab2"), "--salida", str(salida)])


def args_lanzar(td, **cambios):
    base = dict(bateria=str(RAIZ / "bateria" / "bateria-lab2.csv"), precios=str(RAIZ / "precios-ejemplo.json"),
                modelos="proveedor-a/modelo-x,proveedor-b/modelo-y", modos="si,no", repeticiones=2, tope_usd=5.0,
                max_tokens=800, ids=None, salida=str(Path(td) / "ejecuciones"), espera_base=0.0, real=False)
    base.update(cambios)
    return argparse.Namespace(**base)


class Lanzador(unittest.TestCase):
    def setUp(self):
        self.reloj = iter(datetime(2026, 11, 14, 9, 0, 0) + timedelta(seconds=i) for i in range(1000))
        self.ahora = lambda: next(self.reloj)

    def silencio(self):
        self._stdout, sys.stdout = sys.stdout, io.StringIO()

    def tearDown(self):
        if hasattr(self, "_stdout"):
            sys.stdout = self._stdout

    def test_simulacion_por_defecto_no_llama(self):
        self.silencio()
        def prohibido(*a, **k):
            raise AssertionError("la simulación no debe llamar a la API")
        with tempfile.TemporaryDirectory() as td:
            resumen, carpeta = lb.ejecutar(args_lanzar(td), llamar=prohibido, ahora=self.ahora)
            self.assertEqual((resumen["modo"], resumen["hechas"], resumen["esperadas"]), ("simulado", 24, 24))
            uno = next(carpeta.glob("L2-COM__*.md")).read_text(encoding="utf-8")
            self.assertIn("simulado: si", uno)
            self.assertIn("SIMULADA", uno)
            self.assertTrue((Path(td) / "ejecuciones" / "registro-ejecuciones.csv").exists())

    def test_tope_para_antes_de_pasarse(self):
        self.silencio()
        with tempfile.TemporaryDirectory() as td:
            resumen, _ = lb.ejecutar(args_lanzar(td, tope_usd=0.1), ahora=self.ahora)
            self.assertTrue(resumen["parado_por_tope"])
            self.assertLessEqual(resumen["coste_usd"], 0.1)
            self.assertLess(resumen["hechas"], resumen["esperadas"])

    def test_real_sin_clave_falla(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                lb.ejecutar(args_lanzar(td, real=True), clave=None, ahora=self.ahora)

    def test_real_con_precios_ilustrativos_falla(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                lb.ejecutar(args_lanzar(td, real=True), clave="clave-de-prueba", ahora=self.ahora)

    def test_tope_obligatorio_y_positivo(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            lb.parser().parse_args(["--bateria", "b", "--precios", "p", "--modelos", "m"])
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                lb.ejecutar(args_lanzar(td, tope_usd=0), ahora=self.ahora)

    def test_la_clave_no_se_acepta_por_argumento(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            lb.parser().parse_args(["--bateria", "b", "--precios", "p", "--modelos", "m", "--tope-usd", "1", "--clave", "x"])

    def test_reintentos_con_espera(self):
        esperas, intentos = [], []
        def abrir(peticion, timeout):
            intentos.append(1)
            raise urllib.error.HTTPError(lb.URL_API, 429, "demasiadas", {}, None)
        with self.assertRaises(RuntimeError):
            lb.llamar_api("m", "¿p?", "no", 10, "k", espera_base=1.0, reintentos=3, abrir=abrir, dormir=esperas.append)
        self.assertEqual((len(intentos), esperas), (4, [1.0, 2.0, 4.0]))

    def test_real_simulado_con_llamada_falsa(self):
        self.silencio()
        with tempfile.TemporaryDirectory() as td:
            precios = Path(td) / "precios.json"
            datos = json.loads((RAIZ / "precios-ejemplo.json").read_text(encoding="utf-8"))
            datos.pop("ilustrativo")
            precios.write_text(json.dumps(datos), encoding="utf-8")
            llamadas = []
            def falsa(modelo, pregunta, busqueda, max_tokens, clave, espera):
                llamadas.append(busqueda)
                return "1. **Hierro Norte**: x.", {"prompt_tokens": 30, "completion_tokens": 100}
            resumen, carpeta = lb.ejecutar(args_lanzar(td, real=True, precios=str(precios), repeticiones=1),
                                           clave="clave-de-prueba", llamar=falsa, ahora=self.ahora)
            self.assertEqual((resumen["modo"], resumen["hechas"]), ("real", 12))
            todo = "".join(p.read_text(encoding="utf-8") for p in carpeta.iterdir())
            todo += (Path(td) / "ejecuciones" / "registro-ejecuciones.csv").read_text(encoding="utf-8")
            self.assertNotIn("clave-de-prueba", todo)


class Alarma(unittest.TestCase):
    def ejecucion(self, base, nombre, **datos):
        carpeta = base / nombre
        carpeta.mkdir(parents=True)
        resumen = {"fin": "2026-11-14T09:00:00", "modo": "real", "esperadas": 2, "hechas": 2, "errores": [], "parado_por_tope": False, "tope_usd": 5}
        resumen.update(datos)
        for i in range(resumen["hechas"]):
            (carpeta / f"r{i}.md").write_text("x", encoding="utf-8")
        (carpeta / "ejecucion.json").write_text(json.dumps(resumen), encoding="utf-8")

    def test_sin_ejecuciones(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(alarma.comprobar(td, 8, date(2026, 11, 14))[0], 1)

    def test_todo_bien(self):
        with tempfile.TemporaryDirectory() as td:
            self.ejecucion(Path(td), "e1")
            self.assertEqual(alarma.comprobar(td, 8, date(2026, 11, 15))[0], 0)

    def test_antigua(self):
        with tempfile.TemporaryDirectory() as td:
            self.ejecucion(Path(td), "e1")
            self.assertEqual(alarma.comprobar(td, 8, date(2026, 11, 30))[0], 2)

    def test_incompleta_y_mira_la_ultima(self):
        with tempfile.TemporaryDirectory() as td:
            self.ejecucion(Path(td), "e1")
            self.ejecucion(Path(td), "e2", fin="2026-11-21T09:00:00", esperadas=5, hechas=3)
            codigo, problemas, ruta = alarma.comprobar(td, 8, date(2026, 11, 21))
            self.assertEqual((codigo, ruta.name), (3, "e2"))

    def test_simulada(self):
        with tempfile.TemporaryDirectory() as td:
            self.ejecucion(Path(td), "e1", modo="simulado")
            self.assertEqual(alarma.comprobar(td, 8, date(2026, 11, 14))[0], 4)
            self.assertEqual(alarma.comprobar(td, 8, date(2026, 11, 14), permitir_simulada=True)[0], 0)

    def test_escribe_estado(self):
        with tempfile.TemporaryDirectory() as td:
            self._stdout, sys.stdout = sys.stdout, io.StringIO()
            try:
                codigo = alarma.main(["--carpeta", td, "--hoy", "2026-11-14"])
            finally:
                sys.stdout = self._stdout
            self.assertEqual(codigo, 1)
            self.assertIn("AVISO", (Path(td) / "estado-alarma.md").read_text(encoding="utf-8"))


class DatosDemo(unittest.TestCase):
    def test_generador_reproducible(self):
        import generar_respuestas as gr
        with tempfile.TemporaryDirectory() as td:
            original = gr.SALIDA
            try:
                gr.SALIDA = Path(td) / "r"
                self._stdout, sys.stdout = sys.stdout, io.StringIO()
                gr.main()
                sys.stdout = self._stdout
                for sub in ("lab2", "lab4", "lab8"):
                    nuevos = sorted(p.name for p in (gr.SALIDA / sub).iterdir())
                    viejos = sorted(p.name for p in (original / sub).iterdir())
                    self.assertEqual(nuevos, viejos)
                    for n in nuevos:
                        self.assertEqual((gr.SALIDA / sub / n).read_bytes(), (original / sub / n).read_bytes(), n)
            finally:
                gr.SALIDA = original


if __name__ == "__main__":
    unittest.main()
