"""Worker build123d persistant : importe le noyau CAO UNE fois, puis execute
chaque script recu (protocole JSON-lignes sur stdin/stdout).
Elimine le cout d'import (~20 s) paye a chaque generation autrement.

Protocole :
  <- (au demarrage) {"ready": true}
  -> {"code_file": "...", "outdir": "..."}
  <- {"ok": true, "stats": {...}} | {"ok": false, "error": "..."}
"""
import sys, json, traceback
from pathlib import Path


def hollow_tray(part, wall=2.0, height=40.0, base=2.0):
    """Transforme une pièce plate extrudée en vide-poche/coque robuste : fond + parois.
    Utilise shapely pour éroder le contour -> gère les zones fines (creux où possible,
    plein là où c'est trop fin) sans jamais planter."""
    from build123d import (Polygon, Plane, Axis, BuildPart, BuildSketch,
                           add, extrude, Mode)
    from shapely.geometry import Polygon as _ShPoly

    def _sk(shp):
        polys = list(shp.geoms) if shp.geom_type == "MultiPolygon" else [shp]
        s = None
        for p in polys:
            if p.is_empty:
                continue
            f = Polygon(*[(x, y) for x, y in list(p.exterior.coords)[:-1]], align=None)
            for ring in p.interiors:
                f = f - Polygon(*[(x, y) for x, y in list(ring.coords)[:-1]], align=None)
            s = f if s is None else s + f
        return s

    bf = part.faces().sort_by(Axis.Z)[0]      # face du bas = silhouette
    def pts(w, n=400):
        return [(v.X, v.Y) for v in (w @ (i / n) for i in range(n))]
    poly = _ShPoly(pts(bf.outer_wire()), [pts(w) for w in bf.inner_wires()])
    if not poly.is_valid:
        poly = poly.buffer(0)
    inner = poly.buffer(-wall)                # érosion robuste
    full = _sk(poly)
    with BuildPart() as vp:
        with BuildSketch(Plane.XY):
            add(full)
        extrude(amount=base)                  # fond
        with BuildSketch(Plane.XY.offset(base)):
            add(full)
            if not inner.is_empty:
                add(_sk(inner), mode=Mode.SUBTRACT)
        extrude(amount=height)                # parois
    return vp.part


def hook(width=8.0, arm=25.0, rise=28.0, thickness=8.0, fillet_r=None):
    """Crochet / patère en L ARRONDI (queue horizontale + relevé vertical), avec de
    GROS congés au coude et aux arêtes -> aspect courbe, ET géométrie PROPRE qui se
    maille toujours (un crochet balayé continu s'auto-intersecte et est ingérable en
    calcul de structure). Dos dans le plan X=0, queue vers +X, relevé vers +Z, base a
    Z=0, largeur `width` le long de Y. Le modele n'a qu'a POSITIONNER (Pos) puis unir.
    Retourne une Part."""
    from build123d import Box, Pos, Axis, Align, fillet
    tail = Pos(0, 0, 0) * Box(arm, width, thickness,
                              align=(Align.MIN, Align.CENTER, Align.MIN))
    lip = Pos(arm - thickness, 0, 0) * Box(thickness, width, rise + thickness,
                                           align=(Align.MIN, Align.CENTER, Align.MIN))
    part = tail + lip
    r = fillet_r or min(thickness * 0.45, rise * 0.4, arm * 0.4)
    for rr in (r, r * 0.5):                    # congé généreux -> aspect courbe ; repli si trop grand
        try:
            part = fillet(part.edges().filter_by(Axis.Y), rr)
            break
        except Exception:
            continue
    return part


