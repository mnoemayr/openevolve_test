# EVOLVE-BLOCK-START
"""Maximum-area triangle inscribed in unit circle: equilateral with R=1"""

import math
import csv
import os


def construct_geometry():
    """
    Construct the maximum-area triangle inscribed in a unit circle.
    This is an equilateral triangle with vertices at 120° intervals.
    Area = (3*sqrt(3)/4) * R^2 = 3*sqrt(3)/4 for R=1.
    """
    # Equilateral triangle: vertices at 0°, 120°, 240° on unit circle
    angles = [2 * math.pi * i / 3 for i in range(3)]
    triangle_pts = [(math.cos(a), math.sin(a), 0.0) for a in angles]
    
    triangle_edges = [(triangle_pts[i], triangle_pts[(i + 1) % 3]) for i in range(3)]
    
    # Exact area: (3/2) * 1^2 * sin(2*pi/3) = (3/2) * (sqrt(3)/2) = 3*sqrt(3)/4
    triangle_area = 1.5 * math.sin(2 * math.pi / 3)
    
    return triangle_pts, triangle_edges, triangle_area


def run_geometry():
    """Run the geometry constructor and return triangle area for evaluation."""
    base_dir = os.path.join("examples", "simple_geometry")
    os.makedirs(base_dir, exist_ok=True)

    triangle_pts, triangle_edges, triangle_area = construct_geometry()

    path = os.path.join(base_dir, "triangle_pts.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(triangle_pts)

    return triangle_area


# EVOLVE-BLOCK-END