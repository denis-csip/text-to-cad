"""Garde-fou de structure MINIMALISTE (RDM/FEA léger) pour text-to-CAD.

Chaîne : STEP (build123d) -> maillage tétra (Gmsh) -> élasticité linéaire statique
(solveur CST tet pur numpy/scipy) -> von Mises max + COEFFICIENT DE SÉCURITÉ.

But : un verdict de crédibilité rapide (« ça tient / c'est fragile / où ça casse »),
PAS un calcul réglementaire. Système d'unités cohérent : mm / N / MPa (N/mm²).

Cas de charge canonique par défaut : on ENCASTRE la face du bas (z minimal) et on
applique une force totale sur la face du haut (z maximal), dans une direction donnée.
Le LLM pourra plus tard fournir un cas de charge inféré de la fonction.

Aucune dépendance lourde : gmsh (maillage) + numpy/scipy (déjà présents).
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

# --- Matériaux (E en MPa, limite en MPa) -------------------------------------
MATERIALS = {
    "PLA":  {"E": 3500.0, "nu": 0.36, "yield": 50.0},
    "PETG": {"E": 2100.0, "nu": 0.40, "yield": 45.0},
    "ABS":  {"E": 2200.0, "nu": 0.35, "yield": 40.0},
    "TPU":  {"E":  50.0,  "nu": 0.45, "yield": 8.0},
}


def _extract_tets(gmsh):
    tags, coords, _ = gmsh.model.mesh.getNodes()
    if len(tags) < 4:
        return None, None, None
    coords = np.array(coords, dtype=float).reshape(-1, 3)
    tag2idx = {int(t): i for i, t in enumerate(tags)}
    etypes, etags, enodes = gmsh.model.mesh.getElements(3)
    tets = []
    for et, en in zip(etypes, enodes):
        if et == 4:                           # 4 = tétraèdre linéaire (C3D4)
            conn = np.array(en, dtype=int).reshape(-1, 4)
            tets.append(np.vectorize(tag2idx.get)(conn))
    tets = np.vstack(tets) if tets else np.zeros((0, 4), int)
    # Nœuds par FACE géométrique : permet les charges/encastrements par face choisie.
    surfaces = []
    try:
        for dim, tag in gmsh.model.getEntities(2):
            ntags, ncoords, _ = gmsh.model.mesh.getNodes(2, tag, includeBoundary=True)
            idxs = [tag2idx[int(t)] for t in ntags if int(t) in tag2idx]
            if not idxs:
                continue
            try:
                cx, cy, cz = gmsh.model.occ.getCenterOfMass(2, tag)
            except Exception:
                pts = coords[idxs]
                cx, cy, cz = pts.mean(axis=0)
            surfaces.append({"center": [float(cx), float(cy), float(cz)],
                             "nodes": idxs})
    except Exception:
        surfaces = []
    return coords, tets, surfaces


def _mesh_step(step_path, mesh_size=None):
    """STEP -> (coords Nx3 en mm, tets Mx4). ROBUSTE : réparation OCC + plusieurs
    algorithmes 3D et tailles (les géométries générées provoquent souvent des erreurs
    PLC en maillage 3D ; HXT est le plus tolérant, sinon on grossit la maille)."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        # Réparation de la géométrie importée AVANT l'import (petits bords/faces, couture).
        for opt in ("Geometry.OCCFixDegenerated", "Geometry.OCCFixSmallEdges",
                    "Geometry.OCCFixSmallFaces", "Geometry.OCCSewFaces",
                    "Geometry.OCCMakeSolids"):
            try:
                gmsh.option.setNumber(opt, 1)
            except Exception:
                pass
        gmsh.option.setNumber("Geometry.Tolerance", 1e-3)      # fusionne les points proches
        gmsh.open(str(step_path))
        gmsh.model.occ.synchronize()
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        diag = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2) ** 0.5
        base = mesh_size or max(diag * 0.06, 0.8)
        # (algo3D, algo2D, facteur de taille) : 10=HXT/1=Delaunay/4=Frontal (3D) ;
        # 6=Frontal-Delaunay/5=Delaunay/1=MeshAdapt (2D, la surface = cause des PLC).
        last = None
        for a3, a2, k in ((10, 6, 1.0), (1, 5, 1.4), (1, 6, 1.9), (4, 1, 2.6), (1, 1, 3.4)):
            try:
                gmsh.model.mesh.clear()
                gmsh.option.setNumber("Mesh.Algorithm", a2)
                gmsh.option.setNumber("Mesh.Algorithm3D", a3)
                gmsh.option.setNumber("Mesh.MeshSizeMax", base * k)
                gmsh.option.setNumber("Mesh.MeshSizeMin", base * k * 0.3)
                gmsh.model.mesh.generate(3)
                coords, tets, surfaces = _extract_tets(gmsh)
                if tets is not None and len(tets) > 0:
                    return coords, tets, surfaces
            except Exception as e:
                last = e
        raise RuntimeError("maillage 3D impossible (%s)"
                           % (str(last)[:80] if last else "aucun tétra"))
    finally:
        gmsh.finalize()


