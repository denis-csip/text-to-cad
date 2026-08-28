"""Bibliothèque de FORMES PARAMÉTRIQUES robustes — le garde-fou systémique.

Chaque générateur renvoie une Part build123d (1 solide connexe, maillable),
construite en profils 2D extrudés / primitives + booléens (jamais de sweep 3D).
Le LLM ASSEMBLE ces briques au lieu d'improviser la géométrie.

Convention : cotes en mm ; pièce posée base à Z=0 quand ça a un sens.
Les imports build123d sont DANS les fonctions : importer ce module reste léger
(le catalogue CATALOG est lisible sans charger le noyau CAO).
"""

# --- Catalogue (données pures, injectées dans le prompt automatiquement) -----
CATALOG = [
    ("plate", "plate(l, w, t, corner_r=0)",
     "plaque rectangulaire, coins arrondis optionnels, base a Z=0, centree en XY"),
    ("plate_holes", "plate_holes(l, w, t, hole_d=4, margin=6, corner_r=3)",
     "plaque de fixation : 4 trous aux coins a `margin` des bords"),
    ("l_bracket", "l_bracket(a=40, b=40, w=30, t=4, fillet_r=3)",
     "equerre en L : aile horizontale (longueur a, +X) + aile verticale (hauteur b, +Z)"),
    ("u_bracket", "u_bracket(inner_w=30, h=30, depth=20, t=4)",
     "etrier en U ouvert vers +Z : fond + 2 flancs, interieur inner_w"),
    ("tube", "tube(od=20, id=16, h=30)",
     "tube/bague/entretoise creuse, axe Z, base a Z=0"),
    ("ring_open", "ring_open(od=32, id=24, h=10, opening_deg=70, opening_dir_deg=90)",
     "anneau OUVERT (clip, virgule) : secteur retire vers l'angle opening_dir_deg"),
    ("standoff", "standoff(d=8, h=12, hole_d=3.2)",
     "entretoise cylindrique percee (colonne de montage), axe Z"),
    ("gusset", "gusset(a=20, b=20, t=4)",
     "gousset triangulaire de renfort dans le plan XZ (epaisseur Y) entre 2 surfaces"),
    ("rib", "rib(l=40, h=10, t=3)",
     "nervure de rigidification : lame le long de +X, hauteur +Z, base a Z=0"),
    ("funnel", "funnel(d_top=60, d_bot=12, h=50, t=2)",
     "entonnoir/cone creux, grande ouverture en haut, axe Z"),
    ("wedge_stand", "wedge_stand(w=80, d=70, angle=60, t=6, lip=10)",
     "support incline (telephone/tablette) : dossier a `angle` deg + base + levre avant"),
    ("handle", "handle(span=90, grip_d=22, standoff_h=30, foot_w=18)",
     "poignee en U : barre horizontale + 2 pieds, a poser/unir sur une surface (base Z=0)"),
    ("knob", "knob(d=30, h=15, ridges=9, ridge_d=4)",
     "bouton molete : cylindre avec encoches polaires pour la prise en main"),
    ("cable_clip", "cable_clip(cable_d=8, t=3, w=10, base_t=3, hole_d=3.2)",
     "clip de cable : anneau ouvert vers le haut + semelle percee pour vis"),
    ("snap_tab", "snap_tab(l=18, w=6, t=2, lip=1.5)",
     "languette snap-fit cantilever : lame + bec de retenue au bout (flexion)"),
    ("dovetail_rail", "dovetail_rail(l=40, w_top=12, w_bot=8, h=6)",
     "rail male en queue d'aronde le long de +X (glissiere)"),
    ("dovetail_slot", "dovetail_slot(part, l=41, w_top=12.6, w_bot=8.6, h=6.2, at=(0,0,0))",
     "creuse la rainure femelle correspondante dans `part` (jeu ~0.3 inclus si +0.6)"),
    ("tray", "tray(l=80, w=60, h=25, t=2, corner_r=6)",
     "bac rectangulaire ouvert (fond + parois), coins arrondis"),
    ("lid", "lid(l=80, w=60, t=2, lip_h=6, clearance=0.3, corner_r=6)",
     "couvercle emboitant pour le bac `tray` de memes l/w (jeu d'impression inclus)"),
    ("hook", "hook(width=8, arm=25, rise=28, thickness=8)",
     "crochet/patere ANGULAIRE en L arrondi (queue +X, releve +Z, dos en X=0)"),
    ("hook_curved", "hook_curved(radius=16, thickness=6, opening_deg=80, width=12, tab_len=20)",
     "crochet COURBE en virgule/J : anneau ouvert + queue de fixation au dos"),
    ("hollow_tray", "hollow_tray(part, wall=2, height=40, base=2)",
     "evide une piece plate extrudee en bac a parois (erosion robuste du contour)"),
]


def _fillet_safe(part, edges, r):
    from build123d import fillet
    for rr in (r, r * 0.5):
        try:
            return fillet(edges, rr)
        except Exception:
            continue
    return part


