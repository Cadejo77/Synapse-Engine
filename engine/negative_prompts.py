"""
Negative prompt generation utilities
"""
from typing import Dict, Any, List
from .utils import weighted_random

def generate_negative_prompts(context: Dict[str, Any], cfg: Dict[str, Any], 
                             model_profile: str = "sdxl", custom_negative: str = "") -> str:
    """Generate negative prompts based on model profile and context"""
    
    model_profiles = cfg.get('meta', {}).get('model_profiles', {}).get('model_profiles', {})
    profile_data = model_profiles.get(model_profile, {})
    
    # Start with model-specific defaults
    negative_parts = profile_data.get('default_negative_prompts', []).copy()
    
    # Add custom negative if provided
    if custom_negative.strip():
        custom_parts = [part.strip() for part in custom_negative.split(',') if part.strip()]
        negative_parts.extend(custom_parts)
    
    # If model doesn't support negatives, return empty or custom only
    if not profile_data.get('supports_negative_prompts', True):
        return custom_negative.strip()
    
    # Add context-specific negatives from pools
    negative_pools = cfg.get('meta', {}).get('negative_prompts', {}).get('negative_prompts', {})
    
    if negative_pools:
        # Select from different categories
        for category, items in negative_pools.items():
            if isinstance(items, list) and items:
                # Simple random selection from each category
                selected = weighted_random(items, context.get('rng'))
                if selected and selected.get('token'):
                    negative_parts.append(selected['token'])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_parts = []
    for part in negative_parts:
        if part not in seen:
            seen.add(part)
            unique_parts.append(part)
    
    return ', '.join(unique_parts)