def _mesh_from_stl(stl_path, target_faces=6000):
    """REPLI pour les géométries que le maillage B-rep refuse (texte en relief, lofts
    vrillés…) : on tétraédrise le STL SIMPLIFIÉ. La décimation fait disparaître les
    détails décoratifs fins — sans effet notable sur la raideur globale, ce qui est
    exactement le niveau d'un garde-fou."""
    import math, os, tempfile
    import trimesh
    import gmsh
    m = trimesh.load(str(stl_path), force="mesh")
    if len(m.faces) > target_faces:
        try:
            m = m.simplify_quadric_decimation(face_count=target_faces)
        except TypeError:                           # anciennes versions : positionnel
            try:
                m = m.simplify_quadric_decimation(target_faces)
            except Exception:
                pass
        except Exception:
            pass                                    # sans simplif : on tente quand même
    # Réparation MeshFix : supprime auto-intersections et trous (la décimation en crée,
    # et c'est précisément ce qui fait échouer le mailleur volumique).
    try:
        import pymeshfix
        mf = pymeshfix.MeshFix(m.vertices, m.faces)
        mf.repair()
        m = trimesh.Trimesh(mf.points, mf.faces)
    except Exception:
        try:
            m.process(validate=True)
            trimesh.repair.fix_normals(m)
            trimesh.repair.fill_holes(m)
        except Exception:
            pass
    tmp = tempfile.mktemp(suffix=".stl")
    m.export(tmp)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.merge(tmp)
        # Reconstruire une géométrie maillable depuis le maillage discret.
        gmsh.model.mesh.classifySurfaces(40 * math.pi / 180, True, False,
                                         math.pi)
        gmsh.model.mesh.createGeometry()
        surfs = gmsh.model.getEntities(2)
        if not surfs:
            raise RuntimeError("surface STL inexploitable")
        sl = gmsh.model.geo.addSurfaceLoop([s[1] for s in surfs])
        gmsh.model.geo.addVolume([sl])
        gmsh.model.geo.synchronize()
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        diag = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2) ** 0.5
        h = max(diag * 0.06, 0.8)
        gmsh.option.setNumber("Mesh.MeshSizeMax", h)
        gmsh.option.setNumber("Mesh.MeshSizeMin", h * 0.3)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)          # HXT
        try:
            gmsh.model.mesh.generate(3)
        except Exception:
            gmsh.model.mesh.clear()
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)       # Delaunay en secours
            gmsh.model.mesh.generate(3)
        coords, tets, surfaces = _extract_tets(gmsh)
        if tets is None or len(tets) == 0:
            raise RuntimeError("aucun tétra depuis le STL")
        return coords, tets, surfaces
    finally:
        gmsh.finalize()
        try:
            os.unlink(tmp)
        except Exception:
            pass


