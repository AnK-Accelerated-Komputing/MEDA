from ocp_vscode import show, save_screenshot
import cadquery as cq
from ocp_vscode import show, save_screenshot
length:float = 0.0625
width:float = 0.75
height:float = 0.0034

rectangle:cq.Workplane = cq.Workplane("XY").box(length, width, height)

part:cq.Workplane = (
    cq.Workplane("XY")
    .union(rectangle.translate((-length/2+height/2,0,0)))
    .union(rectangle.translate((-length/2+height/2,0,0)).rotate((0,1,0),(0,0,0),90))
)

part = part.translate((-height/2, -width/2, -height/2)).rotate((0, 0, 1),(0, 0, 0), -90)
cq.exporters.export(part, 'Ground_Truth.stl')
show(part)
save_screenshot('002221.png')

show(part)
save_screenshot('00002221.png')