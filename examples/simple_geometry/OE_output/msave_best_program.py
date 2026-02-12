# EVOLVE-BLOCK-START
"""Maximum-area equilateral triangle inscribed in unit circle"""

import math
import csv
import os


def construct_geometry():
    """
    Construct the maximum-area triangle inscribed in a unit circle.
    This is an equilateral triangle with vertices at 120° intervals.
    Area = (3√3)/4 ≈ 1.299
    """
    # Equilateral triangle vertices at 120° apart on unit circle
    triangle_pts = [(math.cos(2*math.pi*i/3), math.sin(2*math.pi*i/3), 0.0) for i in range(3)]
    triangle_edges = [(triangle_pts[i], triangle_pts[(i+1)%3]) for i in range(3)]
    # Area of equilateral triangle inscribed in unit circle: (3/2) * sin(2π/3) = 3√3/4
    triangle_area = 1.5 * math.sin(2*math.pi/3)
    
    return triangle_pts, triangle_edges, triangle_area


def run_geometry():
    """Run the geometry constructor and return triangle area for evaluation."""
    base_dir = os.path.join("examples", "simple_geometry")
    os.makedirs(base_dir, exist_ok=True)

    triangle_pts, triangle_edges, triangle_area = construct_geometry()

    with open(os.path.join(base_dir, "triangle_pts.csv"), "w", newline="") as f:
        csv.writer(f).writerows(triangle_pts)

    return triangle_area

if __name__ == "__main__":
    run_geometry()

# EVOLVE-BLOCK-END