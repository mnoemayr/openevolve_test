# EVOLVE-BLOCK-START
"""Initial program for simple pyramid pavilion structure with base inside unit circle"""

import math
import csv
import os


def construct_pavilion(
    base_radius: float = 0.8,
    num_polygon: int = 3,
    height: float = 5.0,
):
    """
    Construct a pyramid pavilion whose base is a regular polygon inscribed
    in a unit circle (radius 1). base_radius must be <= 1.

    Returns:
        support_pts: List of (x, y, z) base vertices and apex.
        elem_lines: List of line elements (start, end).
        base_area: Area of the pyramid's base polygon.
    """
    if base_radius > 1.0:
        base_radius = 1.0  # Clamp to unit circle

    support_pts = []
    for i in range(num_polygon):
        angle = 2 * math.pi * i / num_polygon
        coord_x = base_radius * math.cos(angle)
        coord_y = base_radius * math.sin(angle)
        support_pts.append((coord_x, coord_y, 0.0))

    apex = (0.0, 0.0, height)
    elem_lines = []
    for j in range(num_polygon):
        next_j = (j + 1) % num_polygon
        elem_lines.append((support_pts[j], support_pts[next_j]))
        elem_lines.append((support_pts[j], apex))
        elem_lines.append((support_pts[next_j], apex))

    # Area of regular n-gon inscribed in circle of radius r: (n/2) * r^2 * sin(2*pi/n)
    base_area = (num_polygon / 2) * base_radius**2 * math.sin(2 * math.pi / num_polygon)

    return support_pts, elem_lines, base_area


def run_pavilion():
    """Run the pavilion constructor and return base area for evaluation."""
    base_dir = os.path.join("examples", "simple_pavilion")
    os.makedirs(base_dir, exist_ok=True)

    support_pts, elem_lines, base_area = construct_pavilion()

    path = os.path.join(base_dir, "support_points.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(support_pts)

    return base_area


# EVOLVE-BLOCK-END
