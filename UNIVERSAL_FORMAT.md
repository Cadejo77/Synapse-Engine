# Universal Format & Regional Prompting

## Overview

The Synapse Engine has been simplified to use a **universal format** that works optimally across all AI models, replacing the previous model-specific formatting system. Additionally, a new **Regional Synapse Node** provides advanced prompt organization capabilities.

## Key Changes

### ✅ What Was Removed
- Model-specific formatting (SDXL, Flux, Illustrious XL, Pony profiles)
- Complex model-dependent prompt structures
- Model profile selection parameter
- Regional output from main node

### ✅ What Was Added
- Universal prompt format that works across all models
- **Regional Synapse Node** for advanced prompt control
- Simplified, consistent prompt structure
- Better semantic organization

## Universal Format Structure

The new universal format follows this standardized structure:

```
[Quality Tags] → [Subject Description] → [Background/Location] → [Supporting Tags]
```

### Example Output
```
masterpiece, best quality, high resolution, epic dragon battle in ancient castle, mystical enchanted forest, dramatic lighting, ethereal atmosphere, cinematic composition
```

**Breakdown:**
- **Quality Tags**: `masterpiece, best quality, high resolution`
- **Subject**: `epic dragon battle in ancient castle` 
- **Background**: `mystical enchanted forest`
- **Supporting**: `dramatic lighting, ethereal atmosphere, cinematic composition`

## Regional Synapse Node

The **Regional Synapse Node** is a companion node that works with the main Synapse node to provide organized, regional prompt outputs.

### Node Inputs
- `main_prompt` (required): Output from the main Synapse Prompt Generator
- `enable_second_subject` (optional): Enable detection of secondary subjects
- `custom_quality_tags` (optional): Override quality tags
- `custom_background` (optional): Override background description  
- `custom_supporting` (optional): Override supporting tags

### Node Outputs
1. **Quality Tags**: Universal quality indicators
2. **Subject Description**: Main character/object/scene focus
3. **Background/Location**: Environmental and location details
4. **Supporting Tags**: Atmosphere, weather, vibe, color palette, style
5. **Second Subject**: Optional secondary subject when enabled

### Example Workflow

```
[Synapse Prompt Generator] → [Regional Synapse Node]
```

**Input to Regional Node:**
```
masterpiece, best quality, high resolution, mystical forest wizard, ancient stone tower, ethereal lighting, magical particles, dramatic atmosphere
```

**Regional Node Outputs:**
- **Quality**: `masterpiece, best quality, high resolution`
- **Subject**: `mystical forest wizard`  
- **Background**: `ancient stone tower`
- **Supporting**: `ethereal lighting, magical particles, dramatic atmosphere`
- **Second Subject**: `(empty)`

## Usage Examples

### Basic Universal Generation
```python
from synapse_node import SynapsePromptGenerator

node = SynapsePromptGenerator()
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text",
    seed=42,
    user_prompt="cyberpunk hacker in neon city"
)
```

### Regional Prompting Workflow  
```python
from synapse_node import SynapsePromptGenerator
from regional_synapse_node import RegionalSynapseNode

# Generate main prompt
main_node = SynapsePromptGenerator()
main_prompt, negative, metadata = main_node.generate_prompt(
    count=1,
    output_format="text", 
    seed=123,
    user_prompt="epic battle scene"
)

# Split into regions
regional_node = RegionalSynapseNode()
quality, subject, background, supporting, second_subject = regional_node.split_regional_prompt(
    main_prompt=main_prompt,
    enable_second_subject=True
)
```

### Advanced Regional Control
```python
# Use custom overrides for specific sections
quality, subject, background, supporting, second_subject = regional_node.split_regional_prompt(
    main_prompt=main_prompt,
    enable_second_subject=True,
    custom_quality_tags="ultra detailed, photorealistic, 8k",
    custom_background="mystical enchanted forest, ethereal lighting",
    custom_supporting="dramatic composition, cinematic angle"
)
```

## Benefits of Universal Format

1. **Simplicity**: One format works with all AI models
2. **Consistency**: Predictable prompt structure every time
3. **Compatibility**: No need to worry about model-specific syntax
4. **Flexibility**: Regional node provides granular control when needed
5. **Maintenance**: Easier to maintain and extend

## Migration Guide

### For Existing Users

**Old way (with model profiles):**
```python
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text",
    seed=42,
    model_profile="sdxl",  # ← REMOVED
    user_prompt="fantasy wizard"
)
```

**New way (universal format):**
```python
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text", 
    seed=42,
    user_prompt="fantasy wizard"  # ← Same user experience
)
```

### For Regional Prompting

**Old way (built into main node):**
```python
positive, negative, metadata = node.generate_prompt(
    output_format="regional"  # ← REMOVED
)
```

**New way (dedicated regional node):**
```python
# Step 1: Generate main prompt
main_prompt, negative, metadata = node.generate_prompt(
    output_format="text"
)

# Step 2: Use regional node for advanced control
regional_node = RegionalSynapseNode()
quality, subject, background, supporting, second_subject = regional_node.split_regional_prompt(
    main_prompt=main_prompt
)
```

## Technical Implementation

### Files Changed
- `synapse_node.py`: Simplified to use universal format
- `engine/universal_formatter.py`: New universal formatting logic
- `regional_synapse_node.py`: New regional prompting node
- `__init__.py`: Updated to register both nodes

### Backward Compatibility
All existing functionality is preserved. The main changes are:
- Simplified interface (fewer parameters)
- More predictable outputs
- Better semantic organization
- Additional regional control through companion node