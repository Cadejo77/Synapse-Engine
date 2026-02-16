import json
import re
from typing import Any, Dict, List


def _get_node_class(name: str):
    """Get a ComfyUI core node class by name."""
    try:
        import nodes  # ComfyUI core
        if hasattr(nodes, "NODE_CLASS_MAPPINGS") and name in nodes.NODE_CLASS_MAPPINGS:
            return nodes.NODE_CLASS_MAPPINGS[name]
        return getattr(nodes, name, None)
    except Exception:
        return None


def _call(node_obj, **kwargs):
    fn_name = getattr(node_obj, "FUNCTION", None)
    if not fn_name:
        raise RuntimeError("Node object has no FUNCTION attribute")
    fn = getattr(node_obj, fn_name)
    return fn(**kwargs)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _join_nonempty(parts: List[str]) -> str:
    return ", ".join([p.strip(" ,") for p in parts if (p or "").strip()]).strip(" ,")


def _filter_subject_tokens(text: str) -> str:
    """
    Remove subject-count tokens from a prompt (helps avoid accidental duplicate subjects
    when the same prompt is applied globally + in a region).
    """
    if not text:
        return ""
    # Split on commas/newlines first, then filter obvious count/subject markers
    raw = re.split(r"[,\n]+", text)
    drop = {
        "solo", "group", "crowd", "couple",
        "1girl", "1boy", "2girls", "2boys", "3girls", "3boys",
        "4girls", "4boys", "5girls", "5boys",
        "multiple_girls", "multiple_boys",
        "1person", "2people", "3people",
    }
    kept = []
    for t in raw:
        s = t.strip(" ,").strip()
        if not s:
            continue
        sl = s.lower().replace(" ", "_")
        if sl in drop:
            continue
        kept.append(s)
    return ", ".join(kept).strip(" ,")


def _anchor_from_prompt(comp: str) -> str:
    """Heuristic anchor chooser from composition text."""
    c = (comp or "").lower()
    # very light heuristic: look for explicit directional hints
    has_left = "left" in c
    has_right = "right" in c
    has_top = "top" in c or "upper" in c
    has_bottom = "bottom" in c or "lower" in c
    if has_top and has_left:
        return "top_left"
    if has_top and has_right:
        return "top_right"
    if has_bottom and has_left:
        return "bottom_left"
    if has_bottom and has_right:
        return "bottom_right"
    # otherwise default to center (safe, avoids ghosts from multi-anchors)
    return "center"