# --- Générateurs -------------------------------------------------------------

def plate(l=60.0, w=40.0, t=4.0, corner_r=0.0):
    from build123d import BuildPart, BuildSketch, Plane, Rectangle, RectangleRounded, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            if corner_r > 0:
                RectangleRounded(l, w, radius=min(corner_r, min(l, w) / 2.2))
            else:
                Rectangle(l, w)
        extrude(amount=t)
    return p.part


def plate_holes(l=60.0, w=40.0, t=4.0, hole_d=4.0, margin=6.0, corner_r=3.0):
    from build123d import (BuildPart, BuildSketch, Plane, RectangleRounded,
                           Circle, Locations, Mode, extrude)
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            RectangleRounded(l, w, radius=min(corner_r, min(l, w) / 2.2))
            dx, dy = l / 2 - margin, w / 2 - margin
            with Locations((dx, dy), (-dx, dy), (dx, -dy), (-dx, -dy)):
                Circle(hole_d / 2, mode=Mode.SUBTRACT)
        extrude(amount=t)
    return p.part


def l_bracket(a=40.0, b=40.0, w=30.0, t=4.0, fillet_r=3.0):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude, Axis
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):          # profil en L, epaisseur selon Y
            Polygon((0, 0), (a, 0), (a, t), (t, t), (t, b), (0, b), align=None)
        extrude(amount=w / 2.0, both=True)
    part = p.part
    return _fillet_safe(part, part.edges().filter_by(Axis.Y), fillet_r)


def u_bracket(inner_w=30.0, h=30.0, depth=20.0, t=4.0):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    W = inner_w + 2 * t
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):          # profil en U, extrude selon Y
            Polygon((-W / 2, 0), (W / 2, 0), (W / 2, h), (W / 2 - t, h),
                    (W / 2 - t, t), (-W / 2 + t, t), (-W / 2 + t, h), (-W / 2, h),
                    align=None)
        extrude(amount=depth / 2.0, both=True)
    return p.part


def tube(od=20.0, id=16.0, h=30.0):
    from build123d import BuildPart, BuildSketch, Plane, Circle, Mode, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Circle(od / 2)
            Circle(max(id, 0.5) / 2, mode=Mode.SUBTRACT)
        extrude(amount=h)
    return p.part


def ring_open(od=32.0, id=24.0, h=10.0, opening_deg=70.0, opening_dir_deg=90.0):
    import math
    from build123d import BuildPart, BuildSketch, Plane, Circle, Polygon, Mode, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Circle(od / 2)
            Circle(max(id, 0.5) / 2, mode=Mode.SUBTRACT)
            half = math.radians(max(15.0, min(opening_deg, 170.0))) / 2
            mid = math.radians(opening_dir_deg)
            big = 2.0 * od
            Polygon((0, 0),
                    (big * math.cos(mid - half), big * math.sin(mid - half)),
                    (big * math.cos(mid + half), big * math.sin(mid + half)),
                    align=None, mode=Mode.SUBTRACT)
        extrude(amount=h)
    return p.part


def standoff(d=8.0, h=12.0, hole_d=3.2):
    return tube(od=d, id=hole_d, h=h)


def gusset(a=20.0, b=20.0, t=4.0):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Polygon((0, 0), (a, 0), (0, b), align=None)
        extrude(amount=t / 2.0, both=True)
    return p.part


def rib(l=40.0, h=10.0, t=3.0):
    from build123d import Box, Align
    return Box(l, t, h, align=(Align.MIN, Align.CENTER, Align.MIN))


def funnel(d_top=60.0, d_bot=12.0, h=50.0, t=2.0):
    from build123d import BuildPart, BuildSketch, Plane, Circle, Mode, extrude, loft
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Circle(d_bot / 2)
        with BuildSketch(Plane.XY.offset(h)):
            Circle(d_top / 2)
        loft()
        with BuildSketch(Plane.XY):
            Circle(max(d_bot / 2 - t, 0.5))
        with BuildSketch(Plane.XY.offset(h)):
            Circle(max(d_top / 2 - t, 1.0))
        loft(mode=Mode.SUBTRACT)
    return p.part


def wedge_stand(w=80.0, d=70.0, angle=60.0, t=6.0, lip=10.0):
    import math
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    a = math.radians(max(20.0, min(angle, 85.0)))
    L = d * 0.95                                   # longueur du dossier
    bx, bz = -L * math.cos(a), L * math.sin(a)     # sommet du dossier (penche vers -X)
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):                # profil : base + dossier + levre avant
            Polygon((0, 0), (d, 0), (d, t), (0, t), align=None)
            Polygon((0, 0), (t, 0), (bx + t, bz), (bx, bz), align=None)
            Polygon((d - t, t), (d, t), (d, t + lip), (d - t, t + lip), align=None)
        extrude(amount=w / 2.0, both=True)
    return p.part


