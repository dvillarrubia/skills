"""Cliente mínimo de DataForSEO. Guarda cada respuesta original, reutiliza capturas y apunta el coste."""
import csv, json, os, sys
import requests
from .comun import ahora

BASE = "https://api.dataforseo.com/v3/"


class DataForSEO:
    def __init__(self, exp, seco=False, fresco=False):
        self.exp, self.seco, self.fresco = exp, seco, fresco
        self.auth = (os.environ.get("DATAFORSEO_LOGIN", ""), os.environ.get("DATAFORSEO_PASSWORD", ""))

    def _exigir_claves(self, para):
        # Las claves solo se exigen al pedir de verdad: con la captura guardada no hacen falta.
        if not all(self.auth):
            sys.exit(f"No hay captura de «{para}» y faltan DATAFORSEO_LOGIN y DATAFORSEO_PASSWORD en .env "
                     "(o usa --seco para ver las peticiones).")

    def post(self, ruta, carga, nombre):
        """Devuelve la lista result de la tarea, o None en modo --seco."""
        fichero = self.exp / "crudo" / f"{nombre}.json"
        if fichero.exists() and not self.fresco:
            guardado = json.loads(fichero.read_text(encoding="utf-8"))
            print(f"  [captura del {guardado['capturado']}] {nombre}  (usa --fresco para volver a pedir)")
            return guardado["respuesta"]["tasks"][0].get("result") or []
        print(f"  POST {ruta}\n       {json.dumps(carga, ensure_ascii=False)}")
        if self.seco:
            return None
        self._exigir_claves(nombre)
        r = requests.post(BASE + ruta, auth=self.auth, json=[carga], timeout=240)
        datos = r.json()
        tarea = (datos.get("tasks") or [{}])[0]
        if datos.get("status_code") != 20000 or tarea.get("status_code") != 20000:
            sys.exit(f"DataForSEO devolvió un error en {ruta}: "
                     f"{datos.get('status_code')} {datos.get('status_message')} / "
                     f"{tarea.get('status_code')} {tarea.get('status_message')}")
        fichero.write_text(json.dumps({"capturado": ahora(), "ruta": ruta, "carga": carga, "respuesta": datos},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
        self._apuntar(ruta, nombre, datos.get("cost"))
        print(f"       coste: {datos.get('cost')} USD")
        return tarea.get("result") or []

    def get(self, ruta):
        self._exigir_claves(ruta)
        r = requests.get(BASE + ruta, auth=self.auth, timeout=60)
        return r.json()

    def _apuntar(self, ruta, nombre, coste):
        libro = self.exp / "costes.csv"
        nuevo = not libro.exists()
        with open(libro, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nuevo:
                w.writerow(["fecha", "ruta", "captura", "coste_usd"])
            w.writerow([ahora(), ruta, nombre, coste])
