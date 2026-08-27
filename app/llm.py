"""Appel a Gemini pour transformer un brief en code build123d."""
import os, re, json, threading
from google import genai
from google.genai import types
from prompt import SYSTEM, FIX_TEMPLATE, INTENT_SYSTEM, VISION_SYSTEM

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
# Gemini 3.x active le "thinking" par defaut (tres lent : ~70s). 'low' suffit
# largement pour de la generation de script et divise le temps par ~10.
THINKING = os.environ.get("GEMINI_THINKING", "low")

_client = None
_client_lock = threading.Lock()


def _cfg(temperature: float = 0.2):
    kwargs = dict(system_instruction=SYSTEM, temperature=temperature)
    if "gemini-3" in MODEL:  # thinking_level n'existe que sur Gemini 3.x
        kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=THINKING)
    return types.GenerateContentConfig(**kwargs)


def _get_client():
    global _client
    if _client is None:
        with _client_lock:                 # init atomique : evite la course
            if _client is None:            # quand N appels best-of-N demarrent ensemble
                key = os.environ.get("GEMINI_API_KEY")
                if not key:
                    raise RuntimeError("GEMINI_API_KEY non definie dans l'environnement.")
                _client = genai.Client(api_key=key)
    return _client


def _extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    code = m.group(1) if m else text
    return code.strip()


def generate_code(brief: str, temperature: float = 0.2, spec=None,
                  sketch_bytes: bytes = None) -> str:
    if spec:
        text = (
            "SPECIFICATION DE CONCEPTION VALIDEE (JSON) — respecte-la fidelement :\n"
            + json.dumps(spec, ensure_ascii=False)
            + "\n\nGenere le code build123d correspondant. Respecte EXACTEMENT les cotes "
            "et features de la spec ; reprends les valeurs (dimensions et hypotheses) comme "
            "cotes reglables en haut du script. Brief initial de l'utilisateur : " + brief)
    else:
        text = brief
    if sketch_bytes:
        text = ("Un CROQUIS de la forme approximative visee par l'utilisateur est fourni : "
                "inspire-t'en pour la silhouette globale et la disposition des features "
                "(en gardant les cotes chiffrees de la spec/du brief).\n\n" + text)
        contents = [types.Part.from_bytes(data=sketch_bytes, mime_type="image/png"), text]
    else:
        contents = text
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=contents,
        config=_cfg(temperature),
    )
    return _extract_code(resp.text)


def _intent_cfg(temperature: float = 0.2):
    kwargs = dict(system_instruction=INTENT_SYSTEM, temperature=temperature,
                  response_mime_type="application/json")
    if "gemini-3" in MODEL:
        kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=THINKING)
    return types.GenerateContentConfig(**kwargs)


def _extract_json(text: str):
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
    if m:
        t = m.group(1).strip()
    try:
        return json.loads(t)
    except Exception:
        m2 = re.search(r"\{.*\}", t, re.DOTALL)
        if m2:
            try:
                return json.loads(m2.group(0))
            except Exception:
                pass
    return {"resume": t[:200], "dimensions": [], "features": [],
            "hypotheses": [], "questions": [], "confiance": 0.0}


def capture_intent(brief: str, sketch_bytes: bytes = None):
    """Interprete le brief NL (+ croquis optionnel) en une spec de conception structuree."""
    if sketch_bytes:
        contents = [types.Part.from_bytes(data=sketch_bytes, mime_type="image/png"),
                    "Croquis fourni par l'utilisateur (forme approximative visee).\n"
                    "Brief : " + (brief or "")]
    else:
        contents = brief
    resp = _get_client().models.generate_content(
        model=MODEL, contents=contents, config=_intent_cfg())
    return _extract_json(resp.text)


def _vision_cfg(temperature: float = 0.2):
    kwargs = dict(system_instruction=VISION_SYSTEM, temperature=temperature,
                  response_mime_type="application/json")
    if "gemini-3" in MODEL:
        kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=THINKING)
    return types.GenerateContentConfig(**kwargs)


TRANSCRIBE_MODEL = os.environ.get("TRANSCRIBE_MODEL", "gemini-3.5-transcribe")


def transcribe(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    """Transcription audio -> texte via le modèle DÉDIÉ gemini-3.5-transcribe
    (API interactions : robuste au bruit réel, nettoie les hésitations).
    Repli sur le Gemini flash générique si indisponible."""
    mime = (mime or "audio/wav").split(";")[0].strip()
    client = _get_client()
    # 1) Modèle dédié (voie principale)
    try:
        import tempfile
        ext = {"audio/wav": ".wav", "audio/webm": ".webm", "audio/ogg": ".ogg",
               "audio/mpeg": ".mp3", "audio/mp3": ".mp3"}.get(mime, ".bin")
        tmp = tempfile.mktemp(suffix=ext)
        with open(tmp, "wb") as fh:
            fh.write(audio_bytes)
        try:
            f = client.files.upload(file=tmp)
            it = client.interactions.create(
                model=TRANSCRIBE_MODEL,
                input=[{"type": "audio", "uri": f.uri, "mime_type": f.mime_type}])
            t = (it.output_text or "").strip()
            if t:
                return t
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass
    except Exception as e:
        print("transcribe dédié KO, repli flash:", str(e)[:120], flush=True)
    # 2) Repli : Gemini flash générique (multimodal)
    cfg = types.GenerateContentConfig(
        system_instruction=("Transcris fidèlement cet audio en français. Réponds "
                            "UNIQUEMENT avec le texte transcrit, sans commentaire."),
        temperature=0.0,
        **({"thinking_config": types.ThinkingConfig(thinking_level=THINKING)}
           if "gemini-3" in MODEL else {}))
    resp = client.models.generate_content(
        model=MODEL,
        contents=[types.Part.from_bytes(data=audio_bytes, mime_type=mime),
                  "Transcris cet audio."],
        config=cfg)
    return (resp.text or "").strip()


def visual_check(image_bytes: bytes, brief: str, spec=None):
    """Le modele regarde le rendu 3D et juge la fidelite vs l'intention.
    Renvoie {match, defauts, correction}."""
    ctx = "Brief utilisateur : " + (brief or "")
    if spec:
        ctx += "\nSpec de conception : " + json.dumps(spec, ensure_ascii=False)
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/png"), ctx],
        config=_vision_cfg())
    return _extract_json(resp.text)


def refine_code(base_code: str, instruction: str, temperature: float = 0.2) -> str:
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=[
            f"Voici le script build123d actuel de la piece :\n```python\n{base_code}\n```",
            f"Modifie-le pour appliquer ce changement demande : « {instruction} ».\n"
            "Garde tout le reste identique autant que possible, respecte le meme contrat "
            "(variable finale `part`, cotes en mm, aucun export). Reponds UNIQUEMENT avec "
            "le bloc ```python ... ``` complet mis a jour.",
        ],
        config=_cfg(temperature),
    )
    return _extract_code(resp.text)


def fix_code(brief: str, bad_code: str, error: str) -> str:
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=[
            f"Brief initial : {brief}",
            f"Script fourni :\n```python\n{bad_code}\n```",
            FIX_TEMPLATE.format(error=error),
        ],
        config=_cfg(0.1),
    )
    return _extract_code(resp.text)
