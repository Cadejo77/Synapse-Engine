"""
Main prompt generator class
"""
from typing import Dict, Any, List, Optional
import copy

from .utils import DeterministicRandom, weighted_random
from .weighting import apply_rarity_and_genre_filters, apply_vibe_bias, apply_overrides
from .relations import apply_species_archetype, apply_archetype_power, apply_biome_structure, apply_vibe_palette
from .conflicts import apply_conflict_rules
from .complexity import get_cost, get_rarity_budget, check_budget_available, consume_budget
from .safety import categorize_tokens, violates_policy, apply_safety_filter
from .synonyms import normalize_all
from .prompt_assembler import assemble_prompt, assemble_style, make_tags_header

class PromptGenerator:
    """Main prompt generator using YAML configuration"""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None, 
                 explicit_content: str = "disabled", fixed_genre: str = "random"):
        self.cfg = config
        self.rng = DeterministicRandom(seed)
        self.explicit_content = explicit_content
        self.fixed_genre = fixed_genre
    
    def pick_genre(self, fixed_genre: str = "random") -> str:
        """Pick a genre - either random or fixed"""
        if fixed_genre != "random":
            return fixed_genre
            
        genres = self.cfg.get('meta', {}).get('genres', {}).get('genres', [])
        if not genres:
            return 'fantasy'
        
        genre_pick = weighted_random(genres, self.rng)
        return genre_pick.get('token', 'fantasy') if genre_pick else 'fantasy'
    
    def pick_rarity(self) -> str:
        """Pick a random rarity"""
        rarities = self.cfg.get('meta', {}).get('rarities', {}).get('rarities', [])
        if not rarities:
            return 'common'
        
        rarity_pick = weighted_random(rarities, self.rng)
        return rarity_pick.get('rarity', 'common') if rarity_pick else 'common'
    
    def pick_vibe(self) -> str:
        """Pick a random vibe"""
        vibes = self.cfg.get('meta', {}).get('vibes', {}).get('vibes', [])
        if not vibes:
            return 'neutral'
        
        vibe_pick = weighted_random(vibes, self.rng)
        return vibe_pick.get('token', 'neutral') if vibe_pick else 'neutral'
    
    def pick_content_type(self) -> str:
        """Pick a random content type"""
        content_types = self.cfg.get('meta', {}).get('content_types', {}).get('content_types', [])
        if not content_types:
            return 'figure'
        
        ct_pick = weighted_random(content_types, self.rng)
        return ct_pick.get('type', 'figure') if ct_pick else 'figure'
    
    def extract_array(self, pools: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
        """Extract array from pool data, handling different possible key formats"""
        pool_data = pools.get(key, {})
        if not pool_data:
            return []
        
        # Try different possible keys
        possible_keys = [key, key.rstrip('s')]
        for k in possible_keys:
            if k in pool_data and isinstance(pool_data[k], list):
                return pool_data[k]
        
        # If no matching key, try any array value
        for v in pool_data.values():
            if isinstance(v, list):
                return v
        
        return []
    
    def weighted_sample(self, entries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sample a weighted entry from the list"""
        return weighted_random(entries, self.rng)
    
    def choose_from_pool(self, context: Dict[str, Any], dim: str, required: bool, 
                        complexity_rules: Dict[str, Any]) -> None:
        """Choose tokens from a dimension pool"""
        # Get candidates from pool
        candidates = self.extract_array(self.cfg.get('pools', {}), dim)
        if not candidates:
            if required:
                context.setdefault('warnings', []).append(f"No candidates found for required {dim}")
            return
        
        # Apply filters
        candidates = apply_rarity_and_genre_filters(candidates, context.get('rarity', 'common'), 
                                                   context.get('genre', 'fantasy'))
        
        # Apply relational biases
        if dim == 'archetypes':
            candidates = apply_species_archetype(candidates, context, self.cfg.get('relations', {}))
        elif dim == 'power_sources':
            candidates = apply_archetype_power(candidates, context, self.cfg.get('relations', {}))
        elif dim == 'structures':
            candidates = apply_biome_structure(candidates, context, self.cfg.get('relations', {}))
        elif dim == 'palettes':
            candidates = apply_vibe_palette(candidates, context, self.cfg.get('relations', {}))
        
        # Apply vibe bias for palettes
        if dim == 'palettes':
            candidates = apply_vibe_bias(candidates, context.get('vibe', ''), self.cfg.get('relations', {}))
        
        # Apply overrides
        candidates = apply_overrides(candidates, context.get('rarity', 'common'), 
                                   context.get('genre', 'fantasy'), 
                                   self.cfg.get('meta', {}).get('rarity_overrides', {}))
        
        # Apply conflict rules
        candidates = apply_conflict_rules(candidates, context, self.cfg.get('relations', {}))
        
        if not candidates:
            if required:
                context.setdefault('warnings', []).append(f"All candidates filtered out for required {dim}")
            return
        
        # Get pool metadata for selection parameters
        pool_meta = self.cfg.get('pools', {}).get(dim, {}).get('metadata', {})
        choose_min = pool_meta.get('choose_min', 1 if required else 0)
        choose_max = pool_meta.get('choose_max', 1)
        probability = pool_meta.get('choose_probability', 1.0)
        second_chance = pool_meta.get('second_pick_chance', 0.0)
        
        complexity_data = self.cfg.get('meta', {}).get('complexity', {}).get('complexity', {})
        diminishing_factor = (pool_meta.get('diminishing_factor') or 
                             complexity_data.get('modifier_cost_scale', {}).get('diminishing_factor', 0.65))
        
        # Check probability
        if self.rng.random() > probability:
            return
        
        chosen = []
        attempts = 0
        max_attempts = choose_max * 6
        
        while len(chosen) < choose_max and attempts < max_attempts:
            attempts += 1
            
            # Create copy of candidates with adjusted weights for diminishing returns
            cand_copy = copy.deepcopy(candidates)
            if len(chosen) > 0 and choose_max > 1:
                for c in cand_copy:
                    c['weight'] = max(1, round(c['weight'] * (diminishing_factor ** len(chosen))))
            
            # Select candidate
            pick = self.weighted_sample(cand_copy)
            if not pick:
                break
            
            # Check complexity budget
            cost = get_cost(pick, complexity_rules)
            if not check_budget_available(context, cost, complexity_rules):
                break
            
            # Add to chosen
            token = pick.get('token') or pick.get('name', '')
            chosen.append(token)
            consume_budget(context, cost)
            
            # Remove from candidates to avoid duplicates
            candidates = [c for c in candidates if (c.get('token') or c.get('name', '')) != token]
            
            # Check if we should continue
            if len(chosen) >= choose_min and len(chosen) < choose_max:
                if self.rng.random() > second_chance:
                    break
            
            if not candidates:
                break
        
        # Store results
        if chosen:
            context.setdefault('tokens', {})[dim] = chosen
        elif required:
            context.setdefault('warnings', []).append(f"Failed to select required items for {dim}")
    
    def legacy_pick(self, context: Dict[str, Any]) -> None:
        """Pick from legacy fused lines"""
        content_type = context.get('content_type', 'figure')
        
        if content_type == 'figure':
            legacy_lines = self.cfg.get('legacy', {}).get('subjects', [])
        else:
            legacy_lines = self.cfg.get('legacy', {}).get('landscapes', [])
        
        if legacy_lines:
            chosen_line = self.weighted_legacy_line(legacy_lines)
            if chosen_line:
                context['chosen_legacy'] = chosen_line
                
                # Add finisher if available
                finishers = self.cfg.get('legacy', {}).get('finishers', [])
                if finishers:
                    finisher = self.pick_finisher()
                    if finisher:
                        context['chosen_legacy'] += " :: " + finisher
    
    def weighted_legacy_line(self, lines: List[str]) -> Optional[str]:
        """Parse and select a weighted legacy line"""
        if not lines:
            return None
        
        parsed = []
        for line in lines:
            # Parse format: "weight, text"
            if ',' in line:
                parts = line.split(',', 1)
                try:
                    weight = int(parts[0].strip())
                    text = parts[1].strip()
                    parsed.append({'weight': weight, 'text': text})
                except ValueError:
                    continue
        
        if not parsed:
            return lines[-1] if lines else None
        
        pick = weighted_random(parsed, self.rng)
        return pick.get('text', '') if pick else None
    
    def pick_finisher(self) -> Optional[str]:
        """Pick a random finisher from legacy data"""
        finishers = self.cfg.get('legacy', {}).get('finishers', [])
        if not finishers:
            return None
        
        pick = weighted_random(finishers, self.rng)
        return pick.get('text', '') if pick else None
    
    def generate_one(self) -> Dict[str, Any]:
        """Generate a single prompt result"""
        # Pick basic parameters
        genre = self.pick_genre(self.fixed_genre)
        rarity = self.pick_rarity()
        vibe = self.pick_vibe()
        content_type = self.pick_content_type()
        
        pipeline = self.cfg.get('pipeline', {}).get('pipeline', {})
        complexity_rules = self.cfg.get('meta', {}).get('complexity', {})
        
        # Determine mode (compositional vs legacy)
        compositional_chance = pipeline.get('mode_selector', {}).get('compositional_chance', 0.7)
        is_compositional = self.rng.random() < compositional_chance
        
        # Initialize context
        context = {
            'genre': genre,
            'rarity': rarity,
            'vibe': vibe,
            'content_type': content_type,
            'tokens': {},
            'complexity_used': 0,
            'budget': get_rarity_budget(rarity, complexity_rules),
            'warnings': [],
            'relations_applied': [],
            'conflicts_applied': [],
            'mode': 'compositional' if is_compositional else 'legacy',
            'rng': self.rng,
        }
        
        if not is_compositional:
            # Legacy mode
            self.legacy_pick(context)
        else:
            # Compositional mode
            fig_dims = pipeline.get('figure_dimensions', {})
            land_dims = pipeline.get('landscape_dimensions', {})
            style_dims = pipeline.get('style_dimensions', {})
            rarity_rules = pipeline.get('rarity_rules', {})
            
            # Choose dimensions based on content type
            if content_type in ['figure', 'hybrid']:
                for dim in fig_dims.get('required', []):
                    self.choose_from_pool(context, dim, True, complexity_rules)
                for dim in fig_dims.get('optional', []):
                    self.choose_from_pool(context, dim, False, complexity_rules)
            
            elif content_type == 'landscape':
                for dim in land_dims.get('required', []):
                    self.choose_from_pool(context, dim, True, complexity_rules)
                for dim in land_dims.get('optional', []):
                    self.choose_from_pool(context, dim, False, complexity_rules)
            
            # Add style dimensions
            for dim in style_dims.get('order', []):
                self.choose_from_pool(context, dim, False, complexity_rules)
            
            # Special rarity rules
            if (rarity == 'epic' and rarity_rules.get('epic_adds_depth_effects') and
                'depth_effects' not in context.get('tokens', {})):
                self.choose_from_pool(context, 'depth_effects', False, complexity_rules)
        
        # Apply safety filtering
        all_tokens = []
        for dim_tokens in context.get('tokens', {}).values():
            all_tokens.extend(dim_tokens)

        safety_cfg = self.cfg.get('meta', {}).get('safety', {})
        filtered_tokens = apply_safety_filter(all_tokens, context, safety_cfg)
        if filtered_tokens != all_tokens:
            allowed_tokens = set(filtered_tokens)
            context['tokens'] = {
                dim: [t for t in dim_tokens if t in allowed_tokens]
                for dim, dim_tokens in context.get('tokens', {}).items()
            }

        safety_map = categorize_tokens(filtered_tokens, safety_cfg)
        if violates_policy(safety_map, safety_cfg):
            context.setdefault('warnings', []).append('Safety violation: blocked category combination')
        
        # Add explicit content if enabled
        self._add_explicit_content(context, genre, rarity)
        
        # Apply synonym normalization
        for dim, tokens in context.get('tokens', {}).items():
            context['tokens'][dim] = normalize_all(tokens, self.cfg.get('meta', {}).get('synonyms', {}))
        
        # Assemble prompt
        prompt_core = assemble_prompt(context)
        if is_compositional:
            style_str = assemble_style(context)
            if style_str:
                prompt_core += ". " + style_str
        
        tags_header = make_tags_header(context)
        full_prompt = f"{tags_header} {prompt_core}".strip()
        
        return {
            'prompt': full_prompt,
            'tags_header': tags_header,
            'metadata': context
        }
    
    def _add_explicit_content(self, context: Dict[str, Any], genre: str, rarity: str) -> None:
        """Add explicit content based on settings and probability"""
        if self.explicit_content == "disabled":
            return
            
        safety_config = self.cfg.get('meta', {}).get('safety', {})
        policy = safety_config.get('policy', {})
        
        # Check rarity-based probability for R-rated content
        r_rated_chances = policy.get('r_rated_chance', {})
        base_chance = r_rated_chances.get(rarity, 0.05)
        
        # Increase chance for artistic nude genres
        artistic_genres = policy.get('artistic_nude_genres', [])
        if genre in artistic_genres:
            base_chance *= 1.5
            
        if self.rng.random() < base_chance:
            # Get appropriate explicit content
            flags = safety_config.get('flags', {})
            
            if self.explicit_content == "artistic_only":
                explicit_tokens = flags.get('r_rated_artistic', [])
            elif self.explicit_content == "full_explicit":
                explicit_tokens = flags.get('explicit', []) + flags.get('r_rated_artistic', [])
            else:
                return
                
            if explicit_tokens:
                # Add one explicit token to modifiers
                chosen_token = self.rng.choice(explicit_tokens)
                context.setdefault('tokens', {}).setdefault('modifiers', []).append(chosen_token)
                context.setdefault('warnings', []).append(f'Added R-rated content: {chosen_token}')
    
    def generate(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple prompts"""
        results = []
        for _ in range(count):
            results.append(self.generate_one())
        return results