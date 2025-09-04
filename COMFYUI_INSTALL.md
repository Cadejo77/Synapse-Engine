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
- **output_type**: 
  - "full_prompt" = Complete formatted prompt
  - "regional_components" = Split into SUBJECT and STYLE for regional prompting
  - "json" = Include metadata and debug info
- **seed**: For reproducible results (-1 for random)
- **model_profile**: Target AI model for optimized formatting
  - "auto" = General purpose
  - "sdxl" = Stable Diffusion XL (tag-based with quality tags)
  - "flux" = Flux.1 (natural language prose style)
  - "illustrious_xl" = Illustrious XL (danbooru-style tags)
  - "pony" = Pony Diffusion XL (score tags, anime-focused)
- **genre_control**: 
  - "random" = Randomly select genre each time
  - "fixed" = Use the genre specified in fixed_genre
- **content_rating**:
  - "safe" = Family-friendly content only
  - "mature" = Adult themes, sophisticated content
  - "artistic_r" = Artistic nude studies, fine art R-rated content

#### Optional Inputs
- **user_prompt**: Your custom prompt text (will be combined with generated content)
- **negative_prompt**: Custom negative prompts (combined with model-specific negatives)
- **fixed_genre**: Genre to use when genre_control is "fixed" (fantasy, sci_fi, cyberpunk, etc.)
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

**SDXL Format:**
> "masterpiece, best quality, ultra detailed, sturdy elf ranger, longbow, leather armor, forest clearing, golden hour lighting, oil painting style"

**Flux Format:**  
> "A sturdy elf ranger that is skilled and weathered, holding a longbow in a forest clearing. rendered with golden hour lighting, oil painting aesthetics"

**Pony Format:**
> "score_9, score_8_up, rating_safe, source_anime, cute elf girl, bow weapon, fantasy forest, golden lighting"

**Regional Components:**
```
SUBJECT: masterpiece, best quality, ultra detailed, elf ranger, sturdy build, longbow, leather armor
STYLE: golden hour lighting, oil painting style, cinematic composition
```

**Artistic R-rated (when enabled):**
> "masterpiece quality, classical nude study, figure drawing pose, renaissance lighting, fine art medium"

The prompts are designed to work optimally with their target models and support both character portraits and landscape scenes.

### Support

- [GitHub Issues](https://github.com/Cadejo77/Synapse-Engine/issues)
- Check the main [README.md](README.md) for technical details
- Run `python test_engine.py` in the node directory to verify installation

### Key Improvements in v1.1.0

- **Pure Python**: No Node.js required - runs entirely in Python
- **Deterministic Seeding**: Reproducible results with seed parameter
- **Direct YAML Processing**: Fast loading with PyYAML
- **Legacy Mode Preserved**: Original fused-line mode still available