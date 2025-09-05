# Enhanced Synapse Engine - Rich Descriptions & Advanced Regional Prompting

## Overview

The Enhanced Synapse Engine provides a complete solution for generating rich, descriptive prompts with advanced regional prompting capabilities. The system now supports full-length, detailed prompts with comprehensive descriptions of quality, subjects, backgrounds, composition, and atmosphere.

## Key Features

### 🎨 Rich Descriptive Prompts
- **Comprehensive Quality Tags**: Genre-specific quality indicators, rarity-based enhancements
- **Detailed Subject Descriptions**: Character details, equipment, poses, expressions, quantity
- **Rich Background Descriptions**: Environment settings, locations, mood, atmosphere
- **Composition Elements**: Camera angles, framing, focus styles, depth effects
- **Atmospheric Details**: Lighting, weather, colors, vibe, style effects

### 🏗️ Advanced Regional Prompting
- **Multiple Regional Modes**: Clean separation of subjects and backgrounds
- **3-Region Support**: Primary subject, background/environment, secondary subject/elements
- **Weighting System**: Adjustable emphasis for subjects, backgrounds, and atmosphere
- **Toggle Functionality**: Easy switch between regional and non-regional modes

### ⚡ Wild Divide Technology
- **Complex Composition**: Advanced layering with attention mapping
- **Multiple Divide Modes**: Wild divide, clean divide, weighted blend, layered composition
- **Composition Styles**: Standard, cinematic, portrait, landscape, action
- **Attention Mapping**: Professional-grade attention weighting

## Node System

### 1. Main Synapse Node (Enhanced)

**New Parameters:**
- `enable_rich_descriptions`: Toggle rich, detailed prompt generation
- `regional_prompting`: Enable regional prompting mode indicator
- `output_format`: Added "regional" format for regional node integration

**Outputs:**
- Full detailed prompt with comprehensive descriptions
- Enhanced negative prompts organized by categories
- Rich metadata with genre, rarity, and vibe information

### 2. Regional Synapse Node (Redesigned)

**Features:**
- Advanced regional prompting with proper subject/background separation
- Support for 2-3 regions with configurable weighting
- Regional vs non-regional toggle mode
- Custom separators (BREAK, AND, |, ::)

**Parameters:**
- `regional_mode`: Enable/disable regional prompting
- `enable_second_subject`: Detect and separate secondary subjects
- `enable_third_region`: Enable third region for additional elements
- `subject_weight`: Weight for subject regions (0.1-3.0)
- `background_weight`: Weight for background region (0.1-3.0)
- `region_separator`: Separator between regions

**Outputs:**
1. `full_prompt`: Complete non-regional prompt
2. `negative_prompt`: Comprehensive negative prompt
3. `region_1`: Primary subject with quality tags
4. `region_2`: Background/environment elements
5. `region_3`: Secondary subject or additional elements
6. `quality_tags`: Extracted quality indicators
7. `metadata`: Regional configuration information

### 3. Wild Divide Regional Node (New)

**Advanced Features:**
- Complex composition with wild divide methodology
- Attention-based layering for professional results
- Multiple divide modes and composition styles
- Advanced weighting with overlapping regions

**Divide Modes:**
- `wild_divide`: Complex layering with wild weighting
- `clean_divide`: Simple clean separation
- `weighted_blend`: Gradual transitions with overlaps
- `layered_composition`: Style-specific layered approach

**Composition Styles:**
- `standard`: Balanced composition
- `cinematic`: Film-like dramatic composition
- `portrait`: Portrait-focused composition
- `landscape`: Landscape-oriented composition
- `action`: Action-oriented dynamic composition

**Outputs:**
1. `composed_prompt`: Final composed prompt with regions
2. `foreground_region`: Primary subject and focus elements
3. `background_region`: Environment and background elements
4. `atmosphere_region`: Atmospheric and technical elements
5. `attention_map`: Attention-based weighting map
6. `metadata`: Composition configuration information

## Usage Examples

### Basic Rich Prompt Generation

```python
# Main Synapse Node with rich descriptions
main_node = SynapsePromptGenerator()

prompt, negative, metadata = main_node.generate_prompt(
    count=1,
    output_format="text",
    seed=12345,
    user_prompt="epic dragon knight battle",
    genre_control="fantasy",
    enable_rich_descriptions=True  # Enable rich descriptions
)

# Result: Comprehensive prompt with quality tags, detailed subject descriptions,
# background elements, composition details, and atmospheric effects
```

### Advanced Regional Workflow

```python
# Step 1: Generate rich prompt
main_node = SynapsePromptGenerator()
main_prompt, main_negative, main_metadata = main_node.generate_prompt(
    count=1,
    output_format="text",
    seed=12345,
    user_prompt="cyberpunk hacker infiltrating corporate tower",
    genre_control="cyberpunk",
    enable_rich_descriptions=True
)

# Step 2: Process with Regional Node
regional_node = RegionalSynapseNode()
full, negative, region_1, region_2, region_3, quality, metadata = regional_node.generate_regional_prompt(
    main_prompt=main_prompt,
    regional_mode=True,
    enable_second_subject=True,
    enable_third_region=True,
    subject_weight=1.2,
    background_weight=0.9,
    region_separator="BREAK"
)

# Use regions for different purposes:
# - region_1: Primary subject conditioning
# - region_2: Background/environment conditioning  
# - region_3: Secondary elements conditioning
```

