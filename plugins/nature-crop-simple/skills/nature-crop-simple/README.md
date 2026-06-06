# nature-crop-simple

A Nature-standard skill for the **SIMPLE** (Soil-Plant-Atmosphere Interactions for Model Evaluation and Learning) crop model — a process-based Python crop simulation model.

## What it does

This skill provides a structured, reproducible workflow for running, calibrating, analysing, and visualising the SIMPLE crop model. It handles:

- **Model execution** — run single or batch simulations for wheat, maize, rice, soybean, and other crops
- **Parameter calibration** — GLUE-based or manual calibration to observed yield/biomass/phenology data
- **Sensitivity analysis** — one-at-a-time parameter perturbation and sensitivity ranking
- **Stress diagnosis** — interpret temperature, heat, and water stress factors from simulation outputs
- **Multi-treatment comparison** — statistical and visual comparison across experiments, CO₂ levels, irrigation regimes
- **Code modification** — guided modifications to the core simulation engine with before/after testing

## Repository

The SIMPLE model itself lives at: `https://github.com/YuanyuanMa03/a-simple-crop-model`

## Trigger keywords

Use proactively when the user asks:

- "Run the SIMPLE crop model"
- "Calibrate the crop model parameters"
- "Analyse this simulation output"
- "Modify the crop model code"
- "Compare treatments in the SIMPLE model"
- "Visualise yield or biomass results"

## Reference files

```
nature-crop-simple/
├── SKILL.md           # Full workflow, rules, function reference, templates
├── README.md          # This file
└── references/
    ├── api.md         # Complete function signatures and return types
    ├── params.md      # Parameter tables with ranges and units
    └── workflows.md   # Step-by-step workflow scripts
```

## Status: Draft

This skill is newly created. It has been designed based on the existing SIMPLE crop model Python codebase. Validation on real calibration and sensitivity tasks is ongoing.
