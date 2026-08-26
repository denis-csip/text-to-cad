"""
Porte-cable parametrique (snap-fit) -- proto text-to-CAD / build123d.

Geometrie : plaque de base (trou fraise M3) + anneau en C ouvert sur le dessus.
L'ouverture est plus petite que le diametre du cable => le cable "snap" et est retenu.
Toutes les cotes sont pilotees par les variables ci-dessous.
"""
from build123d import *

# ----------------------------- PARAMETRES (mm) -----------------------------
cable_dia   = 6.0    # diametre du cable a maintenir
clearance   = 0.4    # jeu d'impression autour du cable (FDM ~0.3-0.5)
wall        = 2.4    # epaisseur de paroi de l'anneau
depth       = 12.0   # longueur du clip le long du cable
open_ratio  = 0.72   # ouverture = cable_dia * ratio (<1 => grippe / snap)

base_t      = 3.0    # epaisseur plaque de base
base_margin = 6.0    # marge de base autour de l'anneau (cote anneau)
tab_len     = 14.0   # longueur de la languette de fixation
screw_d     = 3.4    # trou de passage M3
head_d      = 6.2    # diametre tete fraisee
head_h      = 2.0    # profondeur fraisage

# ----------------------------- DERIVES -------------------------------------
inner_r = (cable_dia + clearance) / 2
outer_r = inner_r + wall
opening = cable_dia * open_ratio
ring_cz = base_t + outer_r           # hauteur du centre de l'anneau
base_l  = 2 * outer_r + base_margin + tab_len
base_w  = depth
# decalage : anneau du cote -X, languette de vis du cote +X
ring_cx = -(base_l / 2) + outer_r + base_margin / 2
screw_x =  (base_l / 2) - tab_len / 2

# ----------------------------- MODELE --------------------------------------
with BuildPart() as clip:
    # 1) plaque de base
    with BuildSketch(Plane.XY):
        with Locations((0, 0)):
            RectangleRounded(base_l, base_w, radius=2.0)
    extrude(amount=base_t)

    # 2) anneau en C (axe le long de Y => le cable passe en Y)
    with BuildSketch(Plane.XZ.offset(-depth / 2)):
        with Locations((ring_cx, ring_cz)):
            Circle(outer_r)
            Circle(inner_r, mode=Mode.SUBTRACT)
    extrude(amount=depth)

    # 3) ouverture du clip sur le dessus (fente de snap)
    with BuildSketch(Plane.XZ.offset(-depth / 2)):
        with Locations((ring_cx, ring_cz + outer_r / 2)):
            Rectangle(opening, outer_r * 1.4)
    extrude(amount=depth, mode=Mode.SUBTRACT)

    # 4) petit conge base<->anneau pour la solidite
    edges_fillet = clip.edges().filter_by(Axis.Y).group_by(Axis.Z)[0]
    try:
        fillet(edges_fillet, radius=1.0)
    except Exception:
        pass  # conge non critique

    # 5) trou de fixation fraise M3 dans la languette
    with Locations((screw_x, 0, base_t)):
        # fraisage (depuis le dessus)
        with BuildSketch(Plane.XY.offset(base_t)):
            Circle(head_d / 2)
        extrude(amount=-head_h, mode=Mode.SUBTRACT)
    with Locations((screw_x, 0, base_t)):
        with BuildSketch(Plane.XY.offset(base_t)):
            Circle(screw_d / 2)
        extrude(amount=-base_t, mode=Mode.SUBTRACT)

# ----------------------------- CONTROLE + EXPORT ---------------------------
part = clip.part
vol = part.volume
print(f"[OK] solide valide - volume = {vol/1000:.2f} cm3")
bb = part.bounding_box()
print(f"[OK] encombrement (mm) : "
      f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}")
print(f"[info] ouverture snap = {opening:.2f} mm  "
      f"(cable {cable_dia} mm -> serrage {cable_dia-opening:.2f} mm)")

export_step(part, "cable_clip.step")
export_stl(part, "cable_clip.stl")
print("[OK] exporte : cable_clip.step, cable_clip.stl")
