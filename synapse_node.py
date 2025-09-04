import json
import traceback
from pathlib import Path
from typing import Dict, Any

# Prefer relative import for robustness; fallback to absolute if needed
try:
    from engine import PromptGenerator, load_all_config
    from engine.model_formatting import apply_model_formatting, get_model_negative_prompts
except ImportError:
    # Attempt relative (in case of packaging quirks)
    from .engine import PromptGenerator, load_all_config
    from .engine.model_formatting import apply_model_formatting, get_model_negative_prompts


class SynapsePromptGenerator:
    """
    A ComfyUI custom node that generates prompts using the Synapse Engine.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "output_type": (["full_prompt", "regional_components", "json"], {"default": "full_prompt"}),
                "seed": ("INT", {"default": -1}),
                "model_profile": (["auto", "sdxl", "flux", "illustrious_xl", "pony"], {"default": "auto"}),
                "genre_control": (["random", "fixed"], {"default": "random"}),
                "content_rating": (["safe", "mature", "artistic_r"], {"default": "safe"}),
            },
            "optional": {
                "user_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "fixed_genre": (["fantasy", "dark_fantasy", "sci_fi", "cyberpunk", "steampunk", "post_apoc", "multi"], {"default": "fantasy"}),
                "custom_root": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt")
    FUNCTION = "generate_prompt"
    CATEGORY = "text/synapse"

    def __init__(self):
        self.node_dir = Path(__file__).parent
        self._config_cache: Dict[str, Any] = {}
        self._last_root = None
        print("[Synapse Engine] SynapsePromptGenerator initialized.")

    def _load_config(self, root_path: str) -> Dict[str, Any]:
        """Load configuration with basic caching and robust error reporting."""
        if root_path != self._last_root or not self._config_cache:
            print(f"[Synapse Engine] Loading config from: {root_path}")
            try:
                self._config_cache = load_all_config(root_path)
                self._last_root = root_path

                # Quick sanity checks
                missing = []
                for key in ["meta", "pools", "pipeline"]:
                    if key not in self._config_cache:
                        missing.append(key)
                if missing:
                    print(f"[Synapse Engine][WARN] Missing top-level keys: {missing}")

                print("[Synapse Engine] Config load complete.")
            except Exception as e:
                print("[Synapse Engine][ERROR] Failed to load configuration.")
                traceback.print_exc()
                raise RuntimeError(f"Failed to load config: {e}") from e
        return self._config_cache

    def generate_prompt(self, count, output_type, seed, model_profile, genre_control, content_rating, 
                       user_prompt="", negative_prompt="", fixed_genre="fantasy", custom_root=""):
        """
        Generate prompts using the Synapse Engine Python implementation.
        """
        try:
            if custom_root and Path(custom_root).exists():
                root_path = custom_root
            else:
                root_path = str(self.node_dir)

            config = self._load_config(root_path)
            actual_seed = seed if seed >= 0 else None

            # Create enhanced generator context
            generator_context = {
                'user_prompt': user_prompt.strip() if user_prompt else '',
                'model_profile': model_profile,
                'genre_control': genre_control,
                'fixed_genre': fixed_genre if genre_control == "fixed" else None,
                'content_rating': content_rating,
                'output_type': output_type
            }

            generator = PromptGenerator(config, seed=actual_seed, context=generator_context)
            results = generator.generate(count)

            if not results:
                return ("No prompts generated", negative_prompt)

            first_result = results[0]
            
            if output_type == "json":
                positive_output = json.dumps(first_result, indent=2)
            else:
                # Get the main prompt and extract components
                prompt = first_result.get('prompt', '')

                # Strip metadata tags if present for clean output
                if prompt.startswith('/'):
                    parts = prompt.split(' ')
                    clean_parts = []
                    for part in parts:
                        if part.startswith('/') and part.endswith('/'):
                            continue
                        clean_parts.append(part)
                    if clean_parts:
                        prompt = ' '.join(clean_parts)
                
                # Handle different output formats
                if output_type == "regional_components":
                    # Split into subject and style components for regional prompting
                    metadata = first_result.get('metadata', {})
                    tokens = metadata.get('tokens', {})
                    
                    # Get subject components (figure/landscape content)
                    subject_parts = []
                    content_type = metadata.get('content_type', 'figure')
                    
                    if content_type in ['figure', 'hybrid']:
                        for dim in ['species', 'archetypes', 'physiques', 'artistic_poses', 'emotions', 'conditions', 
                                   'power_sources', 'gear_primary', 'gear_secondary', 'modifiers']:
                            if dim in tokens and tokens[dim]:
                                subject_parts.extend(tokens[dim])
                    elif content_type == 'landscape':
                        for dim in ['biomes', 'structures', 'atmosphere_mood', 'weather', 'time_of_day', 'special_fx']:
                            if dim in tokens and tokens[dim]:
                                subject_parts.extend(tokens[dim])
                    
                    # Get style components
                    style_parts = []
                    for dim in ['palettes', 'lighting', 'camera', 'media', 'depth_effects', 
                               'framing', 'focus_styles', 'quality_combo']:
                        if dim in tokens and tokens[dim]:
                            style_parts.extend(tokens[dim])
                    
                    subject_prompt = ', '.join(subject_parts) if subject_parts else "character"
                    style_prompt = ', '.join(style_parts) if style_parts else "detailed, high quality"
                    
                    if user_prompt:
                        subject_prompt = f"{user_prompt}, {subject_prompt}"
                    
                    # Apply model-specific formatting to each component
                    model_profiles = config.get('meta', {}).get('model_profiles', {})
                    enhanced_context = generator_context.copy()
                    enhanced_context.update(first_result.get('metadata', {}))
                    
                    formatted_subject = apply_model_formatting(subject_prompt, "", enhanced_context, model_profiles)
                    formatted_style = apply_model_formatting("", style_prompt, enhanced_context, model_profiles)
                    
                    positive_output = f"SUBJECT: {formatted_subject}\nSTYLE: {formatted_style}"
                else:
                    # Full prompt format
                    # Extract style from the prompt if it contains the separator
                    if ". " in prompt:
                        parts = prompt.split(". ", 1)
                        main_prompt = parts[0]
                        style_part = parts[1] if len(parts) > 1 else ""
                    else:
                        main_prompt = prompt
                        style_part = ""
                    
                    if user_prompt:
                        main_prompt = f"{user_prompt}, {main_prompt}"
                    
                    # Apply model-specific formatting
                    model_profiles = config.get('meta', {}).get('model_profiles', {})
                    enhanced_context = generator_context.copy()
                    enhanced_context.update(first_result.get('metadata', {}))
                    
                    positive_output = apply_model_formatting(main_prompt, style_part, enhanced_context, model_profiles)

            # Handle negative prompts
            final_negative = negative_prompt.strip() if negative_prompt else ""
            
            # Add model-specific negative prompts
            model_profiles = config.get('meta', {}).get('model_profiles', {})
            model_negatives = get_model_negative_prompts(model_profile, content_rating, model_profiles)
            if model_negatives:
                if final_negative:
                    final_negative = f"{final_negative}, {model_negatives}"
                else:
                    final_negative = model_negatives

            return (positive_output, final_negative)

        except Exception as e:
            print("[Synapse Engine][ERROR] Exception in generate_prompt:")
            traceback.print_exc()
            return (f"Synapse Engine error: {e}", negative_prompt if negative_prompt else "")


NODE_CLASS_MAPPINGS = {
    "SynapsePromptGenerator": SynapsePromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapsePromptGenerator": "Synapse Prompt Generator"
}