"""
Evaluator for a simple FEA example using the PyNiteFEA library.

MN: this version is for implementing the PyNiteFEA library into the OpenEvolve loop."
"""

import importlib.util
import os
import pickle
import subprocess
import sys
import tempfile
import time
import traceback
import csv
from Pynite import FEModel3D

def _read_nodes_from_csv(program_path, filename="nodes.csv"):
    """
    Nodes are assigned IDs N1, N2, ... in file order.
    """
    program_dir = os.path.dirname(os.path.abspath(program_path))

    candidate_paths = [
        os.path.join(program_dir, filename),
        os.path.join(program_dir, "io", filename),
        os.path.join(program_dir, "input1.csv"),
        os.path.join(program_dir, "io", "input1.csv"),
    ]

    csv_path = None
    for path in candidate_paths:
        if os.path.exists(path):
            csv_path = path
            break
    if csv_path is None:
        return {}
    
    nodes = {}
    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.reader(f)
            for idx, row in enumerate[list[str]](reader, start=1):
                if not row:
                    continue
                try:
                    if len(row) >= 4:
                        node_id = str(row[0]).strip()
                        x, y, z = map(float, row[1:4])
                    else:
                        node_id = f"N{idx}"
                        x, y, z = map(float, row[:3])
                except Exception:
                    continue
                if not node_id:
                    node_id = f"N{idx}"
                nodes[node_id] = (x, y, z)
    except Exception as e:
        print(f"Failed to read nodes from CSV '{csv_path}': {e}")
        return {}
    
    print(f"Loaded {len(nodes)} nodes from CSV:{csv_path}")
    return nodes

def _write_nodes_to_csv(program_path, nodes, filename="nodes.csv"):
    """
    Write node coordinates to a CSV file next to the program.

    This mirrors the geometry being used so external tools
    (e.g. Grasshopper) can read it.
    """
    program_dir = os.path.dirname(os.path.abspath(program_path))
    csv_path = os.path.join(program_dir, filename)

    try:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            for node_id in sorted(nodes.keys()):
                x, y, z = nodes[node_id]
                writer.writerow([x, y, z])
        print(f"Wrote {len(nodes)} nodes to CSV: {csv_path}")
    except Exception as e:
        print(f"Failed to write nodes to CSV '{csv_path}': {e}")

