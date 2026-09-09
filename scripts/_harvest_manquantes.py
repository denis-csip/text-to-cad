# -*- coding: utf-8 -*-
"""Moisson de rattrapage (0 $) : rejoue les requetes en echec du log de moisson
(coupure reseau) et n'ajoute que les articles ABSENTS du corpus deja moissonne."""
import io, json, re, sys
from pathlib import Path
sys.argv += ["--discipline", "plasturgie"]
sys.path.insert(0, str(Path(__file__).parent))
import campagne_openalex as C
log = io.open("scripts/campagne_plasturgie_harvest_log.txt", encoding="utf-8").read()
ko = set(m.group(1).strip() for m in re.finditer(r"\] KO (.*?): ", log))
failed = [q for q in C.QUERIES if q[:40] in ko or any(q.startswith(k) for k in ko)]
print(f"requetes a rejouer : {len(failed)}", flush=True)
deja = json.loads(Path("scripts/campagne_plasturgie_papers.json").read_text(encoding="utf-8"))
seen = {(p.get("doi") or p.get("title") or "").lower().strip() for p in deja}
C.QUERIES[:] = failed
new = [p for p in C.harvest()
       if (p.get("doi") or p.get("title") or "").lower().strip() not in seen]
Path("scripts/campagne_plasturgie_papers_run3.json").write_text(json.dumps(new, ensure_ascii=False), encoding="utf-8")
print(f"\nRATTRAPAGE : {len(new)} articles NOUVEAUX (hors les {len(deja)} deja extraits)")
