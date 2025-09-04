# Synapse Engine - Advanced Prompt Generation System

This repository contains a fully decomposed, compositional prompt generation system designed for AI image generation tools like Stable Diffusion. It works both as a standalone CLI tool and as a **ComfyUI custom node**.

## 🚀 ComfyUI Integration

### Prerequisites
- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)
- **ComfyUI** - [ComfyUI Repository](https://github.com/comfyanonymous/ComfyUI)

### Installation for ComfyUI

#### Method 1: ComfyUI Manager (Recommended)
1. Install [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
2. In ComfyUI, go to Manager → Install Custom Nodes
3. Search for "Synapse Engine" and install

#### Method 2: Manual Installation
1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd /path/to/ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/Cadejo77/Synapse-Engine.git
   cd Synapse-Engine
   ```

3. Run the installation script:
   ```bash
   python install.py
   ```

4. Restart ComfyUI

### Using in ComfyUI
1. After installation, restart ComfyUI
2. Look for "Synapse Prompt Generator" in the node browser under `text/synapse`
3. Connect the output to your text input nodes (like CLIP Text Encode)

### Node Parameters
- **count**: Number of prompts to generate (1-100)
- **output_format**: "text" (clean prompt) or "json" (with metadata)  
- **seed**: Seed for reproducible generation (-1 for random)
- **custom_root**: Optional custom path to config files

## 📋 Features

The system supports:

1. **Mode Selection**: Compositional (dimension-driven) vs Legacy (pre-fused line)
2. **Conditional Gating**: rarity_min/max, allow_genres/block_genres, vibe_bias
3. **Relational Weight Adjustments**: species ↔ archetype, archetype ↔ power_source, biome ↔ structure, vibe ↔ palette
4. **Conflict Handling** (negative_conflicts)
5. **Complexity Budgeting** (complexity_rules.yaml)
6. **Style & Composition Layers**
7. **Safety Filtering** (safety_flags.yaml)
8. **Synonym Normalization** (synonyms.yaml)
9. **Rarity Overrides** (rarity_overrides.yaml)
10. **Tag Emission**: Final prompt can prepend /genre:.../ /rarity:.../ /vibe:.../ etc.

## 🎯 Generation Flow (Recommended)

1. Pick genre (genre_selector)
2. Pick rarity (rarity_tiers)
3. Pick vibe (vibe_selector)
4. Pick content_type (content_type_selector)
5. If legacy fallback (prob from pipeline) → choose line from subject_core_legacy or landscape_core_legacy (+ optional finishers)
6. Else compositional:
   - For figure: choose species, archetype, physique, etc. respecting gating & complexity budget
   - For landscape: choose biome, structure, atmosphere, etc.
   - Apply relation multipliers & conflict rules
   - Apply rarity overrides & vibe/palette bias
   - Add style layers (palette, lighting, camera, medium, depth, framing, focus, quality combo)
7. Safety Pass (remove offending optional tokens or re-roll)
8. Assemble textual prompt using template variants
9. Emit /tag:value/ metadata prefix (optional)
10. Log choices (token usage, rarity, complexity load)

## 💾 Complexity Budget (Default)

Defined per rarity in complexity_rules.yaml. Each chosen token has complexity_cost (default 1 unless elevated). Stop adding optional pools when budget would be exceeded.

## ➕ Adding New Dimension Tokens

- Add an entry with weight + token
- If specialized: set rarity_min and/or allow_genres
- If it synergizes with others: add synergy_tags or a relation multiplier entry
- If it conflicts: add conflict rule in negative_conflicts.yaml or conflicts field directly

## 📁 Files Overview

See file tree in main answer. Each pool file ends with a metadata block showing version & selection parameters.

## 🔧 Standalone CLI Usage

You can also use this as a standalone command-line tool:

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Generate prompts
node dist/index.js --count 3
node dist/index.js --count 5 --json
node dist/index.js --count 1 --root /custom/config/path
```

### CLI Options
- `--count N`: Generate N prompts (default: 1)
- `--json`: Output in JSON format with metadata
- `--root PATH`: Use custom config directory path
- `--out FILE`: Write output to file (JSON mode only)

## 🚀 Next Steps (Optional)

- Add composites (macro archetype bundles)
- Add faction/culture dimension
- Introduce usage_stats tracking & dynamic overrides
- Add template variants file for natural language assembly

## 📄 License

MIT License

## 🤝 Contributing

Issues and pull requests are welcome! Please ensure any changes maintain the existing YAML structure and follow the established patterns.

---

**Version**: dataset_v1_full_decomposed