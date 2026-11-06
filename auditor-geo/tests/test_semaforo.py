"""Pruebas del semáforo con dos webs de prueba servidas en local (sin red)."""
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import semaforo as s  # noqa: E402

PARRAFO_BUENO = ("Una cinta de correr doméstica necesita un motor de al menos 2,5 CV para un uso diario de 30 min. "
                 "Según nuestras pruebas de marzo de 2026 con 12 modelos, las de menos potencia se calientan antes "
                 "de los 45 minutos y pierden velocidad en las pendientes. Por eso recomendamos mirar la potencia "
                 "continua, no la de pico, y comprobar que la garantía del motor sea de 5 años o más.")
PARRAFO_BUENO_2 = ("El banco de musculación plegable aguanta hasta 300 kg si la estructura es de acero de 2 mm. "
                   "En el informe de enero de 2026 revisamos 8 bancos y solo 3 llegaban a esa carga sin holgura en "
                   "el respaldo. Si entrenas con barra, pide la ficha de carga máxima y fíjate en el ancho del "
                   "asiento, que debería superar los 25 cm para que la espalda quede estable.")
RELLENO = ("En este artículo vamos a hablar de muchas cosas interesantes sobre el mundo del fitness y del "
           "entrenamiento en casa, porque es un tema que nos apasiona y que cada vez interesa a más gente que "
           "quiere ponerse en forma sin salir de casa y sin gastar demasiado dinero en un gimnasio.")

JSONLD = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "name": "Atlas Gym", "url": "https://atlasgym.example/",
     "logo": "https://atlasgym.example/logo.png", "sameAs": ["https://example.org/atlas-gym"]},
    {"@type": "Product", "name": "Cinta T-500", "offers": {"@type": "Offer", "price": "899",
                                                            "priceCurrency": "EUR",
                                                            "availability": "https://schema.org/InStock"}}]})

BUENA = f"""<!doctype html><html lang="es"><head><title>Cintas</title>
<script type="application/ld+json">{JSONLD}</script></head><body>
<h1>Cintas de correr para casa</h1><h2>Potencia</h2><p>{PARRAFO_BUENO}</p>
<h2>Bancos</h2><p>{PARRAFO_BUENO_2} <a href="/informe">Ver informe</a></p>
<h3>Medidas</h3><p>{RELLENO}</p><img src="a.jpg" alt="Cinta T-500"></body></html>"""

MALA = """<!doctype html><html><head><title>App</title>
<script type="application/ld+json">{"@type": "Organization", "name": </script>
<script src="a.js"></script><script src="b.js"></script><script src="c.js"></script></head>
<body><div id="root"></div><h2>Ofertas</h2><h4>Detalle</h4><img src="x.jpg"></body></html>"""

ROBOTS_BUENA = "User-agent: *\nDisallow: /carrito/\n"
ROBOTS_MALA = """User-agent: GPTBot
Disallow: /

User-agent: PerplexityBot
Allow: /
Disallow: /

User-agent: OAI-SearchBot
User-agent: Claude-SearchBot
Disallow: /

User-agent: *
Allow: /
"""


def servidor(paginas, robots, llms=None, prohibido_ua=None):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            ua = self.headers.get("User-Agent", "")
            if prohibido_ua and prohibido_ua in ua:
                return self.responder(403, "text/html", "Forbidden")
            if self.path == "/robots.txt":
                return self.responder(200, "text/plain", robots) if robots else self.responder(404, "text/plain", "")
            if self.path == "/llms.txt":
                return self.responder(200, "text/plain", llms) if llms else self.responder(404, "text/html", "<h1>404</h1>")
            if self.path in paginas:
                return self.responder(200, "text/html; charset=utf-8", paginas[self.path])
            return self.responder(404, "text/html", "<h1>No existe</h1>")

        def responder(self, codigo, tipo, cuerpo):
            datos = cuerpo.encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def colores(inf):
    return {p["pilar"].split(". ")[1]: p["color"] for p in inf["pilares"]}


