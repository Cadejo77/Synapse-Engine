# Synapse Engine (ComfyUI custom nodes)

Synapse Engine is a YAML-driven prompt generation toolkit for ComfyUI.

It provides:
- **Procedural prompt generation** with weighted choices and conditional routing.
- **Metadata tag routing** using `meta:*` tags.
- **Prompt cleanup/conflict resolution** to remove common contradictions.
- **Structured section outputs** (subject / scene / composition).
- **Region-plan JSON** for regional prompting workflows.

## What nodes are included

From this package, ComfyUI exposes the following nodes:

- **Procedural Prompt Graph (YAML)**
- **Procedural Prompt Graph v2 (scenarios + sections)**
- **PPG Conflict Resolver**
- **PPG Prompt Sections (from JSON)**
- **PPG Region Plan Builder**

## Installation

1. Clone into your ComfyUI custom nodes folder:

```bash
git clone https://github.com/Cadejo77/Synapse-Engine.git /path/to/ComfyUI/custom_nodes/Synapse-Engine
```

2. Install requirements in your ComfyUI Python environment:

```bash
pip install -r /path/to/ComfyUI/custom_nodes/Synapse-Engine/requirements.txt
```

3. Restart ComfyUI.

---

## Core concept: YAML token expansion

Prompts are assembled by expanding `__tokens__` from YAML modules inside `presets/<preset_name>/`.

A token can be:
- A key in the current module.
- A unique key from another module.
- A module-stem token.
- A path-style token like `__fantasy/subject/class_fantasy__`.

Expansion supports three line modes inside YAML lists:

1. **Weighted choice**
   - `50, cinematic rim light`
2. **Router (first match wins)**
   - `/meta:genre:fantasy/= ornate runic armor`
3. **Sequential append**
   - Plain lines are appended in order when conditions match.

Conditions are attached as one or more `/.../` guards and must all match active tags.

---

## Node usage guide

## 1) Procedural Prompt Graph (YAML)

**Best for:** lightweight generation with optional debug trace.

### Inputs
- `preset_folder`: subfolder in `presets/`.
- `entry_file`: top-level YAML entry point (usually `0_master_generator.yaml`).
- `entry_key`: usually `template`.
- `seed`: deterministic random seed.
- `sep_text`: replacement for `[SEP]` markers.
- `strip_meta_tags`: remove `meta:*` tags from final prompt text.
- `debug`: include expansion trace and active meta tags.

### Outputs
- `positive_prompt`
- `debug_report`

### Typical setup
1. Add **Procedural Prompt Graph (YAML)**.
2. Set `preset_folder=default`, `entry_file=0_master_generator.yaml`, `entry_key=template`.
3. Connect `positive_prompt` to your CLIP text encoder.
4. Enable `debug` when tuning YAML logic.

---

## 2) Procedural Prompt Graph v2 (scenarios + sections)

**Best for:** production workflows where you need structured outputs and optional cleanup.

### Inputs
- `preset_folder`
- `scenario`: lock specific traits from `validator.yaml` (`<none>` disables locks).
- `seed`
- `separator_mode`: `double_newline`, `newline`, `comma`, or `custom`.
- `sep_text`: custom separator text.
- `strip_meta_tags`
- `apply_conflict_resolver`: remove common contradictions.
- `html_unescape`: decode HTML entities.
- `debug`
- Optional: `entry_file`, `entry_key`.

### Outputs
- `positive_prompt`
- `subject_prompt`
- `scene_prompt`
- `composition_prompt`
- `ppg_json` (full structured payload)
- `debug_report`
- `cleanup_report`

### Why use v2
- Lets you feed subject/scene/composition into separate downstream branches.
- Preserves machine-readable state in `ppg_json` for toolchains.
- Reduces prompt conflicts automatically.

---

## 3) PPG Conflict Resolver

**Best for:** cleaning prompts from external sources or user-edited text.

### Inputs
- `prompt`
- `html_unescape`

### Outputs
- `clean_prompt`
- `cleanup_report`

### What it cleans
- Duplicate tokens.
- Lens/DOF one-of conflicts.
- Day/night collisions.
- Unarmed wording when weapon terms exist.

---

## 4) PPG Prompt Sections (from JSON)

**Best for:** splitting `ppg_json` back into text channels.

### Input
- `ppg_json`

### Outputs
- `positive_prompt`
- `subject_prompt`
- `scene_prompt`
- `composition_prompt`
- `meta_json`

Use this when you store JSON in one stage but need explicit strings later.

---

## 5) PPG Region Plan Builder

**Best for:** creating region-control payloads from generated sections.

### Inputs
- `subject_prompt`
- `scene_prompt`
- `composition_prompt`
- `layout_mode`: `single`, `two_shot_left_right`, `foreground_mid_background`, `rule_of_thirds`
- `global_weight`
- `subject_weight`

### Outputs
- `region_plan_json`
- `debug_report`

The resulting JSON can be mapped to region-aware nodes or custom scripts.

---

## Recommended workflow patterns

### A) Fast single prompt
`Procedural Prompt Graph (YAML) -> CLIP Text Encode`

Use when you only need one final positive prompt quickly.

### B) Structured prompt pipeline
`Procedural Prompt Graph v2 -> (optional) PPG Prompt Sections -> encoders`

Use when you want separated prompt channels and reproducible metadata.

### C) Cleanup gateway for mixed sources
`Manual/User Prompt + Generated Prompt -> PPG Conflict Resolver -> CLIP`

Use when combining text from multiple tools.

### D) Regional prompting workflow
`Procedural Prompt Graph v2 -> PPG Region Plan Builder -> region-aware downstream node`

Use when different image areas need distinct emphasis.

---

## Practical use cases

- **Concept art ideation:** rapidly produce varied compositions with deterministic seeds.
- **Batch generation:** fixed scenario + seed sequences for controlled exploration.
- **Style system authoring:** encode art-direction rules in YAML, not Python code.
- **Prompt QA pipelines:** run resolver to normalize prompts before rendering.
- **Regional composition studies:** derive foreground/background plans automatically.
- **Template libraries for teams:** share presets and scenario locks as reusable assets.

---

## Tips for best results

- Keep `strip_meta_tags=True` in normal generation, but disable it when debugging logic.
- Use scenario locks for consistent benchmark runs.
- For readability, use `separator_mode=double_newline` in v2.
- Keep YAML modules focused (one domain per file) to reduce token ambiguity.
- Prefer path tokens when similarly named keys exist across modules.

---

## Quick CLI smoke test

From the repository root:

```bash
python test_generate.py --preset_dir presets/default --entry 0_master_generator.yaml --key template --seed 1234 --debug
```

If that works, YAML loading + expansion is generally healthy.
