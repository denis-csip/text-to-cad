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


def _mesh_step(step_path, mesh_size=None):
    """STEP -> (coords Nx3 en mm, tets Mx4 indices 0-based)."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(str(step_path))
        gmsh.model.occ.synchronize()
        # Taille de maille : ~ 6 % de la diagonale de la boîte englobante (grossier mais suffisant).
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        diag = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2) ** 0.5
        h = mesh_size or max(diag * 0.06, 0.8)
        gmsh.option.setNumber("Mesh.MeshSizeMax", h)
        gmsh.option.setNumber("Mesh.MeshSizeMin", h * 0.3)
        gmsh.model.mesh.generate(3)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        coords = np.array(coords, dtype=float).reshape(-1, 3)
        tag2idx = {int(t): i for i, t in enumerate(tags)}
        etypes, etags, enodes = gmsh.model.mesh.getElements(3)
        tets = []
        for et, en in zip(etypes, enodes):
            if et == 4:                       # 4 = tétraèdre linéaire (C3D4)
                conn = np.array(en, dtype=int).reshape(-1, 4)
                tets.append(np.vectorize(tag2idx.get)(conn))
        tets = np.vstack(tets) if tets else np.zeros((0, 4), int)
        return coords, tets
    finally:
        gmsh.finalize()


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


def analyze_step(step_path, force_N=20.0, direction=(0, 0, -1),
                 material="PLA", mesh_size=None, include_mesh=True):
    """Renvoie un dict : coefficient de sécurité, von Mises max (MPa), zone la plus
    sollicitée, déplacement max (mm), et infos maillage. Jamais d'exception -> {ok:False}."""
    mat = MATERIALS.get(material, MATERIALS["PLA"])
    E, nu, ylimit = mat["E"], mat["nu"], mat["yield"]
    try:
        coords, tets = _mesh_step(step_path, mesh_size)
    except Exception as e:
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

    # --- Conditions aux limites : encastrement face du bas, charge face du haut ---
    z = coords[:, 2]
    zmin, zmax = z.min(), z.max()
    span = max(zmax - zmin, 1e-6)
    tol = span * 0.03 + 1e-6
    fixed_nodes = np.where(z <= zmin + tol)[0]
    load_nodes = np.where(z >= zmax - tol)[0]
    if len(fixed_nodes) < 3 or len(load_nodes) == 0:
        return {"ok": False, "error": "cas de charge indéterminé (géométrie plate ?)"}

    fixed_dofs = np.concatenate([[3 * i, 3 * i + 1, 3 * i + 2] for i in fixed_nodes])
    fixed_mask = np.zeros(ndof, bool); fixed_mask[fixed_dofs] = True
    free = np.where(~fixed_mask)[0]

    f = np.zeros(ndof)
    d = np.array(direction, float); d = d / (np.linalg.norm(d) or 1.0)
    per = force_N / len(load_nodes)
    for ni in load_nodes:
        f[3 * ni:3 * ni + 3] += per * d

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
        "nodes": int(n),
        "tets": int(len(tets)),
        "verdict": ("solide" if sf >= 2 else "limite" if sf >= 1 else "trop fragile"),
        "mesh": viz,
    }
