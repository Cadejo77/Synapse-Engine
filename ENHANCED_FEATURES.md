# Enhanced Synapse Engine Features

This document describes the enhanced features added to the Synapse Engine for improved prompt generation with model-specific formatting and advanced UI controls.

## 🚀 New Features

### Enhanced ComfyUI Node Interface

The Synapse Prompt Generator node now includes comprehensive UI controls:

**Required Inputs:**
- `count`: Number of prompts (1-100)  
- `output_format`: Output format (text, json, regional, structured)
- `seed`: Seed for reproducible generation (-1 for random)
- `model_profile`: Target model (sdxl, flux, illustrious_xl, pony)

**Optional Inputs:**
- `custom_root`: Custom config path
- `user_prompt`: User's custom prompt text (multiline)
- `genre_control`: Fixed genre or random (random, fantasy, dark_fantasy, sci_fi, cyberpunk, steampunk, post_apoc)
- `negative_prompts`: Enable automatic negative prompts
- `custom_negative`: Custom negative prompt text (multiline)
- `explicit_content`: Adult content control (disabled, artistic_only, full_explicit)
- `regional_prompting`: Enable regional prompting format

**Output:**
- Returns 3 outputs: `positive_prompt`, `negative_prompt`, `metadata`

### Model-Specific Formatting

The system now formats prompts according to each model's preferences:

#### SDXL (Stable Diffusion XL)
- **Format**: Tag-based with quality prefixes
- **Quality Tags**: masterpiece, best quality, high resolution
- **Emphasis**: (word) to boost, [word] to suppress  
- **Negative Prompts**: Comprehensive quality and anatomy fixes
- **Structure**: quality → subject → environment → style → enhancers

#### Flux.1
- **Format**: Natural language prose
- **Emphasis**: [important phrase] for highlighting
- **Negative Prompts**: Often not needed
- **Structure**: Descriptive sentences with natural flow

#### Illustrious XL
- **Format**: Danbooru-style tags with quality prefixes
- **Quality Tags**: masterpiece, amazing quality, very aesthetic
- **Emphasis**: Tag order and positioning
- **Negative Prompts**: Highly effective for artifact removal
- **Structure**: quality → rating → subject → pose → background → style

#### Pony Diffusion XL
- **Format**: Score-based tags with anime tokens
- **Quality Tags**: score_9, score_8_up, score_7_up
- **Special Tokens**: source_anime, source_pony, rating_safe
- **Negative Prompts**: Limited usage recommended
- **Structure**: score_quality → source_rating → subject → style

### Enhanced Content Generation

#### Explicit Content Controls
- **Disabled**: No adult content
- **Artistic Only**: Tasteful artistic nudity (figure studies, classical art)
- **Full Explicit**: All adult content types

The system uses rarity-based probability:
- Common: 5% chance for R-rated content
- Rare: 10% chance  
- Epic: 15% chance

Artistic genres (fantasy, dark_fantasy, steampunk) have 1.5x higher chances.

#### Genre Control
- **Random**: System picks genre automatically
- **Fixed**: Lock to specific genre (fantasy, dark_fantasy, sci_fi, cyberpunk, steampunk, post_apoc)

### Output Formats

#### Text Format (Default)
Basic formatted prompt string optimized for the selected model.

#### JSON Format  
Structured data including metadata:
```json
{
  "positive_prompt": "formatted prompt",
  "negative_prompt": "negative terms",
  "metadata": {...},
  "model_profile": "sdxl"
}
```

#### Regional Format
Separates prompts into regions for regional prompting:
```
MAIN: masterpiece, best quality, space marine in alien jungle
BACKGROUND: alien jungle, atmospheric lighting
SUBJECT: space marine, power armor, determined expression
```

#### Structured Format
Clean separation of all components:
```
POSITIVE: [formatted positive prompt]

NEGATIVE: [negative prompt terms]

METADATA: Genre: sci_fi, Rarity: rare, Model: sdxl
```

### Enhanced Safety & Content Controls

The system now includes:
- **R-rated Artistic**: Tasteful nudity for fine art
- **Explicit Adult**: Full adult content options  
- **Content Filtering**: Age-sensitive combination blocking
- **Genre Awareness**: Content appropriateness per genre

## 📋 Usage Examples

### Basic Enhanced Generation
```python
from synapse_node import SynapsePromptGenerator

node = SynapsePromptGenerator()

# SDXL fantasy with custom prompt
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text",
    seed=42,
    model_profile="sdxl",
    genre_control="fantasy",
    user_prompt="ethereal elven mage casting spell",
    negative_prompts=True
)
```

### Flux Natural Language
```python
# Flux with prose formatting
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text", 
    seed=123,
    model_profile="flux",
    user_prompt="a rain-soaked cyberpunk street scene at night with neon reflections"
)
```

### Regional Prompting
```python  
# Regional format for complex compositions
regional_prompt, negative, metadata = node.generate_prompt(
    count=1,
    output_format="regional",
    seed=456,
    model_profile="sdxl",
    user_prompt="epic dragon battle over mountain castle"
)
```

### Artistic Content
```python
# Artistic nudity for fine art
positive, negative, metadata = node.generate_prompt(
    count=1,
    output_format="text",
    seed=789,
    model_profile="sdxl", 
    genre_control="fantasy",
    explicit_content="artistic_only"
)
```

## 🎨 Prompt Quality Improvements

The enhanced system generates richer, more varied prompts:

- **Compositional Variety**: From intimate portraits to epic landscapes
- **Style Richness**: Comprehensive style dimensions (lighting, camera, media, effects)
- **Model Optimization**: Each model receives prompts in its preferred format
- **Natural Integration**: User prompts blend seamlessly with generated content
- **Quality Control**: Automatic negative prompts prevent common artifacts

## 🔧 Technical Implementation

### New Configuration Files
- `config/meta/model_profiles.yaml`: Model-specific formatting rules
- `config/meta/negative_prompts.yaml`: Quality-control negative prompt pools

### New Engine Modules  
- `engine/model_formatter.py`: Model-specific prompt formatting
- `engine/negative_prompts.py`: Negative prompt generation
- Enhanced `engine/generator.py`: Explicit content and genre controls

### Backward Compatibility
All existing functionality is preserved. The node can be used with original parameters, defaulting to SDXL profile with basic generation.

## 📈 Benefits

1. **Model Optimization**: Each AI model receives properly formatted prompts
2. **User Control**: Fine-grained control over content and style
3. **Professional Output**: Multiple output formats for different workflows  
4. **Content Safety**: Graduated content controls with safety measures
5. **Rich Variety**: Enhanced compositional and stylistic diversity
6. **Regional Support**: Advanced prompting techniques for complex scenes

The enhanced Synapse Engine provides professional-grade prompt generation with the flexibility and control needed for serious AI art creation across different models and use cases.