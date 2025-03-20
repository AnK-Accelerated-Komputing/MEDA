from ocp_vscode import show, save_screenshot
import cadquery as cq

height:float = 1.23718
radius:float = 0.54452/2

part:cq.Workplane  = cq.Workplane("XY").cylinder(height, radius)

part = part.translate((0, 0, height/2))
cq.exporters.export(part, 'Ground_Truth.stl')

show(part)
save_screenshot('00003219.png')