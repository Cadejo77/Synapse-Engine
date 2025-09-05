import json
import traceback
from pathlib import Path
from typing import Dict, Any

# Prefer relative import for robustness; fallback to absolute if needed
try:
    from engine import PromptGenerator, load_all_config
except ImportError:
    # Attempt relative (in case of packaging quirks)
    from .engine import PromptGenerator, load_all_config


class SynapsePromptGenerator:
    """
    A ComfyUI custom node that generates prompts using the Synapse Engine.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "output_format": (["text", "json", "structured", "regional"], {"default": "text"}),
                "seed": ("INT", {"default": -1}),
            },
            "optional": {
                "custom_root": ("STRING", {"default": ""}),
                "user_prompt": ("STRING", {"default": "", "multiline": True}),
                "genre_control": (["random", "fantasy", "dark_fantasy", "sci_fi", "cyberpunk", "steampunk", "post_apoc"], {"default": "random"}),
                "negative_prompts": ("BOOLEAN", {"default": True}),
                "custom_negative": ("STRING", {"default": "", "multiline": True}),
                "explicit_content": (["disabled", "artistic_only", "full_explicit"], {"default": "disabled"}),
                "regional_prompting": ("BOOLEAN", {"default": False}),
                "enable_rich_descriptions": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "metadata")
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

    def generate_prompt(self, count, output_format, seed, custom_root="", 
                       user_prompt="", genre_control="random", negative_prompts=True, 
                       custom_negative="", explicit_content="disabled", regional_prompting=False,
                       enable_rich_descriptions=True):
        """
        Generate prompts using the Synapse Engine Python implementation with enhanced features.
        """
        try:
            if custom_root and Path(custom_root).exists():
                root_path = custom_root
            else:
                root_path = str(self.node_dir)

            config = self._load_config(root_path)
            actual_seed = seed if seed >= 0 else None

            # Create generator with new parameters
            generator = PromptGenerator(config, seed=actual_seed, 
                                      explicit_content=explicit_content, 
                                      fixed_genre=genre_control)
            results = generator.generate(count)

            if not results:
                return ("No prompts generated", "", "")

            first_result = results[0]
            
            # Import the universal formatter
            try:
                from engine.universal_formatter import format_universal_prompt, generate_universal_negative_prompts
            except ImportError:
                from .engine.universal_formatter import format_universal_prompt, generate_universal_negative_prompts
            
            # Get the raw prompt
            prompt = first_result.get('prompt', '')
            
            # Strip metadata tags if present for processing
            clean_prompt = prompt
            if prompt.startswith('/'):
                parts = prompt.split(' ')
                clean_parts = []
                for part in parts:
                    if part.startswith('/') and part.endswith('/'):
                        continue
                    clean_parts.append(part)
                if clean_parts:
                    clean_prompt = ' '.join(clean_parts)
            
            # Apply universal formatting with rich descriptions if enabled
            if enable_rich_descriptions:
                formatted_prompt = format_universal_prompt(clean_prompt, first_result.get('metadata', {}), user_prompt)
            else:
                # Basic formatting for simple prompts
                parts = []
                if user_prompt.strip():
                    parts.extend([part.strip() for part in user_prompt.split(',') if part.strip()])
                if clean_prompt.strip():
                    parts.extend([part.strip() for part in clean_prompt.split(',') if part.strip()])
                formatted_prompt = ', '.join(parts) if parts else ""
            
            # Generate negative prompts if enabled
            negative_prompt = ""
            if negative_prompts:
                negative_prompt = generate_universal_negative_prompts(first_result.get('metadata', {}), custom_negative)
            elif custom_negative.strip():
                negative_prompt = custom_negative.strip()
            
            # Create metadata string
            metadata_dict = first_result.get('metadata', {})
            metadata_str = f"Genre: {metadata_dict.get('genre', 'unknown')}, Rarity: {metadata_dict.get('rarity', 'common')}, Vibe: {metadata_dict.get('vibe', 'neutral')}"
            
            # Handle different output formats
            if output_format == "json":
                json_output = {
                    "positive_prompt": formatted_prompt,
                    "negative_prompt": negative_prompt,
                    "metadata": metadata_dict,
                    "regional_prompting": regional_prompting,
                    "rich_descriptions": enable_rich_descriptions
                }
                return (json.dumps(json_output, indent=2), negative_prompt, metadata_str)
                
            elif output_format == "structured":
                structured_output = f"POSITIVE: {formatted_prompt}\n\nNEGATIVE: {negative_prompt}\n\nMETADATA: {metadata_str}"
                if regional_prompting:
                    structured_output += f"\n\nREGIONAL MODE: Enabled (use with Regional Synapse Node)"
                return (structured_output, negative_prompt, metadata_str)
                
            elif output_format == "regional":
                # Regional format provides structured output optimized for regional node
                if regional_prompting:
                    regional_header = "=== REGIONAL PROMPTING MODE ===\nUse this output with Regional Synapse Node for advanced regional control.\n\n"
                    regional_output = f"{regional_header}MAIN: {formatted_prompt}\n\nNEGATIVE: {negative_prompt}\n\nMETADATA: {metadata_str}"
                    return (regional_output, negative_prompt, metadata_str)
                else:
                    return (formatted_prompt, negative_prompt, metadata_str)
                
            else:  # text format
                return (formatted_prompt, negative_prompt, metadata_str)

        except Exception as e:
            print("[Synapse Engine][ERROR] Exception in generate_prompt:")
            traceback.print_exc()
            return (f"Synapse Engine error: {e}", "", "")


NODE_CLASS_MAPPINGS = {
    "SynapsePromptGenerator": SynapsePromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapsePromptGenerator": "Synapse Prompt Generator"
}