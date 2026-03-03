"""
Evaluator for simple geometry example with triangle area metric.

MN: this version also supports reading an externally-computed fitness value from a CSV file (e.g. written by Grasshopper) located next to the program.
"""

import os
import pickle
import subprocess
import sys
import tempfile
import time
import traceback
import csv

class TimeoutError(Exception):
    pass

#MN: this is the CSV external fitness reader
def wait_for_external_fitness(
    program_path,
    fitness_filename: str = "fitness.csv",
    timeout_seconds: int = 30,
    poll_interval: float = 0.5,
):
    """
    Wait for an external process (e.g. Grasshopper) to write a fitness CSV.

    The CSV is expected to live in the same directory as the program file and
    contain the primary fitness value in the first cell of the first row.

    Returns:
        float fitness value if the file is found and parsed, or None if timeout/parse failure.
    """
    program_dir = os.path.dirname(os.path.abspath(program_path))
    fitness_path = os.path.join(program_dir, fitness_filename)

    start = time.time()
    while not os.path.exists(fitness_path):
        if time.time() - start > timeout_seconds:
            print(f"Timed out waiting for external fitness file: {fitness_path}")
            return None
        time.sleep(poll_interval)

    try:
        with open(fitness_path, "r", newline="") as f:
            reader = csv.reader(f)
            first_row = next(reader, None)

        if not first_row:
            print(f"Fitness file {fitness_path} is empty")
            return None

        fitness_str = first_row[0]
        fitness_val = float(fitness_str)
        return fitness_val
    except Exception as e:
        print(f"Failed to read external fitness from {fitness_path}: {e}")
        return None


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

        #MN Optional: wait for the external fitness value (e.g. from Grasshopper)

        # Fake Grasshopper computation here:
        # ------------------------------------------------------------
        # Fake "Grasshopper" computation: write a fitness.csv file
        # next to the program, then use the existing waiting mechanism
        # to read it back in.
        # ------------------------------------------------------------
        # Compute fitness_value somehow
        fitness_value = float(triangle_area) if triangle_area is not None else 0.0

        # Fake GH writes fitness.csv
        program_dir = os.path.dirname(os.path.abspath(program_path))
        fitness_path = os.path.join(program_dir, "fitness.csv")

        with open(fitness_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([fitness_value])

        print("Fake GH wrote fitness to:", fitness_path)

        # Now use your waiting mechanism

        external_fitness = wait_for_external_fitness(
            program_path,
            fitness_filename="fitness.csv", #MN: this is next to the file and not in the IO folder
            timeout_seconds=30,
            poll_interval=0.5,
        )

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

        #MN: if an external fitness value is available (eg. from Grasshopper),
        # use this as the main optimization target.
        # otherwise, fall back to the internal triangle-area-based score.
        if external_fitness is not None:
            combined_score = float(external_fitness)
        else:
            combined_score = target_ratio * validity

        #combined_score = target_ratio * validity

        print(
            f"Evaluation: valid={valid}, triangle_area={triangle_area_val:.6f}, "
            #f"target={TARGET_VALUE}, ratio={target_ratio:.6f}, time={eval_time:.2f}s"
            f"target={TARGET_VALUE}, ratio={target_ratio:.6f}, " #MN new
            f"external_fitness={external_fitness}, eval_time={eval_time:.2f}s" #MN new
        )

        return {
            "triangle_area": triangle_area_val,
            "target_ratio": target_ratio,
            "validity": validity,
            "external_fitness": float(external_fitness) if external_fitness is not None else 0.0, #MN new
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

if __name__ == "__main__":
    #MN: point to the same directory
    this_dir = os.path.dirname(os.path.abspath(__file__))
    program_path = os.path.join(this_dir, "initial_program.py") 

    results = evaluate(program_path)
    print("Final evaluation results:", results)