def _build_plan(
    subject_prompt: str,
    scene_prompt: str,
    composition_prompt: str,
    layout_mode: str,
    global_weight: float,
    subject_weight: float,
    subject_box_scale: float,
    subject_anchor: str = "auto",
) -> Dict[str, Any]:
    """
    Build a minimal region plan (percent coordinates) from a few presets.
    rect = [x0, y0, x1, y1] in 0..1

    IMPORTANT: We keep a SINGLE subject region by default to avoid "ghost" duplicate subjects.
    """
    subject_prompt = (subject_prompt or "").strip()
    scene_prompt = (scene_prompt or "").strip()
    composition_prompt = (composition_prompt or "").strip()

    # Base prompt influences the whole canvas to avoid "glued together" look.
    # Also remove obvious subject-count tokens from the base so we don't accidentally duplicate.
    global_prompt = _join_nonempty([scene_prompt, composition_prompt])
    global_prompt = _filter_subject_tokens(global_prompt)

    regions: List[Dict[str, Any]] = []

    # Subject box scale: 0.4 -> large box, 0.9 -> small box
    s = _clamp(subject_box_scale, 0.20, 0.95)

    def _box_around(ax: float, ay: float) -> List[float]:
        # Use scale to pick a sensible box size
        box_w = _clamp(0.55 * s, 0.18, 0.75)
        box_h = _clamp(0.55 * s, 0.18, 0.75)
        x0 = _clamp(ax - box_w / 2.0, 0.0, 1.0)
        y0 = _clamp(ay - box_h / 2.0, 0.0, 1.0)
        x1 = _clamp(ax + box_w / 2.0, 0.0, 1.0)
        y1 = _clamp(ay + box_h / 2.0, 0.0, 1.0)
        # Ensure non-zero
        if x1 <= x0:
            x1 = _clamp(x0 + 0.05, 0.0, 1.0)
        if y1 <= y0:
            y1 = _clamp(y0 + 0.05, 0.0, 1.0)
        return [x0, y0, x1, y1]

    # Center-box for subject_center
    margin = (1.0 - s) / 2.0
    cx0, cy0, cx1, cy1 = margin, margin, 1.0 - margin, 1.0 - margin

    if layout_mode == "no_regions":
        regions = []
    elif layout_mode == "subject_center":
        regions = [{"name": "subject", "rect": [cx0, cy0, cx1, cy1], "weight": subject_weight, "prompt": subject_prompt}]
    elif layout_mode == "subject_left":
        regions = [{"name": "subject_left", "rect": [0.0, 0.0, 0.42, 1.0], "weight": subject_weight, "prompt": subject_prompt}]
    elif layout_mode == "subject_right":
        regions = [{"name": "subject_right", "rect": [0.58, 0.0, 1.0, 1.0], "weight": subject_weight, "prompt": subject_prompt}]
    elif layout_mode == "foreground_mid_background":
        # Two-layer split: subject foreground + boosted background.
        regions = [
            {"name": "background", "rect": [0.0, 0.0, 1.0, 0.60], "weight": max(0.0, subject_weight * 0.75), "prompt": scene_prompt},
            {"name": "subject_foreground", "rect": [0.0, 0.45, 1.0, 1.0], "weight": subject_weight, "prompt": subject_prompt},
        ]
    else:  # rule_of_thirds (default)
        # SINGLE anchor region (prevents duplicate-subject ghosts).
        if subject_anchor == "auto":
            anchor = _anchor_from_prompt(composition_prompt)
        else:
            anchor = subject_anchor

        anchors = {
            "center": (0.5, 0.5),
            "top_left": (0.33, 0.33),
            "top_right": (0.67, 0.33),
            "bottom_left": (0.33, 0.67),
            "bottom_right": (0.67, 0.67),
        }
        ax, ay = anchors.get(anchor, anchors["center"])
        rect = _box_around(ax, ay)
        regions = [{"name": f"subject_{anchor}", "rect": rect, "weight": subject_weight, "prompt": subject_prompt}]

    return {
        "layout_mode": layout_mode,
        "subject_anchor": subject_anchor,
        "global": {"prompt": global_prompt, "weight": float(global_weight)},
        "regions": regions,
    }



