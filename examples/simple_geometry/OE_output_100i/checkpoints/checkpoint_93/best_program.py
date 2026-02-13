# EVOLVE-BLOCK-START
"""Optimal equilateral triangle in unit circle."""

import math, csv, os

def construct_geometry():
    """Maximum-area triangle: vertices at 120° intervals."""
    a = 2.0943951023931953  # 2π/3
    pts = [(math.cos(i*a), math.sin(i*a), 0.0) for i in range(3)]
    return pts, [(pts[i], pts[(i+1)%3]) for i in range(3)], 1.2990381056766582

def run_geometry():
    """Save vertices and return area."""
    d = os.path.join("examples", "simple_geometry")
    os.makedirs(d, exist_ok=True)
    pts, _, area = construct_geometry()
    with open(os.path.join(d, "triangle_pts.csv"), "w", newline="") as f:
        csv.writer(f).writerows(pts)
    return area

# EVOLVE-BLOCK-END