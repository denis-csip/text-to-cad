# -*- coding: utf-8 -*-
"""Worker build123d chaud pour le banc d'essai (meme protocole que le serveur :
processus persistant, JSON-lines). Importer OCP coute ~20 s : on ne le paie
qu'une fois pour tout le banc."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
_proc = None


def _start():
    global _proc
    if _proc is not None and _proc.poll() is None:
        return _proc
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        py = Path(sys.executable)
    _proc = subprocess.Popen(
        [str(py), str(APP / "worker.py")], cwd=str(APP),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, encoding="utf-8", bufsize=1)
    line = _proc.stdout.readline()          # attend {"ready": true}
    if not line:
        raise RuntimeError("worker n'a pas demarre")
    return _proc


def run_code(code: str, outdir: Path, timeout: int = 90):
    """Execute un script build123d, renvoie (ok, erreur, stats)."""
    outdir.mkdir(parents=True, exist_ok=True)
    script = outdir / "model.py"
    script.write_text(code, encoding="utf-8")
    p = _start()
    job = {"cmd": "build", "code_file": str(script), "outdir": str(outdir)}
    try:
        p.stdin.write(json.dumps(job) + "\n")
        p.stdin.flush()
        line = p.stdout.readline()
    except Exception as e:
        _kill()
        return False, f"worker: {e}", None
    if not line:
        _kill()
        return False, "worker: pas de reponse", None
    try:
        resp = json.loads(line)
    except Exception:
        return False, "worker: reponse illisible", None
    if resp.get("ok"):
        return True, "", resp.get("stats") or {}
    return False, str(resp.get("error", "echec"))[:200], None


def _kill():
    global _proc
    try:
        if _proc:
            _proc.kill()
    except Exception:
        pass
    _proc = None
