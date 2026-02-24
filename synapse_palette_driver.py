import json
import random
from typing import Any, Dict, List, Tuple


from .synapse_utils import call_node as _call, clamp as _clamp, get_node_class as _get_node_class, join_nonempty as _join

def _seeded_rng(seed: int, salt: int) -> random.Random:
    # Keep deterministic but spread out when user wants multiple independent draws
    s = (int(seed) ^ (int(salt) * 0x9E3779B1)) & 0x7FFFFFFF
    return random.Random(s)


class SynapseColorPaletteDriver:
    """Injects a deterministic (seeded) color palette prompt as an extra conditioning part.

    Why this exists:
      - Directly "patching" a diffusion model to always vary palettes is not reliable or portable
        across SDXL/Illustrious/Pony forks.
      - In ComfyUI, the most robust knob is conditioning: add a palette driver prompt with a
        controllable strength.

    Usage:
      - Put this after your main prompt conditioning (or after Synapse Region Conditioning).
      - Feed the output CONDITIONING into KSampler.
    """


    # Palette templates: short, model-friendly, works with both natural language + tag-ish prompts.
    _FAMILIES: Dict[str, List[Dict[str, Any]]] = {
        "cinematic": [
            {"name": "teal_orange", "tokens": ["cinematic_color_grading", "teal_and_orange", "cool_shadows", "warm_highlights", "high_color_separation"]},
            {"name": "film_noir_color", "tokens": ["muted_colors", "deep_blacks", "silver_highlights", "limited_palette", "subtle_warm_accents"]},
            {"name": "blockbuster", "tokens": ["vibrant_colors", "strong_contrast", "warm_rim_light", "cool_ambient_light", "rich_saturation"]},
        ],
        "gothic": [
            {"name": "blood_gold", "tokens": ["desaturated_palette", "crimson_accents", "antique_gold_highlights", "deep_shadows", "chiaroscuro"]},
            {"name": "cathedral", "tokens": ["cold_stone_grays", "candlelight_amber", "dusty_blues", "low_saturation", "dramatic_lighting"]},
            {"name": "necromancer", "tokens": ["sickly_green_glow", "ashen_grays", "violet_shadows", "limited_palette", "ominous_color_grading"]},
        ],
        "fantasy": [
            {"name": "royal", "tokens": ["sapphire_blue", "crimson_red", "gold_accents", "rich_saturation", "storybook_color_grading"]},
            {"name": "forest", "tokens": ["moss_green", "earthy_browns", "sunlit_gold", "natural_palette", "soft_color_variation"]},
            {"name": "ice_fire", "tokens": ["icy_blues", "silver_white", "ember_orange_accents", "high_contrast", "glowing_highlights"]},
        ],
        "neon": [
            {"name": "synthwave", "tokens": ["neon_magenta", "neon_cyan", "deep_purple", "high_saturation", "glow_effects"]},
            {"name": "acid", "tokens": ["acid_green", "electric_yellow", "black_background", "high_contrast", "chromatic_aberration"]},
            {"name": "holo", "tokens": ["iridescent_colors", "prismatic_highlights", "cool_gradients", "color_shift", "vaporwave_palette"]},
        ],
        "sunset": [
            {"name": "dusk", "tokens": ["sunset_palette", "orange_pink", "purple_shadows", "warm_haze", "gradient_sky"]},
            {"name": "dawn", "tokens": ["soft_pastels", "peach_light", "lavender_mist", "gentle_saturation", "airy_colors"]},
            {"name": "infernal", "tokens": ["ember_red", "molten_orange", "charcoal_blacks", "hot_highlights", "smoke_haze"]},
        ],
        "earthy": [
            {"name": "ochre_umber", "tokens": ["ochre", "umber", "olive_green", "muted_earth_tones", "natural_contrast"]},
            {"name": "desert", "tokens": ["sand_beige", "rust_red", "sun_bleached", "low_saturation", "dusty_palette"]},
            {"name": "rustic", "tokens": ["warm_browns", "aged_leather", "copper_accents", "soft_saturation", "organic_colors"]},
        ],
        "monochrome": [
            {"name": "mono_blue", "tokens": ["monochrome", "blue_tint", "single_accent_color", "high_value_contrast"]},
            {"name": "mono_red", "tokens": ["monochrome", "crimson_tint", "single_accent_color", "deep_shadows"]},
            {"name": "bw_gold", "tokens": ["black_and_white", "gold_accents", "limited_palette", "high_contrast"]},
        ],
    }

    _HARMONIES = [
        ("analogous", ["analogous_colors", "smooth_color_transitions"]),
        ("complementary", ["complementary_colors", "strong_color_contrast"]),
        ("triadic", ["triadic_palette", "balanced_color_harmony"]),
        ("duotone", ["duotone", "limited_palette"]),
        ("split_complementary", ["split_complementary_palette", "color_variation"]),
    ]

    @classmethod
    def INPUT_TYPES(cls):
        families = ["auto"] + sorted(list(cls._FAMILIES.keys()))
        harmony_modes = ["auto"] + [h[0] for h in cls._HARMONIES]
        return {
            "required": {
                "clip": ("CLIP",),
                "conditioning": ("CONDITIONING",),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31 - 1}),
                "palette_family": (families,),
                "harmony": (harmony_modes,),
                "palette_strength": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 3.0, "step": 0.05}),
                "anti_repeat": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "salt": ("INT", {"default": 0, "min": 0, "max": 9999999}),
                "extra_tags": ("STRING", {"default": "colorful, detailed_color_grading", "multiline": True}),
            },
        }

    RETURN_TYPES = ("CONDITIONING", "STRING", "STRING")
    RETURN_NAMES = ("conditioning_out", "palette_prompt", "debug_report")
    FUNCTION = "apply"
    CATEGORY = "synapse/color"

    def _pick_palette(self, rng: random.Random, palette_family: str, anti_repeat: bool, seed: int) -> Tuple[str, List[str]]:
        if palette_family == "auto":
            fam = rng.choice(sorted(list(self._FAMILIES.keys())))
        else:
            fam = palette_family
        items = self._FAMILIES.get(fam, [])
        if not items:
            return ("auto", ["colorful", "color_variation"])

        choices = items[:]
        if anti_repeat and len(choices) > 1:
            skip_idx = abs(hash((int(seed), fam))) % len(choices)
            choices = [it for i, it in enumerate(choices) if i != skip_idx] or choices

        item = rng.choice(choices)
        pid = f"{fam}:{item.get('name', 'palette')}"
        return (pid, list(item.get("tokens", [])))

    def _pick_harmony(self, rng: random.Random, harmony: str) -> Tuple[str, List[str]]:
        if harmony == "auto":
            name, toks = rng.choice(self._HARMONIES)
            return name, list(toks)
        for name, toks in self._HARMONIES:
            if name == harmony:
                return name, list(toks)
        return "auto", ["color_harmony"]

    def apply(
        self,
        clip,
        conditioning,
        seed: int,
        palette_family: str,
        harmony: str,
        palette_strength: float,
        anti_repeat: bool,
        salt: int = 0,
        extra_tags: str = "colorful, detailed_color_grading",
    ):
        CLIPTextEncode = _get_node_class("CLIPTextEncode")
        ConditioningCombine = _get_node_class("ConditioningCombine")

        if CLIPTextEncode is None:
            raise RuntimeError("ComfyUI core node CLIPTextEncode not found. This node must run inside ComfyUI.")

        rng = _seeded_rng(seed, salt)
        palette_id, palette_tokens = self._pick_palette(rng, palette_family, anti_repeat, seed)
        harmony_name, harmony_tokens = self._pick_harmony(rng, harmony)

        # Optional micro-variation so adjacent seeds feel more distinct
        vibe = rng.choice([
            "soft_film_grain", "clean_digital", "painterly_color", "high_dynamic_range", "matte_color_grade"
        ])

        # Build prompt snippet
        prompt_parts = []
        prompt_parts.extend(palette_tokens)
        prompt_parts.extend(harmony_tokens)
        if vibe:
            prompt_parts.append(vibe)
        if (extra_tags or "").strip():
            prompt_parts.append(extra_tags.strip())

        palette_prompt = _join(prompt_parts)

        enc = CLIPTextEncode()
        palette_cond = _call(enc, clip=clip, text=palette_prompt)[0]

        # Attach a strength field so KSampler respects how hard this “driver” should push.
        strength = _clamp(palette_strength, 0.0, 100.0)
        if strength > 0.0:
            out_part = []
            for c in palette_cond:
                if isinstance(c, (list, tuple)) and len(c) >= 2 and isinstance(c[1], dict):
                    d = dict(c[1])
                    d["strength"] = strength
                    out_part.append([c[0], d])
                else:
                    # fallback: leave as-is
                    out_part.append(c)
            palette_cond = out_part

        # Combine
        if ConditioningCombine is not None:
            comb = ConditioningCombine()
            out = _call(comb, conditioning_1=conditioning, conditioning_2=palette_cond)[0]
        else:
            out = conditioning + palette_cond

        debug = {
            "palette_id": palette_id,
            "palette_family": palette_family,
            "harmony": harmony_name,
            "strength": strength,
            "salt": int(salt),
        }

        return (out, palette_prompt, json.dumps(debug, ensure_ascii=False))
