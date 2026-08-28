"""Backend text-to-CAD local : texte -> Gemini -> build123d -> STL/STEP/GLB -> slice -> envoi Bambu."""
import os, re, subprocess, sys, json, threading, queue
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))

PROJ = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
load_dotenv(PROJ / ".env")
import llm

APP = PROJ / "app"
WORK = APP / "work"
WORK.mkdir(exist_ok=True)
VENV_PY = PROJ / ".venv" / "Scripts" / "python.exe"
if not VENV_PY.exists():                 # Linux / Docker : pas de venv Windows
    VENV_PY = Path(sys.executable)       # -> le Python courant (a build123d installe)
EXEC = APP / "_exec_model.py"
SEND = PROJ / "bambu_lan_send.py"

ORCA = Path(r"C:\Program Files\OrcaSlicer\orca-slicer.exe")
BBL = ORCA.parent / "resources" / "profiles" / "BBL"
PROC = BBL / "process" / "0.20mm Standard @BBL X1C.json"
MACH = BBL / "machine" / "Bambu Lab X1 Carbon 0.4 nozzle.json"
FILA = BBL / "filament" / "Bambu PLA Basic @BBL X1C.json"

class WarmWorker:
    """Processus build123d persistant : importe le noyau CAO une seule fois."""

    def __init__(self):
        self._lock = threading.Lock()
        self._proc = None

    def _readline(self, timeout):
        q = queue.Queue()
        proc = self._proc

        def rd():
            try:
                q.put(proc.stdout.readline())
            except Exception:
                q.put(None)
        threading.Thread(target=rd, daemon=True).start()
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def _alive(self):
        return self._proc is not None and self._proc.poll() is None

    def _kill(self):
        try:
            self._proc.kill()
        except Exception:
            pass
        self._proc = None

    def _spawn(self):
        self._proc = subprocess.Popen(
            [str(VENV_PY), str(APP / "worker.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, cwd=str(WORK), bufsize=1)
        return self._readline(120) is not None  # import build123d ~20 s

    def warmup(self):
        with self._lock:
            if not self._alive():
                self._spawn()

    def run(self, code_file, outdir, timeout=60):
        with self._lock:
            if not self._alive() and not self._spawn():
                return False, "worker: demarrage impossible", {}
            try:
                self._proc.stdin.write(json.dumps(
                    {"code_file": str(code_file), "outdir": str(outdir)}) + "\n")
                self._proc.stdin.flush()
            except Exception as e:
                self._kill()
                return False, f"worker: ecriture echouee ({e})", {}
            line = self._readline(timeout)
            if line is None:
                self._kill()  # respawn au prochain appel
                return False, "worker: timeout d'execution (script trop long ?)", {}
            try:
                resp = json.loads(line)
            except Exception:
                return False, "worker: reponse invalide", {}
            return resp.get("ok", False), resp.get("error", ""), resp.get("stats", {})

    def run_raw(self, job, timeout=120):
        with self._lock:
            if not self._alive() and not self._spawn():
                return {"ok": False, "error": "worker: demarrage impossible"}
            try:
                self._proc.stdin.write(json.dumps(job) + "\n")
                self._proc.stdin.flush()
            except Exception as e:
                self._kill()
                return {"ok": False, "error": f"worker: ecriture echouee ({e})"}
            line = self._readline(timeout)
            if line is None:
                self._kill()
                return {"ok": False, "error": "worker: timeout"}
            try:
                return json.loads(line)
            except Exception:
                return {"ok": False, "error": "worker: reponse invalide"}


WORKER = WarmWorker()
threading.Thread(target=WORKER.warmup, daemon=True).start()

app = FastAPI(title="text-to-CAD local")

# --- Authentification fédérée IDEAS (portée de ARIZ-Copilot) ----------------
import auth
from fastapi import Request
from starlette.concurrency import run_in_threadpool
auth.init_db()

COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "1") != "0"   # False en dev http
_OPEN_PATHS = {"/", "/healthz", "/api/login", "/api/me", "/api/logout"}


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.middleware("http")
async def _gate(request, call_next):
    """Tout ce qui n'est pas public exige une session IDEAS active."""
    p = request.url.path
    if p in _OPEN_PATHS or p.startswith("/static") or p.startswith("/favicon"):
        return await call_next(request)
    user = await run_in_threadpool(
        auth.current_user, request.cookies.get(auth.COOKIE_NAME, ""))
    if user is None:
        return JSONResponse({"error": "AUTH_REQUIRED"}, status_code=401)
    return await call_next(request)


@app.post("/api/login")
async def api_login(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    if not email or not password:
        return JSONResponse({"error": "Email et mot de passe requis."}, 400)
    res = await run_in_threadpool(auth.signin_ideas, email, password)
    if res.get("error") or not res.get("user"):
        if res.get("unreachable"):
            return JSONResponse({"error": "IDEAS_UNAVAILABLE"}, 503)
        return JSONResponse({"error": "IDEAS_AUTH_FAILED"}, 401)
    u = res["user"]
    user, _is_new = await run_in_threadpool(
        auth.upsert_user, u["email"], u.get("name"), u.get("id"))
    if user["status"] == "blocked":
        return JSONResponse({"error": "BLOCKED"}, 403)
    if user["status"] == "pending":       # nouvel utilisateur : attend validation admin
        return JSONResponse({"pending": True, "name": user["name"]})
    resp = JSONResponse({"ok": True, "user": {
        "email": user["email"], "name": user["name"],
        "is_admin": bool(user["is_admin"])}})
    resp.set_cookie(auth.COOKIE_NAME, auth.make_session(user), httponly=True,
                    samesite="lax", secure=COOKIE_SECURE,
                    max_age=auth.SESSION_TTL, path="/")
    return resp


@app.get("/api/me")
async def api_me(request: Request):
    user = await run_in_threadpool(
        auth.current_user, request.cookies.get(auth.COOKIE_NAME, ""))
    if not user:
        return JSONResponse({"authenticated": False})
    return JSONResponse({"authenticated": True, "user": {
        "email": user["email"], "name": user["name"],
        "is_admin": bool(user["is_admin"])}})


@app.post("/api/logout")
async def api_logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(auth.COOKIE_NAME, path="/")
    return resp


async def _admin(request):
    user = await run_in_threadpool(
        auth.current_user, request.cookies.get(auth.COOKIE_NAME, ""))
    return user if (user and user["is_admin"]) else None


@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    if not await _admin(request):
        return JSONResponse({"error": "forbidden"}, 403)
    return JSONResponse({"users": await run_in_threadpool(auth.list_users)})


@app.post("/api/admin/validate")
async def api_admin_validate(request: Request):
    if not await _admin(request):
        return JSONResponse({"error": "forbidden"}, 403)
    try:
        body = await request.json()
        await run_in_threadpool(auth.set_status,
                                (body.get("email") or "").strip(), body.get("status") or "")
    except Exception as e:
        return JSONResponse({"error": str(e)}, 400)
    return JSONResponse({"ok": True})


class Brief(BaseModel):
    brief: str
    spec: dict | None = None       # spec d'intention confirmee (optionnelle)
    sketch: str | None = None      # croquis (data URL PNG) optionnel


class IntentReq(BaseModel):
    brief: str
    sketch: str | None = None      # croquis (data URL PNG) optionnel


def _dataurl_bytes(s):
    if not s:
        return None
    import base64 as _b
    try:
        return _b.b64decode(s.split(",", 1)[-1])
    except Exception:
        return None


class RefineReq(BaseModel):
    instruction: str
    faces: list = []   # faces sélectionnées : [{i, label, c:[x,y,z]}, ...]
    edges: list = []   # arêtes sélectionnées : centres [x,y,z] (mm)


class RebuildReq(BaseModel):
    overrides: dict


class FaceOpReq(BaseModel):
    face_index: int
    op: str      # "extrude" | "percer"
    shape: str = "hexagone"  # hexagone | cercle | rectangle
    size: float = 10.0       # taille du profil (mm)
    depth: float = 8.0       # hauteur d'extrusion / profondeur (mm)


class EdgeOpReq(BaseModel):
    face_indices: list = []   # 1 face = toutes ses arêtes ; 2+ = arêtes d'intersection
    mids: list | None = None  # centres d'arêtes cliquées (sélection directe d'arêtes)
    op: str = "chamfer"       # "fillet" | "chamfer"
    radius: float = 3.0


class PasteOpReq(BaseModel):
    face_index: int
    source: str = "text"   # "text" | "svg"
    content: str = ""      # texte, ou markup SVG
    size: float = 15.0     # taille cible (mm) : font_size (texte) / plus grande dim (svg)
    mode: str = "relief"   # "relief" | "gravure" | "through"
    depth: float = 2.0     # profondeur relief/gravure (mm) ; ignoré pour through
    solid: bool = False    # texte : remplir les contrepoinçons (centres des o, a, e…)


class SendReq(BaseModel):
    ip: str
    code: str
    serial: str
    start: bool = False


STATE = {"brief": None, "stats": {}}
MESH = {"active": False, "stats": {}}


class MeshStampReq(BaseModel):
    point: list
    normal: list
    source: str = "text"      # text | svg
    content: str = ""
    size: float = 15.0
    mode: str = "relief"      # relief | gravure | through
    depth: float = 2.0
    solid: bool = False


def _current_code() -> str | None:
    f = WORK / "generated_model.py"
    return f.read_text(encoding="utf-8") if f.exists() else None


def _clear_outputs():
    for f in ("model.stl", "model.step", "model.glb", "model.3mf", "plate_1.gcode"):
        (WORK / f).unlink(missing_ok=True)


def _files_ok():
    return {"glb": "/work/model.glb", "stl": "/work/model.stl", "step": "/work/model.step"}


# --- Cotes reglables : parse les parametres numeriques en tete de script ---
PARAM_RE = re.compile(r'^([A-Za-z_]\w*)\s*=\s*(-?\d+(?:\.\d+)?)\s*(?:#\s*(.*))?$')


def _fmt_num(v):
    v = float(v)
    return str(int(v)) if v == int(v) else str(round(v, 3))


def _params_from_code(code):
    params = []
    for raw in (code or "").splitlines():
        m = PARAM_RE.match(raw.strip())
        if not m:
            continue
        name, val = m.group(1), float(m.group(2))
        label = (m.group(3) or name).strip()
        lo = 0.0 if val >= 0 else round(val * 2, 2)
        hi = round(val * 2.5, 2) if val > 0 else 10.0
        if hi <= val:
            hi = val + 10
        step = 1 if (val == int(val) and abs(val) >= 20) else 0.1
        params.append({"name": name, "value": val, "label": label,
                       "min": round(lo, 2), "max": hi, "step": step})
    return params


def _apply_overrides(code, overrides):
    out = []
    for raw in code.splitlines():
        m = PARAM_RE.match(raw.strip())
        if m and m.group(1) in overrides:
            new = _fmt_num(overrides[m.group(1)])
            out.append(re.sub(r'(=\s*)-?\d+(?:\.\d+)?',
                              lambda mm: mm.group(1) + new, raw, count=1))
        else:
            out.append(raw)
    return "\n".join(out)


MAX_ATTEMPTS = 4   # 1 génération + jusqu'à 3 auto-corrections (l'erreur est renvoyée à Gemini)


def _run_with_retry(seed_code: str, context: str) -> dict:
    code = seed_code
    ok, log, stats = _run_model(code)
    attempts = 1
    while not ok and attempts < MAX_ATTEMPTS:
        try:
            code = llm.fix_code(context, code, log)
        except Exception as e:
            log += f"\n[fix LLM echoue: {e}]"
            break
        ok, log2, stats = _run_model(code)
        attempts += 1
        log = log + f"\n\n--- correction auto #{attempts - 1} ---\n" + log2
    if ok:
        STATE.update(brief=context, stats=stats)
    return {"ok": ok, "code": code, "log": log, "stats": stats,
            "attempts": attempts, "files": _files_ok() if ok else {},
            "params": _params_from_code(code) if ok else []}


def _run_model(code: str) -> tuple[bool, str, dict]:
    (WORK / "generated_model.py").write_text(code, encoding="utf-8")
    ok, err, stats = WORKER.run(WORK / "generated_model.py", WORK, timeout=60)
    if ok and stats:
        return True, "OK (worker chaud)", stats
    return False, err or "echec du worker", stats


BEST_OF_N = 3   # candidats generes en parallele (inference-time scaling facon GIFT)


def _best_of_n(gen_fn, context: str, n: int = BEST_OF_N) -> dict:
    """Genere n candidats en parallele (temperatures variees), execute chacun,
    garde le PREMIER qui produit un solide valide. Si aucun n'est valide, repli
    sur la boucle de correction iterative. Ameliore la fiabilite des ordres complexes."""
    import concurrent.futures
    temps = [0.2, 0.5, 0.8, 1.0][:max(1, n)]
    codes = []
    errs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(temps)) as ex:
        futs = [ex.submit(gen_fn, t) for t in temps]
        for f in concurrent.futures.as_completed(futs):
            try:
                c = f.result()
                if c and c.strip():
                    codes.append(c)
            except Exception as e:
                errs.append(f"{type(e).__name__}: {e}")
    if errs:
        print("BEST_OF_N gen errors:", errs, flush=True)
    if not codes:
        return {"ok": False, "log": "Erreur LLM : aucun candidat genere."}
    valid = None
    last_log = ""
    for code in codes:                       # execution serialisee (worker chaud unique)
        ok, log, stats = _run_model(code)
        if ok and stats:
            valid = (code, stats)
            break
        last_log = log
    if valid:
        code, stats = valid
        _run_model(code)                     # regenere les sorties pour le gagnant
        STATE.update(brief=context, stats=stats)
        return {"ok": True, "code": code, "stats": stats, "attempts": 1,
                "candidates": len(codes), "files": _files_ok(),
                "params": _params_from_code(code)}
    return _run_with_retry(codes[0], context)   # aucun valide -> correction iterative


@app.post("/intent")
def intent(req: IntentReq):
    """Capture d'intention : brief NL (+ croquis) -> spec de conception structuree."""
    return {"spec": llm.capture_intent(req.brief, _dataurl_bytes(req.sketch))}


class VisualReq(BaseModel):
    image: str                     # data URL PNG (base64) du rendu 3D
    brief: str = ""
    spec: dict | None = None


class FeaReq(BaseModel):
    force_N: float = 20.0
    material: str = "PLA"
    direction: list | None = None      # [x,y,z] optionnel (defaut : -Z)
    loads: list | None = None          # efforts surfaciques : [{c:[x,y,z], force_N, direction:[x,y,z]}]
    fixed: dict | None = None          # encastrement choisi : {c:[x,y,z]}
    self_weight: bool = False          # ajouter le poids propre de la piece


@app.post("/fea")
def fea_check(req: FeaReq):
    """Garde-fou de structure minimaliste : STEP courant -> coefficient de securite.
    Execute dans le worker (son thread principal) car Gmsh installe un handler de
    signal invalide hors du thread principal."""
    step = WORK / "model.step"
    if not step.exists():
        return {"ok": False, "error": "Aucune piece parametrique (genere d'abord une piece)."}
    d = list(req.direction) if req.direction else [0, 0, -1]
    stl = WORK / "model.stl"
    return WORKER.run_raw({"cmd": "fea", "step_path": str(step), "force_N": req.force_N,
                           "material": req.material, "direction": d,
                           "loads": req.loads, "fixed": req.fixed, "self_weight": req.self_weight,
                           "stl_path": str(stl) if stl.exists() else None}, timeout=180)


class TranscribeReq(BaseModel):
    audio: str                     # data URL (base64) de l'enregistrement
    mime: str = "audio/webm"


@app.post("/transcribe")
def transcribe(req: TranscribeReq):
    """Repli vocal universel : audio -> texte via Gemini (si Web Speech absent)."""
    data = _dataurl_bytes(req.audio)
    if not data:
        return {"ok": False, "error": "audio vide"}
    mime = (req.mime or "audio/wav").split(";")[0].strip()
    print(f"transcribe: {mime}, {len(data)//1024} Ko", flush=True)
    try:  # copie de diagnostic : dernier audio recu (ecrase a chaque fois)
        dbg = Path("/data") if Path("/data").exists() else WORK
        (dbg / "last_audio.bin").write_bytes(data)
        (dbg / "last_audio.txt").write_text(mime, encoding="utf-8")
    except Exception:
        pass
    try:
        t = llm.transcribe(data, mime)
        if not t:                     # les reponses vides sont parfois transitoires
            t = llm.transcribe(data, mime)
        if not t:
            return {"ok": False,
                    "error": f"Transcription vide ({mime}, {len(data)//1024} Ko recus)."}
        return {"ok": True, "text": t}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.post("/visual_check")
def visual_check(req: VisualReq):
    """Feedback visuel : le modele regarde le rendu et juge la fidelite vs l'intention."""
    import base64 as _b64
    data = req.image.split(",", 1)[-1]          # enleve l'entete data:image/png;base64,
    try:
        img = _b64.b64decode(data)
    except Exception:
        return {"verdict": {"match": True, "defauts": [], "correction": ""}}
    return {"verdict": llm.visual_check(img, req.brief, req.spec)}


@app.post("/generate")
def generate(b: Brief):
    MESH["active"] = False
    _clear_outputs()
    _sketch = _dataurl_bytes(b.sketch)
    return _best_of_n(
        lambda t: llm.generate_code(b.brief, temperature=t, spec=b.spec,
                                    sketch_bytes=_sketch), b.brief)


@app.post("/refine")
def refine(r: RefineReq):
    base = _current_code()
    if not base:
        return {"ok": False, "log": "Aucune piece a affiner : genere d'abord une piece."}
    _clear_outputs()
    instruction = r.instruction
    if r.faces:
        desc = " ; ".join(
            f"« {f.get('label','?')} » de centre approx {f.get('c')}" for f in r.faces)
        n = len(r.faces)
        instruction = (
            f"CONTEXTE SPATIAL — l'utilisateur a sélectionné {n} face(s) précise(s) : {desc}. "
            "Applique l'opération demandée UNIQUEMENT à ces faces (ou, pour un congé/chanfrein "
            "entre deux faces, à leur ARÊTE D'INTERSECTION), et surtout PAS au reste de la pièce. "
            "Récupère une face par proximité : "
            "`_sel = min(part.faces(), key=lambda f: (f.center() - Vector(x, y, z)).length)`. "
            "Pour l'arête commune à 2 faces sélectionnées, garde les arêtes de l'une dont le centre "
            "coïncide avec une arête de l'autre, et applique `fillet`/`chamfer` UNIQUEMENT sur ces "
            "arêtes-là (n'arrondis/ne chanfreine JAMAIS toutes les arêtes de la pièce). "
            f"DEMANDE DE L'UTILISATEUR : {r.instruction}")
    if r.edges:
        elist = " ; ".join(str([round(float(x), 2) for x in m]) for m in r.edges)
        instruction = (
            f"CONTEXTE SPATIAL — l'utilisateur a sélectionné à la souris {len(r.edges)} arête(s) "
            f"précise(s), de centres (mm) : {elist}. "
            "L'opération demandée porte sur CES arêtes (ou sur leur voisinage explicitement "
            "demandé), PAS sur le reste de la pièce. Récupère une arête par proximité : "
            "`_e = min(part.edges(), key=lambda e: (e.center() - Vector(x, y, z)).length)`. "
            "Si l'utilisateur parle du CONTOUR (tout le tour, le pourtour, la boucle) d'une arête "
            "sélectionnée, utilise le helper FOURNI `contour_edges(part, (x, y, z))` qui renvoie "
            "TOUTES les arêtes du contour contenant l'arête la plus proche du point — ne devine "
            "jamais le contour toi-même. Encadre fillet/chamfer d'un try/except avec repli de "
            "rayon (r, r/2, r/4). "
            f"DEMANDE DE L'UTILISATEUR : {instruction if r.faces else r.instruction}")
    ctx = f"{STATE.get('brief') or ''} | modification: {r.instruction}"
    return _best_of_n(lambda t: llm.refine_code(base, instruction, temperature=t), ctx)


@app.post("/rebuild")
def rebuild(r: RebuildReq):
    """Reconstruit la piece avec de nouvelles valeurs de cotes (sans LLM, ~0.5 s).
    En cas de geometrie invalide, ne touche PAS au modele courant (dernier etat valide)."""
    code = _current_code()
    if not code:
        return {"ok": False, "error": "Aucune piece a reconstruire."}
    new_code = _apply_overrides(code, r.overrides)
    trial = WORK / "_trial.py"
    trial.write_text(new_code, encoding="utf-8")
    ok, err, stats = WORKER.run(trial, WORK, timeout=60)
    if ok and stats:
        (WORK / "generated_model.py").write_text(new_code, encoding="utf-8")
        STATE.update(stats=stats)
        return {"ok": True, "stats": stats, "files": _files_ok(),
                "params": _params_from_code(new_code)}
    return {"ok": False, "error": err}  # modele courant intact


@app.get("/params")
def get_params():
    return {"params": _params_from_code(_current_code())}


class SvgPartReq(BaseModel):
    content: str
    height: float = 100.0    # taille cible (plus grande dimension, mm)
    thickness: float = 2.0   # épaisseur d'extrusion (mm)
    invert: bool = False     # image : inverser fond/forme


def _vectorize_raster(svg_text, invert=False):
    """Extrait le PNG embarqué d'un SVG-image, le seuille et le vectorise en polygones.
    Retourne [{'ext':[(x,y)...], 'holes':[[...],...]}, ...] ou None."""
    import re, base64, io
    import numpy as np
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    import cv2
    m = re.search(r'data:image/\w+;base64,([^"\')]+)', svg_text)
    if not m:
        return None
    b64 = re.sub(r'&#\d+;|&#x[0-9a-fA-F]+;|\s', '', m.group(1))
    img = Image.open(io.BytesIO(base64.b64decode(b64 + '=' * ((-len(b64)) % 4))))
    img.load()
    arr = np.array(img.convert("RGBA"))
    alpha = arr[:, :, 3]
    if alpha.min() < 250:
        mask = (alpha > 10).astype("uint8") * 255
    else:
        g = np.array(img.convert("L"))
        _, mask = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if invert:
        mask = 255 - mask
    H, W = mask.shape
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    hier = hier[0]
    total = H * W
    groups = {}
    for i, c in enumerate(cnts):
        if cv2.contourArea(c) < total * 0.003:
            continue
        pts = [(float(x), float(H - y)) for x, y in
               cv2.approxPolyDP(c, 1.5, True).reshape(-1, 2)]
        if len(pts) < 3:
            continue
        parent = hier[i][3]
        if parent == -1:
            groups.setdefault(i, {"ext": None, "holes": []})["ext"] = pts
        else:
            groups.setdefault(parent, {"ext": None, "holes": []})["holes"].append(pts)
    return [g for g in groups.values() if g["ext"]]


def _raster_part_code(polys, height, thickness):
    return ("from build123d import *\n"
            "from shapely.geometry import Polygon as ShPoly, MultiPolygon\n"
            "from shapely.affinity import scale as _sc, translate as _tr\n"
            f"hauteur = {height}  # taille cible (mm)\n"
            f"epaisseur = {thickness}  # epaisseur (mm)\n"
            f"_polys = {polys!r}\n"
            "_mp = MultiPolygon([ShPoly(p['ext'], p['holes']) for p in _polys]).buffer(0)\n"
            "_b = _mp.bounds\n"
            "_mp = _sc(_mp, xfact=hauteur/max(_b[2]-_b[0], _b[3]-_b[1]), yfact=hauteur/max(_b[2]-_b[0], _b[3]-_b[1]), origin=(0,0))\n"
            "_b = _mp.bounds\n"
            "_mp = _tr(_mp, -(_b[0]+_b[2])/2, -(_b[1]+_b[3])/2)\n"
            "def _sk(shp):\n"
            "    geoms = list(shp.geoms) if shp.geom_type=='MultiPolygon' else [shp]\n"
            "    s=None\n"
            "    for p in geoms:\n"
            "        if p.is_empty: continue\n"
            "        f = Polygon(*[(x,y) for x,y in list(p.exterior.coords)[:-1]], align=None)\n"
            "        for r in p.interiors:\n"
            "            f = f - Polygon(*[(x,y) for x,y in list(r.coords)[:-1]], align=None)\n"
            "        s = f if s is None else s+f\n"
            "    return s\n"
            "with BuildPart() as _pp:\n"
            "    with BuildSketch():\n"
            "        add(_sk(_mp))\n"
            "    extrude(amount=epaisseur)\n"
            "part = _pp.part\n")


def _parse_perforated_svg(text):
    """Détecte une plaque perforée (beaucoup d'arcs circulaires, ex. trame Inkscape).
    Retourne (W, H, holes=[[cx,cy,r],...]) ou None. Format : `M cx-r cy A r r ...`."""
    circ = re.findall(r'M\s+(-?[\d.]+)\s+(-?[\d.]+)\s+A\s+([\d.]+)', text)
    if len(circ) < 30:                       # trop peu de cercles = pas une trame
        return None
    holes = [[float(mx) + float(rr), float(my), float(rr)] for mx, my, rr in circ]
    vb = re.search(r'viewBox="([-\d.eE\s]+)"', text)
    if vb:
        p = vb.group(1).split()
        W, H = float(p[2]), float(p[3])
    else:
        W = max(h[0] + h[2] for h in holes) + 2
        H = max(h[1] + h[2] for h in holes) + 2
    return W, H, holes


@app.post("/svg_part")
def svg_part(r: SvgPartReq):
    """Crée une pièce en extrudant une silhouette SVG (animaux, logos, formes libres).
    Cas spécial : SVG perforé (trame) -> plaque via booléen maillage (B-rep trop lent)."""
    MESH["active"] = False
    if not r.content.strip():
        return {"ok": False, "log": "SVG vide."}

    perf = _parse_perforated_svg(r.content)
    if perf:
        W, H, holes = perf
        _clear_outputs()
        for f in ("generated_model.py", "faces.json"):
            (WORK / f).unlink(missing_ok=True)
        resp = WORKER.run_raw({"cmd": "svg_perf", "outdir": str(WORK), "W": W,
                               "H": H, "thickness": r.thickness, "holes": holes},
                              timeout=180)
        if resp.get("ok"):
            MESH["active"] = True
            MESH["stats"] = resp.get("stats", {})
            return {"ok": True, "mesh": True, "stats": resp["stats"],
                    "files": {"glb": "/work/model.glb", "stl": "/work/model.stl"}}
        return {"ok": False, "log": resp.get("error", "") or "échec plaque perforée"}

    import uuid
    has_vector = any(t in r.content for t in
                     ("<path", "<polygon", "<polyline", "<rect", "<circle", "<ellipse"))
    if not has_vector and "<image" in r.content:
        polys = _vectorize_raster(r.content, r.invert)
        if not polys:
            return {"ok": False, "log": "Image : aucune forme nette détectée. "
                    "Coche « inverser », ou fournis une silhouette contrastée "
                    "(forme pleine sur fond uni)."}
        code = _raster_part_code(polys, r.height, r.thickness)
    else:
        svgp = WORK / f"_svgpart_{uuid.uuid4().hex[:8]}.svg"
        svgp.write_text(r.content, encoding="utf-8")
        p = str(svgp).replace("\\", "/")
        code = ("from build123d import *\n"
                f"hauteur = {r.height}  # taille cible (mm)\n"
                f"epaisseur = {r.thickness}  # epaisseur d'extrusion (mm)\n"
                f'_p = import_svg(r"{p}")\n'
                "_sk = Sketch() + list(_p)\n"
                "_bb = _sk.bounding_box()\n"
                "_sk = _sk.scale(hauteur / max(_bb.size.X, _bb.size.Y))\n"
                "_bb = _sk.bounding_box()\n"
                "_sk = _sk.translate((-_bb.center().X, -_bb.center().Y, -_bb.center().Z))\n"
                "with BuildPart() as _pp:\n"
                "    with BuildSketch():\n"
                "        add(_sk)\n"
                "    extrude(amount=epaisseur)\n"
                "part = _pp.part\n")
    _clear_outputs()
    (WORK / "generated_model.py").write_text(code, encoding="utf-8")
    ok, err, stats = WORKER.run(WORK / "generated_model.py", WORK, timeout=90)
    if ok and stats:
        STATE.update(brief="(SVG extrude)", stats=stats)
        return {"ok": True, "code": code, "stats": stats,
                "files": _files_ok(), "params": _params_from_code(code)}
    return {"ok": False, "log": err or "echec : SVG invalide ou tracé non fermé ?"}


@app.post("/reset")
def reset():
    MESH["active"] = False
    MESH["stats"] = {}
    STATE["brief"] = None
    STATE["stats"] = {}
    for f in ("model.stl", "model.step", "model.glb", "model.3mf",
              "plate_1.gcode", "faces.json", "generated_model.py",
              "_mesh.stl", "_upload.stl", "_trial.py"):
        (WORK / f).unlink(missing_ok=True)
    return {"ok": True}


def _extrude_for(mode, depth):
    if mode == "relief":
        return f"extrude(amount={depth})"
    if mode == "gravure":
        return f"extrude(amount=-{depth}, mode=Mode.SUBTRACT)"
    return "extrude(amount=-1000, mode=Mode.SUBTRACT)"   # through


def _paste_op_code(source, content, size, mode, depth, c, svg_path, solid=False):
    cx, cy, cz = c
    ex = _extrude_for(mode, depth)
    if source == "text":
        if solid:   # remplir les contrepoinçons (o -> disque)
            prep = (f"_txt = Text({content!r}, font_size={size}, align=(Align.CENTER, Align.CENTER))\n"
                    "_txt = Sketch() + [make_face(_f.outer_wire()) for _f in _txt.faces()]\n")
            profile = ("    with BuildSketch(Plane(_sel)):\n"
                       "        add(_txt)\n")
        else:
            prep = ""
            profile = ("    with BuildSketch(Plane(_sel)):\n"
                       f"        Text({content!r}, font_size={size}, "
                       "align=(Align.CENTER, Align.CENTER))\n")
    else:
        p = str(svg_path).replace("\\", "/")
        prep = (f'_prof = import_svg(r"{p}")\n'
                "_sk = Sketch() + list(_prof)\n"
                "_bb = _sk.bounding_box()\n"
                f"_sk = _sk.scale({size} / max(_bb.size.X, _bb.size.Y))\n"
                "_bb = _sk.bounding_box()\n"
                "_sk = _sk.translate((-_bb.center().X, -_bb.center().Y, -_bb.center().Z))\n")
        profile = ("    with BuildSketch(Plane(_sel)):\n"
                   "        add(_sk)\n")
    return ("\n\n# --- collage 2D sur une face ---\n"
            f"{prep}"
            f"_t = Vector({cx}, {cy}, {cz})\n"
            "_sel = min(part.faces(), key=lambda _f: (_f.center() - _t).length)\n"
            "with BuildPart() as _op:\n"
            "    add(part)\n"
            f"{profile}"
            f"    {ex}\n"
            "part = _op.part\n")


@app.post("/paste_op")
def paste_op(r: PasteOpReq):
    """Colle un profil 2D (texte ou SVG) sur la face : relief / gravure / à travers."""
    code = _current_code()
    if not code:
        return {"ok": False, "error": "Aucune piece."}
    c = _face_centroid(r.face_index)
    if c is None:
        return {"ok": False, "error": "Face inconnue — régénère la pièce."}
    if not r.content.strip():
        return {"ok": False, "error": "Contenu vide."}
    svg_path = None
    if r.source == "svg":
        import uuid
        svg_path = WORK / f"_paste_{uuid.uuid4().hex[:8]}.svg"
        svg_path.write_text(r.content, encoding="utf-8")
    new_code = code + _paste_op_code(r.source, r.content, r.size, r.mode, r.depth, c, svg_path, r.solid)
    trial = WORK / "_trial.py"
    trial.write_text(new_code, encoding="utf-8")
    ok, err, stats = WORKER.run(trial, WORK, timeout=90)
    if ok and stats:
        (WORK / "generated_model.py").write_text(new_code, encoding="utf-8")
        STATE.update(stats=stats)
        return {"ok": True, "code": new_code, "stats": stats,
                "files": _files_ok(), "params": _params_from_code(new_code)}
    return {"ok": False, "error": err}


def _face_centroid(idx):
    fp = WORK / "faces.json"
    if not fp.exists():
        return None
    for f in json.loads(fp.read_text(encoding="utf-8")).get("faces", []):
        if f["i"] == idx:
            return f["c"]
    return None


def _op_code(op, shape, size, depth, c):
    r = size / 2.0
    prof = {
        "hexagone": f"RegularPolygon(radius={r}, side_count=6)",
        "cercle": f"Circle(radius={r})",
        "rectangle": f"Rectangle({size}, {size})",
    }.get(shape, f"Circle(radius={r})")
    cx, cy, cz = c
    head = ("\n\n# --- operation via clic sur une face ---\n"
            f"_t = Vector({cx}, {cy}, {cz})\n"
            "_sel = min(part.faces(), key=lambda _f: (_f.center() - _t).length)\n")
    if op == "conge":
        return head + ("try:\n"
                       f"    part = fillet(_sel.edges(), radius={depth})\n"
                       "except Exception:\n    pass\n")
    verb = (f"extrude(amount={depth})" if op == "extrude"
            else f"extrude(amount=-{depth}, mode=Mode.SUBTRACT)")
    return head + ("with BuildPart() as _op:\n"
                   "    add(part)\n"
                   "    with BuildSketch(Plane(_sel)):\n"
                   f"        {prof}\n"
                   f"    {verb}\n"
                   "part = _op.part\n")


@app.post("/face_op")
def face_op(r: FaceOpReq):
    """Applique une operation deterministe sur la face cliquee (sans LLM)."""
    code = _current_code()
    if not code:
        return {"ok": False, "error": "Aucune piece."}
    c = _face_centroid(r.face_index)
    if c is None:
        return {"ok": False, "error": "Face inconnue — régénère la pièce."}
    new_code = code + _op_code(r.op, r.shape, r.size, r.depth, c)
    trial = WORK / "_trial.py"
    trial.write_text(new_code, encoding="utf-8")
    ok, err, stats = WORKER.run(trial, WORK, timeout=60)
    if ok and stats:
        (WORK / "generated_model.py").write_text(new_code, encoding="utf-8")
        STATE.update(stats=stats)
        return {"ok": True, "code": new_code, "stats": stats,
                "files": _files_ok(), "params": _params_from_code(new_code)}
    return {"ok": False, "error": err}  # modele courant intact


def _edge_op_code(targets, op, radius):
    verb = (f"fillet(_edges, radius={radius})" if op == "fillet"
            else f"chamfer(_edges, length={radius})")
    tlist = ", ".join(f"Vector({c[0]}, {c[1]}, {c[2]})" for c in targets)
    return ("\n\n# --- operation arete (intersection de faces) ---\n"
            f"_targets = [{tlist}]\n"
            "with BuildPart() as _op:\n"
            "    add(part)\n"
            "    _sf = [min(_op.faces(), key=lambda _f: (_f.center() - _t).length) for _t in _targets]\n"
            "    if len(_sf) == 1:\n"
            "        _edges = list(_sf[0].edges())\n"
            "    else:\n"
            "        _edges = []\n"
            "        for _a in range(len(_sf)):\n"
            "            for _b in range(_a + 1, len(_sf)):\n"
            "                for _e1 in _sf[_a].edges():\n"
            "                    if any((_e1.center() - _e2.center()).length < 1e-4 for _e2 in _sf[_b].edges()):\n"
            "                        _edges.append(_e1)\n"
            "    _uniq = []\n"
            "    for _e in _edges:\n"
            "        if not any((_e.center() - _u.center()).length < 1e-4 for _u in _uniq):\n"
            "            _uniq.append(_e)\n"
            "    _edges = _uniq\n"
            f"    {verb}\n"
            "part = _op.part\n")


def _direct_edge_code(mids, op, radius):
    """Arêtes cliquées directement : sélection par proximité du centre d'arête.
    OCCT échoue si le rayon est trop grand pour l'arête -> repli automatique r/2, r/4."""
    verb = ("fillet(_edges, radius=_try)" if op == "fillet"
            else "chamfer(_edges, length=_try)")
    tlist = ", ".join(f"Vector({m[0]}, {m[1]}, {m[2]})" for m in mids)
    return ("\n\n# --- operation arete (selection directe) ---\n"
            f"_targets = [{tlist}]\n"
            "with BuildPart() as _op:\n"
            "    add(part)\n"
            "    _edges = [min(_op.edges(), key=lambda _e: (_e.center() - _t).length)\n"
            "              for _t in _targets]\n"
            "    _uniq = []\n"
            "    for _e in _edges:\n"
            "        if not any((_e.center() - _u.center()).length < 1e-4 for _u in _uniq):\n"
            "            _uniq.append(_e)\n"
            "    _edges = _uniq\n"
            "    _done = False\n"
            f"    for _try in ({radius}, {radius} * 0.5, {radius} * 0.25):\n"
            "        try:\n"
            f"            {verb}\n"
            "            _done = True\n"
            "            break\n"
            "        except Exception:\n"
            "            pass\n"
            "    if not _done:\n"
            "        # Tout-ou-rien refuse -> arete par arete : on traite tout ce qui peut\n"
            "        # l'etre (re-selection par centre a chaque fois, la topologie change).\n"
            "        _mids0 = [_e.center() for _e in _edges]\n"
            "        _ok_n = 0\n"
            "        for _m in _mids0:\n"
            "            _did = False\n"
            f"            for _try in ({radius}, {radius} * 0.5, {radius} * 0.25):\n"
            "                try:\n"
            "                    _edges = [min(_op.edges(), key=lambda _e: (_e.center() - _m).length)]\n"
            f"                    {verb}\n"
            "                    _did = True\n"
            "                    break\n"
            "                except Exception:\n"
            "                    pass\n"
            "            if _did:\n"
            "                _ok_n += 1\n"
            "        if _ok_n == 0:\n"
            "            raise RuntimeError('aucune des aretes selectionnees n\\'accepte "
            "cette operation, meme avec un rayon reduit — valeur plus petite ou autres aretes')\n"
            "part = _op.part\n")


@app.post("/edge_op")
def edge_op(r: EdgeOpReq):
    """Arrondi/chanfrein : arêtes cliquées directement (mids), ou via faces (sans LLM)."""
    code = _current_code()
    if not code:
        return {"ok": False, "error": "Aucune piece."}
    if r.mids:
        new_code = code + _direct_edge_code(r.mids, r.op, r.radius)
    else:
        targets = []
        for idx in r.face_indices:
            c = _face_centroid(idx)
            if c is None:
                return {"ok": False, "error": f"Face {idx} inconnue — régénère."}
            targets.append(c)
        if not targets:
            return {"ok": False, "error": "Aucune sélection."}
        new_code = code + _edge_op_code(targets, r.op, r.radius)
    trial = WORK / "_trial.py"
    trial.write_text(new_code, encoding="utf-8")
    ok, err, stats = WORKER.run(trial, WORK, timeout=60)
    if ok and stats:
        (WORK / "generated_model.py").write_text(new_code, encoding="utf-8")
        STATE.update(stats=stats)
        return {"ok": True, "code": new_code, "stats": stats,
                "files": _files_ok(), "params": _params_from_code(new_code)}
    return {"ok": False, "error": err}


@app.post("/import_mesh")
def import_mesh(file: UploadFile = File(...)):
    data = file.file.read()
    (WORK / "_upload.stl").write_bytes(data)
    for f in ("model.step", "model.3mf", "plate_1.gcode", "faces.json",
              "generated_model.py"):
        (WORK / f).unlink(missing_ok=True)
    resp = WORKER.run_raw({"cmd": "import_mesh",
                           "stl_path": str(WORK / "_upload.stl"),
                           "outdir": str(WORK)}, timeout=180)
    if resp.get("ok"):
        MESH["active"] = True
        MESH["stats"] = resp.get("stats", {})
        return {"ok": True, "mesh": True, "stats": resp["stats"],
                "files": {"glb": "/work/model.glb", "stl": "/work/model.stl"}}
    return {"ok": False, "error": resp.get("error", "")}


@app.post("/mesh_stamp")
def mesh_stamp(r: MeshStampReq):
    if not (WORK / "_mesh.stl").exists():
        return {"ok": False, "error": "Aucun maillage importé."}
    job = {"cmd": "mesh_stamp", "outdir": str(WORK), "point": r.point,
           "normal": r.normal, "source": r.source, "content": r.content,
           "size": r.size, "mode": r.mode, "depth": r.depth, "solid": r.solid}
    if r.source == "svg":
        import uuid
        p = WORK / f"_pastemesh_{uuid.uuid4().hex[:8]}.svg"
        p.write_text(r.content, encoding="utf-8")
        job["svg_path"] = str(p).replace("\\", "/")
    resp = WORKER.run_raw(job, timeout=120)
    if resp.get("ok"):
        MESH["stats"] = resp.get("stats", {})
        return {"ok": True, "mesh": True, "stats": resp["stats"],
                "files": {"glb": "/work/model.glb", "stl": "/work/model.stl"}}
    return {"ok": False, "error": resp.get("error", "")}


# --- VOIE INVENTIVE : contradiction -> principes (matrice) -> variantes mesurées ---
import invent as _invent

VAR_DIR = WORK / "variants"


class InventPrinciplesReq(BaseModel):
    improve: int
    degrade: int


class InventVariantReq(BaseModel):
    principle: int
    contradiction: str = ""


class InventAdoptReq(BaseModel):
    principle: int | str      # numero de principe, ou "lattice"


def _fea_quick(outdir):
    """FEA canonique rapide sur une piece (SF + masse), tolerante a l'echec."""
    step = outdir / "model.step"
    if not step.exists():
        return None, None
    stl = outdir / "model.stl"
    r = WORKER.run_raw({"cmd": "fea", "step_path": str(step), "force_N": 20.0,
                        "material": "PLA", "direction": [0, 0, -1],
                        "stl_path": str(stl) if stl.exists() else None}, timeout=180)
    if not r.get("ok"):
        return None, None
    return r.get("safety_factor"), r


@app.get("/invent/params")
def invent_params():
    return {"parameters": _invent.PARAMETERS}


@app.post("/invent/principles")
def invent_principles(req: InventPrinciplesReq):
    return {"principles": _invent.principles_for(req.improve, req.degrade)}


@app.post("/invent/baseline")
def invent_baseline():
    """Mesure la piece courante (reference de comparaison)."""
    if not (WORK / "model.step").exists():
        return {"ok": False, "error": "Aucune piece de depart : genere d'abord une piece."}
    sf, _ = _fea_quick(WORK)
    vol = (STATE.get("stats") or {}).get("volume_cm3")
    masse = round(vol * 1.24, 1) if vol else None
    return {"ok": True, "sf": sf, "masse_g": masse,
            "ideality": _invent.ideality(sf, masse), "volume_cm3": vol}


@app.post("/invent/variant")
def invent_variant(req: InventVariantReq):
    """Genere UNE variante : principe -> operateur geometrique -> portes de
    validite -> FEA -> idealite. Ecrit dans work/variants/p{N}/ (l'atelier
    courant n'est PAS touche)."""
    base = _current_code()
    if not base:
        return {"ok": False, "error": "Aucune piece de depart."}
    instruction = _invent.operator_instruction(req.principle, req.contradiction)
    outdir = VAR_DIR / f"p{req.principle}"
    outdir.mkdir(parents=True, exist_ok=True)
    label = _invent.PRINCIPLES.get(req.principle, {}).get("label", str(req.principle))
    last_err = ""
    for attempt in range(2):                      # 1 essai + 1 correction
        try:
            code = (llm.refine_code(base, instruction) if attempt == 0
                    else llm.fix_code(instruction, code, last_err))
        except Exception as e:
            return {"ok": False, "error": f"LLM: {e}", "principle": req.principle}
        trial = outdir / "variant.py"
        trial.write_text(code, encoding="utf-8")
        ok, err, stats = WORKER.run(trial, outdir, timeout=90)
        if ok and stats:
            sf, _ = _fea_quick(outdir)
            masse = round(stats.get("volume_cm3", 0) * 1.24, 1)
            return {"ok": True, "principle": req.principle, "label": label,
                    "stats": stats, "sf": sf, "masse_g": masse,
                    "ideality": _invent.ideality(sf, masse),
                    "glb": f"/work/variants/p{req.principle}/model.glb"}
        last_err = err
    return {"ok": False, "principle": req.principle, "label": label,
            "error": (last_err or "generation echouee")[:300]}


class LatticeReq(BaseModel):
    cell_mm: float = 8.0      # taille de cellule (densite du maillage)
    wall_mm: float = 1.6      # epaisseur des parois du gyroide (~diametre de brin)
    shell_mm: float = 1.6     # peau exterieure conservee
    baseline_sf: float | None = None


@app.post("/invent/lattice")
def invent_lattice(req: LatticeReq):
    """Variante LATTICE (principes 31 Porosite / 40 Composites) : ame gyroide.
    SF estime par homogeneisation de Gibson-Ashby : SF ~ SF_plein x densite^2."""
    src = WORK / "model.stl"
    if not src.exists():
        return {"ok": False, "error": "Aucune piece de depart."}
    outdir = VAR_DIR / "lattice"
    r = WORKER.run_raw({"cmd": "lattice", "src_stl": str(src), "outdir": str(outdir),
                        "cell_mm": req.cell_mm, "wall_mm": req.wall_mm,
                        "shell_mm": req.shell_mm}, timeout=300)
    if not r.get("ok"):
        return {"ok": False, "error": str(r.get("error", "lattice echoue"))[:200]}
    st = r["stats"]
    rel = r.get("rel_density")
    masse = round(st.get("volume_cm3", 0) * 1.24, 1)
    sf_est = round(req.baseline_sf * rel * rel, 1) if (req.baseline_sf and rel) else None
    return {"ok": True, "principle": "lattice", "label": "Lattice gyroïde (P31/P40)",
            "stats": st, "rel_density": rel, "masse_g": masse,
            "sf": sf_est, "sf_estime": True,
            "ideality": _invent.ideality(sf_est, masse),
            "glb": "/work/variants/lattice/model.glb"}


@app.post("/invent/adopt")
def invent_adopt(req: InventAdoptReq):
    """Adopte une variante : elle devient la piece courante de l'atelier."""
    if str(req.principle) == "lattice" or req.principle == -1:
        # variante MAILLAGE : bascule l'atelier en mode mesh
        outdir = VAR_DIR / "lattice"
        if not (outdir / "model.glb").exists():
            return {"ok": False, "error": "Variante lattice introuvable."}
        _clear_outputs()
        for f in ("model.glb", "model.stl", "_mesh.stl"):
            if (outdir / f).exists():
                shutil.copy2(outdir / f, WORK / f)
        for f in ("generated_model.py", "model.step", "faces.json", "edges.json"):
            (WORK / f).unlink(missing_ok=True)
        import trimesh as _tm
        m = _tm.load(str(WORK / "model.stl"), force="mesh")
        stats = {"triangles": int(len(m.faces)), "watertight": bool(m.is_watertight),
                 "volume_cm3": round(float(m.volume) / 1000.0, 1),
                 "bbox_mm": [round(float(x), 1) for x in m.extents]}
        MESH["active"] = True
        MESH["stats"] = stats
        return {"ok": True, "mesh": True, "stats": stats, "files": _files_ok(),
                "params": None, "code": None}
    outdir = VAR_DIR / f"p{req.principle}"
    vf = outdir / "variant.py"
    if not vf.exists():
        return {"ok": False, "error": "Variante introuvable."}
    code = vf.read_text(encoding="utf-8")
    _clear_outputs()
    (WORK / "generated_model.py").write_text(code, encoding="utf-8")
    ok, err, stats = WORKER.run(WORK / "generated_model.py", WORK, timeout=90)
    if not ok:
        return {"ok": False, "error": err}
    MESH["active"] = False
    STATE.update(stats=stats)
    return {"ok": True, "code": code, "stats": stats,
            "files": _files_ok(), "params": _params_from_code(code)}


@app.get("/state")
def state():
    return {"code": _current_code(), "brief": STATE.get("brief"),
            "stats": (MESH.get("stats") if MESH.get("active") else STATE.get("stats", {})),
            "params": _params_from_code(_current_code()),
            "mesh": MESH.get("active", False),
            "has_model": (WORK / "model.glb").exists()}


# --- Études : sauver / lister / ouvrir / supprimer (par utilisateur) --------
import shutil
ETUDES_DIR = Path(os.environ.get("TCAD_ETUDES", "/data/etudes"))


class EtudeSaveReq(BaseModel):
    name: str
    id: int | None = None            # si fourni : met a jour cette etude


def _cur_user(request):
    return auth.current_user(request.cookies.get(auth.COOKIE_NAME, ""))


def _etude_snapshot(eid):
    """Copie les sorties courantes dans le dossier persistant de l'etude
    (permet de rouvrir un maillage, ou de retomber sur les fichiers si la
    regeneration d'une etude parametrique echouait)."""
    d = ETUDES_DIR / str(eid)
    d.mkdir(parents=True, exist_ok=True)
    for f in ("model.glb", "model.stl", "model.step", "_mesh.stl",
              "generated_model.py", "faces.json"):
        src = WORK / f
        if src.exists():
            shutil.copy2(src, d / f)


@app.get("/etudes")
def etudes_list(request: Request):
    u = _cur_user(request)
    if not u:
        return JSONResponse({"error": "AUTH_REQUIRED"}, 401)
    return {"etudes": auth.list_etudes(u["id"])}


@app.post("/etudes")
def etudes_save(req: EtudeSaveReq, request: Request):
    u = _cur_user(request)
    if not u:
        return JSONResponse({"error": "AUTH_REQUIRED"}, 401)
    if not (WORK / "model.glb").exists():
        return JSONResponse({"error": "Aucune piece a enregistrer."}, 400)
    code = _current_code()
    brief = STATE.get("brief")
    params = _params_from_code(code) if code else None
    mesh = MESH.get("active", False)
    stats = MESH.get("stats") if mesh else STATE.get("stats", {})
    if req.id:
        if not auth.get_etude(req.id, u["id"]):
            return JSONResponse({"error": "introuvable"}, 404)
        auth.update_etude(req.id, u["id"], name=req.name, brief=brief, code=code,
                          params=params, mesh=mesh, stats=stats)
        eid = req.id
    else:
        eid = auth.create_etude(u["id"], req.name, brief, code, params, mesh, stats)
    _etude_snapshot(eid)
    return {"ok": True, "id": eid, "etudes": auth.list_etudes(u["id"])}


@app.post("/etudes/{eid}/open")
def etudes_open(eid: int, request: Request):
    u = _cur_user(request)
    if not u:
        return JSONResponse({"error": "AUTH_REQUIRED"}, 401)
    e = auth.get_etude(eid, u["id"])
    if not e:
        return JSONResponse({"error": "introuvable"}, 404)
    d = ETUDES_DIR / str(eid)
    _clear_outputs()
    if e.get("code"):
        # Etude parametrique : on regenere depuis le code (cotes reglables).
        (WORK / "generated_model.py").write_text(e["code"], encoding="utf-8")
        ok, err, stats = WORKER.run(WORK / "generated_model.py", WORK, timeout=90)
        if not ok:                       # repli : fichiers sauvegardes
            for f in ("model.glb", "model.stl", "model.step", "faces.json"):
                if (d / f).exists():
                    shutil.copy2(d / f, WORK / f)
            stats = e.get("stats") or {}
        MESH["active"] = False
        MESH["stats"] = {}
        STATE["brief"] = e.get("brief")
        STATE["stats"] = stats
    else:
        # Etude maillage : on restaure les fichiers sauvegardes.
        for f in ("model.glb", "model.stl", "model.step", "_mesh.stl", "faces.json"):
            if (d / f).exists():
                shutil.copy2(d / f, WORK / f)
        MESH["active"] = bool(e.get("mesh"))
        MESH["stats"] = e.get("stats") or {}
        STATE["brief"] = e.get("brief")
        STATE["stats"] = {}
    code = _current_code()
    return {"ok": True, "code": code, "brief": STATE.get("brief"),
            "stats": (MESH.get("stats") if MESH.get("active") else STATE.get("stats", {})),
            "params": _params_from_code(code),
            "mesh": MESH.get("active", False),
            "has_model": (WORK / "model.glb").exists(),
            "files": _files_ok()}


@app.delete("/etudes/{eid}")
def etudes_delete(eid: int, request: Request):
    u = _cur_user(request)
    if not u:
        return JSONResponse({"error": "AUTH_REQUIRED"}, 401)
    auth.delete_etude(eid, u["id"])
    shutil.rmtree(ETUDES_DIR / str(eid), ignore_errors=True)
    return {"ok": True, "etudes": auth.list_etudes(u["id"])}


def _parse_gcode_stats(gpath: Path) -> dict:
    s = {}
    try:
        txt = gpath.read_text(errors="ignore")
    except Exception:
        return s
    def grab(pat):
        m = re.search(pat, txt)
        return m.group(1).strip() if m else None
    s["print_time"] = grab(r"total estimated time:\s*([^\n;]+)")
    s["model_time"] = grab(r"model printing time:\s*([^\n;]+)")
    s["layers"] = grab(r"total layer number:\s*(\d+)")
    s["filament_mm"] = grab(r"filament used \[mm\]\s*=\s*([\d.]+)")
    s["filament_cm3"] = grab(r"filament used \[cm3\]\s*=\s*([\d.]+)")
    return s


@app.post("/slice")
def slice_model():
    stl = WORK / "model.stl"
    if not stl.exists():
        return {"ok": False, "log": "Aucun model.stl : genere d'abord une piece."}
    try:
        p = subprocess.run(
            [str(ORCA), "--slice", "0", "--arrange", "1",
             "--load-settings", f"{PROC};{MACH}",
             "--load-filaments", str(FILA),
             "--export-3mf", "model.3mf", "--outputdir", str(WORK), str(stl)],
            capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return {"ok": False, "log": "Timeout slicing (180 s)."}
    ok = p.returncode == 0 and (WORK / "model.3mf").exists()
    stats = _parse_gcode_stats(WORK / "plate_1.gcode") if ok else {}
    return {"ok": ok, "log": (p.stdout or "") + (p.stderr or ""),
            "stats": stats, "file": "/work/model.3mf" if ok else None}


@app.post("/send")
def send(r: SendReq):
    tmf = WORK / "model.3mf"
    if not tmf.exists():
        return {"ok": False, "log": "Aucun model.3mf : slice d'abord."}
    cmd = [str(VENV_PY), str(SEND), "--ip", r.ip, "--code", r.code,
           "--serial", r.serial, "--file", str(tmf), "--name", "ttc_model.3mf"]
    if r.start:
        cmd.append("--start")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return {"ok": False, "log": "Timeout envoi (90 s) : imprimante injoignable ?"}
    return {"ok": p.returncode == 0, "log": (p.stdout or "") + (p.stderr or ""),
            "started": r.start and p.returncode == 0}


app.mount("/work", StaticFiles(directory=str(WORK)), name="work")
app.mount("/static", StaticFiles(directory=str(APP / "static")), name="static")


@app.get("/")
def index():
    # no-store : les navigateurs gardaient l'ancien JS en cache malgre les deploiements
    return FileResponse(str(APP / "static" / "index.html"),
                        headers={"Cache-Control": "no-store, must-revalidate"})
