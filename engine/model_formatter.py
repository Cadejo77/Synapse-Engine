"""
Model-specific prompt formatting utilities
"""
from typing import Dict, Any

def format_prompt_for_model(prompt: str, context: Dict[str, Any], model_profile: str, 
                           cfg: Dict[str, Any], user_prompt: str = "") -> str:
    """Format prompt according to model-specific requirements"""
    
    model_profiles = cfg.get('meta', {}).get('model_profiles', {}).get('model_profiles', {})
    profile_data = model_profiles.get(model_profile, {})
    
    if not profile_data:
        # Fallback to basic formatting
        combined = []
        if user_prompt.strip():
            combined.append(user_prompt.strip())
        if prompt.strip():
            combined.append(prompt.strip())
        return ', '.join(combined)
    
    formatter = profile_data.get('formatter', 'tags')
    
    if formatter == 'prose':
        return _format_as_prose(prompt, context, profile_data, user_prompt)
    else:
        return _format_as_tags(prompt, context, profile_data, user_prompt)

def _format_as_prose(prompt: str, context: Dict[str, Any], profile_data: Dict[str, Any], 
                     user_prompt: str = "") -> str:
    """Format prompt as natural language prose (for Flux)"""
    
    parts = []
    
    # Add user prompt first if provided
    if user_prompt.strip():
        parts.append(user_prompt.strip())
    
    # Convert tags to more natural language
    if prompt.strip():
        # Basic conversion - replace commas with natural connectors
        natural_prompt = prompt.replace(', ', ' with ').replace(',', ' and')
        parts.append(natural_prompt)
    
    # Apply emphasis syntax for Flux ([important phrase])
    combined = '. '.join(parts) if len(parts) > 1 else (parts[0] if parts else "")
    
    return combined

def _format_as_tags(prompt: str, context: Dict[str, Any], profile_data: Dict[str, Any], 
                    user_prompt: str = "") -> str:
    """Format prompt as comma-separated tags"""
    
    parts = []
    
    # Add quality tags first for certain models
    quality_tags = profile_data.get('quality_tags', [])
    if quality_tags:
        parts.extend(quality_tags)
    
    # Add special tokens for Pony
    special_tokens = profile_data.get('special_tokens', [])
    if special_tokens:
        parts.extend(special_tokens)
    
    # Add user prompt
    if user_prompt.strip():
        user_parts = [part.strip() for part in user_prompt.split(',') if part.strip()]
        parts.extend(user_parts)
    
    # Add generated prompt
    if prompt.strip():
        generated_parts = [part.strip() for part in prompt.split(',') if part.strip()]
        parts.extend(generated_parts)
    
    return ', '.join(parts)

def create_regional_prompt_format(positive: str, negative: str, metadata: str) -> str:
    """Create regional prompting format output"""
    
    # Basic regional prompting format
    regional_sections = []
    
    # Main prompt section
    regional_sections.append(f"MAIN: {positive}")
    
    # Background/environment section (if we can detect landscape elements)
    if any(keyword in positive.lower() for keyword in ['landscape', 'background', 'environment', 'sky', 'forest', 'mountain']):
        bg_parts = [part for part in positive.split(',') if any(kw in part.lower() for kw in ['sky', 'background', 'landscape', 'environment'])]
        if bg_parts:
            regional_sections.append(f"BACKGROUND: {', '.join(bg_parts)}")
    
    # Subject/character section (if we can detect figure elements)
    if any(keyword in positive.lower() for keyword in ['character', 'person', 'figure', 'warrior', 'knight', 'mage']):
        char_parts = [part for part in positive.split(',') if any(kw in part.lower() for kw in ['character', 'person', 'figure', 'warrior', 'knight', 'mage', 'elf'])]
        if char_parts:
            regional_sections.append(f"SUBJECT: {', '.join(char_parts)}")
    
    return '\n'.join(regional_sections)