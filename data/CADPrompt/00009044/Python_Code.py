from ocp_vscode import show, save_screenshot
from ocp_vscode import show, save_screenshot
import cadquery as cq

height:float = 0.375
diameter:float = 1.5
hole_diameter:float = 0.237219

part:cq.Workplane = (
    cq.Workplane("XY")
    .cylinder(height, diameter/2)
    .faces(">Z")
    .hole(hole_diameter, height)
)

part = part.translate((0, 0, height/2)).rotate((1,0,0),(0,0,0),-90)
cq.exporters.export(part, 'Ground_Truth.stl')

show(part)
save_screenshot('00009044.png')

show(part)
save_screenshot('00009044.png')