import json
import random
from typing import Any, Dict, List


def _safe_import_folder_paths():
    try:
        import folder_paths  # ComfyUI
        return folder_paths
    except Exception:
        return None


def _seeded_rng(seed: int, salt: int) -> random.Random:
    s = (int(seed) ^ (int(salt) * 0x9E3779B1)) & 0x7FFFFFFF
    return random.Random(s)


def _normalize_strengths(items: List[Dict[str, Any]], mode: str, target_sum: float) -> List[Dict[str, Any]]:
    """Normalize model/clip strengths across multiple LoRAs.

    modes:
      - off: no change
      - sum_to_target: scale all |weights| so their absolute sum equals target_sum
      - clamp_total: if abs sum > target_sum, scale down to target_sum, else no change
    """

    if mode == "off" or not items:
        return items

    # Use abs sum so negative weights still count toward "how hard" you push.
    sm_sum = sum(abs(float(it["strength_model"])) for it in items)
    sc_sum = sum(abs(float(it["strength_clip"])) for it in items)

    def _scale(cur_sum: float) -> float:
        if cur_sum <= 1e-8:
            return 1.0
        if mode == "sum_to_target":
            return float(target_sum) / float(cur_sum)
        if mode == "clamp_total":
            return min(1.0, float(target_sum) / float(cur_sum))
        return 1.0

    sm_scale = _scale(sm_sum)
    sc_scale = _scale(sc_sum)

    out = []
    for it in items:
        it2 = dict(it)
        it2["strength_model"] = float(it2["strength_model"]) * sm_scale
        it2["strength_clip"] = float(it2["strength_clip"]) * sc_scale
        out.append(it2)
    return out


class SynapseLoRAStyleMixer:
    """Load + mix up to 6 LoRAs with optional weight normalization + jitter.

    Notes on "stability":
      - LoRA application is fundamentally linear (additive deltas). Order should not matter.
      - Instability usually comes from *too much total strength* or mismatched CLIP/UNet strength.
      - This node helps by normalizing total influence and letting you jitter weights slightly
        (optional) to avoid locked-in samey results.
    """

    @classmethod
    def INPUT_TYPES(cls):
        folder_paths = _safe_import_folder_paths()
        loras = ["<none>"]
        if folder_paths is not None:
            try:
                loras = ["<none>"] + folder_paths.get_filename_list("loras")
            except Exception:
                loras = ["<none>"]

        normalize_modes = ["off", "clamp_total", "sum_to_target"]

        def slot(i: int) -> Dict[str, Any]:
            return {
                f"lora_{i}": (loras,),
                f"strength_model_{i}": ("FLOAT", {"default": 0.65, "min": -3.0, "max": 3.0, "step": 0.05}),
                f"strength_clip_{i}": ("FLOAT", {"default": 0.65, "min": -3.0, "max": 3.0, "step": 0.05}),
            }

        required = {
            "model": ("MODEL",),
            "clip": ("CLIP",),
            "normalize_mode": (normalize_modes,),
            "target_total": ("FLOAT", {"default": 1.25, "min": 0.0, "max": 6.0, "step": 0.05}),
            "weight_jitter": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.50, "step": 0.01}),
            "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31 - 1}),
        }

        # 6 slots
        for i in range(1, 7):
            required.update(slot(i))

        optional = {
            "salt": ("INT", {"default": 0, "min": 0, "max": 9999999}),
        }

        return {"required": required, "optional": optional}

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("model_out", "clip_out", "recipe_json", "debug_report")
    FUNCTION = "mix"
    CATEGORY = "synapse/lora"

    def mix(self, model, clip, normalize_mode: str, target_total: float, weight_jitter: float, seed: int,
            lora_1: str, strength_model_1: float, strength_clip_1: float,
            lora_2: str, strength_model_2: float, strength_clip_2: float,
            lora_3: str, strength_model_3: float, strength_clip_3: float,
            lora_4: str, strength_model_4: float, strength_clip_4: float,
            lora_5: str, strength_model_5: float, strength_clip_5: float,
            lora_6: str, strength_model_6: float, strength_clip_6: float,
            salt: int = 0):

        folder_paths = _safe_import_folder_paths()
        if folder_paths is None:
            raise RuntimeError("folder_paths not found. This node must run inside ComfyUI.")

        # Import comfy modules lazily so this file can be imported outside ComfyUI tooling.
        import comfy.sd
        import comfy.utils

        slots = [
            (lora_1, strength_model_1, strength_clip_1),
            (lora_2, strength_model_2, strength_clip_2),
            (lora_3, strength_model_3, strength_clip_3),
            (lora_4, strength_model_4, strength_clip_4),
            (lora_5, strength_model_5, strength_clip_5),
            (lora_6, strength_model_6, strength_clip_6),
        ]

        items: List[Dict[str, Any]] = []
        for name, sm, sc in slots:
            if not name or name == "<none>":
                continue
            # If both strengths are near-zero, skip.
            if abs(float(sm)) < 1e-6 and abs(float(sc)) < 1e-6:
                continue
            items.append({
                "name": str(name),
                "strength_model": float(sm),
                "strength_clip": float(sc),
            })

        rng = _seeded_rng(seed, salt)

        # Apply optional jitter (multiplicative, symmetric) before normalization.
        jit = float(weight_jitter)
        if jit > 0.0:
            for it in items:
                j = rng.uniform(-jit, jit)
                it["strength_model"] = float(it["strength_model"]) * (1.0 + j)
                it["strength_clip"] = float(it["strength_clip"]) * (1.0 + j)

        items = _normalize_strengths(items, normalize_mode, float(target_total))

        debug_lines = []
        debug_lines.append(f"loras={len(items)} | normalize={normalize_mode} | target_total={target_total:.2f} | jitter={jit:.2f}")

        # Load + apply
        cur_model, cur_clip = model, clip
        applied: List[Dict[str, Any]] = []

        for it in items:
            name = it["name"]
            sm = float(it["strength_model"])
            sc = float(it["strength_clip"])

            full_path = folder_paths.get_full_path("loras", name)
            if not full_path:
                raise FileNotFoundError(f"LoRA not found in ComfyUI loras folder: {name}")

            lora = comfy.utils.load_torch_file(full_path, safe_load=True)
            cur_model, cur_clip = comfy.sd.load_lora_for_models(cur_model, cur_clip, lora, sm, sc)

            applied.append({"name": name, "strength_model": sm, "strength_clip": sc})
            debug_lines.append(f"- {name} | model={sm:.3f} clip={sc:.3f}")

        recipe = {
            "normalize_mode": normalize_mode,
            "target_total": float(target_total),
            "weight_jitter": float(jit),
            "seed": int(seed),
            "salt": int(salt),
            "loras": applied,
        }

        return (cur_model, cur_clip, json.dumps(recipe, ensure_ascii=False), "\n".join(debug_lines))
