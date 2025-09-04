"""
Prompt assembly functions
"""
from typing import Dict, Any, List

def assemble_prompt(context: Dict[str, Any]) -> str:
    """Assemble the main prompt from selected tokens"""
    tokens = context.get('tokens', {})
    
    if context.get('mode') == 'legacy':
        # For legacy mode, return the chosen legacy line
        return context.get('chosen_legacy', '')
    
    # For compositional mode, assemble from tokens
    parts = []
    
    # Determine content type and add appropriate dimensions
    content_type = context.get('content_type', 'figure')
    
    if content_type in ['figure', 'hybrid']:
        # Add figure dimensions in order
        for dim in ['species', 'archetypes', 'physiques', 'emotions', 'conditions', 
                   'power_sources', 'gear_primary', 'gear_secondary', 'modifiers']:
            if dim in tokens and tokens[dim]:
                parts.extend(tokens[dim])
    
    elif content_type == 'landscape':
        # Add landscape dimensions in order
        for dim in ['biomes', 'structures', 'atmosphere_mood', 'weather', 'time_of_day', 'special_fx']:
            if dim in tokens and tokens[dim]:
                parts.extend(tokens[dim])
    
    return ', '.join(parts)

def assemble_style(context: Dict[str, Any]) -> str:
    """Assemble the style portion of the prompt"""
    tokens = context.get('tokens', {})
    style_parts = []
    
    # Style dimensions in order
    for dim in ['palettes', 'lighting', 'camera', 'media', 'depth_effects', 'framing', 'focus_styles', 'quality_combo']:
        if dim in tokens and tokens[dim]:
            style_parts.extend(tokens[dim])
    
    return ', '.join(style_parts)

def make_tags_header(context: Dict[str, Any]) -> str:
    """Create metadata tags header"""
    tags = []
    
    genre = context.get('genre')
    if genre:
        tags.append(f"/genre:{genre}/")
    
    rarity = context.get('rarity')
    if rarity:
        tags.append(f"/rarity:{rarity}/")
    
    vibe = context.get('vibe') 
    if vibe:
        tags.append(f"/vibe:{vibe}/")
    
    content_type = context.get('content_type')
    if content_type:
        tags.append(f"/content:{content_type}/")
    
    return ' '.join(tags)