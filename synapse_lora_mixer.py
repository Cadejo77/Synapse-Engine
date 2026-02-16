import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


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
    if mode == "off" or not items:
        return items

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


def _clean_token(token: str) -> str:
    return " ".join((token or "").replace("_", " ").split()).strip()


def _extract_list_like(value: Any) -> List[str]:
    out: List[str] = []
    if isinstance(value, str):
        parts = re.split(r"[,\n;|]", value)
        out.extend(p.strip() for p in parts if p and p.strip())
    elif isinstance(value, (list, tuple, set)):
        for it in value:
            out.extend(_extract_list_like(it))
    elif isinstance(value, dict):
        for v in value.values():
            out.extend(_extract_list_like(v))
    return out


def _extract_trigger_words_from_json(data: Any) -> List[str]:
    keys_of_interest = {
        "trainedwords",
        "triggerwords",
        "trigger_words",
        "activation text",
        "activationtext",
        "activation",
        "tags",
    }

    found: List[str] = []

    def _walk(v: Any):
        if isinstance(v, dict):
            for k, vv in v.items():
                if str(k).strip().lower() in keys_of_interest:
                    found.extend(_extract_list_like(vv))
                _walk(vv)
        elif isinstance(v, (list, tuple, set)):
            for it in v:
                _walk(it)

    _walk(data)
    deduped = []
    seen = set()
    for token in found:
        t = _clean_token(token)
        if not t:
            continue
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        deduped.append(t)
    return deduped


def _load_sidecar_json(path: Path) -> Optional[Any]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_trigger_words_for_lora(full_path: str) -> List[str]:
    p = Path(full_path)
    candidates = [
        p.with_suffix(".civitai.info"),
        p.with_suffix(".cm-info.json"),
        p.with_suffix(".json"),
    ]

    for c in candidates:
        data = _load_sidecar_json(c)
        if data is None:
            continue
        words = _extract_trigger_words_from_json(data)
        if words:
            return words

    txt_sidecar = p.with_suffix(".txt")
    if txt_sidecar.exists() and txt_sidecar.is_file():
        try:
            text = txt_sidecar.read_text(encoding="utf-8")
        except Exception:
            text = ""
        words = [_clean_token(t) for t in re.split(r"[,\n;|]", text)]
        words = [w for w in words if w]
        if words:
            return list(dict.fromkeys(words))

    return []


def _resolve_lora_path(folder_paths, name: str) -> Optional[Tuple[str, str]]:
    clean = (name or "").strip()
    if not clean:
        return None

    direct = folder_paths.get_full_path("loras", clean)
    if direct:
        return clean, direct

    try:
        loras: Sequence[str] = folder_paths.get_filename_list("loras")
    except Exception:
        loras = []

    clean_lower = clean.lower()
    for cand in loras:
        if str(cand).lower() == clean_lower:
            p = folder_paths.get_full_path("loras", cand)
            if p:
                return cand, p

    clean_stem = Path(clean).stem.lower()
    for cand in loras:
        if Path(str(cand)).stem.lower() == clean_stem:
            p = folder_paths.get_full_path("loras", cand)
            if p:
                return cand, p

    return None


def _parse_lora_text(lora_text: str, default_strength: float) -> List[Dict[str, Any]]:
    text = (lora_text or "").replace("\r", "")
    if not text.strip():
        return []

    results: List[Dict[str, Any]] = []

    # format: <lora:name:strength> or <lora:name:strength_model:strength_clip>
    tag_pattern = re.compile(r"<\s*lora\s*:\s*([^:>]+?)\s*:\s*([+-]?\d*\.?\d+)\s*(?::\s*([+-]?\d*\.?\d+)\s*)?>", re.IGNORECASE)
    for m in tag_pattern.finditer(text):
        name = m.group(1).strip()
        sm = float(m.group(2))
        sc = float(m.group(3)) if m.group(3) is not None else sm
        results.append({"name": name, "strength_model": sm, "strength_clip": sc, "source": "tag"})

    text_wo_tags = tag_pattern.sub("\n", text)

    for raw_line in text_wo_tags.split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        for part in [p.strip() for p in line.split(",") if p.strip()]:
            cols = [c.strip() for c in re.split(r"[|:]", part)]
            if not cols:
                continue
            name = cols[0]
            if not name:
                continue

            sm = float(default_strength)
            sc = float(default_strength)
            if len(cols) >= 2 and cols[1]:
                try:
                    sm = float(cols[1])
                    sc = sm
                except Exception:
                    pass
            if len(cols) >= 3 and cols[2]:
                try:
                    sc = float(cols[2])
                except Exception:
                    pass

            results.append({"name": name, "strength_model": sm, "strength_clip": sc, "source": "line"})

    return results


