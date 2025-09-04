"""
Universal prompt formatting for standardized output structure
Following the requested format: quality tags → subject → background → supporting tags
"""
from typing import Dict, Any, List

def format_universal_prompt(prompt: str, context: Dict[str, Any], user_prompt: str = "") -> str:
    """
    Format prompt using universal structure:
    1. Quality tags
    2. Subject description
    3. Background/location description  
    4. Supporting tags (atmosphere, weather, vibe, color palette, style)
    """
    
    parts = []
    
    # 1. Quality tags - universal quality indicators
    quality_tags = ["masterpiece", "best quality", "high resolution"]
    parts.extend(quality_tags)
    
    # Parse and organize all content by semantic categories
    all_content = []
    
    # Add user prompt content first (usually contains main subject)
    if user_prompt.strip():
        user_parts = [part.strip() for part in user_prompt.split(',') if part.strip()]
        all_content.extend(user_parts)
    
    # Add generated prompt content
    if prompt.strip():
        # Clean up any style separators (::) and split
        clean_prompt = prompt.replace(' :: ', ', ').replace('::', ', ')
        prompt_parts = [part.strip() for part in clean_prompt.split(',') if part.strip()]
        all_content.extend(prompt_parts)
    
    # Categorize all content parts
    subject_parts = []
    background_parts = []
    supporting_parts = []
    
    for part in all_content:
        if not part:
            continue
            
        part_lower = part.lower()
        
        # Subject indicators (characters, beings, main objects)
        if any(keyword in part_lower for keyword in [
            'knight', 'warrior', 'mage', 'wizard', 'sorceress', 'battlemage', 'shadowblade',
            'elf', 'dwarf', 'human', 'orc', 'character', 'person', 'figure', 'barbarian',
            'rogue', 'paladin', 'archer', 'fighter', 'spellcaster', 'adventurer', 'hero',
            'dragon', 'beast', 'creature', 'demon', 'angel', 'spirit', 'ghost',
            'with', 'wearing', 'holding', 'carrying'  # descriptive phrases about subjects
        ]):
            subject_parts.append(part)
            
        # Background/location indicators  
        elif any(keyword in part_lower for keyword in [
            'forest', 'mountain', 'castle', 'temple', 'landscape', 'glade', 'chapel', 'tower',
            'cathedral', 'overpass', 'cityscape', 'environment', 'background', 'scene',
            'clearing', 'alleyway', 'dungeon', 'cavern', 'ruins', 'village', 'city', 'plains',
            'desert', 'ocean', 'river', 'lake', 'valley', 'cliff', 'bridge', 'palace',
            'interior', 'exterior', 'room', 'hall', 'chamber', 'courtyard', 'garden'
        ]):
            background_parts.append(part)
            
        # Supporting tags (atmosphere, weather, style, effects, mood, gear)
        else:
            supporting_parts.append(part)
    
    # Add categorized parts in the requested order:
    # quality tags → subject → background → supporting tags
    parts.extend(subject_parts)
    parts.extend(background_parts) 
    parts.extend(supporting_parts)
    
    return ', '.join(parts)


def generate_universal_negative_prompts(context: Dict[str, Any], custom_negative: str = "") -> str:
    """Generate universal negative prompts suitable for most models"""
    
    if custom_negative.strip():
        return custom_negative.strip()
    
    # Universal negative prompts that work well across models
    universal_negatives = [
        "ugly", "deformed", "bad hands", "worst quality", "lowres", 
        "bad anatomy", "bad proportions", "blurry", "bad face",
        "extra fingers", "missing fingers", "malformed", "watermark",
        "text", "error", "artifacts", "noise"
    ]
    
    return ', '.join(universal_negatives)