"""
Universal prompt formatting for standardized output structure
Following the requested format: quality tags → subject → background → supporting tags
Generates rich, descriptive prompts with detailed composition elements
"""
from typing import Dict, Any

def format_universal_prompt(prompt: str, context: Dict[str, Any], user_prompt: str = "") -> str:
    """
    Format prompt using enhanced universal structure for rich, detailed prompts:
    1. Quality tags (detailed quality indicators)
    2. Subject description (character details, outfit, class, weapons, pose, quantity)
    3. Background/location description (environment, setting, mood)
    4. Supporting tags (composition, camera angle, lighting, colors, atmosphere, vibe)
    """
    
    parts = []
    
    # 1. Enhanced Quality tags - much more comprehensive
    genre = context.get('genre', 'fantasy')
    rarity = context.get('rarity', 'common')
    
    # Base quality tags
    quality_tags = ["masterpiece", "best quality", "high resolution", "ultra detailed"]
    
    # Add rarity-based quality enhancements
    if rarity in ['legendary', 'mythic']:
        quality_tags.extend(["exceptional masterpiece", "museum quality", "award winning"])
    elif rarity == 'epic':
        quality_tags.extend(["professional artwork", "highly detailed", "8k"])
    elif rarity == 'rare':
        quality_tags.extend(["detailed", "crisp quality"])
    
    # Add genre-specific quality indicators
    if genre == 'fantasy':
        quality_tags.extend(["epic fantasy art", "detailed fantasy illustration"])
    elif genre == 'sci_fi':
        quality_tags.extend(["sci-fi masterpiece", "futuristic concept art"])
    elif genre == 'cyberpunk':
        quality_tags.extend(["cyberpunk artwork", "neon-lit masterpiece"])
    elif genre == 'dark_fantasy':
        quality_tags.extend(["dark fantasy art", "gothic masterpiece"])
    
    parts.extend(quality_tags)
    
    # Parse and organize all content with enhanced categorization
    all_content = []
    
    # Add user prompt content first (usually contains main subject)
    if user_prompt.strip():
        user_parts = [part.strip() for part in user_prompt.split(',') if part.strip()]
        all_content.extend(user_parts)
    
    # Add generated prompt content
    if prompt.strip():
        # Clean up any style separators and split
        clean_prompt = prompt.replace(' :: ', ', ').replace('::', ', ')
        prompt_parts = [part.strip() for part in clean_prompt.split(',') if part.strip()]
        all_content.extend(prompt_parts)
    
    # Enhanced categorization with detailed subject descriptions
    subject_parts = []
    background_parts = []
    composition_parts = []
    atmosphere_parts = []
    technical_parts = []
    
    # Extract metadata tokens for richer descriptions
    tokens = context.get('tokens', {})
    
    # Add detailed subject descriptions
    if tokens.get('species') or tokens.get('archetypes'):
        subject_desc_parts = []
        
        # Species and archetype
        if tokens.get('species'):
            subject_desc_parts.extend(tokens['species'])
        if tokens.get('archetypes'):
            subject_desc_parts.extend(tokens['archetypes'])
        
        # Physical details
        if tokens.get('physiques'):
            subject_desc_parts.extend(tokens['physiques'])
        if tokens.get('conditions'):
            subject_desc_parts.extend(tokens['conditions'])
        if tokens.get('emotions'):
            subject_desc_parts.extend(tokens['emotions'])
            
        # Equipment and gear
        gear_parts = []
        if tokens.get('gear_primary'):
            gear_parts.extend([f"wielding {gear}" for gear in tokens['gear_primary']])
        if tokens.get('gear_secondary'):
            gear_parts.extend([f"carrying {gear}" for gear in tokens['gear_secondary']])
        
        # Create detailed subject description
        if subject_desc_parts:
            subject_parts.extend(subject_desc_parts)
        if gear_parts:
            subject_parts.extend(gear_parts)
    
    # Add user content and generated content with smart categorization
    for part in all_content:
        if not part:
            continue
            
        part_lower = part.lower()
        
        # Subject indicators (characters, beings, main objects)
        if any(keyword in part_lower for keyword in [
            'knight', 'warrior', 'mage', 'wizard', 'sorceress', 'battlemage', 'shadowblade',
            'elf', 'dwarf', 'human', 'orc', 'character', 'person', 'figure', 'barbarian',
            'rogue', 'paladin', 'archer', 'fighter', 'spellcaster', 'adventurer', 'hero',
            'dragon', 'beast', 'creature', 'demon', 'angel', 'spirit', 'ghost', 'elemental',
            'with', 'wearing', 'holding', 'carrying', 'wielding', 'armed with'
        ]):
            subject_parts.append(part)
            
        # Background/location indicators  
        elif any(keyword in part_lower for keyword in [
            'forest', 'mountain', 'castle', 'temple', 'landscape', 'glade', 'chapel', 'tower',
            'cathedral', 'overpass', 'cityscape', 'environment', 'background', 'scene',
            'clearing', 'alleyway', 'dungeon', 'cavern', 'ruins', 'village', 'city', 'plains',
            'desert', 'ocean', 'river', 'lake', 'valley', 'cliff', 'bridge', 'palace',
            'interior', 'exterior', 'room', 'hall', 'chamber', 'courtyard', 'garden',
            'battlefield', 'arena', 'wasteland', 'sanctuary', 'library', 'laboratory',
            'in', 'at', 'within', 'surrounded by', 'standing in'
        ]):
            background_parts.append(part)
            
        # Composition and camera work
        elif any(keyword in part_lower for keyword in [
            'shot', 'angle', 'view', 'perspective', 'composition', 'framing', 'focus',
            'close-up', 'wide shot', 'medium shot', 'portrait', 'full body', 'three-quarter view',
            'diagonal', 'centered', 'rule of thirds', 'depth of field', 'bokeh'
        ]):
            composition_parts.append(part)
            
        # Atmosphere and mood
        elif any(keyword in part_lower for keyword in [
            'lighting', 'shadows', 'glow', 'illuminated', 'dramatic', 'soft', 'harsh',
            'ambient', 'rim light', 'backlighting', 'volumetric', 'god rays',
            'moody', 'atmospheric', 'ethereal', 'mystical', 'dark', 'bright', 'vibrant',
            'muted', 'saturated', 'desaturated', 'warm', 'cool', 'color temperature'
        ]):
            atmosphere_parts.append(part)
            
        # Technical and style elements
        elif any(keyword in part_lower for keyword in [
            'style', 'art', 'painting', 'digital', 'traditional', 'concept art',
            'illustration', 'photorealistic', 'stylized', 'anime', 'realistic',
            'texture', 'brush strokes', 'rendering', 'shading', 'cel-shaded'
        ]):
            technical_parts.append(part)
            
        # Everything else goes to atmosphere
        else:
            atmosphere_parts.append(part)
    
    # Add rich background descriptions from tokens
    if tokens.get('biomes') or tokens.get('structures'):
        bg_desc_parts = []
        if tokens.get('biomes'):
            bg_desc_parts.extend([f"in {biome.replace('_', ' ')}" for biome in tokens['biomes']])
        if tokens.get('structures'):
            bg_desc_parts.extend([f"near {structure.replace('_', ' ')}" for structure in tokens['structures']])
        background_parts.extend(bg_desc_parts)
    
    # Add comprehensive atmospheric details from tokens
    if tokens.get('lighting'):
        atmosphere_parts.extend([f"{light.replace('_', ' ')} lighting" for light in tokens['lighting']])
    if tokens.get('weather'):
        atmosphere_parts.extend([f"{weather.replace('_', ' ')} weather" for weather in tokens['weather']])
    if tokens.get('time_of_day'):
        atmosphere_parts.extend([f"during {time.replace('_', ' ')}" for time in tokens['time_of_day']])
    if tokens.get('palettes'):
        atmosphere_parts.extend([f"{palette.replace('_', ' ')} color palette" for palette in tokens['palettes']])
    if tokens.get('atmosphere_mood'):
        atmosphere_parts.extend([mood.replace('_', ' ') for mood in tokens['atmosphere_mood']])
    
    # Add composition and camera details from tokens
    if tokens.get('framing'):
        composition_parts.extend([f"{frame.replace('_', ' ')} composition" for frame in tokens['framing']])
    if tokens.get('camera_styles'):
        composition_parts.extend([f"{cam.replace('_', ' ')} shot" for cam in tokens['camera_styles']])
    if tokens.get('focus_styles'):
        composition_parts.extend([focus.replace('_', ' ') for focus in tokens['focus_styles']])
    if tokens.get('depth_effects'):
        composition_parts.extend([depth.replace('_', ' ') for depth in tokens['depth_effects']])
    
    # Add technical quality from tokens  
    if tokens.get('media'):
        technical_parts.extend([f"{medium.replace('_', ' ')} style" for medium in tokens['media']])
    if tokens.get('quality_combo'):
        technical_parts.extend([quality.replace('_', ' ') for quality in tokens['quality_combo']])
    
    # Assemble final prompt in structured order:
    # quality tags → subject (detailed) → background (rich) → composition → atmosphere → technical
    parts.extend(subject_parts)
    parts.extend(background_parts)
    parts.extend(composition_parts) 
    parts.extend(atmosphere_parts)
    parts.extend(technical_parts)
    
    return ', '.join(parts)


