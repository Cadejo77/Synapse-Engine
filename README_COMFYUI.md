# Synapse Engine - ComfyUI Custom Node

A sophisticated prompt generation system that creates compositional prompts using YAML-based configuration files. Originally written in TypeScript, now converted to Python for ComfyUI integration.

## Features

### Dual Generation Modes
- **Legacy Mode**: Uses pre-written prompt lines from YAML files
- **Compositional Mode**: Builds prompts from individual token pools (species, archetypes, gear, etc.)

### Intelligent Selection System
- **Rarity-based complexity budgeting**: Higher rarities get more detailed prompts
- **Genre filtering**: Tokens can be restricted to specific genres
- **Vibe bias**: Certain tokens get weight bonuses for specific vibes
- **Relations system**: Some token combinations are encouraged (e.g., species→archetype)

### Metadata & Tags
- Comprehensive metadata tags in the output (e.g., `/genre:fantasy/ /rarity:epic/`)
- Warnings for failed selections or constraint violations
- Deterministic generation with seed support

## Example Outputs

### Common Rarity (Simple)
```
/genre:fantasy/ /rarity:common/ /vibe:heroic/ A human ranger bearing recurve_bow, focused
```

### Epic Rarity (Complex with Style)
```
/genre:cyberpunk/ /rarity:epic/ /vibe:grim/ A legendary sleek android rogue empowered by quantum adorned with neural_links, bearing plasma_rifle + data_siphon, calculating (chrome_scarred). Style: high_contrast_neon, volumetric_lighting, wide_angle_cinematic, holographic_layered, dramatic_depth_of_field, rule_of_thirds
```

### Legacy Mode
```
/genre:steampunk/ /rarity:rare/ brass observatory, rotating astrolabe ring :: rain-slick surfaces reflecting neon signage
```

## Installation

1. Copy the entire `Synapse-Engine` folder to your `ComfyUI/custom_nodes/` directory
2. Install required dependencies: `pip install PyYAML>=5.0`
3. Restart ComfyUI

## Usage in ComfyUI

1. Add the **Synapse Prompt Generator** node to your workflow (found in the "Synapse" category)
2. Connect the output to any text input (e.g., positive prompt on KSampler)
3. Configure parameters:
   - **Count**: Number of prompts to generate (only first is returned to ComfyUI)
   - **Seed**: For deterministic generation (-1 for random)

## Configuration System

The system uses extensive YAML configuration files in the `config/` directory:

### Core Settings (`config/meta/`)
- `genre_selector.yaml`: Available genres (fantasy, cyberpunk, steampunk, etc.)
- `rarity_tiers.yaml`: Rarity levels and their weights
- `complexity_rules.yaml`: Complexity budgets per rarity
- `vibe_selector.yaml`: Available vibes (heroic, mysterious, grim, etc.)

### Token Pools
- **Subjects** (`config/subjects/subjects/`): Species, archetypes, physiques, emotions
- **Environments** (`config/environments/`): Biomes, structures, weather, time of day
- **Style** (`config/style/style/`): Color palettes, lighting, camera angles, media types
- **Composition** (`config/composition/`): Framing, focus styles, depth effects

### Behavioral Rules
- **Relations** (`config/meta/relations_*.yaml`): Token combination bonuses
- **Conflicts** (`config/meta/relations_negative_conflicts.yaml`): Forbidden combinations
- **Safety** (`config/meta/safety_flags.yaml`): Content filtering rules

## Rarity System

- **Common (Budget: 8)**: Basic prompts with core tokens only
- **Rare (Budget: 11)**: Moderate complexity with some style elements  
- **Epic (Budget: 15)**: Full complexity with extensive style composition

Each token has a `complexity_cost` (usually 1-2), and selection stops when the budget is exhausted.

## Customization

You can modify the YAML files to:
- Add new tokens to any dimension pool
- Adjust weights and rarity constraints
- Create new genre/vibe combinations
- Add relational bonuses between tokens
- Modify complexity budgets and costs

## Troubleshooting

### Common Issues
- **"Missing YAML" errors**: Check that all configuration files are present
- **Empty prompts**: Usually means complexity budget exceeded or all tokens filtered out
- **Style elements missing**: Expected for low rarity prompts due to budget constraints

### Debug Information
The node includes warnings in the output when selections fail. Check the ComfyUI console for detailed error messages.

## Technical Notes

This Python implementation faithfully replicates the TypeScript original, including:
- Weighted random selection algorithms
- Rarity/genre filtering logic
- Complexity budgeting system
- Synonym normalization
- Template-based prompt assembly
- Comprehensive metadata tracking

The code is designed to be drop-in compatible with the existing YAML configuration files without modification.