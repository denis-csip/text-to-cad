"""Appel a Gemini pour transformer un brief en code build123d."""
import os, re, threading
from google import genai
from google.genai import types
from prompt import SYSTEM, FIX_TEMPLATE

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


def generate_code(brief: str, temperature: float = 0.2) -> str:
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=brief,
        config=_cfg(temperature),
    )
    return _extract_code(resp.text)


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