def handle(span=90.0, grip_d=22.0, standoff_h=30.0, foot_w=18.0):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, RectangleRounded, extrude, Pos, Rot
    g = grip_d
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            # 2 pieds + barre : profil en U inversé plein (simple, costaud)
            Polygon((-span / 2, 0), (-span / 2 + foot_w, 0),
                    (-span / 2 + foot_w, standoff_h),
                    (span / 2 - foot_w, standoff_h), (span / 2 - foot_w, 0),
                    (span / 2, 0), (span / 2, standoff_h + g),
                    (-span / 2, standoff_h + g), align=None)
        extrude(amount=g / 2.0, both=True)
    return p.part


def knob(d=30.0, h=15.0, ridges=9, ridge_d=4.0):
    from build123d import (BuildPart, BuildSketch, Plane, Circle, Mode,
                           PolarLocations, extrude)
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Circle(d / 2)
            with PolarLocations(d / 2, max(3, int(ridges))):
                Circle(ridge_d / 2, mode=Mode.SUBTRACT)
        extrude(amount=h)
    return p.part


def cable_clip(cable_d=8.0, t=3.0, w=10.0, base_t=3.0, hole_d=3.2):
    from build123d import (BuildPart, BuildSketch, Plane, Circle, Polygon,
                           Locations, Mode, extrude)
    R = cable_d / 2 + t
    base_l = 2 * R + 2 * hole_d + 8
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            # semelle
            Polygon((-base_l / 2, 0), (base_l / 2, 0),
                    (base_l / 2, base_t), (-base_l / 2, base_t), align=None)
            # anneau pose sur la semelle (leger recouvrement)
            with Locations((0, base_t + R - 0.5)):
                Circle(R)
                Circle(cable_d / 2, mode=Mode.SUBTRACT)
            # fente d'insertion du cable, vers le haut
            Polygon((-cable_d / 4, base_t + R - 0.5), (cable_d / 4, base_t + R - 0.5),
                    (cable_d / 4, base_t + 2 * R + 2), (-cable_d / 4, base_t + 2 * R + 2),
                    align=None, mode=Mode.SUBTRACT)
        extrude(amount=w / 2.0, both=True)
        # trous de vis traversant la semelle
        with BuildSketch(Plane.XY):
            with Locations((base_l / 2 - hole_d, 0), (-base_l / 2 + hole_d, 0)):
                Circle(hole_d / 2)
        extrude(amount=base_t + 1, mode=Mode.SUBTRACT)
    return p.part


def snap_tab(l=18.0, w=6.0, t=2.0, lip=1.5):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):          # lame + bec (profil), largeur selon Y
            Polygon((0, 0), (l, 0), (l, t + lip), (l - lip, t + lip),
                    (l - 2 * lip, t), (0, t), align=None)
        extrude(amount=w / 2.0, both=True)
    return p.part


def dovetail_rail(l=40.0, w_top=12.0, w_bot=8.0, h=6.0):
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    with BuildPart() as p:
        with BuildSketch(Plane.YZ):          # trapezoide, extrude le long de +X
            Polygon((-w_bot / 2, 0), (w_bot / 2, 0),
                    (w_top / 2, h), (-w_top / 2, h), align=None)
        extrude(amount=l)
    return p.part


def dovetail_slot(part, l=41.0, w_top=12.6, w_bot=8.6, h=6.2, at=(0, 0, 0)):
    from build123d import Pos
    tool = Pos(*at) * dovetail_rail(l=l, w_top=w_top, w_bot=w_bot, h=h)
    return part - tool


def tray(l=80.0, w=60.0, h=25.0, t=2.0, corner_r=6.0):
    from build123d import BuildPart, BuildSketch, Plane, RectangleRounded, Mode, extrude
    r_out = min(corner_r, min(l, w) / 2.2)
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            RectangleRounded(l, w, radius=r_out)
        extrude(amount=t)                    # fond
        with BuildSketch(Plane.XY.offset(t)):
            RectangleRounded(l, w, radius=r_out)
            RectangleRounded(l - 2 * t, w - 2 * t,
                             radius=max(r_out - t, 0.5), mode=Mode.SUBTRACT)
        extrude(amount=max(h - t, 1.0))      # parois
    return p.part


def lid(l=80.0, w=60.0, t=2.0, lip_h=6.0, clearance=0.3, corner_r=6.0):
    from build123d import BuildPart, BuildSketch, Plane, RectangleRounded, Mode, extrude
    r_out = min(corner_r, min(l, w) / 2.2)
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            RectangleRounded(l, w, radius=r_out)
        extrude(amount=t)                    # dessus
        with BuildSketch(Plane.XY.offset(t)):
            li, wi = l - 2 * t - 2 * clearance, w - 2 * t - 2 * clearance
            RectangleRounded(li, wi, radius=max(r_out - t, 0.5))
            RectangleRounded(li - 2 * t, wi - 2 * t,
                             radius=max(r_out - 2 * t, 0.4), mode=Mode.SUBTRACT)
        extrude(amount=lip_h)                # jupe interieure
    return p.part
