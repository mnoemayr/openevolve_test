"""
Visualize triangle_pts.csv with matplotlib.
Plots the 3 points and the triangle they form (xy-plane, z=0).
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for saving figure
import matplotlib.pyplot as plt
import numpy as np


def main():
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / "triangle_pts.csv"

    # Load points (x, y, z)
    points = []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                points.append([float(x) for x in row])

    if not points:
        print("No data in CSV.")
        return

    pts = np.array(points)
    x, y = pts[:, 0], pts[:, 1]

    fig, ax = plt.subplots(figsize=(6, 6))

     # Unit circle (radius 1, center at origin)
    circle = plt.Circle((0, 0), 1, fill=False, color="gray", linestyle="--", linewidth=1.5, label="Unit circle")
    ax.add_patch(circle)

    # Draw triangle edges (close the loop)
    tri_x = np.append(x, x[0])
    tri_y = np.append(y, y[0])
    ax.plot(tri_x, tri_y, "b-", linewidth=2, label="Triangle")

    # Plot vertices
    ax.scatter(x, y, s=120, c="C0", edgecolors="black", linewidths=1.5, zorder=5)
    for i, (xi, yi) in enumerate(zip(x, y)):
        ax.annotate(f"  P{i}", (xi, yi), fontsize=10)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Triangle points (triangle_pts.csv)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    out_path = script_dir / "triangle_pts_plot.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path}")

    plt.show()


if __name__ == "__main__":
    main()
