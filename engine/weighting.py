"""
Weighting functions for applying genre, rarity, and vibe filters
"""
from typing import List, Dict, Any, Optional
import copy

def apply_rarity_and_genre_filters(entries: List[Dict[str, Any]], rarity: str, genre: str) -> List[Dict[str, Any]]:
    """Filter entries based on rarity and genre restrictions"""
    filtered = []
    
    rarity_order = ['common', 'rare', 'epic']
    min_rarity_level = rarity_order.index(rarity) if rarity in rarity_order else 0
    
    for entry in entries:
        # Check rarity minimum
        rarity_min = entry.get('rarity_min')
        if rarity_min:
            required_level = rarity_order.index(rarity_min) if rarity_min in rarity_order else 0
            if min_rarity_level < required_level:
                continue
        
        # Check rarity maximum  
        rarity_max = entry.get('rarity_max')
        if rarity_max:
            max_level = rarity_order.index(rarity_max) if rarity_max in rarity_order else len(rarity_order) - 1
            if min_rarity_level > max_level:
                continue
        
        # Check allowed genres
        allow_genres = entry.get('allow_genres', [])
        if allow_genres and genre not in allow_genres:
            continue
        
        # Check blocked genres
        block_genres = entry.get('block_genres', [])
        if block_genres and genre in block_genres:
            continue
        
        filtered.append(entry)
    
    return filtered

def apply_vibe_bias(entries: List[Dict[str, Any]], vibe: str, relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply vibe bias to palette entries"""
    if not entries:
        return entries
        
    vibe_palette_relations = relations.get('vibe_palette', {}).get('relations', [])
    
    # Create a copy to avoid modifying original entries
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        
        # Look for matching vibe-palette relation
        for relation in vibe_palette_relations:
            if (relation.get('vibe') == vibe and 
                relation.get('palette') == entry_copy.get('token')):
                multiplier = relation.get('weight_multiplier', 1.0)
                entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                break
        
        result.append(entry_copy)
    
    return result

def apply_overrides(entries: List[Dict[str, Any]], rarity: str, genre: str, 
                   rarity_overrides: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply rarity override rules"""
    if not rarity_overrides or not rarity_overrides.get('overrides'):
        return entries
    
    # Create a copy to avoid modifying original entries
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        token = entry_copy.get('token') or entry_copy.get('name', '')
        
        # Check for matching override
        for override in rarity_overrides.get('overrides', []):
            if override.get('token') == token:
                # Check if conditions match
                target_rarity = override.get('rarity')
                target_genre = override.get('genre')
                
                conditions_match = True
                if target_rarity and target_rarity != rarity:
                    conditions_match = False
                if target_genre and target_genre != genre:
                    conditions_match = False
                
                if conditions_match:
                    # Apply weight multiplier
                    multiplier = override.get('weight_multiplier', 1.0)
                    entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                    break
        
        result.append(entry_copy)
    
    return result