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

# --- Protection par mot de passe (active uniquement si APP_PASSWORD est defini) ---
import base64, secrets
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.middleware("http")
async def _auth(request, call_next):
    if APP_PASSWORD and request.url.path != "/healthz":
        hdr = request.headers.get("authorization", "")
        ok = False
        if hdr.startswith("Basic "):
            try:
                _, _, pw = base64.b64decode(
                    hdr[6:]).decode("utf-8", "ignore").partition(":")
                ok = secrets.compare_digest(pw, APP_PASSWORD)
            except Exception:
                ok = False
        if not ok:
            return JSONResponse(
                {"detail": "authentification requise"}, status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="text-to-CAD"'})
    return await call_next(request)


class Brief(BaseModel):
    brief: str


class RefineReq(BaseModel):
    instruction: str
    faces: list = []   # faces sélectionnées : [{i, label, c:[x,y,z]}, ...]


class RebuildReq(BaseModel):
    overrides: dict


class FaceOpReq(BaseModel):
    face_index: int
    op: str      # "extrude" | "percer"
    shape: str = "hexagone"  # hexagone | cercle | rectangle
    size: float = 10.0       # taille du profil (mm)
    depth: float = 8.0       # hauteur d'extrusion / profondeur (mm)


class EdgeOpReq(BaseModel):
    face_indices: list     # 1 face = toutes ses arêtes ; 2+ = arêtes d'intersection
    op: str = "chamfer"    # "fillet" | "chamfer"
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


@app.post("/generate")
def generate(b: Brief):
    MESH["active"] = False
    _clear_outputs()
    return _best_of_n(lambda t: llm.generate_code(b.brief, temperature=t), b.brief)


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


@app.post("/edge_op")
def edge_op(r: EdgeOpReq):
    """Arrondi/chanfrein sur les arêtes des faces sélectionnées (sans LLM)."""
    code = _current_code()
    if not code:
        return {"ok": False, "error": "Aucune piece."}
    targets = []
    for idx in r.face_indices:
        c = _face_centroid(idx)
        if c is None:
            return {"ok": False, "error": f"Face {idx} inconnue — régénère."}
        targets.append(c)
    if not targets:
        return {"ok": False, "error": "Aucune face sélectionnée."}
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


@app.get("/state")
def state():
    return {"code": _current_code(), "brief": STATE.get("brief"),
            "stats": (MESH.get("stats") if MESH.get("active") else STATE.get("stats", {})),
            "params": _params_from_code(_current_code()),
            "mesh": MESH.get("active", False),
            "has_model": (WORK / "model.glb").exists()}


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


@app.get("/")
def index():
    return FileResponse(str(APP / "static" / "index.html"))
