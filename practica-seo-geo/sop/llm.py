"""Llamadas al modelo de lenguaje (Gemini, con clave gratuita, o Anthropic). El modelo redacta y etiqueta; las
decisiones las toma Python."""
import json, os, re, sys, time
import requests
from .comun import ahora

GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/"


def disponible(caso):
    p = caso["modelo"]["proveedor"]
    if p == "claudecode":        # el modelo es Claude Code (esta sesión); no necesita clave
        return True
    return bool(os.environ.get("GEMINI_API_KEY" if p == "gemini" else "ANTHROPIC_API_KEY"))


def _gemini(modelo, cuerpo):
    clave = os.environ.get("GEMINI_API_KEY")
    if not clave:
        sys.exit("Falta GEMINI_API_KEY en .env. La clave gratuita se crea en aistudio.google.com.")
    for intento in range(4):
        r = requests.post(f"{GEMINI}{modelo}:generateContent", params={"key": clave}, json=cuerpo, timeout=600)
        if r.status_code == 429:                      # el plan gratuito limita las peticiones por minuto
            espera = 20 * (intento + 1)
            print(f"       límite por minuto del plan gratuito; espero {espera} s")
            time.sleep(espera)
            continue
        break
    datos = r.json()
    if r.status_code != 200:
        sys.exit(f"La API de Gemini devolvió {r.status_code}: {datos.get('error', {}).get('message', datos)}")
    return datos


def texto_gemini(datos):
    partes = ((datos.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in partes)


def pedir(caso, exp, nombre, sistema, usuario, max_tokens=4000, seco=False, fresco=False):
    """Guarda el prompt (para enseñarlo) y la respuesta (para no repetir la llamada)."""
    mod = caso["modelo"]
    modelo = {"gemini": mod.get("nombre_gemini"),
              "anthropic": mod.get("nombre_anthropic"),
              "claudecode": mod.get("nombre_claudecode", "claude-code")}.get(mod["proveedor"])
    (exp / "prompts" / f"{nombre}.md").write_text(
        f"# Prompt: {nombre}\n\n## Sistema\n\n{sistema}\n\n## Usuario\n\n{usuario}\n", encoding="utf-8")
    fichero = exp / "crudo" / f"llm-{nombre}.json"
    if fichero.exists() and not fresco:
        guardado = json.loads(fichero.read_text(encoding="utf-8"))
        print(f"  [respuesta del modelo del {guardado['capturado']}] {nombre}  (usa --fresco para repetir)")
        return guardado["texto"]
    print(f"  Modelo {modelo} <- prompts/{nombre}.md ({len(usuario):,} caracteres)")
    if seco:
        return None
    if mod["proveedor"] == "claudecode":
        # El modelo es Claude Code (esta sesión). No se llama a ninguna API: Claude escribe la
        # respuesta a mano en crudo/llm-<nombre>.json y al re-ejecutar el paso se reutiliza.
        sys.exit(f"[Claude Code es el modelo] No hay respuesta guardada para «{nombre}». "
                 f"Claude: lee prompts/{nombre}.md y escribe la respuesta en crudo/llm-{nombre}.json "
                 f'con la forma {{"capturado": "<fecha ISO>", "modelo": "{modelo}", "uso": null, "texto": "<respuesta>"}}. '
                 f"Después vuelve a ejecutar este paso (reutilizará la respuesta, no vuelve a parar).")
    if mod["proveedor"] == "gemini":
        datos = _gemini(modelo, {"system_instruction": {"parts": [{"text": sistema}]},
                                 "contents": [{"role": "user", "parts": [{"text": usuario}]}],
                                 "generationConfig": {"maxOutputTokens": max_tokens * 2}})
        texto, uso = texto_gemini(datos), datos.get("usageMetadata")
    else:
        clave = os.environ.get("ANTHROPIC_API_KEY")
        if not clave:
            sys.exit("Falta ANTHROPIC_API_KEY en .env.")
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=600,
                          headers={"x-api-key": clave, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                          json={"model": modelo, "max_tokens": max_tokens, "system": sistema,
                                "messages": [{"role": "user", "content": usuario}]})
        datos = r.json()
        if r.status_code != 200:
            sys.exit(f"La API de Anthropic devolvió {r.status_code}: {datos.get('error', datos)}")
        texto = "".join(b.get("text", "") for b in datos.get("content", []) if b.get("type") == "text")
        uso = datos.get("usage")
    if not texto.strip():
        sys.exit("El modelo devolvió una respuesta vacía. Repite con --fresco o revisa el límite de salida.")
    fichero.write_text(json.dumps({"capturado": ahora(), "modelo": modelo, "uso": uso, "texto": texto},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return texto


def pedir_json(*a, **k):
    texto = pedir(*a, **k)
    if texto is None:
        return None
    limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        m = re.search(r"[\[{].*[\]}]", limpio, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        sys.exit("El modelo no devolvió JSON válido. Revisa crudo/llm-*.json y repite con --fresco.")


def asistente_gemini(caso, pregunta):
    """Gemini con búsqueda de Google: devuelve la respuesta, las fuentes en que se apoya y las búsquedas que lanzó."""
    datos = _gemini(caso["modelo"]["nombre_gemini"], {"contents": [{"role": "user", "parts": [{"text": pregunta}]}],
                                                      "tools": [{"google_search": {}}]})
    meta = (datos.get("candidates") or [{}])[0].get("groundingMetadata") or {}
    fuentes = [{"url": (c.get("web") or {}).get("uri"), "titulo": (c.get("web") or {}).get("title")}
               for c in meta.get("groundingChunks") or [] if (c.get("web") or {}).get("uri")]
    return {"texto": texto_gemini(datos), "fuentes": fuentes, "busquedas": meta.get("webSearchQueries") or [], "crudo": datos}


SOLO_FUENTES = ("Trabaja solo con el material que se te da. No añadas conocimiento propio. "
                "No inventes cifras, citas, testimonios ni experiencias. Si algo no está en el material, dilo. ")