class Robots(unittest.TestCase):
    def setUp(self):
        self.g = s.parsear_robots(ROBOTS_MALA)

    def test_bloqueo_propio(self):
        self.assertFalse(s.evaluar_robots(self.g, "GPTBot", "/")["permitido"])

    def test_comodin(self):
        r = s.evaluar_robots(self.g, "ClaudeBot", "/")
        self.assertTrue(r["permitido"]); self.assertEqual(r["grupo"], "*")

    def test_varios_agentes_en_un_grupo(self):
        self.assertFalse(s.evaluar_robots(self.g, "Claude-SearchBot", "/blog/")["permitido"])

    def test_contradiccion_allow_gana_empate(self):
        r = s.evaluar_robots(self.g, "PerplexityBot", "/")
        self.assertTrue(r["permitido"])
        self.assertTrue(r["contradicciones"])

    def test_regla_mas_larga(self):
        g = s.parsear_robots("User-agent: *\nDisallow: /blog/\nAllow: /blog/guias/\n")
        self.assertTrue(s.evaluar_robots(g, "GPTBot", "/blog/guias/cintas")["permitido"])
        self.assertFalse(s.evaluar_robots(g, "GPTBot", "/blog/otro")["permitido"])

    def test_comodines_y_fin(self):
        g = s.parsear_robots("User-agent: *\nDisallow: /*.pdf$\n")
        self.assertFalse(s.evaluar_robots(g, "x", "/a/ficha.pdf")["permitido"])
        self.assertTrue(s.evaluar_robots(g, "x", "/a/ficha.pdf?v=2")["permitido"])

    def test_disallow_vacio(self):
        g = s.parsear_robots("User-agent: GPTBot\nDisallow:\n")
        self.assertTrue(s.evaluar_robots(g, "GPTBot", "/")["permitido"])


class Citabilidad(unittest.TestCase):
    def test_pasaje_bueno(self):
        self.assertTrue(s.es_citable({"texto": PARRAFO_BUENO, "enlace": False})["citable"])

    def test_relleno(self):
        self.assertFalse(s.es_citable({"texto": RELLENO, "enlace": False})["citable"])

    def test_corto(self):
        self.assertIsNone(s.es_citable({"texto": "Precio: 899 € en 2026.", "enlace": False}))


class WebBuena(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv, base = servidor({"/cintas/": BUENA}, ROBOTS_BUENA, llms="# Atlas Gym\n> Tienda ficticia\n")
        cls.inf = s.auditar(base + "/cintas/", timeout=5)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def test_colores(self):
        c = colores(self.inf)
        self.assertEqual(c["Schema"], s.VERDE)
        self.assertEqual(c["Acceso de bots"], s.VERDE)
        self.assertEqual(c["Encabezados"], s.VERDE)
        self.assertEqual(c["llms.txt"], s.VERDE)
        self.assertEqual(c["Citabilidad"], s.VERDE)

    def test_renderizado_avisa_de_js(self):
        p = self.inf["pilares"][0]
        self.assertIn("Falta comparar con JavaScript", p["evidencia"])
        self.assertTrue(any("JavaScript" in x for x in self.inf["no_comprobado"]))

    def test_markdown_y_json(self):
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "semaforo.md"
            base = self.inf["url"]
            self.assertEqual(s.main([base, "--salida", str(destino)]), 0)
            md = destino.read_text(encoding="utf-8")
            self.assertIn("| 7. Citabilidad |", md)
            self.assertEqual(len(json.loads(destino.with_suffix(".json").read_text(encoding="utf-8"))["pilares"]), 7)


class WebMala(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv, base = servidor({"/": MALA}, ROBOTS_MALA, prohibido_ua="PerplexityBot")
        cls.inf = s.auditar(base + "/", timeout=5)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def test_colores(self):
        c = colores(self.inf)
        self.assertEqual(c["Renderizado"], s.ROJO)
        self.assertEqual(c["Schema"], s.ROJO)
        self.assertEqual(c["Encabezados"], s.ROJO)
        self.assertEqual(c["Densidad"], s.ROJO)
        self.assertEqual(c["Citabilidad"], s.ROJO)

    def test_llms_ausente_no_es_rojo(self):
        p = colores(self.inf)["llms.txt"]
        self.assertEqual(p, s.AMBAR)

    def test_bots(self):
        p = self.inf["pilares"][2]
        self.assertEqual(p["color"], s.ROJO)  # los tres bots de búsqueda, bloqueados o con 403
        self.assertIn("GPTBot bloqueado en robots.txt", p["evidencia"])
        perplexity = next(b for b in self.inf["detalle"]["bots"] if b["bot"] == "PerplexityBot")
        self.assertEqual(perplexity["robots"], "permitido")
        self.assertEqual(perplexity["http"], 403)
        self.assertTrue(perplexity["contradicciones"])


class Errores(unittest.TestCase):
    def test_esquema_no_valido(self):
        with self.assertRaises(ValueError):
            s.auditar("ftp://atlasgym.example/")

    def test_pagina_404(self):
        srv, base = servidor({}, None)
        try:
            inf = s.auditar(base + "/no-existe/", timeout=5)
            self.assertEqual(inf["codigo"], 404)
            self.assertTrue(all(p["color"] == s.NC for p in inf["pilares"]))
        finally:
            srv.shutdown(); srv.server_close()


if __name__ == "__main__":
    unittest.main()
