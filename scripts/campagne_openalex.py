# -*- coding: utf-8 -*-
"""CAMPAGNE de moisson massive — Phase A (OpenAlex, gratuit) + Phase B (extraction
Gemini, ~0,5-1 $) pour peupler la matrice geometrique a l'echelle.

~100 requetes savantes couvrant les familles d'astuces geometriques ->
~2000-3000 abstracts dedoublonnes -> extraction TRIZ par lots de 12 (parallele)
-> candidats etiquetes AVEC sources, dedoublonnes entre eux et contre le
catalogue existant. AUCUNE adoption automatique : la sortie alimente la revue
d'expert (Phase C).

Usage : python scripts/campagne_openalex.py [--harvest-only]
Sortie : scripts/campagne_result.json  {stats, candidates}
"""
import json
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

QUERIES = [
    # --- Lattices & cellulaires ---
    "gyroid lattice mechanical properties additive manufacturing",
    "triply periodic minimal surface lattice stiffness strength",
    "octet truss lattice additive manufacturing mechanical",
    "plate lattice stiffness limit additive manufacturing",
    "functionally graded lattice density design",
    "conformal lattice infill freeform design",
    "honeycomb core out-of-plane crush additive manufacturing",
    "Voronoi irregular lattice design 3D printing",
    "hierarchical multiscale lattice mechanical metamaterial",
    "pentamode metamaterial design fabrication",
    "negative stiffness metamaterial energy absorption",
    "auxetic re-entrant honeycomb design 3D printing",
    "chiral auxetic metamaterial mechanical behavior",
    "rotating squares auxetic perforated sheet design",
    "negative Poisson ratio structure impact protection",
    "Kelvin cell open foam lattice additive manufacturing",
    "strut diameter gradient lattice optimization",
    "shell TPMS lattice wall thickness gradient",
    # --- Origami / pliage ---
    "Miura-ori fold core sandwich stiffness",
    "origami tube stiff reconfigurable structure",
    "kirigami stretchable structure design",
    "origami crash box energy absorption",
    "bistable origami mechanism design",
    "folded corrugated core sandwich panel",
    "deployable structure origami engineering",
    # --- Mecanismes compliants & liaisons ---
    "compliant mechanism flexure hinge design 3D printed",
    "cross-axis flexural pivot design",
    "bistable compliant mechanism switch design",
    "living hinge design fatigue polypropylene",
    "snap-fit joint design guidelines additive manufacturing",
    "print-in-place joint clearance 3D printing",
    "3D printed thread tolerance design",
    "topological interlocking assembly blocks mechanics",
    "dovetail interlocking 3D printed joint strength",
    "lattice hinge kerf bending design",
    "ratchet pawl mechanism compact design",
    "constant force compliant mechanism design",
    # --- Textures de surface / tribologie / mouillage ---
    "riblet surface drag reduction texture",
    "shark skin inspired surface texture",
    "superhydrophobic micropillar surface 3D printed",
    "surface texture friction control sliding",
    "dimple texture lubrication friction reduction",
    "anti-icing surface microstructure design",
    "gecko adhesion fibrillar microstructure",
    "anti-fouling surface topography design",
    # --- Fluidique / thermique ---
    "conformal cooling channel injection mold design",
    "TPMS heat exchanger thermal performance",
    "capillary wick 3D printed heat pipe",
    "microchannel capillary passive liquid transport",
    "vascular network channel self-healing design",
    "self-draining geometry drainage design",
    "static mixer geometry 3D printed",
    "Tesla valve fluidic diode design",
    "flow distribution manifold header optimization",
    "graded porous media 3D printed filtration",
    # --- Raidissement structurel ---
    "rib layout optimization thin wall stiffening",
    "isogrid stiffened panel design",
    "corrugated panel bending stiffness design",
    "sandwich core shear design additive manufacturing",
    "stress concentration fillet shape optimization",
    "variable thickness tailored design structure",
    "arch dome compression structure form finding",
    "tensegrity structure design fabrication",
    "geodesic rib shell reinforcement",
    "buckling resistant thin structure stiffener design",
    # --- Absorption d'energie / impact ---
    "crash box crush initiator geometry",
    "cellular structure energy absorption plateau stress",
    "bistable array reusable energy absorption",
    "helmet liner lattice impact optimization",
    "thin-walled tube crush trigger design",
    # --- Vibration / acoustique ---
    "phononic crystal bandgap design",
    "acoustic metamaterial sound absorption structure",
    "acoustic black hole vibration damping",
    "particle damping 3D printed cavity",
    "architected lattice damping viscoelastic",
    # --- DFAM / geometrie pilotee fabrication ---
    "support-free self-supporting overhang design additive manufacturing",
    "part consolidation assembly reduction additive manufacturing",
    "topology optimization design features additive manufacturing",
    "build orientation anisotropy strength design FDM",
    "residual stress distortion compensation geometry additive",
    "teardrop horizontal hole design FDM",
    "infill pattern strength optimization FDM",
    "screw boss design plastic part guidelines",
    "press fit interference design polymer part",
    # --- Bio-inspire ---
    "Bouligand helicoidal architecture toughness",
    "nacre brick and mortar architecture toughness",
    "trabecular bone inspired lattice implant",
    "bamboo node structure bending inspiration",
    "plant stem inspired structural design",
    "spider web architecture energy absorption",
    "honeycomb bee comb structure optimization",
    "conch shell hierarchical structure impact",
    # --- Morphing / 4D ---
    "4D printing shape morphing structure design",
    "anisotropic swelling hinge actuator geometry",
    "shape memory polymer printed structure design",
    "bistable morphing panel skin design",
    # --- Mecanismes divers ---
    "Geneva mechanism compact intermittent motion design",
    "flexure bearing linear guide design",
    "origami inspired stent geometry",
    "graded stiffness interface joint dissimilar materials",
]

