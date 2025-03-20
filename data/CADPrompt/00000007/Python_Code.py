from ocp_vscode import show, save_screenshot
from ocp_vscode import show, save_screenshot
import cadquery as cq

radius:float = 1.5/2
height:float = 0.20923

sketch:cq.Sketch = cq.Sketch().circle(radius)
part:cq.Workplane = cq.Workplane("XY").placeSketch(sketch).extrude(height)
cq.exporters.export(part, 'Ground_Truth.stl')

show(part)
save_screenshot('00000007.png')

show(part)
save_screenshot('00000007.png')