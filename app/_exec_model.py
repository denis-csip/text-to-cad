"""Execute un script build123d genere et exporte model.step/.stl/.glb.
Lance en sous-processus : python _exec_model.py <code_file> <outdir>
Imprime une ligne 'STATS::{json}' en cas de succes, sinon leve/trace l'erreur."""
import sys, json, traceback
from pathlib import Path


def main():
    code_file, outdir = sys.argv[1], Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    src = Path(code_file).read_text(encoding="utf-8")

    import build123d as b
    from build123d import export_step, export_stl, export_gltf

    ns = {}
    exec(compile(src, "generated_model.py", "exec"), ns)

    part = ns.get("part") or ns.get("result") or ns.get("model")
    if part is None:
        for v in ns.values():
            if isinstance(v, (b.Part, b.Solid, b.Compound)):
                part = v
                break
    if part is None:
        raise RuntimeError(
            "Aucun solide trouve : le script doit definir une variable 'part'.")

    if getattr(part, "volume", 0) <= 0:
        raise RuntimeError("Le solide 'part' a un volume nul (geometrie invalide).")

    export_step(part, str(outdir / "model.step"))
    export_stl(part, str(outdir / "model.stl"))
    export_gltf(part, str(outdir / "model.glb"), binary=True)

    bb = part.bounding_box()
    stats = {
        "volume_cm3": round(part.volume / 1000.0, 2),
        "bbox_mm": [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)],
    }
    print("STATS::" + json.dumps(stats))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
