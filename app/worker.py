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


def _fea_job(job):
    """Calcul de structure minimaliste, exécuté ICI (thread principal du worker) :
    Gmsh installe un handler de signal qui n'est valide que dans le thread principal."""
    import fea
    return fea.analyze_step(
        job["step_path"], force_N=job.get("force_N", 20.0),
        direction=tuple(job.get("direction", (0, 0, -1))),
        material=job.get("material", "PLA"),
        stl_path=job.get("stl_path"))


def main():
    import build123d as b
    from build123d import export_step, export_stl, export_gltf

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
            code = Path(job["code_file"]).read_text(encoding="utf-8")
            outdir = Path(job["outdir"])
            outdir.mkdir(parents=True, exist_ok=True)

            ns = {"hollow_tray": hollow_tray, "hook": hook}
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