def hook_curved(radius=16.0, thickness=6.0, opening_deg=80.0, width=12.0,
                tab_len=20.0):
    """Crochet COURBE en « virgule / J » : anneau ouvert (profil 2D) + queue droite
    de fixation, EXTRUDÉ en largeur -> prismatique, robuste, toujours maillable
    (contrairement à un balayage 3D de section ronde qui s'auto-intersecte).
    Profil dans le plan XZ, extrudé le long de Y (largeur `width`, centrée).
    L'ouverture de l'anneau regarde vers le HAUT-AVANT (+X/+Z) : on y suspend
    l'objet. La queue monte vers +Z depuis l'arrière (X=-radius) pour être unie
    à une plaque murale. Origine au centre de l'anneau. Retourne une Part."""
    import math
    from build123d import (BuildPart, BuildSketch, Plane, Circle, Polygon,
                           Mode, extrude, fillet, Axis)
    R = float(radius)
    r = max(R - float(thickness), 1.0)
    with BuildPart() as hp:
        with BuildSketch(Plane.XZ):
            Circle(R)
            Circle(r, mode=Mode.SUBTRACT)
            # ouverture en coin (vers le haut-avant) pour former la virgule
            a0 = math.radians(35.0)
            a1 = math.radians(35.0 + max(20.0, min(float(opening_deg), 160.0)))
            big = 3.0 * R
            Polygon((0, 0), (big * math.cos(a0), big * math.sin(a0)),
                    (big * math.cos(a1), big * math.sin(a1)), align=None,
                    mode=Mode.SUBTRACT)
            # queue de fixation : montant droit colle au dos de l'anneau
            Polygon((-R, 0), (-r, 0), (-r, R + float(tab_len)),
                    (-R, R + float(tab_len)), align=None)
        extrude(amount=float(width) / 2.0, both=True)
    part = hp.part
    try:
        part = fillet(part.edges().filter_by(Axis.Y), min(1.5, thickness * 0.2))
    except Exception:
        pass
    return part


def contour_edges(part, center):
    """Toutes les arêtes du CONTOUR (wire) contenant l'arête la plus proche de `center`.
    Permet « sélectionne une arête → saisis tout son contour » de façon déterministe :
    le LLM n'a pas à deviner la topologie. center = (x, y, z) en mm."""
    from build123d import Vector
    t = Vector(*center)
    e0 = min(part.edges(), key=lambda e: (e.center() - t).length)
    best = None
    for f in part.faces():
        wires = [f.outer_wire()] + list(f.inner_wires())
        for w in wires:
            try:
                if any((e.center() - e0.center()).length < 1e-6 for e in w.edges()):
                    if best is None or len(w.edges()) > len(best.edges()):
                        best = w
            except Exception:
                continue
    return list(best.edges()) if best is not None else [e0]


def _face_label(n):
    ax = max(range(3), key=lambda k: abs(n[k]))
    if abs(n[ax]) < 0.85:
        return "face inclinée / courbe"
    if ax == 2:
        return "dessus (+Z)" if n[2] >= 0 else "dessous (−Z)"
    names = "XY"
    return f"côté {'+' if n[ax] >= 0 else '−'}{names[ax]}"


def _export_faces(part, outdir):
    faces = []
    for i, f in enumerate(part.faces()):
        c = f.center()
        try:
            nn = f.normal_at(c)
        except Exception:
            try:
                nn = f.normal_at()
            except Exception:
                nn = None
        n = [round(nn.X, 4), round(nn.Y, 4), round(nn.Z, 4)] if nn is not None else [0, 0, 0]
        faces.append({
            "i": i,
            "c": [round(c.X, 3), round(c.Y, 3), round(c.Z, 3)],
            "n": n,
            "area": round(float(f.area), 2),
            "label": _face_label(n),
        })
    (outdir / "faces.json").write_text(
        json.dumps({"faces": faces, "unit": "mm"}), encoding="utf-8")


def _export_edges(part, outdir):
    """Arêtes cliquables : polylignes échantillonnées + centre, indexées.
    Le front les rend en surcouche three.js et les raycast au survol/clic."""
    edges = []
    for i, e in enumerate(part.edges()):
        if i >= 400:                      # garde-fou pièces pathologiques
            break
        try:
            gt = str(getattr(e, "geom_type", "")).upper()
            n = 1 if "LINE" in gt else 12
            pts = []
            for k in range(n + 1):
                p = e @ (k / n)
                pts.append([round(p.X, 3), round(p.Y, 3), round(p.Z, 3)])
            c = e.center()
            edges.append({"i": i,
                          "mid": [round(c.X, 3), round(c.Y, 3), round(c.Z, 3)],
                          "pts": pts})
        except Exception:
            continue
    (outdir / "edges.json").write_text(
        json.dumps({"edges": edges, "unit": "mm"}), encoding="utf-8")


