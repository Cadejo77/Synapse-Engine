# ComfyUI-ProceduralPromptGraph

A ComfyUI custom node that generates long, coherent prompts by expanding `__tokens__` from YAML modules with simple conditional routing via `meta:*` tags.

## Install

1. Copy this folder into:

   `ComfyUI/custom_nodes/ComfyUI-ProceduralPromptGraph`

2. Restart ComfyUI.

3. In the node menu, search for:

   **Procedural Prompt Graph (YAML)**

## Usage

- **preset_folder**: which preset subfolder in `presets/` to use (default: `default`)
- **entry_file**: usually `0_master_generator.yaml`
- **entry_key**: usually `template`
- **seed**: deterministic randomness
- **sep_text**: replaces `[SEP]` tokens (default: blank line)
- **strip_meta_tags**: removes `meta:*` tokens from the final prompt while still using them for logic
- **debug**: outputs a debug report (choices + active tags)

## DSL supported

- Weighted option:
  - `50, some text`
  - `/meta:tag/ 25, some text`

- Router (exclusive, first match wins):
  - `/meta:tag/= __some_token__`

- Sequential lists (no weights / no routers):
  - every line that matches conditions (or has no conditions) is appended in order.

- Path tokens:
  - `__fantasy/subject/class_fantasy__` resolves module `class_fantasy.yaml` and key `class` (stem without `_fantasy` / `_scifi` if present).
  - `__shared/scene/composition__` resolves module `composition.yaml` and key `composition`.

## Quick CLI test

From inside this custom node folder:

```bash
python test_generate.py --preset_dir presets/default --entry 0_master_generator.yaml --key template --seed 1234 --debug
```

