"""
Configuration loader for YAML files
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any

def read_yaml(file_path: str) -> Dict[str, Any]:
    """Read and parse a YAML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Failed to load {file_path}: {e}")
        return {}

def ensure_array(value: Any) -> List[Any]:
    """Ensure a value is an array"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def load_all_config(root_dir: str) -> Dict[str, Any]:
    """Load all configuration files from the root directory"""
    root_path = Path(root_dir)
    
    # Directory paths
    meta_dir = root_path / 'config' / 'meta'
    style_dir = root_path / 'config' / 'style'  
    subjects_dir = root_path / 'config' / 'subjects'
    env_dir = root_path / 'config' / 'environments'
    composition_dir = root_path / 'config' / 'composition'
    plans_dir = root_path / 'plans'
    data_dir = root_path / 'data'
    
    # Load meta configs
    meta = {
        'genres': read_yaml(str(meta_dir / 'genre_selector.yaml')),
        'rarities': read_yaml(str(meta_dir / 'rarity_tiers.yaml')),
        'rarity_overrides': read_yaml(str(meta_dir / 'rarity_override.yaml')),
        'content_types': read_yaml(str(meta_dir / 'content_type_selector.yaml')),
        'vibes': read_yaml(str(meta_dir / 'vibe_selector.yaml')),
        'safety': read_yaml(str(meta_dir / 'safety_flags.yaml')),
        'synonyms': read_yaml(str(meta_dir / 'synonyms.yaml')),
        'complexity': read_yaml(str(meta_dir / 'complexity_rules.yaml')),
        'model_profiles': read_yaml(str(meta_dir / 'model_profiles.yaml')),
        'negative_prompts': read_yaml(str(meta_dir / 'negative_prompts.yaml')),
    }
    
    # Load relations
    relations = {
        'species_archetype': read_yaml(str(meta_dir / 'relations_species_archetype_bias.yaml')),
        'archetype_power_source': read_yaml(str(meta_dir / 'relations_archetype_power_source_bias.yaml')),
        'biome_structure': read_yaml(str(meta_dir / 'relations_biome_structure_bias.yaml')),
        'vibe_palette': read_yaml(str(meta_dir / 'relations_vibe_palette_bias.yaml')),
        'conflicts': read_yaml(str(meta_dir / 'relations_negative_conflicts.yaml')),
    }
    
    # Pool files mapping
    pool_files = {
        'species': 'species.yaml',
        'archetypes': 'archetypes.yaml',
        'physiques': 'physiques.yaml',
        'emotions': 'emotions.yaml',
        'conditions': 'conditions.yaml',
        'power_sources': 'power_sources.yaml',
        'gear_primary': 'gear_primary.yaml',
        'gear_secondary': 'gear_secondary.yaml',
        'modifiers': 'modifiers_general.yaml',
        'biomes': 'biomes.yaml',
        'structures': 'structures.yaml',
        'atmosphere_mood': 'atmosphere_mood.yaml',
        'weather': 'weather.yaml',
        'time_of_day': 'time_of_day.yaml',
        'special_fx': 'special_fx.yaml',
        'palettes': 'color_palettes.yaml',
        'lighting': 'lighting_styles.yaml',
        'camera': 'camera_styles.yaml',
        'media': 'medium_textures.yaml',
        'quality_combo': 'style_quality_combo.yaml',
        'depth_effects': 'depth_effects.yaml',
        'framing': 'framing.yaml',
        'focus_styles': 'focus_styles.yaml',
    }
    
    # Load pools from appropriate directories
    pools = {}
    for key, filename in pool_files.items():
        # Determine base directory for each pool type
        if key in ['biomes', 'structures', 'atmosphere_mood', 'weather', 'time_of_day', 'special_fx']:
            base_dir = env_dir
        elif key in ['palettes', 'lighting', 'camera', 'media', 'quality_combo']:
            base_dir = style_dir / 'style'
        elif key in ['depth_effects', 'framing', 'focus_styles']:
            base_dir = composition_dir
        elif key in ['species', 'archetypes', 'physiques', 'emotions', 'conditions', 
                     'power_sources', 'gear_primary', 'gear_secondary', 'modifiers']:
            base_dir = subjects_dir / 'subjects'
        else:
            base_dir = composition_dir
        
        pools[key] = read_yaml(str(base_dir / filename))
    
    # Load pipeline and hybrid plans
    pipeline = read_yaml(str(plans_dir / 'generation_pipeline.yaml'))
    hybrid = read_yaml(str(plans_dir / 'hybrid_subject_selector.yaml'))
    
    # Load legacy data
    legacy_subjects_raw = read_yaml(str(data_dir / 'subject_core_legacy.yaml'))
    legacy_land_raw = read_yaml(str(data_dir / 'landscape_core_legacy.yaml'))
    legacy_fin_raw = read_yaml(str(data_dir / 'env_style_finish_legacy.yaml'))
    
    legacy = {
        'subjects': ensure_array(legacy_subjects_raw.get('subjects', [])),
        'landscapes': ensure_array(legacy_land_raw.get('landscapes', [])),
        'finishers': ensure_array(legacy_fin_raw.get('finishers', [])),
    }
    
    return {
        'root_dir': root_dir,
        'meta': meta,
        'relations': relations,
        'pools': pools,
        'pipeline': pipeline,
        'hybrid': hybrid.get('hybrid_plan', {}),
        'legacy': legacy
    }