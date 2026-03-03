import math
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "input.csv")

# EVOLVE-BLOCK-START
"""Initial program for a triangle inside a unit circle (FEA variant)."""


def construct_geometry(
    polygon_radius: float = 0.8,
    num_polygon: int = 3,
):
    """
    Construct a regular polygon inscribed in a unit circle (radius 1).
    polygon_radius for the polygon must be <= 1.

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


# EVOLVE-BLOCK-END


def run_geometry():
    """
    Run the geometry constructor, write CSV and return triangle_area.

    CSV format (new):
        N1,x,y,z
        N2,x,y,z
        ...
    """
    os.makedirs(BASE_DIR, exist_ok=True)
    output_path = INPUT_PATH

    triangle_pts, triangle_edges, triangle_area = construct_geometry()

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        for idx, (x, y, z) in enumerate(triangle_pts, start=1):
            node_id = f"N{idx}"
            writer.writerow([node_id, x, y, z])

    print(f"csv written to {output_path}")
    print("ABS PATH:", os.path.abspath(output_path))
    print("EXISTS:", os.path.exists(output_path))
    print("SIZE:", os.path.getsize(output_path) if os.path.exists(output_path) else 0)

    return triangle_area


if __name__ == "__main__":
    run_geometry()