def _mesh_stats(m):
    return {"triangles": int(len(m.faces)),
            "watertight": bool(m.is_watertight),
            "volume_cm3": round(float(m.volume) / 1000.0, 1),
            "bbox_mm": [round(float(x), 1) for x in m.extents]}


def _mesh_import(job):
    import trimesh
    outdir = Path(job["outdir"])
    m = trimesh.load(job["stl_path"], force="mesh")
    m.export(str(outdir / "_mesh.stl"))
    m.export(str(outdir / "model.stl"))
    m.export(str(outdir / "model.glb"))
    return {"ok": True, "mesh": True, "stats": _mesh_stats(m)}


def _mesh_stamp(job):
    import trimesh, numpy as np
    import build123d as bd
    outdir = Path(job["outdir"])
    m = trimesh.load(str(outdir / "_mesh.stl"), force="mesh")
    source, content, size = job["source"], job["content"], float(job["size"])
    mode, depth = job["mode"], float(job["depth"])
    solid = bool(job.get("solid", False))
    point = np.array(job["point"], dtype=float)
    normal = np.array(job["normal"], dtype=float)
    normal = normal / (np.linalg.norm(normal) or 1.0)

    with bd.BuildPart() as _s:
        with bd.BuildSketch():
            if source == "text":
                if solid:
                    _t = bd.Text(content, font_size=size,
                                 align=(bd.Align.CENTER, bd.Align.CENTER))
                    bd.add(bd.Sketch() + [bd.make_face(f.outer_wire()) for f in _t.faces()])
                else:
                    bd.Text(content, font_size=size,
                            align=(bd.Align.CENTER, bd.Align.CENTER))
            else:
                _p = bd.import_svg(job["svg_path"])
                _sk = bd.Sketch() + list(_p)
                _bb = _sk.bounding_box()
                _sk = _sk.scale(size / max(_bb.size.X, _bb.size.Y))
                _bb = _sk.bounding_box()
                _sk = _sk.translate((-_bb.center().X, -_bb.center().Y, -_bb.center().Z))
                bd.add(_sk)
        _h = 1000.0 if mode == "through" else (depth + 1.5)
        bd.extrude(amount=_h)

    verts, faces = _s.part.tessellate(0.2)
    prism = trimesh.Trimesh(
        np.array([(v.X, v.Y, v.Z) for v in verts]),
        np.array(faces))

    into = (mode != "relief")           # gravure / through = creuser
    d = -normal if into else normal
    M = trimesh.geometry.align_vectors([0, 0, 1], d)
    M[:3, 3] = point - d * 1.5          # recouvrement pour un booleen propre
    prism.apply_transform(M)

    if into:
        res = trimesh.boolean.difference([m, prism], engine="manifold")
    else:
        res = trimesh.boolean.union([m, prism], engine="manifold")
    res.export(str(outdir / "_mesh.stl"))
    res.export(str(outdir / "model.stl"))
    res.export(str(outdir / "model.glb"))
    return {"ok": True, "mesh": True, "stats": _mesh_stats(res)}


def _svg_perf(job):
    """Plaque perforée : boîte W×H×t moins les cylindres (trous) via booléen maillage.
    Rapide même pour des milliers de trous, là où le B-rep OpenCASCADE s'effondre."""
    import trimesh
    outdir = Path(job["outdir"])
    W, H, t = float(job["W"]), float(job["H"]), float(job["thickness"])
    holes = job["holes"]                         # [[cx, cy, r], ...]
    plate = trimesh.creation.box([W, H, t])
    plate.apply_translation([W / 2.0, H / 2.0, t / 2.0])
    cyls = [trimesh.creation.cylinder(
                radius=float(r), height=t * 2.0, sections=12,
                transform=trimesh.transformations.translation_matrix(
                    [float(cx), float(cy), t / 2.0]))
            for cx, cy, r in holes]
    tool = trimesh.util.concatenate(cyls)
    res = trimesh.boolean.difference([plate, tool], engine="manifold")
    res.export(str(outdir / "_mesh.stl"))
    res.export(str(outdir / "model.stl"))
    res.export(str(outdir / "model.glb"))
    return {"ok": True, "mesh": True, "stats": _mesh_stats(res)}


