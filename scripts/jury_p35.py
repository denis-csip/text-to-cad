# -*- coding: utf-8 -*-
"""JURY DE MODELES sur le principe 35 : un modele d'une AUTRE famille rejoue le
juge strict de `reetiquette_p35.py` ; on compare avec le verdict Gemini deja
applique. Les DESACCORDS sont marques `jury.accord_p35 = false` et remontent
en priorite a l'expert humain.

REGLES DE COUT (incident du 2026-09-09, cf. memoire opencode-zen) :
  - modele SANS raisonnement uniquement (minimax-m2.5 : 2 s, JSON propre) ;
  - PLAFOND DE DEPENSE (--cap, defaut 0,08 $) : le script s'arrete SEUL des que
    le cout cumule mesure (tokens reels x tarif) atteint le plafond ;
  - avancement affiche a chaque lot, avec cout cumule.

Usage : python scripts/jury_p35.py --discipline plasturgie [--model minimax-m2.5] [--cap 0.08]
"""
import io
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


DISC = _arg("--discipline", "plasturgie")
MODEL = _arg("--model", "minimax-m2.5")
CAP = float(_arg("--cap", "0.08"))
PATH = ROOT / "scripts" / f"campagne_{DISC}_candidates.json"
# tarifs Zen ($ par M tokens, entree/sortie) — verifies sur opencode.ai/docs/zen
PRIX = {"minimax-m2.5": (0.30, 1.20), "minimax-m2.7": (0.30, 1.20), "minimax-m3": (0.30, 1.20),
        "glm-5.3-flash": (0.15, 0.50), "deepseek-v4-flash": (0.14, 0.28),
        "gemini-3.5-flash-lite": (0.30, 2.50), "gpt-5.4-nano": (0.20, 1.25)}


def main():
    import invent
    import llm
    from reetiquette_p35 import JUGE
    pin, pout = PRIX.get(MODEL, (1.0, 5.0))          # inconnu = tarif prudent
    cands = json.load(io.open(PATH, encoding="utf-8"))
    cibles = [c for c in cands if "principles_avant" in c]
    print(f"{DISC} : {len(cibles)} candidats -> jury {MODEL}, plafond {CAP:.2f} $", flush=True)
    principes_txt = "; ".join(f"{n} {p.get('label','')}" for n, p in sorted(invent.PRINCIPLES.items()))
    system = JUGE.format(principes=principes_txt)
    lots = [cibles[i:i + 8] for i in range(0, len(cibles), 8)]
    lock = threading.Lock()
    etat = {"cout": 0.0, "in": 0, "out": 0, "stop": False, "done": 0}

    def run(lot):
        if etat["stop"]:
            return []
        corpus = "\n\n".join(
            f"id: {c['id']}\nnom: {c.get('name')}\nportee: {c.get('portee')}\n"
            f"principes actuels: {c['principles_avant']}\ndesc: {c.get('desc','')[:400]}\n"
            f"consigne: {c.get('instruction','')[:400]}" for c in lot)
        try:
            text, usage = llm.zen_chat(system, corpus, model=MODEL, temperature=0.1,
                                       max_tokens=1500, timeout=120)
        except Exception as e:
            print("  lot KO:", str(e)[:100], flush=True)
            return []
        ti, to = int(usage.get("prompt_tokens", 0) or 0), int(usage.get("completion_tokens", 0) or 0)
        with lock:
            etat["in"] += ti; etat["out"] += to
            etat["cout"] += ti * pin / 1e6 + to * pout / 1e6
            etat["done"] += 1
            print(f"  lot {etat['done']}/{len(lots)} — {to} tok sortie — cumul {etat['cout']:.4f} $",
                  flush=True)
            if etat["cout"] >= CAP:
                etat["stop"] = True
                print(f"  PLAFOND {CAP:.2f} $ ATTEINT : arret des lots suivants", flush=True)
        data = llm._extract_json(text)
        return data.get("resultats", []) if isinstance(data, dict) else []

    t0 = time.time()
    verdicts = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(run, lots):
            for r in res:
                verdicts[str(r.get("id"))] = r
    accord = desaccord = absent = 0
    journal = []
    for c in cibles:
        v = verdicts.get(c["id"])
        if not v or not isinstance(v.get("principles"), list):
            absent += 1
            continue
        try:
            ds = sorted({int(x) for x in v["principles"] if 1 <= int(x) <= 40})
        except Exception:
            absent += 1
            continue
        gem = sorted(c["principles"])
        ok35 = ((35 in ds) == (35 in gem))
        jacc = len(set(ds) & set(gem)) / max(1, len(set(ds) | set(gem)))
        c["jury"] = {"modele": MODEL, "principles": ds, "accord_p35": ok35,
                     "jaccard": round(jacc, 2), "motif": str(v.get("motif", ""))[:80]}
        if ok35:
            accord += 1
        else:
            desaccord += 1
            journal.append({"id": c["id"], "name": c.get("name"), "origine": c["principles_avant"],
                            "gemini": gem, MODEL: ds, "motif_jury": c["jury"]["motif"],
                            "motif_gemini": c.get("p35_motif", "")})
    json.dump(cands, io.open(PATH, "w", encoding="utf-8"), ensure_ascii=False)
    (ROOT / "scripts" / f"jury_p35_{DISC}.json").write_text(
        json.dumps(journal, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\naccord P35 {accord} | DESACCORD {desaccord} | sans verdict {absent} | "
          f"{time.time()-t0:.0f}s | tokens in {etat['in']} out {etat['out']} | "
          f"COUT REEL {etat['cout']:.4f} $ (plafond {CAP:.2f})")


if __name__ == "__main__":
    main()
