# RC-Pinching-OpenSeesPy

OpenSeesPy modeling of RC hysteretic behavior with pinching — experimental data processing, nonlinear analysis, and experimental–numerical comparison.

## Workflow
1. `data/experimental.csv` — experimental force–displacement history.
2. `models/model.py` — zeroLength + Hysteretic spring model.
3. `results/opensees_response.csv` — OpenSeesPy response generated from the project model.
4. `compare.py` — overlay and four validation metrics.
5. `results/experimental_vs_opensees.png` and `results/metrics.csv` — final validation outputs.

## Units
Force: kN. Displacement: mm. Stiffness: kN/mm.
