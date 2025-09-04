import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from engine import PromptGenerator, load_all_config


class SynapsePromptGenerator:
    """
    A ComfyUI custom node that generates prompts using the Synapse Engine.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "output_format": (["text", "json"], {"default": "text"}),
                "seed": ("INT", {"default": -1}),
            },
            "optional": {
                "custom_root": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_prompt"
    CATEGORY = "text/synapse"
    
    def __init__(self):
        # Get the path to this node's directory
        self.node_dir = Path(__file__).parent
        self._config_cache = {}
        self._last_root = None
        
    def _load_config(self, root_path: str) -> Dict[str, Any]:
        """Load configuration with simple caching"""
        if root_path != self._last_root or not self._config_cache:
            try:
                self._config_cache = load_all_config(root_path)
                self._last_root = root_path
                print(f"[Synapse Engine] Loaded config from: {root_path}")
            except Exception as e:
                print(f"[Synapse Engine] Error loading config: {e}")
                raise
        return self._config_cache
        
    def generate_prompt(self, count, output_format, seed, custom_root=""):
        """
        Generate prompts using the Synapse Engine Python implementation.
        """
        try:
            # Determine root path
            if custom_root and Path(custom_root).exists():
                root_path = custom_root
            else:
                root_path = str(self.node_dir)
            
            # Load configuration
            config = self._load_config(root_path)
            
            # Use seed if provided, otherwise let it be random
            actual_seed = seed if seed >= 0 else None
            
            # Create generator and generate prompts
            generator = PromptGenerator(config, seed=actual_seed)
            results = generator.generate(count)
            
            if not results:
                return ("No prompts generated",)
            
            # Format output based on requested format
            if output_format == "json":
                # Return JSON representation
                result_data = results[0] if results else {}
                return (json.dumps(result_data, indent=2),)
            else:
                # Return clean text prompt (first result)
                first_result = results[0]
                prompt = first_result.get('prompt', '')
                
                # Clean up the prompt by removing metadata tags if present
                if prompt.startswith('/'):
                    # Find where the actual prompt starts after metadata tags
                    parts = prompt.split(' ')
                    clean_parts = []
                    
                    for part in parts:
                        if part.startswith('/') and part.endswith('/'):
                            # This is a metadata tag, skip it
                            continue
                        else:
                            # This is part of the prompt
                            clean_parts.append(part)
                    
                    if clean_parts:
                        clean_prompt = ' '.join(clean_parts)
                        return (clean_prompt,)
                
                return (prompt,)
                    
        except Exception as e:
            error_msg = f"Synapse Engine error: {str(e)}"
            print(f"[Synapse Engine] Error: {error_msg}")
            return (error_msg,)


# ComfyUI Node Registration
NODE_CLASS_MAPPINGS = {
    "SynapsePromptGenerator": SynapsePromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapsePromptGenerator": "Synapse Prompt Generator"
}