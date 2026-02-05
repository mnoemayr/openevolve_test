# EVOLVE-BLOCK-START
import numpy as np
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math

#to be exported
support_pts = []
elem_lines = []

#cirlce divid into three and define height
base = 3.0
num_polygon = 3
height = 5.0

# export three pts
for i in range (num_polygon):
    angle = 2 * math.pi * i / num_polygon
    x = base * math.cos(angle)
    y = base * math.sin(angle)
    z = 0.0
    
    support_pts.append(rg.Point3d(x, y, z))

# connect base points to point height and
top_pt = rg.Point3d(0,0,height)

for j in range (num_polygon):
    edge = rg.Line(support_pts[j], top_pt)
    
    elem_lines.append(edge)
    
for k in range (num_polygon):
    p1 = support_pts[k]
    p2 = support_pts[(k+1)%num_polygon]
    print(k+1)%num_polygon
    triangle_edge = rg.Line(p1, p2)
    elem_lines.append(triangle_edge)

# export all lines


# EVOLVE-BLOCK-END