MAX_PAPERS = 3000
UA = {"User-Agent": "text-to-cad/1.0"}
_print_lock = threading.Lock()


def openalex(query, rows=30):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(query)
           + f"&per-page={rows}&filter=has_abstract:true")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    out = []
    for w in data.get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        words = {}
        for tok, positions in inv.items():
            for p in positions:
                words[p] = tok
        abstract = " ".join(words[i] for i in sorted(words))[:1200]
        doi = w.get("doi")
        oa = (w.get("open_access") or {}).get("oa_url")
        out.append({"title": w.get("display_name"),
                    "year": w.get("publication_year"),
                    "doi": doi, "url": doi or oa or w.get("id"),
                    "abstract": abstract})
    return out


def harvest():
    papers, seen = [], set()
    for i, q in enumerate(QUERIES):
        try:
            got = openalex(q)
        except Exception as e:
            print(f"[{i+1}/{len(QUERIES)}] KO {q[:40]}: {e}", flush=True)
            continue
        new = 0
        for p in got:
            key = (p.get("doi") or p.get("title") or "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                papers.append(p)
                new += 1
        print(f"[{i+1}/{len(QUERIES)}] {q[:50]} -> {new} nouveaux "
              f"(total {len(papers)})", flush=True)
        if len(papers) >= MAX_PAPERS:
            break
        time.sleep(0.15)
    return papers


def extract_all(papers, workers=5):
    import veille
    batches = [papers[i:i + 12] for i in range(0, len(papers), 12)]
    results, done = [], [0]

    def run(batch):
        try:
            c = veille.extract_candidates(batch)
        except Exception as e:
            c = []
            with _print_lock:
                print("batch KO:", str(e)[:100], flush=True)
        with _print_lock:
            done[0] += 1
            if done[0] % 10 == 0:
                print(f"  extraction {done[0]}/{len(batches)} lots", flush=True)
        return c

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for cands in ex.map(run, batches):
            results.extend(cands)
    return results


def dedup(cands):
    import geo_solutions as geo
    out, ids, names = [], set(), set()
    for c in cands:
        cid = str(c.get("id") or "").strip()
        name = str(c.get("name") or "").lower().strip()
        if not cid or not c.get("instruction"):
            continue
        if cid in ids or cid in geo._BY_ID or (name and name in names):
            continue
        ids.add(cid)
        names.add(name)
        out.append(c)
    return out


def main():
    t0 = time.time()
    papers = harvest()
    print(f"\nPhase A terminee : {len(papers)} articles dedoublonnes "
          f"({time.time()-t0:.0f}s)", flush=True)
    if "--harvest-only" in sys.argv:
        Path(__file__).with_name("campagne_papers.json").write_text(
            json.dumps(papers, ensure_ascii=False), encoding="utf-8")
        return
    t1 = time.time()
    raw = extract_all(papers)
    cands = dedup(raw)
    stats = {"papers": len(papers), "candidats_bruts": len(raw),
             "candidats_dedoublonnes": len(cands),
             "articles_sources_distincts": len({
                 (s.get("url") or s.get("title") or "").lower()
                 for c in cands for s in c.get("sources", []) if s}),
             "duree_harvest_s": round(t1 - t0),
             "duree_extraction_s": round(time.time() - t1)}
    out = Path(__file__).with_name("campagne_result.json")
    out.write_text(json.dumps({"stats": stats, "candidates": cands},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n=== CAMPAGNE TERMINEE ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
