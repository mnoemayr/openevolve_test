"""
Evaluator for simple geometry example with triangle area metric.
"""

import os
import pickle
import subprocess
import sys
import tempfile
import time
import traceback


class TimeoutError(Exception):
    pass


def validate_geometry(triangle_area):
    """
    Validate that triangle_area is a valid metric value.

    Args:
        triangle_area: Area of the polygon.

    Returns:
        True if valid, False otherwise.
    """
    if triangle_area is None:
        print("triangle_area is None")
        return False
    try:
        val = float(triangle_area)
    except (TypeError, ValueError):
        print(f"triangle_area is not a valid number: {triangle_area}")
        return False
    if val != val:  # NaN check
        print("triangle_area is NaN")
        return False
    if val <= 0:
        print(f"triangle_area must be positive, got {val}")
        return False
    if val == float("inf") or val == float("-inf"):
        print("triangle_area is infinite")
        return False
    return True


def run_with_timeout(program_path, timeout_seconds=20):
    """
    Run the program in a separate process with timeout.

    Args:
        program_path: Path to the program file
        timeout_seconds: Maximum execution time in seconds

    Returns:
        triangle_area from run_geometry()
    """
    program_path = os.path.abspath(program_path)
    program_dir = os.path.dirname(program_path)

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        script = f'''
import sys
import os
import pickle
import traceback

sys.path.insert(0, {repr(program_dir)})

try:
    spec = __import__("importlib.util").util.spec_from_file_location(
        "program", {repr(program_path)}
    )
    program = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(program)

    triangle_area = program.run_geometry()

    with open({repr(temp_file.name + ".results")}, "wb") as f:
        pickle.dump({{"triangle_area": triangle_area}}, f)

except Exception as e:
    traceback.print_exc()
    with open({repr(temp_file.name + ".results")}, "wb") as f:
        pickle.dump({{"error": str(e)}}, f)
'''
        temp_file.write(script.encode())
        temp_file_path = temp_file.name

    results_path = temp_file_path + ".results"

    try:
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=program_dir,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            exit_code = process.returncode

            print(stdout.decode())
            if stderr:
                print(stderr.decode())

            if exit_code != 0:
                raise RuntimeError(f"Process exited with code {exit_code}")

            if os.path.exists(results_path):
                with open(results_path, "rb") as f:
                    results = pickle.load(f)

                if "error" in results:
                    raise RuntimeError(f"Program execution failed: {results['error']}")

                return results["triangle_area"]
            else:
                raise RuntimeError("Results file not found")

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise TimeoutError(f"Process timed out after {timeout_seconds} seconds")

    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if os.path.exists(results_path):
            os.unlink(results_path)


def evaluate(program_path):
    """
    Evaluate the program by running it once and checking the triangle area.

    Args:
        program_path: Path to the program file

    Returns:
        Dictionary of metrics
    """
    # Max area for regular n-gon in unit circle: hexagon (n=6) with r=1 ≈ 2.598
    TARGET_VALUE = 1.29903811

    try:
        start_time = time.time()

        triangle_area = run_with_timeout(program_path, timeout_seconds=600)

        eval_time = time.time() - start_time

        if not validate_geometry(triangle_area):
            return {
                "triangle_area": 0.0,
                "target_ratio": 0.0,
                "validity": 0.0,
                "eval_time": float(eval_time),
                "combined_score": 0.0,
            }

        valid = True
        triangle_area_val = float(triangle_area)
        target_ratio = triangle_area_val / TARGET_VALUE if valid else 0.0
        validity = 1.0 if valid else 0.0
        combined_score = target_ratio * validity

        print(
            f"Evaluation: valid={valid}, triangle_area={triangle_area_val:.6f}, "
            f"target={TARGET_VALUE}, ratio={target_ratio:.6f}, time={eval_time:.2f}s"
        )

        return {
            "triangle_area": triangle_area_val,
            "target_ratio": target_ratio,
            "validity": validity,
            "eval_time": eval_time,
            "combined_score": combined_score,
        }

    except Exception as e:
        print(f"Evaluation failed completely: {str(e)}")
        traceback.print_exc()
        return {
            "triangle_area": 0.0,
            "target_ratio": 0.0,
            "validity": 0.0,
            "eval_time": 0.0,
            "combined_score": 0.0,
        }


def evaluate_stage1(program_path):
    """
    First stage evaluation - quick validation check.
    """
    try:
        try:
            triangle_area = run_with_timeout(program_path, timeout_seconds=600)

            valid = validate_geometry(triangle_area)
            triangle_area_val = float(triangle_area) if valid else 0.0

            target = 1.29903811
            combined_score = (triangle_area_val / target) if valid else 0.0

            return {
                "validity": 1.0 if valid else 0.0,
                "triangle_area": triangle_area_val,
                "target_ratio": triangle_area_val / target if valid else 0.0,
                "combined_score": combined_score,
            }

        except TimeoutError as e:
            print(f"Stage 1 evaluation timed out: {e}")
            return {"validity": 0.0, "combined_score": 0.0, "error": "Timeout"}
        except Exception as e:
            print(f"Stage 1 evaluation failed: {e}")
            print(traceback.format_exc())
            return {"validity": 0.0, "combined_score": 0.0, "error": str(e)}

    except Exception as e:
        print(f"Stage 1 evaluation failed completely: {e}")
        print(traceback.format_exc())
        return {"validity": 0.0, "combined_score": 0.0, "error": str(e)}


def evaluate_stage2(program_path):
    """
    Second stage evaluation - full evaluation.
    """
    return evaluate(program_path)
