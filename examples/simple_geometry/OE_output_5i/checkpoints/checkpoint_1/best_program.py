# EVOLVE-BLOCK-START
"""Maximum-area triangle inscribed in a unit circle - equilateral with 120° spacing"""

import math

def construct_geometry():
    """
    Construct the maximum-area equilateral triangle inscribed in unit circle.
    Vertices at 120° intervals (2π/3 radians) on radius 1.
    Area = (3√3)/4 ≈ 1.299
    """
    # Equilateral triangle: 3 vertices at 120° apart on unit circle
    angles = [2 * math.pi * i / 3 for i in range(3)]
    triangle_pts = [(math.cos(a), math.sin(a), 0.0) for a in angles]
    triangle_edges = [(triangle_pts[i], triangle_pts[(i+1) % 3]) for i in range(3)]
    triangle_area = 1.5 * math.sin(2 * math.pi / 3)  # (3/2) * sin(120°)
    
    return triangle_pts, triangle_edges, triangle_area


def run_geometry():
    """Run the geometry constructor and return triangle area for evaluation."""
    _, _, triangle_area = construct_geometry()
    return triangle_area

# EVOLVE-BLOCK-END

if __name__ == "__main__":
    import csv
    import os
    triangle_pts, triangle_edges, triangle_area = construct_geometry()
    print(triangle_pts)
    base_dir = os.path.join("examples", "simple_geometry")
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, "triangle_pts.csv")
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(triangle_pts)