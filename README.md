# Synapse Engine (ComfyUI custom nodes)

Synapse Engine is a **prompt + composition control** mini-pack for ComfyUI.

This simplified version originally exposed only **3 nodes**, but it can also include **optional utility nodes** (see below):

1) **Procedural Prompt Graph v2 (Synapse)**  
   Generates **structured** prompt sections:
   - subject
   - scene
   - composition
   - negative

2) **Synapse Region Conditioning**  
   Turns those sections into **real spatial conditioning** (subject/background in separate regions) and outputs:
   - `positive_conditioning` (plug directly into KSampler)
   - `negative_conditioning`
   - `region_plan_json` (for debugging / preview)

3) **Synapse Region Preview** *(optional)*  
   Draws an overlay image of the region rectangles from `region_plan_json`.

4) **Synapse Color Palette Driver** *(optional)*  
   Injects a deterministic, seed-driven palette/harmony prompt as an extra CONDITIONING part (with its own strength).

5) **Synapse LoRA Style Mixer** *(optional)*  
   Loads and applies up to 6 LoRAs with optional total-strength normalization and optional weight jitter.

---

## Quick start (recommended wiring)

**Checkpoint Loader**
- `CLIP` → **Procedural Prompt Graph v2 (Synapse)** and **Synapse Region Conditioning**
- `MODEL` → `KSampler`
- `VAE` → `VAE Decode`

**Procedural Prompt Graph v2 (Synapse)**
- `subject_prompt` → **Synapse Region Conditioning**
- `scene_prompt` → **Synapse Region Conditioning**
- `composition_prompt` → **Synapse Region Conditioning**
- `negative_prompt` → **Synapse Region Conditioning**

**Synapse Region Conditioning**
- `positive_conditioning` → `KSampler` **positive**
- `negative_conditioning` → `KSampler` **negative**
- *(optional)* `region_plan_json` → **Synapse Region Preview**

*(optional)* **Synapse Color Palette Driver**
- `positive_conditioning` → **Synapse Color Palette Driver** → `KSampler` **positive**

*(optional)* **Synapse LoRA Style Mixer**
- `MODEL, CLIP` from **Checkpoint Loader** → **Synapse LoRA Style Mixer** → `KSampler` (MODEL) and all CLIP encoders

Then `KSampler` → `VAE Decode` → `Save Image`.

---

## Presets (layout_mode)

- **subject_center**: strong center subject box (size controlled by `subject_box_scale`)
- **rule_of_thirds**: encourages strong anchors at thirds intersections
- **subject_left / subject_right**: anchor subject on one side
- **foreground_mid_background**: a “depth bands” layout (subject foreground, scene background)
- **no_regions**: disables region splits (uses global prompt only)

---

## Tips for better composition control

- Keep `base_strength` around **0.20–0.40** to preserve a unified look across regions.
- Increase `subject_weight` if the subject is drifting.
- If the image looks “split” or inconsistent across regions, lower `region_strength_multiplier` slightly.

---

## Install

Unzip into:

`ComfyUI/custom_nodes/Synapse-Engine/`

Restart ComfyUI and search for nodes containing **Synapse**.
