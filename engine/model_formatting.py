"""
Model-specific prompt formatting
"""
from typing import Dict, Any, List

def apply_model_formatting(prompt: str, style: str, context: Dict[str, Any], 
                          model_profiles: Dict[str, Any]) -> str:
    """Apply model-specific formatting to the prompt"""
    model_profile = context.get('model_profile', 'auto')
    profiles = model_profiles.get('model_profiles', {})
    profile_config = profiles.get(model_profile, profiles.get('auto', {}))
    
    if not profile_config:
        return prompt
    
    formatter = profile_config.get('formatter', 'tags')
    quality_tags = profile_config.get('quality_tags', [])
    structure_order = profile_config.get('structure_order', [])
    special_tokens = profile_config.get('special_tokens', [])
    
    if formatter == 'prose':
        # Flux-style natural language formatting
        return format_as_prose(prompt, style, quality_tags, context)
    else:
        # Tag-based formatting (SDXL, Illustrious XL, Pony)
        return format_as_tags(prompt, style, quality_tags, special_tokens, structure_order, context)

def format_as_prose(prompt: str, style: str, quality_tags: List[str], context: Dict[str, Any]) -> str:
    """Format prompt in natural language style (Flux)"""
    # Flux prefers descriptive sentences over tag lists
    parts = []
    
    # Convert comma-separated tags to more natural language
    prompt_parts = [p.strip() for p in prompt.split(',')]
    
    # Try to construct natural sentences
    if prompt_parts:
        # Start with the main subject
        main_subject = prompt_parts[0]
        descriptors = prompt_parts[1:3] if len(prompt_parts) > 1 else []
        actions_attributes = prompt_parts[3:] if len(prompt_parts) > 3 else []
        
        sentence = main_subject
        if descriptors:
            sentence += f" that is {' and '.join(descriptors)}"
        
        if actions_attributes:
            sentence += f", {', '.join(actions_attributes)}"
        
        parts.append(sentence)
        
        # Add style as a separate descriptive element
        if style and style.strip():
            style_parts = [s.strip() for s in style.split(',')]
            if style_parts:
                style_description = f"rendered with {', '.join(style_parts)}"
                parts.append(style_description)
    
    return '. '.join(parts)

def format_as_tags(prompt: str, style: str, quality_tags: List[str], 
                   special_tokens: List[str], structure_order: List[str], 
                   context: Dict[str, Any]) -> str:
    """Format prompt in tag-based style (SDXL, Illustrious XL, Pony)"""
    parts = []
    
    # Add quality tags first (for Illustrious XL and Pony)
    if quality_tags:
        parts.extend(quality_tags)
    
    # Add special tokens for Pony
    if special_tokens:
        content_rating = context.get('content_rating', 'safe')
        if content_rating == 'safe':
            if 'rating_safe' in special_tokens:
                parts.append('rating_safe')
        
        # Add source tokens based on genre
        genre = context.get('genre', '')
        if genre in ['fantasy', 'dark_fantasy'] and 'source_anime' in special_tokens:
            parts.append('source_anime')
    
    # Add the main prompt
    if prompt:
        parts.append(prompt)
    
    # Add style
    if style and style.strip():
        parts.append(style)
    
    return ', '.join(parts)

def get_model_negative_prompts(model_profile: str, content_rating: str, model_profiles: Dict[str, Any]) -> str:
    """Get model-specific negative prompts"""
    profiles = model_profiles.get('model_profiles', {})
    profile_config = profiles.get(model_profile, profiles.get('auto', {}))
    
    if not profile_config:
        return ""
    
    negative_essentials = profile_config.get('negative_essentials', [])
    focus_positive = profile_config.get('focus_positive', False)
    
    # Flux and Pony often need fewer negatives
    if focus_positive or model_profile == 'flux':
        if content_rating == 'safe':
            return ', '.join(negative_essentials[:2]) if negative_essentials else ""
        else:
            return ""
    
    return ', '.join(negative_essentials) if negative_essentials else ""