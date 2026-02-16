# Synapse Engine (ComfyUI Custom Nodes)

Synapse Engine is a YAML-driven prompt-generation and composition-control pack for ComfyUI. It provides structured prompt construction, region-aware conditioning, optional palette steering, and optional LoRA mixing.

## Why this project exists (and why YAML is the core)

This project was built to quickly generate coherent prompts in a **procedural** way, especially for:

- **Fantasy** scenes (characters, classes, magic, locations, weather, mood)
- **Sci-fi** scenes (species, factions, technology, settings, action)
- **Pinup / poster-style** prompt flows

The same system can be adapted to **any theme or style** by editing YAML content instead of rewriting Python logic. In other words, the engine stays stable while your creative vocabulary evolves.

Unlike classic wildcard packs (usually flat token lists with simple random picks), Synapse uses categorized YAML blocks and relationship rules so outputs stay more coherent across subject, environment, action, style, and quality.

## YAML content map (what the files contain)

Synapse is organized by content categories so each part of a prompt is intentionally controlled:

- `presets/default/`
  - High-level generators and themed packs (`master_generator_fantasy.yaml`, `master_generator_scifi.yaml`, `pinup_*`, roles, outfits, moods, lens, lighting, quality, negatives, etc.).
  - Think of these as user-facing building blocks you can combine quickly.

- `config/subjects/subjects/`
  - Subject identity and variation layers (species, archetypes, physiques, emotions, gear, conditions, power sources).

- `config/environments/`
  - Scene/world context (biomes, structures, weather, atmosphere, time of day, effects).

- `config/style/style/`
  - Visual treatment (camera style, lighting, palette/color direction, medium textures, quality/style combos).

- `config/composition/`
  - Framing and image-readability controls (framing style, focus strategy, depth effects).

- `config/meta/`
  - Behavior controls and glue logic:
  - selectors and profiles,
  - rarity/weight rules,
  - synonyms,
  - safety and negative prompt systems,
  - cross-category relation bias files (for coherence).

- `plans/`
  - Pipeline/selection plans that define how generation stages are executed.

- `data/`
  - Legacy core YAML datasets retained for compatibility.

## How to customize the YAML files (in depth)

If your goal is new themes, stronger consistency, or better style targeting, treat customization as a layered workflow:

1. **Start with presets for fast wins**
   - Duplicate a file in `presets/default/` that is closest to your theme.
   - Rename it clearly (example pattern: `master_generator_<theme>.yaml`).
   - Swap or add category references (role, outfit, location, action, mood, lighting).
   - This gives immediate new prompt behavior without touching engine code.

2. **Extend base vocab in category configs**
   - Add new entries in the matching folders:
     - character concepts → `config/subjects/subjects/`
     - world/environment concepts → `config/environments/`
     - look/finish concepts → `config/style/style/`
   - Keep additions grouped semantically so future tuning remains easy.

3. **Tune coherence with meta relations**
   - Use `config/meta/relations_*.yaml` files to bias compatible combinations.
   - Example approach: push specific species toward matching archetypes, or specific biomes toward fitting structures.
   - This is where Synapse moves beyond random assembly into structured procedural generation.

4. **Control diversity and stability**
   - Adjust rarity/selection behavior in `rarity_tiers.yaml`, `rarity_override.yaml`, selector files, and complexity rules.
   - Increase diversity when outputs feel repetitive; tighten rarity/bias when outputs feel too chaotic.

5. **Curate safety and negative guidance**
   - Refine `negative_prompts.yaml` and `safety_flags.yaml` for your model/workflow.
   - You can keep a consistent quality floor while still allowing wide thematic variety.

6. **Validate in small iterations**
   - Change one category at a time, generate multiple seeds, and compare.
   - If coherence drops, update relation bias files before adding more raw tokens.

### Practical customization strategy

- **For a new theme** (for example: noir detective, mythic horror, retro anime):
  1) copy a close preset,
  2) add subject/environment/style vocab,
  3) add relation biases,
  4) tune rarity,
  5) polish negatives.

- **For stronger fantasy/scifi identity**:
  - Prioritize archetype ↔ power source and biome ↔ structure relation files.
  - Keep camera/lighting/style entries aligned with the intended genre mood.

- **For pinup workflows**:
  - Use `pinup_*` presets as your top-level routing,
  - then fine-tune appearance, pose, composition, and quality packs,
  - and keep explicit negatives to avoid drift into unintended scene complexity.

## Why this is an alternative to wildcards

Traditional wildcard systems are great for speed but often weak on multi-part coherence. Synapse is designed as a stronger alternative when you need structured procedural generation:

- **Category-aware generation** instead of single flat pools.
- **Cross-category relations** instead of independent random picks.
- **Rarity and selector control** for balancing novelty vs consistency.
- **Composable presets** for themed pipelines (fantasy, sci-fi, pinup, studio, etc.).
- **YAML-first editing** so non-programmers can shape behavior safely.

If your main goal is generating coherent fantasy scenes quickly—with the freedom to pivot into any theme later—this architecture is exactly what Synapse is built for.

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
   - Best used when your composition is working but color grading is inconsistent across seeds.
   - Typical uses:
     - enforce a family (`cinematic`, `neon`, `earthy`, etc.)
     - lock harmony mode (`analogous`, `complementary`, `triadic`)
     - apply subtle style glue by keeping `palette_strength` around `0.35–1.0`

5. **Synapse LoRA Style Mixer** *(optional)*
   - Text-driven LoRA loader with no fixed slot limit.
   - Paste LoRA references as:
     - `<lora:name:strength>`
     - `<lora:name:model_strength:clip_strength>`
     - `name`, `name:strength`, or `name|model|clip` per line
   - Auto-generates a `LORA_STACK` output for compatibility with external stack/apply nodes.
   - Extracts trigger words (from sidecar metadata when available) and exposes them as a string output.
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
  - Use when outputs need consistent palette identity while keeping prompt content flexible.

- **Synapse LoRA Style Mixer**
  - `MODEL, CLIP` from checkpoint loader → LoRA mixer → downstream model/CLIP consumers
  - Use when you want to paste a LoRA list quickly (instead of adding many fixed slots).
  - Forward `lora_stack` to third-party LoRA stack/apply nodes if your workflow already uses that ecosystem.
  - Forward `trigger_words` to prompt-combine/text nodes if the LoRA pack relies on activation phrases.

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
