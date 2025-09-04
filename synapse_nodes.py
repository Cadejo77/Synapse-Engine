import os
import yaml
import random
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# ComfyUI imports - only import when running in ComfyUI
try:
    import folder_paths
    COMFYUI_AVAILABLE = True
except ImportError:
    COMFYUI_AVAILABLE = False

class SynapsePromptGenerator:
    """
    Python translation of the TypeScript PromptGenerator class.
    Loads YAML configurations and generates compositional prompts.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.config = self.load_all_config()
    
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load a YAML file and return its contents."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing YAML: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def ensure_array(self, value: Any) -> List[Any]:
        """Ensure a value is a list."""
        return value if isinstance(value, list) else []
    
    def load_all_config(self) -> Dict[str, Any]:
        """Load all YAML configuration files."""
        meta_dir = os.path.join(self.root_dir, 'config/meta')
        style_dir = os.path.join(self.root_dir, 'config/style')
        subjects_dir = os.path.join(self.root_dir, 'config/subjects')
        env_dir = os.path.join(self.root_dir, 'config/environments')
        composition_dir = os.path.join(self.root_dir, 'config/composition')
        plans_dir = os.path.join(self.root_dir, 'plans')
        data_dir = os.path.join(self.root_dir, 'data')
        
        # Load meta configuration
        meta = {
            'genres': self.load_yaml(os.path.join(meta_dir, 'genre_selector.yaml')),
            'rarities': self.load_yaml(os.path.join(meta_dir, 'rarity_tiers.yaml')),
            'rarity_overrides': self.load_yaml(os.path.join(meta_dir, 'rarity_override.yaml')),
            'content_types': self.load_yaml(os.path.join(meta_dir, 'content_type_selector.yaml')),
            'vibes': self.load_yaml(os.path.join(meta_dir, 'vibe_selector.yaml')),
            'safety': self.load_yaml(os.path.join(meta_dir, 'safety_flags.yaml')),
            'synonyms': self.load_yaml(os.path.join(meta_dir, 'synonyms.yaml')),
            'complexity': self.load_yaml(os.path.join(meta_dir, 'complexity_rules.yaml')),
        }
        
        # Load relations
        relations = {
            'species_archetype': self.load_yaml(os.path.join(meta_dir, 'relations_species_archetype_bias.yaml')),
            'archetype_power_source': self.load_yaml(os.path.join(meta_dir, 'relations_archetype_power_source_bias.yaml')),
            'biome_structure': self.load_yaml(os.path.join(meta_dir, 'relations_biome_structure_bias.yaml')),
            'vibe_palette': self.load_yaml(os.path.join(meta_dir, 'relations_vibe_palette_bias.yaml')),
            'conflicts': self.load_yaml(os.path.join(meta_dir, 'relations_negative_conflicts.yaml')),
        }
        
        # Define pool files mapping
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
            'depth_effects': 'depth_effects.yaml',
            'framing': 'framing.yaml',
            'focus_styles': 'focus_styles.yaml',
            'quality_combo': 'style_quality_combo.yaml'
        }
        
        # Load all pools with correct directory mapping
        pools = {}
        for key, filename in pool_files.items():
            if key in ['biomes', 'structures', 'atmosphere_mood', 'weather', 'time_of_day', 'special_fx']:
                base_dir = env_dir
            elif key in ['palettes', 'lighting', 'camera', 'media', 'quality_combo']:
                base_dir = os.path.join(style_dir, 'style')
            elif key in ['depth_effects', 'framing', 'focus_styles']:
                base_dir = composition_dir
            elif key in ['species', 'archetypes', 'physiques', 'emotions', 'conditions', 'power_sources', 'gear_primary', 'gear_secondary', 'modifiers']:
                base_dir = os.path.join(subjects_dir, 'subjects')
            else:
                base_dir = composition_dir
            
            pools[key] = self.load_yaml(os.path.join(base_dir, filename))
        
        # Load pipeline and plans
        pipeline = self.load_yaml(os.path.join(plans_dir, 'generation_pipeline.yaml'))
        hybrid = self.load_yaml(os.path.join(plans_dir, 'hybrid_subject_selector.yaml'))
        
        # Load legacy data
        legacy_subjects_raw = self.load_yaml(os.path.join(data_dir, 'subject_core_legacy.yaml'))
        legacy_land_raw = self.load_yaml(os.path.join(data_dir, 'landscape_core_legacy.yaml'))
        legacy_fin_raw = self.load_yaml(os.path.join(data_dir, 'env_style_finish_legacy.yaml'))
        
        legacy = {
            'subjects': self.ensure_array(legacy_subjects_raw.get('subjects', [])),
            'landscapes': self.ensure_array(legacy_land_raw.get('landscapes', [])),
            'finishers': self.ensure_array(legacy_fin_raw.get('finishers', []))
        }
        
        return {
            'root_dir': self.root_dir,
            'meta': meta,
            'relations': relations,
            'pools': pools,
            'pipeline': pipeline.get('pipeline', {}),
            'hybrid': hybrid.get('hybrid_plan', {}),
            'legacy': legacy
        }
    
    def weighted_random(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select a random item based on weights."""
        if not items:
            return {}
        
        total = sum(item.get('weight', 0) for item in items)
        if total <= 0:
            return items[0] if items else {}
        
        r = random.random() * total
        for item in items:
            r -= item.get('weight', 0)
            if r <= 0:
                return item
        
        return items[-1] if items else {}
    
    def pick_genre(self) -> str:
        """Pick a random genre."""
        genres = self.config['meta']['genres'].get('genres', [])
        genre_pick = self.weighted_random(genres)
        return genre_pick.get('token', 'fantasy')
    
    def pick_rarity(self) -> str:
        """Pick a random rarity."""
        rarities = self.config['meta']['rarities'].get('rarities', [])
        rarity_pick = self.weighted_random(rarities)
        return rarity_pick.get('rarity', 'common')
    
    def pick_vibe(self) -> str:
        """Pick a random vibe."""
        vibes = self.config['meta']['vibes'].get('vibes', [])
        vibe_pick = self.weighted_random(vibes)
        return vibe_pick.get('token', 'mystical')
    
    def pick_content_type(self) -> str:
        """Pick a random content type."""
        content_types = self.config['meta']['content_types'].get('content_types', [])
        ct_pick = self.weighted_random(content_types)
        return ct_pick.get('type', 'figure')
    
    def get_complexity_budget(self, rarity: str) -> int:
        """Get complexity budget for a rarity."""
        complexity_config = self.config['meta']['complexity']
        complexity_rules = complexity_config.get('complexity', {})
        budgets = complexity_rules.get('rarity_budgets', {})
        default_budget = complexity_rules.get('default_budget', 10)
        return budgets.get(rarity, default_budget)
    
    def apply_rarity_and_genre_filters(self, candidates: List[Dict[str, Any]], rarity: str, genre: str) -> List[Dict[str, Any]]:
        """Filter candidates based on rarity and genre constraints."""
        rarity_order = {'common': 0, 'rare': 1, 'epic': 2}
        current_rarity_level = rarity_order.get(rarity, 0)
        
        filtered = []
        for candidate in candidates:
            # Check rarity constraints
            rarity_min = candidate.get('rarity_min')
            rarity_max = candidate.get('rarity_max')
            
            if rarity_min and rarity_order.get(rarity_min, 0) > current_rarity_level:
                continue
            if rarity_max and rarity_order.get(rarity_max, 2) < current_rarity_level:
                continue
            
            # Check genre constraints
            allow_genres = candidate.get('allow_genres', [])
            block_genres = candidate.get('block_genres', [])
            
            if allow_genres and genre not in allow_genres:
                continue
            if block_genres and genre in block_genres:
                continue
            
            filtered.append(candidate.copy())
        
        return filtered
    
    def apply_vibe_bias(self, candidates: List[Dict[str, Any]], vibe: str) -> List[Dict[str, Any]]:
        """Apply vibe bias to candidate weights."""
        for candidate in candidates:
            vibe_bias = candidate.get('vibe_bias')
            if vibe_bias == vibe:
                candidate['weight'] = candidate.get('weight', 1) * 2.0
        return candidates
    
    def apply_relations(self, dimension: str, chosen_token: str, candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Apply relational biases to candidates."""
        applied_relations = []
        
        if dimension == 'archetypes' and chosen_token:
            relations = self.config['relations']['species_archetype'].get('relations', [])
            for rel in relations:
                if rel.get('species') == chosen_token:
                    archetype = rel.get('archetype', '')
                    multiplier = rel.get('weight_multiplier', 1.0)
                    for candidate in candidates:
                        if candidate.get('token') == archetype or candidate.get('name') == archetype:
                            candidate['weight'] = candidate.get('weight', 1) * multiplier
                            applied_relations.append(f"species->archetype bias: {chosen_token}->{archetype} (*{multiplier})")
        
        elif dimension == 'power_sources':
            # Get the chosen archetype
            archetype_token = None  # This would need to be passed from context
            relations = self.config['relations']['archetype_power_source'].get('relations', [])
            for rel in relations:
                if rel.get('archetype') == archetype_token:
                    power = rel.get('power_source', '')
                    multiplier = rel.get('weight_multiplier', 1.0)
                    for candidate in candidates:
                        if candidate.get('token') == power or candidate.get('name') == power:
                            candidate['weight'] = candidate.get('weight', 1) * multiplier
                            applied_relations.append(f"archetype->power bias: {archetype_token}->{power} (*{multiplier})")
        
        return candidates, applied_relations
    
    def choose_from_pool(self, context: Dict[str, Any], dimension: str, required: bool) -> List[str]:
        """Choose tokens from a specific dimension pool."""
        pool = self.config['pools'].get(dimension, {})
        pool_items = pool.get(dimension, [])
        
        if not pool_items:
            if required:
                context['warnings'].append(f"No items found in required pool: {dimension}")
            return []
        
        # Apply filters
        candidates = self.apply_rarity_and_genre_filters(pool_items, context['rarity'], context['genre'])
        candidates = self.apply_vibe_bias(candidates, context['vibe'])
        
        if not candidates:
            if required:
                context['warnings'].append(f"All candidates filtered out for required {dimension}")
            return []
        
        # Get pool metadata for selection parameters
        metadata = pool.get('metadata', {})
        choose_min = metadata.get('choose_min', 1 if required else 0)
        choose_max = metadata.get('choose_max', 1)
        probability = metadata.get('choose_probability', 1.0)
        second_chance = metadata.get('second_pick_chance', 0.0)
        
        if random.random() > probability:
            return []
        
        chosen = []
        attempts = 0
        while len(chosen) < choose_max and attempts < choose_max * 6:
            attempts += 1
            
            # Apply diminishing returns if multiple picks
            cand_copy = [c.copy() for c in candidates]
            if len(chosen) > 0 and choose_max > 1:
                diminishing_factor = 0.65
                for c in cand_copy:
                    c['weight'] = max(1, round(c['weight'] * (diminishing_factor ** len(chosen))))
            
            pick = self.weighted_random(cand_copy)
            if not pick:
                break
            
            # Check complexity budget
            cost = pick.get('complexity_cost', 1)
            if context['complexity_used'] + cost > context['budget']:
                break
            
            token = pick.get('token', pick.get('name', ''))
            if token:
                chosen.append(token)
                context['complexity_used'] += cost
                
                # Remove from candidates to avoid duplicates
                candidates = [c for c in candidates if c.get('token') != token and c.get('name') != token]
            
            if not candidates:
                break
            
            # Second chance logic
            if len(chosen) >= choose_min and len(chosen) < choose_max:
                if random.random() > second_chance:
                    break
        
        if chosen:
            context['tokens'][dimension] = chosen
        elif required:
            context['warnings'].append(f"Failed to select required items for {dimension}")
        
        return chosen
    
    def normalize_tokens(self, tokens: List[str]) -> List[str]:
        """Normalize tokens using synonyms configuration."""
        synonyms_config = self.config['meta']['synonyms']
        normalization = synonyms_config.get('normalization', {})
        synonyms = synonyms_config.get('synonyms', {})
        
        normalized = []
        for token in tokens:
            t = token
            if normalization.get('lowercase'):
                t = t.lower()
            if normalization.get('replace_spaces_with_underscores'):
                t = t.replace(' ', '_')
            
            # Check synonyms
            for canonical, variants in synonyms.items():
                if t == canonical:
                    t = canonical
                    break
                elif t in variants:
                    t = canonical
                    break
            
            normalized.append(t)
        
        return normalized
    
    def assemble_prompt(self, context: Dict[str, Any]) -> str:
        """Assemble the final prompt from context tokens."""
        if context.get('mode') == 'legacy' and context.get('chosen_legacy'):
            return context['chosen_legacy']
        
        def list_or_empty(key: str, joiner: str = ", ") -> str:
            tokens = context['tokens'].get(key, [])
            return joiner.join(tokens) if tokens else ""
        
        def rarity_adjective(r: str) -> str:
            adjectives = {
                'common': '',
                'rare': 'rare ',
                'epic': 'legendary '
            }
            return adjectives.get(r, '')
        
        if context['content_type'] in ['figure', 'hybrid']:
            # Figure templates
            templates = [
                "A {rarityAdj}{physique}{species} {archetype}{power_source}{modifiers} {gear_primary}{gear_secondary}, {emotion}{condition}",
                "{rarityAdj}{species} {archetype}{power_source}{modifiers}, bearing {gear_primary}{gear_secondary}, {emotion}{condition}"
            ]
            template = random.choice(templates)
            
            species = list_or_empty('species', ' ')
            archetype = list_or_empty('archetypes', ' ')
            physique = list_or_empty('physiques', ' ')
            power = list_or_empty('power_sources', ' & ')
            mods = list_or_empty('modifiers', ', ')
            gp = list_or_empty('gear_primary', ' & ')
            gs = list_or_empty('gear_secondary', ' & ')
            emotion = list_or_empty('emotions', ' ')
            condition = list_or_empty('conditions', ' ')
            
            result = template.format(
                rarityAdj=rarity_adjective(context['rarity']),
                physique=physique + ' ' if physique else '',
                species=species,
                archetype=' ' + archetype if archetype else '',
                power_source=' empowered by ' + power if power else '',
                modifiers=' adorned with ' + mods if mods else '',
                gear_primary=gp,
                gear_secondary=' + ' + gs if gs else '',
                emotion=emotion,
                condition=' (' + condition + ')' if condition else ''
            )
        
        else:  # landscape
            templates = [
                "A {rarityAdj}{biomes}{structures}{atmosphere_mood}{weather}{time_of_day}{special_fx}",
                "{rarityAdj}{biomes} scene{structures}{atmosphere_mood}{time_of_day}{special_fx}"
            ]
            template = random.choice(templates)
            
            biome = list_or_empty('biomes', ' ')
            structure = list_or_empty('structures', ' ')
            mood = list_or_empty('atmosphere_mood', ', ')
            weather = list_or_empty('weather', ' ')
            tod = list_or_empty('time_of_day', ' ')
            fx = list_or_empty('special_fx', ', ')
            
            result = template.format(
                rarityAdj=rarity_adjective(context['rarity']),
                biomes=biome,
                structures=' with ' + structure if structure else '',
                atmosphere_mood=' under ' + mood if mood else '',
                weather=' ' + weather if weather else '',
                time_of_day=' at ' + tod if tod else '',
                special_fx=' featuring ' + fx if fx else ''
            )
        
        # Clean up multiple spaces
        import re
        result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    def make_tags_header(self, context: Dict[str, Any]) -> str:
        """Create metadata tags header."""
        tags = []
        tags.append(f"/genre:{context['genre']}/")
        tags.append(f"/rarity:{context['rarity']}/")
        tags.append(f"/vibe:{context['vibe']}/")
        tags.append(f"/mode:{context.get('mode', 'compositional')}/")
        tags.append(f"/type:{context['content_type']}/")
        
        # Add token tags for chosen items
        for key, tokens in context['tokens'].items():
            if tokens:
                tags.append(f"/{key}:{','.join(tokens[:2])}/")  # Limit to first 2 tokens
        
        return ' '.join(tags)
    
    def generate_one(self) -> Dict[str, Any]:
        """Generate a single prompt with metadata."""
        # Initialize generation context
        context = {
            'genre': self.pick_genre(),
            'rarity': self.pick_rarity(),
            'vibe': self.pick_vibe(),
            'content_type': self.pick_content_type(),
            'tokens': {},
            'warnings': [],
            'relations_applied': [],
            'complexity_used': 0,
            'budget': 0,
            'mode': 'compositional',
            'chosen_legacy': None
        }
        
        context['budget'] = self.get_complexity_budget(context['rarity'])
        
        # Check for legacy mode
        pipeline = self.config['pipeline']
        legacy_probability = pipeline.get('legacy_probability', 0.1)
        
        if random.random() < legacy_probability:
            context['mode'] = 'legacy'
            if context['content_type'] == 'figure':
                legacy_subjects = self.config['legacy']['subjects']
                if legacy_subjects:
                    context['chosen_legacy'] = random.choice(legacy_subjects)
            else:
                legacy_landscapes = self.config['legacy']['landscapes']
                if legacy_landscapes:
                    context['chosen_legacy'] = random.choice(legacy_landscapes)
            
            # Add finisher
            legacy_finishers = self.config['legacy']['finishers']
            if legacy_finishers and context['chosen_legacy']:
                finisher = random.choice(legacy_finishers)
                if isinstance(finisher, dict):
                    finisher_text = finisher.get('text', finisher.get('token', ''))
                else:
                    finisher_text = str(finisher)
                context['chosen_legacy'] += " :: " + finisher_text
        
        else:
            # Compositional mode
            if context['content_type'] == 'figure':
                # Required figure dimensions
                required_dims = pipeline.get('figure_dimensions', {}).get('required', [])
                for dim in required_dims:
                    self.choose_from_pool(context, dim, True)
                
                # Optional figure dimensions  
                optional_dims = pipeline.get('figure_dimensions', {}).get('optional', [])
                for dim in optional_dims:
                    self.choose_from_pool(context, dim, False)
            
            elif context['content_type'] == 'landscape':
                # Required landscape dimensions
                required_dims = pipeline.get('landscape_dimensions', {}).get('required', [])
                for dim in required_dims:
                    self.choose_from_pool(context, dim, True)
                
                # Optional landscape dimensions
                optional_dims = pipeline.get('landscape_dimensions', {}).get('optional', [])
                for dim in optional_dims:
                    self.choose_from_pool(context, dim, False)
            
            # Style dimensions for both types
            style_dims = pipeline.get('style_dimensions', {}).get('order', [])
            for dim in style_dims:
                self.choose_from_pool(context, dim, False)
        
        # Normalize all tokens
        for key, tokens in context['tokens'].items():
            context['tokens'][key] = self.normalize_tokens(tokens)
        
        # Assemble final prompt
        prompt_core = self.assemble_prompt(context)
        tags_header = self.make_tags_header(context)
        
        full_prompt = f"{tags_header} {prompt_core}".strip()
        
        return {
            'prompt': full_prompt,
            'tags_header': tags_header,
            'metadata': context
        }
    
    def generate(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple prompts."""
        return [self.generate_one() for _ in range(count)]


class SynapseGeneratorNode:
    """
    ComfyUI custom node for Synapse prompt generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 10}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "Synapse"
    
    def __init__(self):
        # Get the path to this custom node directory
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.generator = None
    
    def generate_prompt(self, count: int = 1, seed: int = -1):
        """Generate prompt using Synapse Engine."""
        try:
            # Initialize generator if needed
            if self.generator is None:
                self.generator = SynapsePromptGenerator(self.root_dir)
            
            # Set seed if provided
            if seed != -1:
                random.seed(seed)
            
            # Generate prompts
            results = self.generator.generate(count)
            
            # Return the first prompt (ComfyUI expects single string output)
            if results:
                return (results[0]['prompt'],)
            else:
                return ("Error: No prompt generated",)
                
        except Exception as e:
            return (f"Error: {str(e)}",)


# ComfyUI node registration
NODE_CLASS_MAPPINGS = {
    "SynapseGeneratorNode": SynapseGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapseGeneratorNode": "Synapse Prompt Generator"
}