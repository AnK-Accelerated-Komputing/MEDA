from ocp_vscode import show, save_screenshot
import cadquery as cq

length:float = 0.75
width:float = 0.1875
height:float = 0.00391
hole_diameter:float = 0.06256*2

part:cq.Workplane = (
    cq.Workplane("XY")
    .box(length, width, height, centered = False)
    .faces(">Z")
    .hole(hole_diameter, height)
)

cq.exporters.export(part, 'Ground_Truth.stl')

show(part)
save_screenshot('00000633.png')