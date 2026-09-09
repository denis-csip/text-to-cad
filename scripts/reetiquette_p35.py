# -*- coding: utf-8 -*-
"""RE-ETIQUETAGE STRICT DU PRINCIPE 35 (fourre-tout) sur les candidats d'une
campagne. Regle : P35 « modification des proprietes » n'est garde QUE si le
coeur inventif de la solution est un changement d'etat ou de propriete de la
MATIERE elle-meme (etat d'agregation, concentration, flexibilite, temperature
de la substance...). Sinon, le juge choisit le(s) principe(s) PRECIS parmi les
40. Les principes d'origine sont conserves dans `principles_avant` (audit).

Usage : python scripts/reetiquette_p35.py --discipline plasturgie [--dry]
Cout mesure : ~0,003 $ par lot de 15 candidats (~0,07 $ pour 308).
"""
import json
import io
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

DISC = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--discipline=")), None) \
    or (sys.argv[sys.argv.index("--discipline") + 1] if "--discipline" in sys.argv else "plasturgie")
DRY = "--dry" in sys.argv
PATH = ROOT / "scripts" / f"campagne_{DISC}_candidates.json"

JUGE = """Tu es un expert TRIZ rigoureux. On te donne des solutions techniques deja
etiquetees avec des principes inventifs. Le principe 35 « Modification des
proprietes/parametres » a ete SUR-UTILISE comme fourre-tout. Ta tache : pour
chaque solution, decider si le 35 est JUSTIFIE et, sinon, le REMPLACER.

REGLE STRICTE pour garder le 35 : le coeur inventif de la solution doit etre un
changement d'ETAT ou de PROPRIETE de la matiere elle-meme (etat d'agregation,
concentration, degre de flexibilite, temperature de la substance, densite...).
NE SONT PAS des 35 : un reglage de procede (-> 19 action periodique, 21 action
eclair, 20 continuite, 10 action prealable...), un changement de forme ou de
geometrie (-> 3 qualite locale, 4 asymetrie, 14 spheroidalite, 17 autre
dimension), une substitution de materiau par un autre (-> 40 composites,
31 poreux, 27 objet bon marche, 26 copie), un ajout de fonction (-> 6
universalite, 5 combinaison), un capteur ou controle (-> 23 retroaction,
28 substitution mecanique), une separation (-> 1 segmentation, 2 extraction).

Les 40 principes : {principes}

Reponds UNIQUEMENT en JSON : {{"resultats": [
  {{"id": "...", "p35_justifie": true|false,
    "principles": [liste finale COMPLETE des n° de principes, 1 a 4 max, le 35
                   inclus seulement s'il est justifie],
    "motif": "10 mots max"}} ]}}
Garde les autres principes deja presents s'ils sont pertinents."""


def juge(lot, principes_txt):
    import llm
    from google.genai import types
    corpus = "\n\n".join(
        f"id: {c['id']}\nnom: {c.get('name')}\nportee: {c.get('portee')}\n"
        f"principes actuels: {c.get('principles')}\ndesc: {c.get('desc','')[:400]}\n"
        f"consigne: {c.get('instruction','')[:400]}" for c in lot)
    cfg = types.GenerateContentConfig(
        system_instruction=JUGE.format(principes=principes_txt), temperature=0.1,
        response_mime_type="application/json",
        **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)}
           if "gemini-3" in llm.MODEL else {}))
    resp = llm._get_client().models.generate_content(
        model=llm.MODEL, contents=corpus, config=cfg)
    data = llm._extract_json(resp.text)
    return data.get("resultats", []) if isinstance(data, dict) else []


def main():
    import invent
    cands = json.load(io.open(PATH, encoding="utf-8"))
    cibles = [c for c in cands if 35 in c.get("principles", [])]
    print(f"{DISC} : {len(cands)} candidats, {len(cibles)} portent P35")
    if DRY:
        return
    principes_txt = "; ".join(f"{n} {p.get('label','')}" for n, p in sorted(invent.PRINCIPLES.items()))
    lots = [cibles[i:i + 15] for i in range(0, len(cibles), 15)]
    t0 = time.time()
    verdicts = {}

    def run(lot):
        try:
            return juge(lot, principes_txt)
        except Exception as e:
            print("lot KO:", str(e)[:100], flush=True)
            return []

    with ThreadPoolExecutor(max_workers=5) as ex:
        for res in ex.map(run, lots):
            for r in res:
                verdicts[str(r.get("id"))] = r
    garde = retire = inchange = 0
    journal = []
    for c in cibles:
        v = verdicts.get(c["id"])
        if not v or not isinstance(v.get("principles"), list):
            inchange += 1
            continue
        new = sorted({int(x) for x in v["principles"] if 1 <= int(x) <= 40})[:4]
        if not new:
            inchange += 1
            continue
        c["principles_avant"] = c["principles"]
        c["principles"] = new
        c["p35_motif"] = str(v.get("motif", ""))[:80]
        if 35 in new:
            garde += 1
        else:
            retire += 1
        journal.append({"id": c["id"], "name": c.get("name"), "avant": c["principles_avant"],
                        "apres": new, "motif": c["p35_motif"]})
    # re-annotation de l'apport (poids + seuil de specificite) et tri
    sys.argv.append("--discipline"); sys.argv.append(DISC)
    sys.path.insert(0, str(ROOT / "scripts"))
    import campagne_openalex as C
    C.annote_impact(cands)
    json.dump(cands, io.open(PATH, "w", encoding="utf-8"), ensure_ascii=False)
    (ROOT / "scripts" / f"reetiquetage_p35_{DISC}.json").write_text(
        json.dumps(journal, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"P35 garde {garde} | P35 retire {retire} | inchange {inchange} | "
          f"{time.time()-t0:.0f}s | journal -> reetiquetage_p35_{DISC}.json")


if __name__ == "__main__":
    main()
