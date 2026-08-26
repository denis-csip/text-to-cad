"""Genere une vue isometrique SVG du porte-cable (projection HLR, sans GPU)."""
from build123d import import_step, ExportSVG, LineType, Color

part = import_step("cable_clip.step")

# projection isometrique : oeil place en (1,-1,1)
visible, hidden = part.project_to_viewport((60, -60, 45))

max_dim = max(*part.bounding_box().size)
exporter = ExportSVG(scale=6, margin=8)
exporter.add_layer("hidden", line_color=Color(0.6, 0.6, 0.6),
                   line_type=LineType.ISO_DOT, line_weight=0.2)
exporter.add_layer("visible", line_color=Color(0.05, 0.05, 0.1),
                   line_weight=0.5)
exporter.add_shape(hidden, layer="hidden")
exporter.add_shape(visible, layer="visible")
exporter.write("clip_iso.svg")
print("[OK] clip_iso.svg ecrit")