def generate_universal_negative_prompts(context: Dict[str, Any], custom_negative: str = "") -> str:
    """Generate comprehensive universal negative prompts suitable for most models"""
    
    if custom_negative.strip():
        return custom_negative.strip()
    
    # Comprehensive negative prompts organized by category
    quality_negatives = [
        "worst quality", "low quality", "lowres", "blurry", "out of focus",
        "jpeg artifacts", "compression artifacts", "noise", "grain", "pixelated"
    ]
    
    anatomy_negatives = [
        "bad anatomy", "bad proportions", "malformed", "deformed", "disfigured",
        "extra limbs", "missing limbs", "extra arms", "missing arms", "extra legs", "missing legs",
        "bad hands", "malformed hands", "extra fingers", "missing fingers", "fused fingers",
        "bad face", "asymmetrical face", "cropped face", "distorted features"
    ]
    
    technical_negatives = [
        "watermark", "signature", "text", "logo", "copyright", "username", "artist name",
        "border", "frame", "duplicate", "error", "glitch", "broken", "incomplete"
    ]
    
    style_negatives = [
        "amateur", "sketch", "unfinished", "rough", "messy", "sloppy",
        "childish", "simple", "cartoon" if context.get('genre') not in ['anime', 'cartoon'] else ""
    ]
    
    # Filter out empty strings
    all_negatives = quality_negatives + anatomy_negatives + technical_negatives + [neg for neg in style_negatives if neg]
    
    return ', '.join(all_negatives)