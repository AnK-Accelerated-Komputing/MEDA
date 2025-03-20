from ocp_vscode import show, save_screenshot
from ocp_vscode import show, save_screenshot
import cadquery as cq

length:float = 0.75
width:float = 0.0075
height:float = 0.075

part:cq.Workplane = cq.Workplane("XY").box(length, width, height)

part = part.translate((length/2, -width/2, height/2))
cq.exporters.export(part, 'Ground_Truth.stl')

show(part)
save_screenshot('00008315.png')

show(part)
save_screenshot('00008315.png')