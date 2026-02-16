"""
Relational weight adjustments between different dimensions
"""
from typing import List, Dict, Any
import copy

def apply_species_archetype(entries: List[Dict[str, Any]], context: Dict[str, Any], 
                           relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply species-archetype relational weighting"""
    species_tokens = context.get('tokens', {}).get('species', [])
    if not species_tokens:
        return entries
    
    relations_data = relations.get('species_archetype', {}).get('relations', [])
    if not relations_data:
        return entries
    
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        
        for species in species_tokens:
            for relation in relations_data:
                if (relation.get('species') == species and
                    relation.get('archetype') == entry_copy.get('token')):
                    multiplier = relation.get('weight_multiplier', 1.0)
                    entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                    context.setdefault('relations_applied', []).append(
                        f"species-archetype: {species} -> {entry_copy.get('token')} ({multiplier}x)"
                    )
                    break
        
        result.append(entry_copy)
    
    return result

def apply_archetype_power(entries: List[Dict[str, Any]], context: Dict[str, Any],
                         relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply archetype-power_source relational weighting"""
    archetype_tokens = context.get('tokens', {}).get('archetypes', [])
    if not archetype_tokens:
        return entries
    
    relations_data = relations.get('archetype_power_source', {}).get('relations', [])
    if not relations_data:
        return entries
    
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        
        for archetype in archetype_tokens:
            for relation in relations_data:
                if (relation.get('archetype') == archetype and
                    relation.get('power_source') == entry_copy.get('token')):
                    multiplier = relation.get('weight_multiplier', 1.0)
                    entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                    context.setdefault('relations_applied', []).append(
                        f"archetype-power: {archetype} -> {entry_copy.get('token')} ({multiplier}x)"
                    )
                    break
        
        result.append(entry_copy)
    
    return result

def apply_biome_structure(entries: List[Dict[str, Any]], context: Dict[str, Any],
                         relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply biome-structure relational weighting"""
    biome_tokens = context.get('tokens', {}).get('biomes', [])
    if not biome_tokens:
        return entries
    
    relations_data = relations.get('biome_structure', {}).get('relations', [])
    if not relations_data:
        return entries
    
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        
        for biome in biome_tokens:
            for relation in relations_data:
                if (relation.get('biome') == biome and
                    relation.get('structure') == entry_copy.get('token')):
                    multiplier = relation.get('weight_multiplier', 1.0)
                    entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                    context.setdefault('relations_applied', []).append(
                        f"biome-structure: {biome} -> {entry_copy.get('token')} ({multiplier}x)"
                    )
                    break
        
        result.append(entry_copy)
    
    return result

def apply_vibe_palette(entries: List[Dict[str, Any]], context: Dict[str, Any],
                      relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply vibe-palette relational weighting"""
    vibe = context.get('vibe')
    if not vibe:
        return entries
    
    relations_data = relations.get('vibe_palette', {}).get('relations', [])
    if not relations_data:
        return entries
    
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        
        for relation in relations_data:
            if (relation.get('vibe') == vibe and
                relation.get('palette') == entry_copy.get('token')):
                multiplier = relation.get('weight_multiplier', 1.0)
                entry_copy['weight'] = int(entry_copy.get('weight', 1) * multiplier)
                context.setdefault('relations_applied', []).append(
                    f"vibe-palette: {vibe} -> {entry_copy.get('token')} ({multiplier}x)"
                )
                break
        
        result.append(entry_copy)
    
    return result