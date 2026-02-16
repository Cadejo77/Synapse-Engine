# Synapse Engine (ComfyUI Custom Nodes)

Synapse Engine is a prompt-generation and composition-control pack for ComfyUI. It provides structured prompt construction, region-aware conditioning, optional palette steering, and optional LoRA mixing.

## Included nodes

1. **Procedural Prompt Graph v2 (Synapse)**
   - Generates structured prompt sections:
     - `subject_prompt`
     - `scene_prompt`
     - `composition_prompt`
     - `negative_prompt`

2. **Synapse Region Conditioning**
   - Converts prompt sections into spatial conditioning (subject/background regions).
   - Outputs:
     - `positive_conditioning`
     - `negative_conditioning`
     - `region_plan_json`
     - `debug_report`

3. **Synapse Region Preview** *(optional)*
   - Draws a visual overlay from `region_plan_json` for debugging composition boxes.

4. **Synapse Color Palette Driver** *(optional)*
   - Adds deterministic, seed-driven palette/harmony conditioning with separate strength control.

5. **Synapse LoRA Style Mixer** *(optional)*
   - Loads and applies up to 6 LoRAs.
   - Supports optional normalization and optional jitter for variation.

---

## Installation

1. Copy this folder into:
   - `ComfyUI/custom_nodes/Synapse-Engine/`
2. Restart ComfyUI.
3. Search for nodes containing **Synapse**.

---

## Recommended graph wiring

### Base flow

- **Checkpoint Loader**
  - `CLIP` → **Procedural Prompt Graph v2 (Synapse)** and **Synapse Region Conditioning**
  - `MODEL` → `KSampler`
  - `VAE` → `VAE Decode`

- **Procedural Prompt Graph v2 (Synapse)**
  - `subject_prompt` → **Synapse Region Conditioning**
  - `scene_prompt` → **Synapse Region Conditioning**
  - `composition_prompt` → **Synapse Region Conditioning**
  - `negative_prompt` → **Synapse Region Conditioning**

- **Synapse Region Conditioning**
  - `positive_conditioning` → `KSampler` positive
  - `negative_conditioning` → `KSampler` negative
  - *(optional)* `region_plan_json` → **Synapse Region Preview**

- `KSampler` → `VAE Decode` → `Save Image`

### Optional additions

- **Synapse Color Palette Driver**
  - `positive_conditioning` (from region node) → palette driver → `KSampler` positive

- **Synapse LoRA Style Mixer**
  - `MODEL, CLIP` from checkpoint loader → LoRA mixer → downstream model/CLIP consumers

---

## Layout presets (`layout_mode`)

- `subject_center`: strong center subject box
- `rule_of_thirds`: subject anchors at thirds intersections
- `subject_left` / `subject_right`: side anchor compositions
- `foreground_mid_background`: depth-band composition
- `no_regions`: disables splits and uses global-only conditioning

---

## Tuning guidance

- Start with:
  - `base_strength`: **0.20–0.40**
  - `region_strength_multiplier`: **0.80–1.20**
  - `subject_weight`: increase when subject drifts
- If the image looks fragmented between regions, reduce `region_strength_multiplier`.
- If composition adherence is weak, slightly increase `subject_box_scale` and `subject_weight` together.

---

## Repository structure

- `procedural_prompt_graph.py` — core prompt graph node logic
- `synapse_regions.py` — regional conditioning + preview logic
- `synapse_palette_driver.py` — palette conditioning node
- `synapse_lora_mixer.py` — LoRA mixer node
- `engine/` — prompt-generation subsystems (selection, weighting, safety, formatting)
- `config/`, `plans/`, `presets/`, `data/` — YAML-driven content and behavior

---

## Development checks (pre-ship)

Run from repository root:

```bash
ruff check engine *.py
python -m compileall -q .
```

These checks validate style/quality and basic Python syntax health before release.
