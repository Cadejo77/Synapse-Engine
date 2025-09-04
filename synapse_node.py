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

    def generate_prompt(self, count, output_format, seed, custom_root=""):
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

            generator = PromptGenerator(config, seed=actual_seed)
            results = generator.generate(count)

            if not results:
                return ("No prompts generated",)

            if output_format == "json":
                return (json.dumps(results[0], indent=2),)
            else:
                first_result = results[0]
                prompt = first_result.get('prompt', '')

                # Strip metadata tags if present
                if prompt.startswith('/'):
                    parts = prompt.split(' ')
                    clean_parts = []
                    for part in parts:
                        if part.startswith('/') and part.endswith('/'):
                            continue
                        clean_parts.append(part)
                    if clean_parts:
                        return (' '.join(clean_parts),)
                return (prompt,)

        except Exception as e:
            print("[Synapse Engine][ERROR] Exception in generate_prompt:")
            traceback.print_exc()
            return (f"Synapse Engine error: {e}",)


NODE_CLASS_MAPPINGS = {
    "SynapsePromptGenerator": SynapsePromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapsePromptGenerator": "Synapse Prompt Generator"
}