def _elasticity_D(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[0, 0] = D[1, 1] = D[2, 2] = lam + 2 * mu
    D[3, 3] = D[4, 4] = D[5, 5] = mu
    return D


def _tet_B_V(p):
    """Matrice déformation-déplacement B (6x12) et volume V d'un tétra linéaire.
    p : 4x3 coordonnées des noeuds."""
    M = np.hstack([np.ones((4, 1)), p])           # 4x4
    detM = np.linalg.det(M)
    V = abs(detM) / 6.0
    if V < 1e-12:
        return None, 0.0
    C = np.linalg.inv(M)                            # N_i = C[0,i] + C[1,i]x + C[2,i]y + C[3,i]z
    dN = C[1:4, :]                                  # 3x4 : lignes = d/dx,d/dy,d/dz ; col = noeud
    B = np.zeros((6, 12))
    for i in range(4):
        bx, by, bz = dN[0, i], dN[1, i], dN[2, i]
        c = 3 * i
        B[0, c] = bx; B[1, c + 1] = by; B[2, c + 2] = bz
        B[3, c] = by; B[3, c + 1] = bx
        B[4, c + 1] = bz; B[4, c + 2] = by
        B[5, c] = bz; B[5, c + 2] = bx
    return B, V


def _face_nodes(coords, surfaces, center, diag):
    """Nœuds de la face géométrique la plus proche de `center` ; à défaut (repli STL
    sans faces propres), zone de nœuds de surface autour du point (rayon 12% diag)."""
    c = np.array(center, float)
    if surfaces:
        best = min(surfaces, key=lambda s: np.linalg.norm(np.array(s["center"]) - c))
        if best["nodes"]:
            return list(best["nodes"])
    d = np.linalg.norm(coords - c, axis=1)
    idx = np.where(d < 0.12 * diag)[0]
    return list(idx) if len(idx) else [int(d.argmin())]


def analyze_step(step_path, force_N=20.0, direction=(0, 0, -1),
                 material="PLA", mesh_size=None, include_mesh=True, stl_path=None,
                 loads=None, fixed=None):
    """Renvoie un dict : coefficient de sécurité, von Mises max (MPa), zone la plus
    sollicitée, déplacement max (mm), et infos maillage. Jamais d'exception -> {ok:False}.
    Si le maillage B-rep échoue et qu'un `stl_path` est fourni, repli sur le STL
    simplifié (détails décoratifs lissés -> résultat 'approché')."""
    mat = MATERIALS.get(material, MATERIALS["PLA"])
    E, nu, ylimit = mat["E"], mat["nu"], mat["yield"]
    approx = False
    try:
        coords, tets, surfaces = _mesh_step(step_path, mesh_size)
    except Exception as e:
        if stl_path:
            try:
                coords, tets, surfaces = _mesh_from_stl(stl_path)
                approx = True
            except Exception as e2:
                return {"ok": False,
                        "error": f"maillage échoué (B-rep : {e} ; repli STL : {e2})"}
        else:
            return {"ok": False, "error": f"maillage échoué : {e}"}
    n = len(coords)
    if n == 0 or len(tets) == 0:
        return {"ok": False, "error": "maillage vide"}

    D = _elasticity_D(E, nu)
    ndof = 3 * n
    rows, cols, vals = [], [], []
    Bs, Vs, good = [], [], []
    for t in tets:
        B, V = _tet_B_V(coords[t])
        if B is None:
            Bs.append(None); Vs.append(0.0); good.append(False); continue
        Ke = V * (B.T @ D @ B)
        dofs = np.array([[3 * ni, 3 * ni + 1, 3 * ni + 2] for ni in t]).ravel()
        for a in range(12):
            for b in range(12):
                rows.append(dofs[a]); cols.append(dofs[b]); vals.append(Ke[a, b])
        Bs.append(B); Vs.append(V); good.append(True)
    K = sparse.coo_matrix((vals, (rows, cols)), shape=(ndof, ndof)).tocsr()

    # --- Conditions aux limites -------------------------------------------------
    # Par défaut : encastrement face du bas + charge répartie face du haut.
    # Personnalisable : `fixed` = {c:[x,y,z]} (face d'encastrement choisie) et
    # `loads` = [{c, force_N, direction}] (efforts SURFACIQUES multiples, chaque
    # effort réparti uniformément sur les nœuds de la face la plus proche de c).
    z = coords[:, 2]
    zmin, zmax = z.min(), z.max()
    span = max(zmax - zmin, 1e-6)
    tol = span * 0.03 + 1e-6
    diag0 = float(np.linalg.norm(coords.max(0) - coords.min(0))) or 1.0

    if fixed and fixed.get("c"):
        fixed_nodes = np.array(_face_nodes(coords, surfaces, fixed["c"], diag0), int)
    else:
        fixed_nodes = np.where(z <= zmin + tol)[0]
    if len(fixed_nodes) < 3:
        return {"ok": False, "error": "encastrement indéterminé (face trop petite ?)"}

    fixed_dofs = np.concatenate([[3 * i, 3 * i + 1, 3 * i + 2] for i in fixed_nodes])
    fixed_mask = np.zeros(ndof, bool); fixed_mask[fixed_dofs] = True
    free = np.where(~fixed_mask)[0]

    f = np.zeros(ndof)
    applied = []
    if loads:
        for ld in loads:
            nodes = [n for n in _face_nodes(coords, surfaces, ld.get("c", [0, 0, zmax]), diag0)
                     if not fixed_mask[3 * n]]
            if not nodes:
                continue
            dv = np.array(ld.get("direction") or (0, 0, -1), float)
            dv = dv / (np.linalg.norm(dv) or 1.0)
            F = float(ld.get("force_N", force_N))
            per = F / len(nodes)
            for ni in nodes:
                f[3 * ni:3 * ni + 3] += per * dv
            applied.append({"point": [round(float(x), 1) for x in coords[nodes].mean(0)],
                            "dir": [round(float(x), 3) for x in dv],
                            "force_N": F, "nodes": len(nodes)})
    else:
        load_nodes = np.where(z >= zmax - tol)[0]
        load_nodes = load_nodes[~fixed_mask[3 * load_nodes]] if len(load_nodes) else load_nodes
        if len(load_nodes) == 0:
            return {"ok": False, "error": "cas de charge indéterminé (géométrie plate ?)"}
        d = np.array(direction, float); d = d / (np.linalg.norm(d) or 1.0)
        per = force_N / len(load_nodes)
        for ni in load_nodes:
            f[3 * ni:3 * ni + 3] += per * d
        applied.append({"point": [round(float(x), 1) for x in coords[load_nodes].mean(0)],
                        "dir": [round(float(x), 3) for x in d],
                        "force_N": float(force_N), "nodes": int(len(load_nodes))})
    if not applied:
        return {"ok": False, "error": "aucun effort applicable (faces confondues avec l'encastrement ?)"}

    try:
        u = np.zeros(ndof)
        u[free] = spsolve(K[free][:, free].tocsc(), f[free])
    except Exception as e:
        return {"ok": False, "error": f"résolution échouée : {e}"}

    # --- Contrainte de von Mises par élément + accumulation nodale (pour la visu) ---
    elem_vm = np.zeros(len(tets))
    nodal_sum = np.zeros(n)
    nodal_cnt = np.zeros(n)
    max_vm, worst = 0.0, None
    for k, (t, B, g) in enumerate(zip(tets, Bs, good)):
        if not g:
            continue
        dofs = np.array([[3 * ni, 3 * ni + 1, 3 * ni + 2] for ni in t]).ravel()
        s = D @ (B @ u[dofs])                          # [sxx,syy,szz,sxy,syz,szx]
        vm = float((0.5 * ((s[0] - s[1]) ** 2 + (s[1] - s[2]) ** 2 + (s[2] - s[0]) ** 2)
                    + 3 * (s[3] ** 2 + s[4] ** 2 + s[5] ** 2)) ** 0.5)
        elem_vm[k] = vm
        for ni in t:
            nodal_sum[ni] += vm
            nodal_cnt[ni] += 1
        if vm > max_vm:
            max_vm = vm
            worst = coords[t].mean(axis=0)
    nodal_vm = nodal_sum / np.maximum(nodal_cnt, 1)
    disp = u.reshape(-1, 3)
    umax = float(np.abs(disp).sum(axis=1).max())
    sf = float(ylimit / max_vm) if max_vm > 1e-9 else 999.0
    # Sanity : un déplacement absurde signale un cas de charge mal posé (modes parasites,
    # ex. forme organique sans face d'encastrement franche) -> on le signale.
    diag = float(np.linalg.norm(coords.max(0) - coords.min(0)))
    wellposed = umax < 5.0 * diag

    # --- Maillage de surface (faces frontières) coloré par la contrainte, pour la visu ---
    viz = None
    if include_mesh:
        from collections import defaultdict
        FACES = ((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2))
        cnt = defaultdict(int)
        rep = {}
        for t, g in zip(tets, good):
            if not g:
                continue
            for a, b, c in FACES:
                tri = (int(t[a]), int(t[b]), int(t[c]))
                key = tuple(sorted(tri))
                cnt[key] += 1
                rep.setdefault(key, tri)
        surf = [rep[k] for k, v in cnt.items() if v == 1]     # faces vues une seule fois = surface
        used = sorted({i for tri in surf for i in tri})
        remap = {o: j for j, o in enumerate(used)}
        viz = {
            "nodes": [[round(float(x), 2) for x in coords[i]] for i in used],
            "tris": [[remap[a], remap[b], remap[c]] for (a, b, c) in surf],
            "vm": [round(float(nodal_vm[i]), 3) for i in used],
            "disp": [[round(float(x), 4) for x in disp[i]] for i in used],
            "vm_max": round(float(max_vm), 3),
        }

    return {
        "ok": True,
        "material": material,
        "force_N": float(force_N),
        "safety_factor": round(sf, 2),
        "max_von_mises_MPa": round(float(max_vm), 2),
        "yield_MPa": float(ylimit),
        "max_displacement_mm": round(umax, 3) if wellposed else None,
        "load_case_wellposed": bool(wellposed),
        "weakest_point_mm": [round(float(x), 1) for x in worst] if worst is not None else None,
        "load_point_mm": applied[0]["point"],
        "load_dir": applied[0]["dir"],
        "loads_applied": applied,
        "fixed_nodes": int(len(fixed_nodes)),
        "nodes": int(n),
        "tets": int(len(tets)),
        "verdict": ("solide" if sf >= 2 else "limite" if sf >= 1 else "trop fragile"),
        "approx_geometry": bool(approx),   # calculé sur STL simplifié (détails lissés)
        "mesh": viz,
    }
