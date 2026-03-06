import math
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "input1.csv")

# EVOLVE-BLOCK-START
"""
Initial program for a cantilver beam with two nodes.

Only one degree of freedom for OpenEvolve:
the x-coordinate of the second node (N2), and with this the beam's span length.
"""

SECOND_NODE_X = 300.0  # Initial x-coordinate of the second node (N2)

def construct_geometry():
    """
    Construct a two-node cantilever:
    - N1 at (0.0, 0.0, 0.0)
    - N2 at (SECOND_NODE_X, 0.0, 0.0)

    Returns:
        pts: List of (x, y, z) node coordinates.
        edges: List of member edges (start, end) for convenience.
        span_length: The cantilever span, used as a scalar metric.
    """

    n1 = (0.0, 0.0, 0.0)
    n2 = (float(SECOND_NODE_X), 0.0, 0.0)

    pts = [n1, n2]
    edges = [(n1, n2)]
    span_length = abs(n2[0] - n1[0])

    return pts, edges, span_length


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
