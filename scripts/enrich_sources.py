# -*- coding: utf-8 -*-
"""Adosse les fiches du catalogue geo_solutions a des articles reels.

Pipeline par fiche sans sources :
  1. requete savante EN ecrite a la main (ci-dessous)
  2. OpenAlex (API academique GRATUITE, sans cle) -> top 6 candidats + abstracts
  3. juge Gemini Flash : ne garder QUE les papiers qui demontrent reellement la
     geometrie de la fiche (max 2) — pas de citation approximative
  4. sortie : overlay JSON {id, sources:[{title, year, url}]} a fusionner dans
     /data/geo_solutions_ext.json (voir geo_solutions.save_sources / load-merge)

Usage :  python scripts/enrich_sources.py [--dry]   (--dry = OpenAlex seul, 0 appel Gemini)
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

QUERIES = {
    "lattice_gyroid":     "gyroid lattice infill additive manufacturing lightweight mechanical properties",
    "lattice_gradient":   "functionally graded lattice density additive manufacturing",
    "lattice_schwarz":    "Schwarz primitive TPMS lattice mechanical properties 3D printing",
    "lattice_diamond":    "diamond TPMS lattice structure energy absorption additive manufacturing",
    "shell_ribs":         "rib stiffened thin shell design stiffness to weight injection 3D printing",
    "pockets":            "pocketing lightweighting topology material removal stiffness part design",
    "gussets":            "gusset bracket reinforcement stress reduction design additive manufacturing",
    "arches":             "arch compression structure replacing bending beam design",
    "tubular":            "hollow tubular section bending stiffness weight optimization design",
    "local_bosses":       "local boss reinforcement screw insert plastic part design guidelines",
    "fillets_stress":     "fillet radius stress concentration reduction design fatigue",
    "fold_3d":            "folded sheet structure stiffness origami engineering design",
    "nesting":            "telescopic nesting compact stowage mechanism design",
    "asym":               "asymmetric design poka-yoke assembly error prevention",
    "living_hinge":       "living hinge polypropylene flexure design 3D printing",
    "snapfit":            "snap-fit cantilever joint design 3D printing guidelines",
    "dovetail_mod":       "dovetail joint modular 3D printed assembly mechanical interlocking",
    "flat_print":         "build orientation flatness support-free design for additive manufacturing FDM",
    "draft_chamfers":     "chamfer overhang 45 degree support-free FDM design rule",
    "compliant":          "compliant mechanism monolithic flexure 3D printing design",
    "counterweight_geom": "center of gravity lowering stability base design tip-over",
    "capillary_pores":    "capillary rise microchannel 3D printed passive liquid transport Jurin",
    "conformal":          "conformal contact cradle support ergonomic fixture design 3D printed",
}

JUDGE_SYSTEM = """Tu es un chercheur en conception mecanique et fabrication additive.
On te donne UNE solution geometrique (nom, description, consigne CAO) et des
articles candidats (titre + resume). Garde UNIQUEMENT les articles qui DEMONTRENT,
CARACTERISENT ou VALIDENT reellement cette geometrie precise — pas un sujet voisin,
pas une simple mention. Mieux vaut 0 source qu'une citation approximative.
Reponds en JSON : {"keep": [indices des articles retenus, 2 MAXIMUM, ordre de pertinence]}"""


def openalex(query, rows=6):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(query)
           + f"&per-page={rows}&filter=has_abstract:true")
    req = urllib.request.Request(url, headers={"User-Agent": "text-to-cad/1.0"})
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
        oa = (w.get("open_access") or {}).get("oa_url")
        out.append({"title": w.get("display_name"),
                    "year": w.get("publication_year"),
                    "url": w.get("doi") or oa or w.get("id"),
                    "abstract": abstract})
    return out


def judge(sol, cands):
    import llm
    from google.genai import types
    corpus = "\n\n".join(f"[{i}] {c['title']} ({c['year']})\n{c['abstract']}"
                         for i, c in enumerate(cands))
    prompt = (f"SOLUTION : {sol['name']}\nDescription : {sol.get('desc','')}\n"
              f"Consigne CAO : {sol.get('instruction','')[:500]}\n\nCANDIDATS :\n{corpus}")
    cfg = types.GenerateContentConfig(
        system_instruction=JUDGE_SYSTEM, temperature=0.1,
        response_mime_type="application/json",
        **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)}
           if "gemini-3" in llm.MODEL else {}))
    resp = llm._get_client().models.generate_content(
        model=llm.MODEL, contents=prompt, config=cfg)
    data = llm._extract_json(resp.text)
    keep = data.get("keep", []) if isinstance(data, dict) else []
    return [cands[int(i)] for i in keep[:2] if 0 <= int(i) < len(cands)]


def main():
    dry = "--dry" in sys.argv
    import geo_solutions as geo
    overlay = []
    for sid, q in QUERIES.items():
        s = geo.get(sid)
        if not s or s.get("sources"):
            continue
        try:
            cands = openalex(q)
        except Exception as e:
            print(f"{sid}: OpenAlex KO ({e})")
            continue
        print(f"{sid}: {len(cands)} candidats OpenAlex", flush=True)
        if dry:
            for c in cands[:3]:
                print("   -", (c["title"] or "")[:80], c["year"])
            continue
        try:
            kept = judge(s, cands)
        except Exception as e:
            print(f"{sid}: juge KO ({e})")
            continue
        srcs = [{"title": c["title"], "year": c["year"], "url": c["url"]} for c in kept]
        print(f"   retenus: {len(srcs)}" + "".join(f"\n   + {x['title'][:80]}" for x in srcs))
        if srcs:
            overlay.append({"id": sid, "sources": srcs})
        time.sleep(0.4)
    if not dry:
        out = Path(__file__).parent / "sources_overlay.json"
        out.write_text(json.dumps(overlay, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n{len(overlay)} fiches adossees -> {out}")


if __name__ == "__main__":
    main()
