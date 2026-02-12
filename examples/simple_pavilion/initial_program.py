# EVOLVE-BLOCK-START
"""Initial program for a triangle inside a unit cirle"""

import math
import csv
import os


def construct_geometry(
    polygon_radius: float = 0.8,
    num_polygon: int = 3,
):
    
    if polygon_radius > 1.0:
        polygon_radius = 1.0  # Clamp to unit circle

    triangle_pts = []
    for i in range(num_polygon):
        angle = 2 * math.pi * i / num_polygon
        coord_x = polygon_radius * math.cos(angle)
        coord_y = polygon_radius * math.sin(angle)
        triangle_pts.append((coord_x, coord_y, 0.0))

    triangle_edges = []
    for j in range(num_polygon):
        next_j = (j + 1) % num_polygon
        triangle_edges.append((triangle_pts[j], triangle_pts[next_j]))

    # Area of regular n-gon inscribed in circle of radius r: (n/2) * r^2 * sin(2*pi/n)
    triangle_area = (num_polygon / 2) * polygon_radius**2 * math.sin(2 * math.pi / num_polygon)

    return triangle_pts, triangle_edges, triangle_area


def run_geometry():
    
    base_dir = os.path.join("examples", "simple_geometry")
    os.makedirs(base_dir, exist_ok=True)

    triangle_pts, triangle_edges, triangle_area = construct_geometry()

    path = os.path.join(base_dir, "triangle_pts.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(triangle_pts)

    return triangle_area


# EVOLVE-BLOCK-END