class SynapseRegionConditioning:
    """
    Minimal region-conditioning node:
    - accepts prompts from Procedural Prompt Graph v2
    - applies a small set of region presets
    - outputs CONDITIONING ready for KSampler
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "subject_prompt": ("STRING", {"multiline": True, "default": ""}),
                "scene_prompt": ("STRING", {"multiline": True, "default": ""}),
                "composition_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": "worst quality, low quality, lowres, blurry, watermark, text"}),
                "layout_mode": (["subject_center", "rule_of_thirds", "subject_left", "subject_right", "foreground_mid_background", "no_regions"],),
                "subject_anchor": (["auto","center","top_left","top_right","bottom_left","bottom_right"],),
                "subject_box_scale": ("FLOAT", {"default": 0.70, "min": 0.20, "max": 0.95, "step": 0.05}),
                "global_weight": ("FLOAT", {"default": 1.00, "min": 0.0, "max": 3.0, "step": 0.05}),
                "subject_weight": ("FLOAT", {"default": 1.10, "min": 0.0, "max": 3.0, "step": 0.05}),
                "base_strength": ("FLOAT", {"default": 0.60, "min": 0.0, "max": 10.0, "step": 0.05}),
                "region_strength_multiplier": ("FLOAT", {"default": 1.00, "min": 0.0, "max": 10.0, "step": 0.05}),
            },
            "optional": {
                "width_px": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "height_px": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "strength_cap": ("FLOAT", {"default": 10.0, "min": 0.1, "max": 50.0, "step": 0.5}),
            },
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "STRING", "STRING")
    RETURN_NAMES = ("positive_conditioning", "negative_conditioning", "region_plan_json", "debug_report")
    FUNCTION = "apply"
    CATEGORY = "synapse/regions"

    def apply(
        self,
        clip,
        subject_prompt: str,
        scene_prompt: str,
        composition_prompt: str,
        negative_prompt: str,
        layout_mode: str,
        subject_anchor: str,
        subject_box_scale: float,
        global_weight: float,
        subject_weight: float,
        base_strength: float,
        region_strength_multiplier: float,
        width_px: int = 1024,
        height_px: int = 1024,
        strength_cap: float = 10.0,
    ):
        CLIPTextEncode = _get_node_class("CLIPTextEncode")
        ConditioningSetAreaPercentage = _get_node_class("ConditioningSetAreaPercentage")
        ConditioningSetArea = _get_node_class("ConditioningSetArea")
        ConditioningCombine = _get_node_class("ConditioningCombine")

        if CLIPTextEncode is None:
            raise RuntimeError("ComfyUI core node CLIPTextEncode not found. This node must run inside ComfyUI.")

        enc = CLIPTextEncode()

        plan = _build_plan(
            subject_prompt=subject_prompt,
            scene_prompt=scene_prompt,
            composition_prompt=composition_prompt,
            layout_mode=layout_mode,
            global_weight=global_weight,
            subject_weight=subject_weight,
            subject_box_scale=subject_box_scale,
            subject_anchor=subject_anchor,
        )
        region_plan_json = json.dumps(plan, ensure_ascii=False)

        regions = plan.get("regions", []) if isinstance(plan, dict) else []
        g = plan.get("global", {}) if isinstance(plan, dict) else {}
        global_prompt = str(g.get("prompt", "") or "")
        global_weight_val = float(g.get("weight", 1.0) or 1.0)

        debug_lines: List[str] = []
        debug_lines.append(f"layout_mode={layout_mode} | regions={len(regions)} | global_chars={len(global_prompt)}")

        # Negative conditioning
        neg_text = (negative_prompt or "").strip()
        # Heuristic: if subject indicates a single person, discourage accidental extra characters/duplicates
        subj_l = (subject_prompt or "").lower()
        if any(t in subj_l for t in ["1girl", "1boy", "solo", "1person"]):
            extra_neg = "multiple_girls, multiple_boys, 2girls, 2boys, 2people, extra_person, extra_character, duplicate, twins, cloned"
            if extra_neg not in neg_text:
                neg_text = (neg_text + ", " + extra_neg).strip(" ,")
        neg_cond = _call(enc, clip=clip, text=neg_text)[0] if neg_text else _call(enc, clip=clip, text="")[0]

        pos_parts: List[Any] = []

        # Global conditioning over full canvas
        if global_prompt.strip():
            base_cond = _call(enc, clip=clip, text=global_prompt.strip())[0]
            g_strength = _clamp(float(base_strength) * float(global_weight_val), 0.0, float(strength_cap))
            if g_strength > 0.0:
                if ConditioningSetAreaPercentage is not None:
                    sa = ConditioningSetAreaPercentage()
                    base_area = _call(sa, conditioning=base_cond, width=1.0, height=1.0, x=0.0, y=0.0, strength=g_strength)[0]
                    pos_parts.append(base_area)
                    debug_lines.append(f"global=full | strength={g_strength:.2f} | pct")
                elif ConditioningSetArea is not None:
                    sa = ConditioningSetArea()
                    base_area = _call(sa, conditioning=base_cond, width=int(width_px), height=int(height_px), x=0, y=0, strength=g_strength)[0]
                    pos_parts.append(base_area)
                    debug_lines.append(f"global=full | strength={g_strength:.2f} | px")
                else:
                    pos_parts.append(base_cond)
                    debug_lines.append("global=full | no set-area node found (non-spatial)")

        # Regions
        for idx, r in enumerate(regions):
            if not isinstance(r, dict):
                continue
            name = str(r.get("name", f"region_{idx+1}"))
            rect = r.get("rect", None)
            prompt = str(r.get("prompt", "") or "").strip()
            weight = float(r.get("weight", 1.0) or 1.0)

            if not prompt:
                continue
            if not (isinstance(rect, list) and len(rect) == 4):
                continue

            x0, y0, x1, y1 = [float(v) for v in rect]
            x0 = _clamp(x0, 0.0, 1.0)
            y0 = _clamp(y0, 0.0, 1.0)
            x1 = _clamp(x1, 0.0, 1.0)
            y1 = _clamp(y1, 0.0, 1.0)
            w = _clamp(x1 - x0, 0.0, 1.0)
            h = _clamp(y1 - y0, 0.0, 1.0)
            if w <= 0.0 or h <= 0.0:
                continue

            cond = _call(enc, clip=clip, text=prompt)[0]
            strength = _clamp(weight * float(region_strength_multiplier), 0.0, float(strength_cap))

            if ConditioningSetAreaPercentage is not None:
                sa = ConditioningSetAreaPercentage()
                cond_area = _call(sa, conditioning=cond, width=w, height=h, x=x0, y=y0, strength=strength)[0]
                pos_parts.append(cond_area)
                debug_lines.append(f"{name}={x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f} | strength={strength:.2f}")
            elif ConditioningSetArea is not None:
                px_w = int(round(w * int(width_px)))
                px_h = int(round(h * int(height_px)))
                px_x = int(round(x0 * int(width_px)))
                px_y = int(round(y0 * int(height_px)))
                sa = ConditioningSetArea()
                cond_area = _call(sa, conditioning=cond, width=px_w, height=px_h, x=px_x, y=px_y, strength=strength)[0]
                pos_parts.append(cond_area)
                debug_lines.append(f"{name}=px({px_x},{px_y},{px_w},{px_h}) | strength={strength:.2f}")
            else:
                pos_parts.append(cond)
                debug_lines.append(f"{name}=no set-area node (non-spatial)")

        if not pos_parts:
            pos_out = _call(enc, clip=clip, text="")[0]
            debug_lines.append("no parts -> empty conditioning")
            return (pos_out, neg_cond, region_plan_json, "\n".join(debug_lines))

        # Combine positive parts
        if ConditioningCombine is not None and len(pos_parts) >= 2:
            comb = ConditioningCombine()
            cur = pos_parts[0]
            for nxt in pos_parts[1:]:
                cur = _call(comb, conditioning_1=cur, conditioning_2=nxt)[0]
            pos_out = cur
        else:
            pos_out = []
            for part in pos_parts:
                pos_out = pos_out + part

        return (pos_out, neg_cond, region_plan_json, "\n".join(debug_lines))


class SynapseRegionPreview:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "region_plan_json": ("STRING", {"multiline": True, "default": ""}),
                "width_px": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 8}),
                "height_px": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 8}),
                "border_thickness": ("INT", {"default": 3, "min": 1, "max": 20, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview", "debug_report")
    FUNCTION = "render"
    CATEGORY = "synapse/regions"

    def render(self, region_plan_json: str, width_px: int, height_px: int, border_thickness: int = 3):
        import torch

        try:
            plan = json.loads(region_plan_json) if region_plan_json else {}
        except Exception:
            plan = {}

        regions = plan.get("regions", []) if isinstance(plan, dict) else []

        img = torch.zeros((1, int(height_px), int(width_px), 3), dtype=torch.float32)

        debug_lines = [f"preview {width_px}x{height_px} | regions={len(regions)}"]
        t = max(1, int(border_thickness))

        def draw_rect(x0, y0, x1, y1):
            x0 = max(0, min(int(width_px) - 1, int(x0)))
            x1 = max(0, min(int(width_px) - 1, int(x1)))
            y0 = max(0, min(int(height_px) - 1, int(y0)))
            y1 = max(0, min(int(height_px) - 1, int(y1)))
            if x1 <= x0 or y1 <= y0:
                return
            img[:, y0:y0 + t, x0:x1, :] = 1.0
            img[:, y1 - t:y1, x0:x1, :] = 1.0
            img[:, y0:y1, x0:x0 + t, :] = 1.0
            img[:, y0:y1, x1 - t:x1, :] = 1.0

        for idx, r in enumerate(regions):
            if not isinstance(r, dict):
                continue
            rect = r.get("rect", None)
            name = str(r.get("name", f"region_{idx+1}"))
            if not (isinstance(rect, list) and len(rect) == 4):
                continue
            x0, y0, x1, y1 = [float(v) for v in rect]
            px0 = int(round(_clamp(x0, 0.0, 1.0) * width_px))
            py0 = int(round(_clamp(y0, 0.0, 1.0) * height_px))
            px1 = int(round(_clamp(x1, 0.0, 1.0) * width_px))
            py1 = int(round(_clamp(y1, 0.0, 1.0) * height_px))
            draw_rect(px0, py0, px1, py1)
            debug_lines.append(f"{name}: {x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}")

        return (img, "\n".join(debug_lines))