### Wild Divide Advanced Composition

```python
# Wild Divide for complex scenes
wild_divide_node = WildDivideRegionalNode()

composed, foreground, background, atmosphere, attention, metadata = wild_divide_node.generate_wild_divide(
    main_prompt=main_prompt,
    divide_mode="wild_divide",
    composition_style="cinematic",
    subject_emphasis=1.3,
    background_emphasis=0.8,
    atmosphere_weight=1.1,
    enable_attention_layers=True,
    use_break_syntax=True
)

# Results in professional-grade regional composition with:
# - Weighted foreground elements
# - Separated background elements  
# - Atmospheric layering
# - Attention mapping for focus control
```

## Integration with ComfyUI

### Node Workflow Setup

1. **Main Generation**: Use "Synapse Prompt Generator" node
   - Set `enable_rich_descriptions=True` for detailed prompts
   - Choose appropriate genre and seed
   - Connect output to regional nodes or directly to CLIP

2. **Regional Processing**: Use "Regional Synapse Node (Advanced)"
   - Connect main node output to `main_prompt` input
   - Configure regional settings
   - Connect regional outputs to different CLIP nodes or conditioning

3. **Advanced Composition**: Use "Wild Divide Regional Node" 
   - For complex scenes requiring professional composition
   - Connect to attention/weighting nodes
   - Use with advanced regional conditioning systems

### Prompt Structure Examples

**Rich Description Output:**
```
masterpiece, best quality, high resolution, ultra detailed, epic fantasy art, detailed fantasy illustration, armored dragon knight wielding flaming sword, mystical forest clearing with ancient ruins, cinematic lighting, dramatic composition, ethereal atmosphere, detailed textures, photorealistic rendering
```

**Regional Split Output:**
- **Region 1**: `masterpiece, best quality, (armored dragon knight wielding flaming sword:1.2), dramatic pose`
- **Region 2**: `(mystical forest clearing with ancient ruins:0.9), ethereal atmosphere, cinematic lighting`  
- **Region 3**: `magical particles, glowing effects, atmospheric depth`

**Wild Divide Composition:**
```
masterpiece, best quality, (armored dragon knight:1.3), dramatic pose, cinematic composition BREAK (mystical forest clearing:0.8), ancient ruins, ethereal lighting BREAK (magical particles:1.1), atmospheric effects, depth of field
```

## Best Practices

### For Rich Descriptions
- Use genre-specific settings for optimal quality tags
- Enable rich descriptions for detailed, comprehensive prompts
- Combine with user prompts for targeted subject matter

### For Regional Prompting
- Use regional mode for complex multi-element scenes
- Adjust weights based on desired emphasis (1.0-1.5 for emphasis, 0.7-0.9 for de-emphasis)
- Enable second subject detection for scenes with multiple characters

### For Wild Divide
- Use "wild_divide" mode for most complex scenes
- Use "cinematic" composition style for dramatic scenes
- Enable attention layers for professional-grade results
- Adjust emphasis values based on scene requirements:
  - Subject emphasis: 1.2-1.5 for main characters
  - Background emphasis: 0.7-1.0 for environments
  - Atmosphere emphasis: 1.0-1.3 for mood control

## Technical Details

### Enhanced Universal Formatter
- Utilizes full metadata token system for rich descriptions
- Categorizes elements by semantic meaning
- Adds genre-specific quality enhancements
- Incorporates composition and technical details

### Regional Processing Algorithm
- Advanced semantic parsing with enhanced indicators
- Multi-subject detection and separation
- Configurable weighting system
- Support for multiple regional formats

### Wild Divide Methodology
- Complex composition analysis
- Attention-based element distribution
- Style-specific layering strategies
- Professional-grade weighting systems

## Troubleshooting

### Common Issues
1. **Empty Regions**: Check main prompt quality and enable rich descriptions
2. **Unbalanced Weighting**: Adjust emphasis values between 0.5-2.0 range
3. **Regional Mode Not Working**: Ensure `regional_mode=True` in Regional Node
4. **Poor Composition**: Try different composition styles and divide modes

### Performance Tips
- Use appropriate seeds for consistent results
- Start with default weights and adjust gradually
- Test different divide modes for optimal results
- Use attention mapping for complex scenes

## Migration from Previous Version

### For Existing Users
- Previous functionality remains unchanged with `enable_rich_descriptions=False`
- Regional node now provides much more advanced functionality
- Old regional outputs still work but new outputs provide better control

### Recommended Updates
1. Enable rich descriptions for better prompt quality
2. Use new regional node for advanced regional prompting
3. Try wild divide node for complex compositions
4. Update workflows to use new weighting systems

## Future Enhancements

The system is designed for extensibility and future enhancements may include:
- Additional composition styles
- More sophisticated attention mapping
- Integration with specific model optimizations
- Advanced prompt chaining capabilities

---

For more examples and advanced usage, see the test files:
- `test_enhanced_regional.py`: Basic enhanced functionality
- `test_comprehensive_regional.py`: Complete system testing