class SynapseLoRAStyleMixer:
    """Text-driven LoRA mixer with unlimited entries + trigger word extraction.

    Input formats (can be mixed):
      - <lora:my_style.safetensors:0.8>
      - <lora:my_style:0.9:0.7>  # model, clip
      - my_style.safetensors
      - my_style.safetensors:0.8
      - my_style.safetensors:0.8:0.7
      - my_style|0.8|0.7
    """

    @classmethod
    def INPUT_TYPES(cls):
        normalize_modes = ["off", "clamp_total", "sum_to_target"]
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_text": (
                    "STRING",
                    {
                        "default": "# One per line, comma-separated, or <lora:name:strength> tags\n",
                        "multiline": True,
                    },
                ),
                "default_strength": ("FLOAT", {"default": 0.65, "min": -3.0, "max": 3.0, "step": 0.05}),
                "normalize_mode": (normalize_modes,),
                "target_total": ("FLOAT", {"default": 1.25, "min": 0.0, "max": 12.0, "step": 0.05}),
                "weight_jitter": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.50, "step": 0.01}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31 - 1}),
                "extract_trigger_words": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "salt": ("INT", {"default": 0, "min": 0, "max": 9999999}),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "LORA_STACK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("model_out", "clip_out", "lora_stack", "trigger_words", "recipe_json", "debug_report")
    FUNCTION = "mix"
    CATEGORY = "synapse/lora"

    def mix(
        self,
        model,
        clip,
        lora_text: str,
        default_strength: float,
        normalize_mode: str,
        target_total: float,
        weight_jitter: float,
        seed: int,
        extract_trigger_words: bool,
        salt: int = 0,
    ):
        folder_paths = _safe_import_folder_paths()
        if folder_paths is None:
            raise RuntimeError("folder_paths not found. This node must run inside ComfyUI.")

        import comfy.sd
        import comfy.utils

        parsed = _parse_lora_text(lora_text, default_strength)
        if not parsed:
            debug = "loras=0 | no valid LoRA entries found in lora_text"
            return (model, clip, [], "", json.dumps({"loras": []}, ensure_ascii=False), debug)

        resolved: List[Dict[str, Any]] = []
        unresolved_names: List[str] = []
        for it in parsed:
            hit = _resolve_lora_path(folder_paths, str(it["name"]))
            if hit is None:
                unresolved_names.append(str(it["name"]))
                continue
            actual_name, full_path = hit
            resolved.append(
                {
                    "name": actual_name,
                    "full_path": full_path,
                    "strength_model": float(it["strength_model"]),
                    "strength_clip": float(it["strength_clip"]),
                    "source": str(it.get("source", "text")),
                }
            )

        if not resolved:
            raise FileNotFoundError("No LoRA entries from lora_text were found in ComfyUI loras folder.")

        rng = _seeded_rng(seed, salt)
        jit = float(weight_jitter)
        if jit > 0.0:
            for it in resolved:
                j = rng.uniform(-jit, jit)
                it["strength_model"] = float(it["strength_model"]) * (1.0 + j)
                it["strength_clip"] = float(it["strength_clip"]) * (1.0 + j)

        resolved = _normalize_strengths(resolved, normalize_mode, float(target_total))

        debug_lines = [
            f"loras={len(resolved)} | normalize={normalize_mode} | target_total={target_total:.2f} | jitter={jit:.2f}",
        ]

        if unresolved_names:
            unique_unresolved = sorted(set(unresolved_names))
            debug_lines.append("unresolved=" + ", ".join(unique_unresolved))

        cur_model, cur_clip = model, clip
        lora_cache: Dict[str, Any] = {}
        applied: List[Dict[str, Any]] = []
        trigger_words: List[str] = []
        trigger_word_keys = set()

        for it in resolved:
            name = it["name"]
            full_path = it["full_path"]
            sm = float(it["strength_model"])
            sc = float(it["strength_clip"])

            if full_path not in lora_cache:
                lora_cache[full_path] = comfy.utils.load_torch_file(full_path, safe_load=True)
            lora = lora_cache[full_path]
            cur_model, cur_clip = comfy.sd.load_lora_for_models(cur_model, cur_clip, lora, sm, sc)

            item = {"name": name, "strength_model": sm, "strength_clip": sc}
            applied.append(item)
            debug_lines.append(f"- {name} | model={sm:.3f} clip={sc:.3f}")

            if extract_trigger_words:
                words = _extract_trigger_words_for_lora(full_path)
                for w in words:
                    key = w.lower()
                    if key not in trigger_word_keys:
                        trigger_word_keys.add(key)
                        trigger_words.append(w)

        # Common inter-pack shape for stacker/apply nodes.
        lora_stack: List[Tuple[str, float, float]] = [
            (str(it["name"]), float(it["strength_model"]), float(it["strength_clip"]))
            for it in applied
        ]

        recipe = {
            "normalize_mode": normalize_mode,
            "target_total": float(target_total),
            "weight_jitter": float(jit),
            "seed": int(seed),
            "salt": int(salt),
            "unresolved": sorted(set(unresolved_names)),
            "loras": applied,
            "trigger_words": trigger_words,
        }

        trigger_text = ", ".join(trigger_words)
        return (cur_model, cur_clip, lora_stack, trigger_text, json.dumps(recipe, ensure_ascii=False), "\n".join(debug_lines))