def extract_geometry(program_path):
    """
    Load the candidate program and extract FEA geometry.

    There are two ways to provide geometry:

    1) CSV-based (preferred for GH workflows)
       - A CSV file with node coordinates is loaded if present:
         * nodes.csv
         * io/nodes.csv
         * input1.csv
         * io/input1.csv
       - Elements, supports, and loads are then generated procedurally
         from these nodes:
           * Elements connect N1-N2, N2-N3, ..., forming a chain
           * N1 is fully fixed
           * A vertical load FY is applied at the last node

    2) Program-based
       - The evolved program defines either:
           * get_fea_geometry() -> (nodes, elements, supports, loads)
             or
           * extract_geometry() -> (nodes, elements, supports, loads)
       - In this case we also mirror the nodes out to nodes.csv.

    Geometry format (for program-based path):
    - nodes: dict[node_id] = (x, y, z)
    - elements: list of dicts with at least:
        {
            "name": "M1",
            "i": "N1",
            "j": "N2",
            "material": "Steel",
            "section": "MySection",
        }
    - supports: list of dicts like:
        {"node": "N1", "DX": True, "DY": True, "DZ": True, "RX": False, "RY": False, "RZ": False}
    - loads: list of dicts like:
        {"node": "N2", "direction": "FY", "value": -10.0, "case": "D"}
    """
    program_path = os.path.abspath(program_path)
    program_dir = os.path.dirname(program_path)

    # 1) CSV-based geometry (preferred)
    nodes = _read_nodes_from_csv(program_path, filename="nodes.csv")
    if nodes:
        # Create a simple chain of members along the nodes
        node_ids = sorted(nodes.keys(), key=lambda nid: int(nid[1:]) if nid[1:].isdigit() else nid)
        elements = []
        for i in range(len(node_ids) - 1):
            i_id = node_ids[i]
            j_id = node_ids[i + 1]
            elements.append(
                {
                    "name": f"M{i+1}",
                    "i": i_id,
                    "j": j_id,
                    "material_name": "A36",
                    "section_name": "Wsect",
                }
            )
        print("elements: ",elements)

        supports = []
        if node_ids:
            # Fix the first node (cantilever root)
            supports.append( #UX = fixed, UY = fixed
                {
                    "node": node_ids[0],
                    "DX": True,
                    "DY": True,
                    "DZ": True,
                    "RX": True,
                    "RY": True,
                    "RZ": True,
                }
            )
        print("supports: ",supports)

        loads = []
        if node_ids:
            # Apply a vertical load at the last node
            loads.append(
                {
                    "node": node_ids[1],
                    "direction": "FZ",
                    "value": 5.0,
                    "case": "D",
                }
            )
        print("loads: ",loads)

        return nodes, elements, supports, loads

    # 2) Program-based geometry (fallback)
    spec = importlib.util.spec_from_file_location("candidate_program", program_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    if hasattr(module, "get_fea_geometry"):
        result = module.get_fea_geometry()
    elif hasattr(module, "extract_geometry"):
        result = module.extract_geometry()
    else:
        raise AttributeError(
            "Program must define get_fea_geometry() or extract_geometry() "
            "returning (nodes, elements, supports, loads), "
            "or provide a nodes.csv / input1.csv file."
        )

    # Allow dict-style return for convenience
    if isinstance(result, dict):
        nodes = result.get("nodes", {})
        elements = result.get("elements", [])
        supports = result.get("supports", [])
        loads = result.get("loads", [])
    else:
        # Tuple / list style return
        if len(result) == 2:
            nodes, elements = result
            supports, loads = [], []
        elif len(result) == 4:
            nodes, elements, supports, loads = result
        else:
            raise ValueError(
                "Geometry function must return (nodes, elements) or "
                "(nodes, elements, supports, loads)."
            )

    # Mirror nodes out to CSV so external tools can use them
    if nodes:
        _write_nodes_to_csv(program_path, nodes, filename="nodes.csv")

    return nodes, elements, supports, loads

def build_pynite_model(nodes, elements, supports=None, loads=None):
    """
    Build a PyNite FEModel3D instance from the provided geometry.
    """
    model = FEModel3D()

    # Add nodes
    for node_id, coords in nodes.items():
        x, y, z = coords
        model.add_node(str(node_id), float(x), float(y), float(z))

    # Define default material/section if user did not already
    # (Users can choose to call add_material/add_section in their geometry function instead.)
    if hasattr(model, "add_material"):
        # Simple generic material
        model.add_material("A36", E=29_000_000.0, G=11_200_000.0, nu=0.3, rho=0.283)

    if hasattr(model, "add_section"):
        # Match FEA_tut: W-section properties
        model.add_section("Wsect", A=10.0, Iy=100.0, Iz=200.0, J=5.0)

    # Add elements (members)
    for elem in elements:
        name = str(elem.get("name"))
        i_node = str(elem.get("i"))
        j_node = str(elem.get("j"))
        material = str(elem.get("material_name", "A36")) #material_name or material
        section = str(elem.get("section_name", "Wsect")) #section_name or section
        model.add_member(name, i_node, j_node, material, section)

    # Supports
    supports = supports or []
    for sup in supports:
        node = str(sup.get("node"))
        if not node:
            continue
        dx = bool(sup.get("DX", False))
        dy = bool(sup.get("DY", False))
        dz = bool(sup.get("DZ", False))
        rx = bool(sup.get("RX", False))
        ry = bool(sup.get("RY", False))
        rz = bool(sup.get("RZ", False))
        model.def_support(node, dx, dy, dz, rx, ry, rz)

    # Nodal loads (simple case)
    loads = loads or []
    for load in loads:
        node = str(load.get("node"))
        direction = str(load.get("direction", "FZ"))
        value = float(load.get("value", 0.0))
        case = str(load.get("case", "D"))
        if not node:
            continue
        if hasattr(model, "add_node_load"):
            model.add_node_load(node, direction, value, case)

    # Match FEA_tut: define a basic load combination using case 'D'
    if hasattr(model, "add_load_combo"):
        try:
            model.add_load_combo("1.0D", {"D": 1.0})
        except TypeError:
            # Fallback for older signatures
            pass

    return model

def evaluate(program_path):
    """
    Evaluate a candidate program by:
    1. Extracting geometry.
    2. Building a PyNite model.
    3. Running an FEA analysis.
    4. Computing a fitness based on maximum nodal displacement.

    Fitness convention:
    - fitness = -max_displacement
    - Higher fitness is better (smaller displacement -> less negative).
    """
    start_time = time.time()

    try:
        nodes, elements, supports, loads = extract_geometry(program_path)
        model = build_pynite_model(nodes, elements, supports, loads)

        # Run the analysis
        # Prefer the FEA_tut-style linear analysis if available
        if hasattr(model, "analyze_linear"):
            try:
                model.analyze_linear(log=False)
            except TypeError:
                model.analyze_linear()
        else:
            model.analyze()

        # Collect maximum absolute displacement over all nodes and load combos
        max_disp = 0.0
        try:
            for node in model.nodes.values():
                # PyNite stores displacements per load combo in dicts like node.DX, node.DY, node.DZ
                for attr_name in ("DX", "DY", "DZ"):
                    disp_attr = getattr(node, attr_name, None)
                    if isinstance(disp_attr, dict):
                        for val in disp_attr.values():
                            try:
                                mag = abs(float(val))
                                if mag > max_disp:
                                    max_disp = mag
                            except Exception:
                                continue
        except Exception as disp_err:
            print(f"Warning: failed to extract displacements cleanly: {disp_err}")

        fitness = -float(max_disp)
        eval_time = time.time() - start_time

        print(
            f"FEA evaluation: max_disp={max_disp:.6e}, fitness={fitness:.6e}, "
            f"time={eval_time:.2f}s"
        )

        return {
            "max_displacement": float(max_disp),
            "fitness": float(fitness),
            "validity": 1.0,
            "eval_time": float(eval_time),
            "combined_score": float(fitness),
        }

    except Exception as e:
        print(f"FEA evaluation failed completely: {e}")
        traceback.print_exc()
        return {
            "max_displacement": 0.0,
            "fitness": -1e9,  # very poor score
            "validity": 0.0,
            "eval_time": 0.0,
            "combined_score": -1e9,
            "error": str(e),
        }

def evaluate_stage1(program_path):
    """
    First stage evaluation - quick validation check.
    """
    return evaluate(program_path)


def evaluate_stage2(program_path):
    """
    Second stage evaluation - full evaluation.
    """
    return evaluate(program_path)

if __name__ == "__main__":
    #MN: point to the same directory
    this_dir = os.path.dirname(os.path.abspath(__file__))
    program_path = os.path.join(this_dir, "initial_program.py") 

    results = evaluate(program_path)
    print("Final evaluation results:", results)