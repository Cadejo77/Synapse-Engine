# ComfyUI Installation Guide - Synapse Engine

## Quick Start

### Prerequisites
- **ComfyUI** installed and working
- **Python** (3.8+) - Usually already available with ComfyUI

### Installation Steps

#### Option 1: ComfyUI Manager (Recommended)
1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) if you haven't already
2. Restart ComfyUI
3. Click "Manager" button
4. Go to "Install Custom Nodes"
5. Search for "Synapse Engine" 
6. Click Install
7. Restart ComfyUI

#### Option 2: Manual Installation
```bash
cd /path/to/ComfyUI/custom_nodes/
git clone https://github.com/Cadejo77/Synapse-Engine.git
cd Synapse-Engine
pip install -r requirements.txt
```
Then restart ComfyUI.

### Using the Node

1. After restarting ComfyUI, look for "Synapse Prompt Generator" in the node browser
2. It's located under: `Add Node > text > synapse > SynapsePromptGenerator`
3. Connect the text output to your CLIP Text Encode node

### Node Settings

- **count**: How many prompts to generate (1-100)
- **output_format**: 
  - "text" = Clean prompt only
  - "json" = Include metadata tags
- **seed**: For reproducible results (-1 for random)
- **custom_root**: Advanced - custom config path (leave empty normally)

### Troubleshooting

**Node doesn't appear:**
- Restart ComfyUI completely
- Check the console for error messages
- Make sure PyYAML is installed (`pip install PyYAML>=6.0`)

**"PyYAML not found" error:**
- Install PyYAML: `pip install PyYAML>=6.0`
- Restart ComfyUI
- Try again

**Generated prompts are too long:**
- The node generates rich, detailed prompts
- You can truncate them or use the JSON mode to extract specific parts

**Want to customize the generation:**
- The YAML config files in the `/config` directory can be edited
- Each file controls different aspects (genres, rarities, styles, etc.)
- Restart ComfyUI after editing configs

### Example Workflow

1. Add "Synapse Prompt Generator" node
2. Set count to 1, format to "text"
3. Connect output to "CLIP Text Encode (Prompt)" input
4. Connect CLIP output to your checkpoint model
5. Generate!

### Generated Prompt Examples

**Fantasy:**
> "A sturdy elf_high barbarian empowered by mundane twin_daggers + tool_satchel, grim (pristine)"

**Sci-Fi:**  
> "chrome-faced enforcer, subsystem glyphs, violet haze :: storm-charged skyline, electric horizon arcs"

**Landscape:**
> "ancient_forest scene with ruined_tower under electro_static at dawn featuring drifting_embers"

The prompts are designed to work well with Stable Diffusion and similar models.

### Support

- [GitHub Issues](https://github.com/Cadejo77/Synapse-Engine/issues)
- Check the main [README.md](README.md) for technical details
- Run `python test_engine.py` in the node directory to verify installation

### Key Improvements in v1.1.0

- **Pure Python**: No Node.js required - runs entirely in Python
- **Deterministic Seeding**: Reproducible results with seed parameter
- **Direct YAML Processing**: Fast loading with PyYAML
- **Legacy Mode Preserved**: Original fused-line mode still available