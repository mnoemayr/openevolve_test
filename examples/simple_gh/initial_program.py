# EVOLVE-BLOCK-START
"""Initial program for a triangle inside a unit cirle"""

import math
import csv
import os
import time


def construct_geometry(
    polygon_radius: float = 0.8,
    num_polygon: int = 3,
):
    """
    Construct a regular polygon inscribed
    in a unit circle (radius 1). polygon_radius for the polygon must be <= 1.

    Returns:
        triangle_pts: List of (x, y, z) triangle vertices.
        triangle_edges: List of triangle edges (start, end).
        triangle_area: Area of the triangle.
    """
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
    """Run the geometry constructor, write CSV and return (trianle_pts, triangle_edges, triangle_area)."""
    base_dir = os.path.dirname(os.path.abspath(__file__)) #MN: abspath
    os.makedirs(base_dir, exist_ok=True)

    triangle_pts, triangle_edges, triangle_area = construct_geometry()

    path = os.path.join(base_dir, "triangle_pts.csv") 
    #path = os.path.join(base_dir, f"triangle_pts_{time.time():.0f}.csv") #MN: path + identifier
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(triangle_pts)
    print(f"csv written to {base_dir}")

    return triangle_area# triangle_edges, triangle_pts

# EVOLVE-BLOCK-END

if __name__ == "__main__":
    run_geometry()
        