def _voxel_fill(m, pitch):
    """Voxelisation PLEINE rapide : rasterisation des triangles colonne par
    colonne (Z) puis remplissage par parité. ~100x plus rapide que
    trimesh.voxelized().fill() qui dominait le temps de calcul."""
    import numpy as np
    (x0, y0, z0), (x1, y1, z1) = m.bounds
    nx = int(np.ceil((x1 - x0) / pitch)) + 2
    ny = int(np.ceil((y1 - y0) / pitch)) + 2
    nz = int(np.ceil((z1 - z0) / pitch)) + 2
    cross = [[[] for _ in range(ny)] for _ in range(nx)]
    for a, b, c in m.triangles:
        i0 = max(int((min(a[0], b[0], c[0]) - x0) / pitch) - 1, 0)
        i1 = min(int((max(a[0], b[0], c[0]) - x0) / pitch) + 1, nx - 1)
        j0 = max(int((min(a[1], b[1], c[1]) - y0) / pitch) - 1, 0)
        j1 = min(int((max(a[1], b[1], c[1]) - y0) / pitch) + 1, ny - 1)
        if i1 < i0 or j1 < j0:
            continue
        den = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(den) < 1e-12:
            continue                       # triangle vertical : colonnes couvertes ailleurs
        px = x0 + np.arange(i0, i1 + 1) * pitch
        py = y0 + np.arange(j0, j1 + 1) * pitch
        PX, PY = np.meshgrid(px, py, indexing="ij")
        wx, wy = PX - a[0], PY - a[1]
        u = (wx * (c[1] - a[1]) - (c[0] - a[0]) * wy) / den
        v = ((b[0] - a[0]) * wy - wx * (b[1] - a[1])) / den
        inside = (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
        if not inside.any():
            continue
        z = a[2] + u * (b[2] - a[2]) + v * (c[2] - a[2])
        ii, jj = np.nonzero(inside)
        zz = z[inside]
        for k in range(len(ii)):
            cross[i0 + ii[k]][j0 + jj[k]].append(zz[k])
    M = np.zeros((nx, ny, nz), bool)
    zg = z0 + np.arange(nz) * pitch
    for i in range(nx):
        ci = cross[i]
        for j in range(ny):
            zs = ci[j]
            if len(zs) < 2:
                continue
            zs = sorted(zs)
            for k in range(0, len(zs) - 1, 2):
                M[i, j, (zg >= zs[k] - 1e-9) & (zg <= zs[k + 1] + 1e-9)] = True
    return M, np.array([x0, y0, z0])


def _lattice(job):
    """LATTIFIE la pièce : peau extérieure conservée + âme remplacée par un
    gyroïde TPMS (auto-supporté en FDM). Réglages : cell_mm = taille de cellule
    (densité du maillage), wall_mm = épaisseur des parois du gyroïde (~diamètre
    de brin), shell_mm = épaisseur de la peau. Pipeline voxels (B-rep ingérable
    pour des milliers de brins) : voxelisation -> érosion (peau) -> champ
    implicite gyroïde -> marching cubes."""
    import numpy as np
    import trimesh
    from scipy import ndimage
    from trimesh.voxel.ops import matrix_to_marching_cubes
    outdir = Path(job["outdir"])
    outdir.mkdir(parents=True, exist_ok=True)
    cell = max(3.0, float(job.get("cell_mm", 8.0)))
    wall = max(0.8, float(job.get("wall_mm", 1.6)))
    shell = max(0.8, float(job.get("shell_mm", 1.6)))
    m = trimesh.load(str(job["src_stl"]), force="mesh")
    ext = m.extents
    # résolution voxel : fine assez pour les parois, bornée pour la mémoire
    pitch = max(min(wall / 2.2, cell / 8.0), float(max(ext)) / 180.0)
    M, origin = _voxel_fill(m, pitch)
    it = max(1, int(round(shell / pitch)))
    inner = ndimage.binary_erosion(M, iterations=it)
    shell_mask = M & ~inner
    # Champ TPMS (période = cell) : gyroïde / Schwarz-P / diamant
    kind = str(job.get("kind", "gyroid"))
    k = 2.0 * np.pi / cell
    nx, ny, nz = M.shape
    ax = (np.arange(nx) * pitch + origin[0]) * k
    ay = (np.arange(ny) * pitch + origin[1]) * k
    az = (np.arange(nz) * pitch + origin[2]) * k
    sx, cx = np.sin(ax)[:, None, None], np.cos(ax)[:, None, None]
    sy, cy = np.sin(ay)[None, :, None], np.cos(ay)[None, :, None]
    sz, cz = np.sin(az)[None, None, :], np.cos(az)[None, None, :]
    if kind == "schwarz":
        G = (cx + cy + cz).astype(np.float32)
    elif kind == "diamond":
        G = (sx * sy * sz + sx * cy * cz + cx * sy * cz + cx * cy * sz).astype(np.float32)
    else:
        G = (sx * cy + sy * cz + sz * cx).astype(np.float32)
    # Épaisseur de paroi : uniforme, ou GRADIENT de densité (Qualité locale, P3) :
    # brins pleins du côté "dense" (bas par défaut), affinés de 55% à l'opposé.
    grad = job.get("gradient")                 # None | 'z' (dense en bas) | 'z-top'
    if grad in ("z", "z-top"):
        frac = np.linspace(0.0, 1.0, nz, dtype=np.float32)
        if grad == "z-top":
            frac = 1.0 - frac
        wall_z = wall * (1.0 - 0.55 * frac)    # wall -> 0.45*wall
        t = (np.pi * wall_z / cell)[None, None, :]
    else:
        t = np.pi * wall / cell
    # ÂME SEULEMENT, surfaces d'origine INTOUCHÉES : on ne reconstruit pas la
    # pièce en voxels (peau en escalier), on SOUSTRAIT le VIDE du coeur —
    # vide = (coeur érodé de la peau) ∖ (parois TPMS). Champ CONTINU (masque
    # lissé par gaussienne) -> marching cubes niveau 0 -> booléen manifold.
    # Les zones minces n'ont pas de coeur : elles restent pleines d'elles-mêmes.
    Sin = ndimage.gaussian_filter(inner.astype(np.float32), sigma=1.1)
    F_void = np.minimum(Sin - 0.5, (np.abs(G) - t) * 0.5)
    mesh = m                                   # repli : pièce inchangée
    if bool((F_void > 0).any()):
        from skimage import measure
        verts, faces_, _, _ = measure.marching_cubes(
            F_void, level=0.0, spacing=(pitch, pitch, pitch))
        void = trimesh.Trimesh(vertices=verts + np.asarray(origin), faces=faces_)
        try:
            void.update_faces(void.nondegenerate_faces())
            void.remove_unreferenced_vertices()
            void.process(validate=True)
            void.fix_normals()
            if void.volume < 0:        # marching cubes sort les normales inversées
                void.invert()
        except Exception:
            pass
        try:
            out = trimesh.boolean.difference([m, void], engine="manifold")
            if out is not None and out.volume > 0:
                mesh = out
        except Exception:
            # repli historique : reconstruction voxel complète (approchée)
            final = shell_mask | (inner & (np.abs(G) < t))
            mesh = matrix_to_marching_cubes(final, pitch=pitch)
            mesh.apply_translation(origin)
    try:
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.remove_unreferenced_vertices()
    except Exception:
        pass
    rel = float(mesh.volume / m.volume) if m.volume else 1.0
    mesh.export(str(outdir / "_mesh.stl"))
    mesh.export(str(outdir / "model.stl"))
    mesh.export(str(outdir / "model.glb"))
    st = _mesh_stats(mesh)
    st["rel_density"] = round(rel, 3)
    return {"ok": True, "mesh": True, "stats": st, "rel_density": round(rel, 3)}


def _fea_job(job):
    """Calcul de structure minimaliste, exécuté ICI (thread principal du worker) :
    Gmsh installe un handler de signal qui n'est valide que dans le thread principal."""
    import fea
    return fea.analyze_step(
        job["step_path"], force_N=job.get("force_N", 20.0),
        direction=tuple(job.get("direction", (0, 0, -1))),
        material=job.get("material", "PLA"),
        stl_path=job.get("stl_path"),
        loads=job.get("loads"), fixed=job.get("fixed"),
        self_weight=bool(job.get("self_weight")))


def main():
    import build123d as b
    from build123d import export_step, export_stl, export_gltf

    # Bibliothèque de formes paramétriques (garde-fou systémique)
    import shapes as _shapes
    SHAPE_FNS = {n: getattr(_shapes, n) for n, _, _ in _shapes.CATALOG
                 if hasattr(_shapes, n)}
    try:
        from bd_warehouse.gear import SpurGear
        from bd_warehouse.thread import IsoThread
        SHAPE_FNS["SpurGear"] = SpurGear
        SHAPE_FNS["IsoThread"] = IsoThread
    except Exception:
        pass

    sys.stdout.write(json.dumps({"ready": True}) + "\n")
    sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            job = json.loads(line)
            cmd = job.get("cmd", "build")
            if cmd == "import_mesh":
                resp = _mesh_import(job)
                sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush(); continue
            if cmd == "mesh_stamp":
                resp = _mesh_stamp(job)
                sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush(); continue
            if cmd == "svg_perf":
                resp = _svg_perf(job)
                sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush(); continue
            if cmd == "fea":
                resp = _fea_job(job)
                sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush(); continue
            if cmd == "lattice":
                resp = _lattice(job)
                sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush(); continue
            code = Path(job["code_file"]).read_text(encoding="utf-8")
            outdir = Path(job["outdir"])
            outdir.mkdir(parents=True, exist_ok=True)

            ns = {"hollow_tray": hollow_tray, "hook": hook,
                  "hook_curved": hook_curved, "contour_edges": contour_edges}
            ns.update(SHAPE_FNS)
            exec(compile(code, "generated_model.py", "exec"), ns)

            part = ns.get("part") or ns.get("result") or ns.get("model")
            if part is None:
                for v in ns.values():
                    if isinstance(v, (b.Part, b.Solid, b.Compound)):
                        part = v
                        break
            if part is None:
                raise RuntimeError(
                    "Aucun solide trouve : le script doit definir 'part'.")
            if getattr(part, "volume", 0) <= 0:
                raise RuntimeError("Le solide 'part' a un volume nul.")
            # Porte de CONNEXITÉ : une pièce en plusieurs morceaux disjoints est
            # inutilisable (rien ne les relie physiquement) — echec explicite pour
            # que la boucle de correction demande a Gemini de les CONNECTER.
            try:
                _solids = list(part.solids())
            except Exception:
                _solids = []
            if len(_solids) > 1:
                _vols = sorted((round(s.volume / 1000.0, 1) for s in _solids),
                               reverse=True)
                raise RuntimeError(
                    f"PIECE INVALIDE : {len(_solids)} solides DISJOINTS "
                    f"(volumes {_vols} cm3) — les elements ne se touchent pas. "
                    "Fais-les se CHEVAUCHER franchement (au moins 1 mm de "
                    "recouvrement) puis unis-les pour obtenir UN SEUL solide connexe.")

            export_step(part, str(outdir / "model.step"))
            export_stl(part, str(outdir / "model.stl"))
            export_gltf(part, str(outdir / "model.glb"), binary=True)
            try:
                _export_faces(part, outdir)
            except Exception:
                (outdir / "faces.json").write_text('{"faces":[]}', encoding="utf-8")
            try:
                _export_edges(part, outdir)
            except Exception:
                (outdir / "edges.json").write_text('{"edges":[]}', encoding="utf-8")

            bb = part.bounding_box()
            stats = {
                "volume_cm3": round(part.volume / 1000.0, 2),
                "bbox_mm": [round(bb.size.X, 1), round(bb.size.Y, 1),
                            round(bb.size.Z, 1)],
            }
            resp = {"ok": True, "stats": stats}
        except Exception:
            resp = {"ok": False, "error": traceback.format_exc()[-1600:]}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
