"""
model.py
--------

Units:
    force       = kN
    displacement = mm
    stiffness   = kN/mm

Input:
    data/experimental.csv

The CSV should contain at least two columns:
    displacement_mm, force_kN

"""

from pathlib import Path
import csv
import numpy as np
import openseespy.opensees as ops


# ============================================================
# 1. Paths
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "experimental.csv"
RESULT_FILE = ROOT / "results" / "opensees_response.csv"


# ============================================================
# 2. Experimental displacement protocol
# ============================================================

def read_experimental_protocol(path):
    displacement = []

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # Accept the project's standard column name.
        for row in reader:
            displacement.append(float(row["displacement_mm"]))

    return np.asarray(displacement, dtype=float)


# ============================================================
# 3. OpenSees model
# ============================================================

def build_model():
    ops.wipe()
    ops.model("basic", "-ndm", 1, "-ndf", 1)

    # Node 1 = fixed reference
    # Node 2 = moving point
    ops.node(1, 0.0)
    ops.node(2, 0.0)

    ops.fix(1, 1)

    # --------------------------------------------------------
    # Hysteretic material
    #
    # The points below are a compact approximation of the
    # experimental backbone extracted from the supplied data.
    #
    # Positive backbone:
    #   (2.03 mm,  78.52 kN)
    #   (6.77 mm, 178.58 kN)
    #   (27.55 mm, 302.52 kN)
    #
    # Negative backbone:
    #   (-1.94 mm, -97.11 kN)
    #   (-7.01 mm, -192.80 kN)
    #   (-27.93 mm, -314.75 kN)
    #
    # pinchX / pinchY control the degree of pinching.
    # damage1 / damage2 control cyclic degradation.
    # --------------------------------------------------------

    mat_tag = 1

    ops.uniaxialMaterial(
        "Hysteretic",
        mat_tag,

        # Positive envelope
        78.52,  2.03,
        178.58, 6.77,
        302.52, 27.55,

        # Negative envelope
        -97.11,  -1.94,
        -192.80, -7.01,
        -314.75, -27.93,

        # Pinching
        0.45,     # pinchX
        0.35,     # pinchY

        # Cyclic damage
        0.0,      # damage1
        0.0,      # damage2

        # Exponent
        0.0
    )

    # Zero-length spring between the two nodes
    ops.element(
        "zeroLength",
        1,
        1,
        2,
        "-mat", mat_tag,
        "-dir", 1
    )


# ============================================================
# 4. Run displacement-controlled analysis
# ============================================================

def run_analysis(target_displacements):

    build_model()

    # Dummy load pattern used by DisplacementControl.
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)

    # Unit reference load.
    ops.load(2, 1.0)

    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-8, 50)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.0)
    ops.analysis("Static")

    # Initial displacement
    current = float(target_displacements[0])

    # Set the first displacement directly with displacement control.
    ops.integrator("DisplacementControl", 2, 1, current)
    ok = ops.analyze(1)

    if ok != 0:
        raise RuntimeError(
            f"OpenSees failed at initial displacement {current:.6g} mm."
        )

    results = [(current, ops.eleForce(1)[0])]

    # Follow the exact experimental displacement history.
    for target in target_displacements[1:]:

        target = float(target)
        current = float(ops.nodeDisp(2, 1))
        increment = target - current

        if abs(increment) < 1.0e-12:
            results.append((target, ops.eleForce(1)[0]))
            continue

        # Divide large jumps into smaller increments.
        max_step = 0.10  # mm
        n_steps = max(1, int(np.ceil(abs(increment) / max_step)))
        step = increment / n_steps

        ops.integrator(
            "DisplacementControl",
            2,
            1,
            step
        )

        for _ in range(n_steps):

            ok = ops.analyze(1)

            if ok != 0:
                # One simple fallback: modified Newton.
                ops.algorithm("ModifiedNewton")
                ok = ops.analyze(1)
                ops.algorithm("Newton")

            if ok != 0:
                raise RuntimeError(
                    "OpenSees analysis failed at "
                    f"target displacement {target:.6g} mm."
                )

         # Save only the response corresponding to the
         # original experimental displacement point.
        results.append(
            (
                target,
                float(ops.eleForce(1)[0])
            )
        )

    ops.wipe()

    return np.asarray(results)


# ============================================================
# 5. Save results
# ============================================================

def save_results(results, path):

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "displacement_mm",
            "force_kN"
        ])

        writer.writerows(results)


# ============================================================
# 6. Main
# ============================================================

if __name__ == "__main__":

    protocol = read_experimental_protocol(DATA_FILE)

    if len(protocol) < 2:
        raise ValueError(
            "Experimental displacement protocol contains fewer "
            "than two points."
        )

    response = run_analysis(protocol)

    save_results(response, RESULT_FILE)

    print("OpenSees analysis completed.")
    print(f"Input : {DATA_FILE}")
    print(f"Output: {RESULT_FILE}")
    print(f"Points: {len(response)}")
