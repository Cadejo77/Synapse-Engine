# Synapse Engine - Advanced Prompt Generation System

This repository contains a fully decomposed, compositional prompt generation system designed for AI image generation tools like Stable Diffusion. It works as a **pure Python ComfyUI custom node** using only YAML configuration files.

## 🚀 ComfyUI Integration

### Prerequisites
- **Python** (3.8 or higher)
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

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Restart ComfyUI

### Using in ComfyUI
1. After installation, restart ComfyUI
2. Look for "Synapse Prompt Generator" in the node browser under `text/synapse`
3. Connect the output to your text input nodes (like CLIP Text Encode)

### Node Parameters

**Required:**
- **count**: Number of prompts to generate (1-100)
- **output_format**: "text" (clean prompt), "json" (with metadata), "regional" (regional prompting), or "structured" (separated format)
- **seed**: Seed for reproducible generation (-1 for random)
- **model_profile**: Target AI model ("sdxl", "flux", "illustrious_xl", "pony")

**Optional:**
- **custom_root**: Optional custom path to config files
- **user_prompt**: Your custom prompt text (integrates with generated content)
- **genre_control**: Fix genre ("random", "fantasy", "dark_fantasy", "sci_fi", "cyberpunk", "steampunk", "post_apoc")
- **negative_prompts**: Enable automatic negative prompts (Boolean)
- **custom_negative**: Custom negative prompt text  
- **explicit_content**: Adult content control ("disabled", "artistic_only", "full_explicit")
- **regional_prompting**: Enable regional prompting format output (Boolean)

**Outputs:** Returns 3 outputs: `positive_prompt`, `negative_prompt`, `metadata`

## 📋 Enhanced Features (NEW!)

The Synapse Engine now includes professional-grade enhancements:

### 🎯 Universal Format (UPDATED!)
- **Single Universal Format**: Simplified from 4 model-specific variants to one optimized format
- **Standardized Structure**: Quality tags → Subject → Background → Supporting tags
- **Cross-Model Compatibility**: Works optimally with SDXL, Flux, Illustrious XL, Pony and other models
- **Regional Synapse Node**: New companion node for advanced prompt organization

### 🎨 Advanced UI Controls
- **User Prompt Integration**: Blend your prompts with AI-generated content
- **Genre Control**: Lock to specific genres or use random selection
- **Explicit Content**: Graduated controls (disabled → artistic only → full explicit)
- **Multiple Output Formats**: Text, JSON, Structured

### 🚀 Quality Improvements
- **Automatic Negative Prompts**: Universal quality control system
- **Enhanced Variety**: Richer language and more diverse compositions
- **Regional Prompting**: Advanced composition control through dedicated Regional Synapse Node
- **R-Rated Artistic Content**: Tasteful nudity for fine art generation

See [UNIVERSAL_FORMAT.md](UNIVERSAL_FORMAT.md) for complete documentation of the new system.

## 📋 Core Features

The system supports:

1. **Pure Python Implementation**: No Node.js required - runs entirely in Python with PyYAML
2. **Deterministic Seeding**: Reproducible results using Python's random.Random(seed)
3. **Mode Selection**: Compositional (dimension-driven) vs Legacy (pre-fused line)
4. **Conditional Gating**: rarity_min/max, allow_genres/block_genres, vibe_bias
5. **Relational Weight Adjustments**: species ↔ archetype, archetype ↔ power_source, biome ↔ structure, vibe ↔ palette
6. **Conflict Handling** (negative_conflicts)
7. **Complexity Budgeting** (complexity_rules.yaml)
8. **Style & Composition Layers**
9. **Safety Filtering** (safety_flags.yaml)
10. **Synonym Normalization** (synonyms.yaml)
11. **Rarity Overrides** (rarity_overrides.yaml)
12. **Tag Emission**: Final prompt can prepend /genre:.../ /rarity:.../ /vibe:.../ etc.

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

## 🔧 Testing Your Installation

You can test your installation using the provided test scripts:

```bash
# Navigate to the Synapse-Engine directory
cd /path/to/ComfyUI/custom_nodes/Synapse-Engine

# Test the new universal format and regional node
python test_universal.py

# Test the original engine functionality
python test_engine.py

# Test enhanced features (legacy model-specific tests)
python test_enhanced.py
```

The new `test_universal.py` validates:
- Universal format generation (no model profiles)
- Regional Synapse Node functionality
- Integration between both nodes
- Different output formats (text, JSON, structured)

This will validate that:
- Configuration files load correctly
- Both compositional and legacy modes work
- Seeding produces reproducible results
- JSON and text output formats function properly

## 🚀 Next Steps (Optional)

- Add composites (macro archetype bundles)
- Add faction/culture dimension  
- Introduce usage_stats tracking & dynamic overrides
- Add template variants file for natural language assembly

### Legacy Mode Support

This implementation preserves the original "fused line" mode from `data/subject_core_legacy.yaml`, `data/landscape_core_legacy.yaml`, and finishers. The probability is controlled by the `compositional_chance` setting in `generation_pipeline.yaml` (set to 1.0 to force compositional-only mode).

## 📄 License

MIT License

## 🤝 Contributing

Issues and pull requests are welcome! Please ensure any changes maintain the existing YAML structure and follow the established patterns.

---

**Version**: dataset_v1_full_decomposed