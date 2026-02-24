import os
import re
import html as _html
import yaml
import random
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set


# ----------------------------
# YAML loading + caching
# ----------------------------

_YAML_CACHE: Dict[str, Tuple[float, Any]] = {}

def _load_yaml(path: str) -> Any:
    """Load YAML with caching by mtime."""
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        raise FileNotFoundError(f"YAML file not found: {path}")

    cached = _YAML_CACHE.get(path)
    if cached and cached[0] == mtime:
        return cached[1]

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    _YAML_CACHE[path] = (mtime, data)
    return data


# ----------------------------
# DSL parsing
# ----------------------------

_META_RE = re.compile(r"\bmeta:[A-Za-z0-9_:\-]+\b")
_TOKEN_RE = re.compile(r"__(.+?)__")  # supports slashes inside tokens
_WEIGHT_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*,\s*(.*)\s*$")

@dataclass
class Entry:
    kind: str  # "weighted" | "router" | "plain"
    conditions: List[str] = field(default_factory=list)
    weight: float = 0.0
    text: str = ""

def _normalize_item(item: Any) -> Optional[str]:
    """Convert YAML list item into a usable string, handling dicts created by ':' parsing."""
    if item is None:
        return None
    if isinstance(item, str):
        s = item.strip()
        return s if s else None
    if isinstance(item, dict) and len(item) == 1:
        k, v = next(iter(item.items()))
        if isinstance(k, (int, float)):
            if v is None:
                return str(k)
            return f"{k}, {str(v).strip()}"
        s = f"{str(k).strip()}: {str(v).strip()}"
        return s if s else None
    # Fallback to string conversion
    s = str(item).strip()
    return s if s else None

def _parse_entry(line: str) -> Entry:
    s = line.strip()

    # Extract one or more leading /cond/ segments
    conditions: List[str] = []
    while s.startswith("/"):
        end = s.find("/", 1)
        if end == -1:
            break
        cond = s[1:end].strip()
        conditions.append(cond)
        s = s[end+1:].lstrip()

        # Router marker immediately after a condition: "/cond/="
        if s.startswith("="):
            s = s[1:].lstrip()
            return Entry(kind="router", conditions=conditions, text=s)

        # Support optional extra whitespace between conditions
        if not s.startswith("/"):
            break

    # Weighted entry: "W, text"
    m = _WEIGHT_RE.match(s)
    if m:
        w = float(m.group(1))
        txt = m.group(2).strip()
        return Entry(kind="weighted", conditions=conditions, weight=w, text=txt)

    # Plain entry: just text (possibly conditional)
    return Entry(kind="plain", conditions=conditions, text=s)

def _conditions_match(active_tags: Set[str], conds: List[str]) -> bool:
    # AND semantics
    for c in conds:
        if c not in active_tags:
            return False
    return True


# ----------------------------
# Expansion engine
# ----------------------------

def _primary_key_for_module_stem(stem: str, module: Dict[str, Any]) -> Optional[str]:
    """For 'class_fantasy.yaml' choose 'class' if present; else stem itself."""
    for suf in ("_fantasy", "_scifi"):
        if stem.endswith(suf):
            base = stem[:-len(suf)]
            if base in module:
                return base
    if stem in module:
        return stem
    # last resort: if the module has exactly one top-level key, use it
    if isinstance(module, dict) and len(module) == 1:
        return next(iter(module.keys()))
    return None

@dataclass
class Context:
    rng: random.Random
    strip_meta: bool
    sep_text: str
    active_tags: Set[str] = field(default_factory=set)
    call_stack: List[Tuple[str, str]] = field(default_factory=list)  # (module_stem, key)
    call_stack_set: Set[Tuple[str, str]] = field(default_factory=set)
    debug_lines: Optional[List[str]] = None
    max_depth: int = 80
    complexity_budget: int = 80
    complexity_used: int = 0
    enable_synonym_normalize: bool = False

class Preset:
    def __init__(self, preset_dir: str):
        self.preset_dir = preset_dir
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.key_index: Dict[str, List[str]] = {}  # key -> [module_stem...]
        self._load_all()

    def _load_all(self):
        if not os.path.isdir(self.preset_dir):
            raise FileNotFoundError(f"Preset directory not found: {self.preset_dir}")

        for fn in os.listdir(self.preset_dir):
            if not fn.lower().endswith(".yaml"):
                continue
            path = os.path.join(self.preset_dir, fn)
            stem = os.path.splitext(fn)[0]
            data = _load_yaml(path)
            if not isinstance(data, dict):
                data = {}
            self.modules[stem] = data

        # build key index
        self.key_index.clear()
        for stem, mod in self.modules.items():
            if not isinstance(mod, dict):
                continue
            for k in mod.keys():
                self.key_index.setdefault(k, []).append(stem)

    def resolve_token(self, token: str, current_stem: str) -> Tuple[str, str]:
        """
        Return (module_stem, key) for a token name.
        Supports:
        - path tokens like 'fantasy/subject/class_fantasy' -> module 'class_fantasy', key 'class'
        - local keys first
        - unique key across all modules
        """
        # Path token
        if "/" in token:
            stem = token.split("/")[-1].strip()
            if stem not in self.modules:
                raise KeyError(f"Token '{token}' points to missing module '{stem}.yaml'")
            key = _primary_key_for_module_stem(stem, self.modules[stem])
            if not key:
                raise KeyError(f"Module '{stem}.yaml' has no resolvable primary key for token '{token}'")
            return stem, key

        # 1) current module wins
        cur_mod = self.modules.get(current_stem, {})
        if isinstance(cur_mod, dict) and token in cur_mod:
            return current_stem, token

        # 2) unique key in index
        stems = self.key_index.get(token, [])
        if len(stems) == 1:
            return stems[0], token

        # 3) token might refer to a module stem primary key (e.g., "__composition__")
        if token in self.modules:
            key = _primary_key_for_module_stem(token, self.modules[token])
            if key:
                return token, key

        # 4) suffix handling: token might be base key inside token_fantasy.yaml
        for suf in ("_fantasy", "_scifi"):
            if token.endswith(suf):
                stem = token
                if stem in self.modules:
                    key = _primary_key_for_module_stem(stem, self.modules[stem])
                    if key:
                        return stem, key

        # Ambiguous or missing
        if len(stems) > 1:
            raise KeyError(f"Ambiguous token '{token}': defined in multiple modules {stems}. Use a path token like __folder/{stems[0]}__.")
        raise KeyError(f"Unknown token '{token}' (not found in current module '{current_stem}' or globally).")

def _extract_meta_tags(text: str) -> List[str]:
    tags = []
    for m in _META_RE.finditer(text):
        tag = m.group(0).strip()
        if tag:
            tags.append(tag)
    return tags

def _strip_meta_from_text(text: str) -> str:
    # Remove meta tags but preserve other text
    parts = [p.strip() for p in text.split(",")]
    kept = []
    for p in parts:
        if not p:
            continue
        # remove meta tokens inside the part
        p2 = _META_RE.sub("", p).strip()
        # clean double spaces
        p2 = re.sub(r"\s{2,}", " ", p2).strip()
        if not p2:
            continue
        kept.append(p2)
    out = ", ".join(kept)
    # cleanup stray punctuation/spaces
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ",", out)
    return out

def _replace_sep(text: str, sep_text: str) -> str:
    return text.replace("[SEP]", sep_text)


def _relation_multiplier(active_tags: Set[str], text: str) -> float:
    text_l = text.lower()
    # lightweight relation biasing based on active routing tags
    if "meta:vibe:dark" in active_tags and any(t in text_l for t in ["necro", "death", "warlock", "gothic", "ashen"]):
        return 1.35
    if "meta:vibe:epic" in active_tags and any(t in text_l for t in ["legendary", "heroic", "epic", "paladin", "knight"]):
        return 1.25
    if "meta:vibe:romantic" in active_tags and any(t in text_l for t in ["soft", "warm", "pastel", "rose", "intimate"]):
        return 1.2
    if "meta:biome:forest" in active_tags and any(t in text_l for t in ["grove", "wood", "tree", "moss"]):
        return 1.2
    return 1.0


def _apply_safety_filter(prompt: str) -> str:
    banned = ["loli", "shota"]
    cleaned = prompt
    for b in banned:
        cleaned = re.sub(rf"\b{re.escape(b)}\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r",\s*,", ",", cleaned).strip(" ,")
    return cleaned


def _normalize_synonyms(prompt: str) -> str:
    parts = [p.strip() for p in re.split(r"[,\n]+", prompt) if p.strip()]
    mapping = {
        "ultra detailed": "highly detailed",
        "masterpiece": "high quality",
        "cinematic lighting": "dramatic lighting",
    }
    out: List[str] = []
    for p in parts:
        out.append(mapping.get(p.lower(), p))
    return ", ".join(out)


def _budget_cost(text: str) -> int:
    # basic complexity estimation by token count
    return max(1, len([p for p in re.split(r"[,\s]+", text) if p]))

def expand_text(preset: Preset, ctx: Context, current_stem: str, text: str) -> str:
    """
    Expand any __tokens__ in the text. During expansion:
    - Update ctx.active_tags whenever meta:* tokens appear.
    - Optionally strip meta tags from the emitted output.
    """
    text = _replace_sep(text, ctx.sep_text)

    def _expand_token(match: re.Match) -> str:
        token_name = match.group(1).strip()
        stem, key = preset.resolve_token(token_name, current_stem)
        return expand_key(preset, ctx, stem, key)

    # Expand iteratively until no tokens or depth exceeded
    out = text
    for _ in range(ctx.max_depth):
        if "__" not in out:
            break
        out2 = _TOKEN_RE.sub(_expand_token, out)
        if out2 == out:
            break
        out = out2

    # Update tags from the expanded text
    for tag in _extract_meta_tags(out):
        ctx.active_tags.add(tag)

    # Optionally strip meta tags from final output
    if ctx.strip_meta:
        out = _strip_meta_from_text(out)

    # final cleanup
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out

def expand_key(preset: Preset, ctx: Context, stem: str, key: str) -> str:
    # recursion guard
    if len(ctx.call_stack) >= ctx.max_depth:
        raise RecursionError(f"Expansion exceeded max depth ({ctx.max_depth}). Stack tail: {ctx.call_stack[-5:]}")

    if (stem, key) in ctx.call_stack_set:
        cycle = " -> ".join([f"{s}.{k}" for s, k in ctx.call_stack] + [f"{stem}.{key}"])
        raise RecursionError(f"Detected recursive cycle while expanding {stem}.{key}: {cycle}")

    mod = preset.modules.get(stem)
    if not isinstance(mod, dict) or key not in mod:
        raise KeyError(f"Missing key '{key}' in module '{stem}.yaml'")

    ctx.call_stack.append((stem, key))
    ctx.call_stack_set.add((stem, key))
    try:
        val = mod[key]

        # String value
        if isinstance(val, str):
            out = expand_text(preset, ctx, stem, val)
            if ctx.debug_lines is not None:
                ctx.debug_lines.append(f"[{stem}.{key}] STR -> {out}")
            return out

        # List value
        if isinstance(val, list):
            lines = []
            for it in val:
                s = _normalize_item(it)
                if s is None:
                    continue
                lines.append(_parse_entry(s))

            has_weight = any(e.kind == "weighted" for e in lines)
            has_router = any(e.kind == "router" for e in lines)

            # Sequential (no weights, no routers)
            if not has_weight and not has_router:
                outs = []
                for e in lines:
                    if e.conditions and not _conditions_match(ctx.active_tags, e.conditions):
                        continue
                    piece = expand_text(preset, ctx, stem, e.text)
                    if piece:
                        outs.append(piece)
                        if ctx.debug_lines is not None:
                            cond = " & ".join(e.conditions) if e.conditions else "ALL"
                            ctx.debug_lines.append(f"[{stem}.{key}] SEQ({cond}) -> {piece}")
                return ", ".join([o for o in outs if o]).strip(", ").strip()

            # Router-only
            if has_router and not has_weight:
                for e in lines:
                    if e.kind != "router":
                        continue
                    if _conditions_match(ctx.active_tags, e.conditions):
                        piece = expand_text(preset, ctx, stem, e.text)
                        if ctx.debug_lines is not None:
                            cond = " & ".join(e.conditions) if e.conditions else "ALL"
                            ctx.debug_lines.append(f"[{stem}.{key}] ROUTE({cond}) -> {piece}")
                        return piece
                if ctx.debug_lines is not None:
                    ctx.debug_lines.append(f"[{stem}.{key}] ROUTE -> (no match)")
                return ""

            # Weighted-only
            if has_weight and not has_router:
                candidates: List[Entry] = []
                for e in lines:
                    if e.kind != "weighted":
                        continue
                    if e.conditions and not _conditions_match(ctx.active_tags, e.conditions):
                        continue
                    if e.weight <= 0:
                        continue
                    candidates.append(e)

                if not candidates:
                    if ctx.debug_lines is not None:
                        ctx.debug_lines.append(f"[{stem}.{key}] WEIGHTED -> (no candidates)")
                    return ""

                if ctx.complexity_used >= ctx.complexity_budget:
                    candidates = sorted(candidates, key=lambda e: _budget_cost(e.text))
                weighted_rows = [(e, e.weight * _relation_multiplier(ctx.active_tags, e.text)) for e in candidates]
                total = sum(max(0.0, w) for _, w in weighted_rows)
                r = ctx.rng.random() * total if total > 0 else 0.0
                upto = 0.0
                chosen = candidates[-1]
                for e, w in weighted_rows:
                    upto += max(0.0, w)
                    if r <= upto:
                        chosen = e
                        break
                piece = expand_text(preset, ctx, stem, chosen.text)
                ctx.complexity_used += _budget_cost(piece)
                if ctx.debug_lines is not None:
                    cond = " & ".join(chosen.conditions) if chosen.conditions else "ALL"
                    ctx.debug_lines.append(f"[{stem}.{key}] WEIGHTED({cond}, w={chosen.weight}) -> {piece}")
                return piece

            # Mixed weights + routers (used in weapon_fantasy.yaml.weapon):
            # Interpret weighted entries as an "override chance" out of 100, otherwise fall through to router.
            weighted = [e for e in lines if e.kind == "weighted" and (not e.conditions or _conditions_match(ctx.active_tags, e.conditions)) and e.weight > 0]
            # Default: 100 - sum(weights) chance to NOT override
            sum_w = sum(e.weight for e in weighted)
            no_override_w = max(0.0, 100.0 - sum_w)

            # If nothing weighted applies, just route
            override = False
            chosen_override: Optional[Entry] = None
            if weighted and (sum_w > 0 or no_override_w > 0):
                total = sum_w + no_override_w
                r = ctx.rng.random() * total
                if r <= sum_w:
                    # choose an override
                    rr = ctx.rng.random() * sum_w
                    upto = 0.0
                    for e in weighted:
                        upto += e.weight
                        if rr <= upto:
                            chosen_override = e
                            break
                    override = chosen_override is not None

            if override and chosen_override:
                piece = expand_text(preset, ctx, stem, chosen_override.text)
                if ctx.debug_lines is not None:
                    cond = " & ".join(chosen_override.conditions) if chosen_override.conditions else "ALL"
                    ctx.debug_lines.append(f"[{stem}.{key}] MIXED OVERRIDE({cond}, w={chosen_override.weight}) -> {piece}")
                return piece

            # fallthrough: router
            for e in lines:
                if e.kind != "router":
                    continue
                if _conditions_match(ctx.active_tags, e.conditions):
                    piece = expand_text(preset, ctx, stem, e.text)
                    if ctx.debug_lines is not None:
                        cond = " & ".join(e.conditions) if e.conditions else "ALL"
                        ctx.debug_lines.append(f"[{stem}.{key}] MIXED ROUTE({cond}) -> {piece}")
                    return piece
            if ctx.debug_lines is not None:
                ctx.debug_lines.append(f"[{stem}.{key}] MIXED -> (no route match)")
            return ""

        # Other types
        out = str(val)
        out = expand_text(preset, ctx, stem, out)
        if ctx.debug_lines is not None:
            ctx.debug_lines.append(f"[{stem}.{key}] OTHER -> {out}")
        return out
    finally:
        ctx.call_stack.pop()
        ctx.call_stack_set.discard((stem, key))


# ----------------------------
# ComfyUI Node
# ----------------------------

class ProceduralPromptGraph:
    """
    Generate a prompt by expanding YAML tokens with simple constraint routing via meta:* tags.
    """

    @classmethod
    def _base_dir(cls) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def _presets_root(cls) -> str:
        return os.path.join(cls._base_dir(), "presets")

    @classmethod
    def _list_preset_folders(cls) -> List[str]:
        root = cls._presets_root()
        if not os.path.isdir(root):
            return ["default"]
        items = []
        for name in os.listdir(root):
            p = os.path.join(root, name)
            if os.path.isdir(p):
                items.append(name)
        return sorted(items) or ["default"]

    @classmethod
    def _list_yaml_files(cls, preset_folder: str) -> List[str]:
        folder = os.path.join(cls._presets_root(), preset_folder)
        if not os.path.isdir(folder):
            return []
        files = [f for f in os.listdir(folder) if f.lower().endswith(".yaml")]
        return sorted(files)

    @classmethod
    def INPUT_TYPES(cls):
        preset_folders = cls._list_preset_folders()
        default_preset = "default" if "default" in preset_folders else preset_folders[0]
        yaml_files = cls._list_yaml_files(default_preset)
        default_entry = "0_master_generator.yaml" if "0_master_generator.yaml" in yaml_files else (yaml_files[0] if yaml_files else "0_master_generator.yaml")

        return {
            "required": {
                "preset_folder": (preset_folders,),
                "entry_file": (yaml_files or [default_entry],),
                "entry_key": ("STRING", {"default": "template"}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31-1}),
                "sep_text": ("STRING", {"default": ", "}),
                "strip_meta_tags": ("BOOLEAN", {"default": True}),
                "debug": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "debug_report")
    FUNCTION = "generate"
    CATEGORY = "prompt"

    def generate(self, preset_folder: str, entry_file: str, entry_key: str, seed: int, sep_text: str, strip_meta_tags: bool, debug: bool):
        # Build preset
        preset_dir = os.path.join(self._presets_root(), preset_folder)
        preset = Preset(preset_dir)

        # Determine entry stem
        entry_stem = os.path.splitext(entry_file)[0]
        if entry_stem not in preset.modules:
            raise FileNotFoundError(f"Entry module not found: {entry_file} in preset '{preset_folder}'")

        ctx = Context(
            rng=random.Random(int(seed)),
            strip_meta=bool(strip_meta_tags),
            sep_text=str(sep_text),
            active_tags=set(),
            debug_lines=[] if debug else None,
        )

        try:
            prompt = expand_key(preset, ctx, entry_stem, entry_key)
            prompt = _replace_sep(prompt, ctx.sep_text)
            # Final cleanup: remove empty commas / extra spaces
            prompt = re.sub(r",\s*,", ",", prompt)
            prompt = re.sub(r"\s{2,}", " ", prompt).strip(" ,")
            # Split lines cleanup if sep contains newlines
            prompt = "\n".join([ln.strip(" ,") for ln in prompt.splitlines()]).strip()
        except Exception as e:
            dbg = "\n".join(ctx.debug_lines) if debug else ""
            raise RuntimeError(f"ProceduralPromptGraph failed: {e}\n\nDebug trace:\n{dbg}")

        debug_report = ""
        if debug:
            debug_report = "\n".join(ctx.debug_lines)
            debug_report += "\n\nActive meta tags:\n" + ", ".join(sorted([t for t in ctx.active_tags if t.startswith("meta:")]))
        return (prompt, debug_report)



# ============================
# v2 + companion nodes
# ============================

def _safe_unescape(s: str) -> str:
    try:
        return _html.unescape(s)
    except Exception:
        return s

def _split_tokens(prompt: str) -> List[str]:
    # Split on commas and newlines, preserve order
    parts = re.split(r"[,\n]+", prompt)
    out: List[str] = []
    for p in parts:
        t = p.strip()
        if not t:
            continue
        # remove empty quotes tokens
        if t in ('""', "''"):
            continue
        out.append(t)
    return out

def _dedupe_tokens(tokens: List[str]) -> Tuple[List[str], List[str]]:
    seen = set()
    kept = []
    removed = []
    for t in tokens:
        key = re.sub(r"\s+", " ", t.strip().lower())
        if key in seen:
            removed.append(t)
            continue
        seen.add(key)
        kept.append(t)
    return kept, removed

_ONEOF_GROUPS = {
    "lens": [
        r"\b35mm\b", r"\b50mm\b", r"\b85mm\b", r"\b24mm\b",
        r"wide-?angle lens", r"telephoto lens", r"anamorphic lens",
        r"macro lens", r"fisheye lens", r"portrait lens",
    ],
    "dof": [
        r"shallow depth of field", r"deep depth of field", r"medium depth of field",
        r"sharp focus throughout",
    ],
    "timeofday_day": [
        r"\bdaytime\b", r"sun high", r"bright sun", r"\bmidday\b",
        r"sunset", r"sunrise", r"golden hour",
    ],
    "timeofday_night": [
        r"pitch black night", r"\bnight\b", r"no moon", r"moonlight",
        r"starlit", r"\btwilight\b",
    ],
}

_WEAPON_HINTS = [
    "wielding", "holding", "gripping", "drawn sword", "longbow", "bow", "quiver",
    "sword", "dagger", "axe", "spear", "halberd", "mace", "hammer", "staff", "wand",
    "pistol", "rifle", "shotgun", "sniper", "katana", "blade", "scythe", "shield",
]

_UNARMED_HINTS = {"unarmed", "empty-handed", "empty handed", "barehanded", "hands empty"}

def _apply_oneof(tokens: List[str], patterns: List[str]) -> Tuple[List[str], List[str]]:
    kept = []
    removed = []
    chosen = None
    regexes = [re.compile(p, re.I) for p in patterns]
    for t in tokens:
        hit = any(r.search(t) for r in regexes)
        if not hit:
            kept.append(t)
            continue
        if chosen is None:
            chosen = t
            kept.append(t)
        else:
            removed.append(t)
    return kept, removed

def _resolve_weapon_conflicts(tokens: List[str]) -> Tuple[List[str], List[str]]:
    has_weapon = any(any(h in t.lower() for h in _WEAPON_HINTS) for t in tokens)
    if not has_weapon:
        return tokens, []
    kept = []
    removed = []
    for t in tokens:
        if t.strip().lower() in _UNARMED_HINTS:
            removed.append(t)
        else:
            kept.append(t)
    return kept, removed

def _resolve_time_conflicts(tokens: List[str]) -> Tuple[List[str], List[str]]:
    # If any night token exists, remove day tokens; if any day token exists, remove night tokens.
    has_night = any(any(re.search(p, t, re.I) for p in _ONEOF_GROUPS["timeofday_night"]) for t in tokens)
    has_day = any(any(re.search(p, t, re.I) for p in _ONEOF_GROUPS["timeofday_day"]) for t in tokens)
    removed = []
    if has_night and has_day:
        # Prefer whichever appears first in the token stream
        first_night = min([i for i,t in enumerate(tokens) if any(re.search(p,t,re.I) for p in _ONEOF_GROUPS["timeofday_night"])], default=10**9)
        first_day = min([i for i,t in enumerate(tokens) if any(re.search(p,t,re.I) for p in _ONEOF_GROUPS["timeofday_day"])], default=10**9)
        prefer_night = first_night < first_day
        kept=[]
        for t in tokens:
            is_night = any(re.search(p,t,re.I) for p in _ONEOF_GROUPS["timeofday_night"])
            is_day = any(re.search(p,t,re.I) for p in _ONEOF_GROUPS["timeofday_day"])
            if prefer_night and is_day:
                removed.append(t)
                continue
            if (not prefer_night) and is_night:
                removed.append(t)
                continue
            kept.append(t)
        return kept, removed
    return tokens, []

def conflict_resolve_prompt(prompt: str, *, html_unescape: bool=True) -> Tuple[str, Dict[str, Any]]:
    """Lightweight conflict resolver + sanitizer."""
    original = prompt
    if html_unescape:
        prompt = _safe_unescape(prompt)

    tokens = _split_tokens(prompt)

    removed_total = []

    # Remove exact duplicates
    tokens, removed = _dedupe_tokens(tokens)
    removed_total += removed

    # Enforce 1 lens + 1 DOF
    tokens, removed = _apply_oneof(tokens, _ONEOF_GROUPS["lens"])
    removed_total += removed
    tokens, removed = _apply_oneof(tokens, _ONEOF_GROUPS["dof"])
    removed_total += removed

    # Resolve time conflicts
    tokens, removed = _resolve_time_conflicts(tokens)
    removed_total += removed

    # Resolve weapon conflicts
    tokens, removed = _resolve_weapon_conflicts(tokens)
    removed_total += removed

    cleaned = ", ".join([t.strip(" ,") for t in tokens if t.strip(" ,")])

    report = {
        "removed": removed_total,
        "removed_count": len(removed_total),
        "html_unescaped": html_unescape,
        "changed": (cleaned != original),
    }
    return cleaned, report


class ProceduralPromptGraphV2(ProceduralPromptGraph):
    """Enhanced version with scenario dropdown + structured outputs."""

    @classmethod
    def _load_validator(cls, preset_folder: str) -> Dict[str, Any]:
        path = os.path.join(cls._presets_root(), preset_folder, "validator.yaml")
        if not os.path.isfile(path):
            return {}
        try:
            data = _load_yaml(path)
            return data.get("validator", {}) if isinstance(data, dict) else {}
        except Exception:
            return {}

    @classmethod
    def _scenario_names(cls, preset_folder: str) -> List[str]:
        v = cls._load_validator(preset_folder)
        sc = v.get("scenarios", [])
        out = []
        if isinstance(sc, list):
            for s in sc:
                if isinstance(s, dict) and s.get("name"):
                    out.append(str(s["name"]))
        return sorted(set(out))

    @classmethod
    def _scenario_locks(cls, preset_folder: str, scenario_name: str) -> List[str]:
        v = cls._load_validator(preset_folder)
        sc = v.get("scenarios", [])
        if isinstance(sc, list):
            for s in sc:
                if isinstance(s, dict) and s.get("name") == scenario_name:
                    locks = s.get("locks", [])
                    return [str(x) for x in locks] if isinstance(locks, list) else []
        return []

    @classmethod
    def INPUT_TYPES(cls):
        preset_folders = cls._list_preset_folders()
        default_preset = "default" if "default" in preset_folders else preset_folders[0]
        scenario_names = cls._scenario_names(default_preset)
        scenario_choices = ["<none>"] + scenario_names

        sep_mode = ["comma", "double_newline", "newline", "custom"]

        return {
            "required": {
                "preset_folder": (preset_folders,),
                "scenario": (scenario_choices,),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31-1}),
                "separator_mode": (sep_mode,),
                "sep_text": ("STRING", {"default": ", "}),
                "strip_meta_tags": ("BOOLEAN", {"default": True}),
                "apply_conflict_resolver": ("BOOLEAN", {"default": True}),
                "html_unescape": ("BOOLEAN", {"default": True}),
                "danbooru_normalize": ("BOOLEAN", {"default": True}),
                "dedupe_tags": ("BOOLEAN", {"default": True}),
                "normalize_synonyms": ("BOOLEAN", {"default": False}),
                "debug": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "entry_file": ("STRING", {"default": "0_master_generator.yaml"}),
                "entry_key": ("STRING", {"default": "template"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "subject_prompt", "scene_prompt", "composition_prompt", "ppg_json", "debug_report", "cleanup_report")
    FUNCTION = "generate_v2"
    CATEGORY = "prompt"

    def generate_v2(self,
                    preset_folder: str,
                    scenario: str,
                    seed: int,
                    separator_mode: str,
                    sep_text: str,
                    strip_meta_tags: bool,
                    apply_conflict_resolver: bool,
                    html_unescape: bool,
                    danbooru_normalize: bool,
                    dedupe_tags: bool,
                    normalize_synonyms: bool,
                    debug: bool,
                    entry_file: str = "0_master_generator.yaml",
                    entry_key: str = "template"):

        preset_dir = os.path.join(self._presets_root(), preset_folder)
        preset = Preset(preset_dir)

        entry_stem = os.path.splitext(entry_file)[0]
        if entry_stem not in preset.modules:
            raise FileNotFoundError(f"Entry module not found: {entry_file} in preset '{preset_folder}'")

        if separator_mode == "double_newline":
            sep_text2 = "\n\n"
        elif separator_mode == "newline":
            sep_text2 = "\n"
        elif separator_mode == "comma":
            sep_text2 = ", "
        else:
            sep_text2 = sep_text

        ctx = Context(
            rng=random.Random(seed),
            strip_meta=strip_meta_tags,
            sep_text=sep_text2,
            complexity_budget=80,
            enable_synonym_normalize=normalize_synonyms,
            debug_lines=[] if debug else None,
        )

        locks = []
        if scenario and scenario != "<none>":
            locks = self._scenario_locks(preset_folder, scenario)
            for t in locks:
                ctx.active_tags.add(t)

        subject = ""
        scene = ""
        comp = ""
        full_prompt = ""

        try:
            # Important: do NOT re-roll randomness for sections.
            # If we're using the standard master template, generate subject/scene/comp once
            # and assemble the final prompt from those same draws.
            module_dict = preset.modules.get(entry_stem, {})
            has_master_sections = (
                entry_key == "template"
                and isinstance(module_dict, dict)
                and "subject_prompt" in module_dict
                and "scene_prompt" in module_dict
            )

            if has_master_sections:
                subject = expand_key(preset, ctx, entry_stem, "subject_prompt")
                scene = expand_key(preset, ctx, entry_stem, "scene_prompt")
                try:
                    comp = expand_key(preset, ctx, "composition", "composition")
                except Exception:
                    comp = ""

                parts = [p for p in [subject, scene, comp] if p]
                full_prompt = (ctx.sep_text or ", ").join(parts)
            else:
                full_prompt = expand_key(preset, ctx, entry_stem, entry_key)
            full_prompt = _replace_sep(full_prompt, ctx.sep_text)
            subject = _replace_sep(subject, ctx.sep_text)
            scene = _replace_sep(scene, ctx.sep_text)
            comp = _replace_sep(comp, ctx.sep_text)

            negative_key = "negative_prompt" if isinstance(module_dict, dict) and "negative_prompt" in module_dict else "negative"
            negative_prompt = ""
            if isinstance(module_dict, dict) and negative_key in module_dict:
                negative_prompt = expand_key(preset, ctx, entry_stem, negative_key)
            elif "negative" in preset.modules and isinstance(preset.modules.get("negative"), dict) and "negative" in preset.modules["negative"]:
                negative_prompt = expand_key(preset, ctx, "negative", "negative")

            def _clean_basic(s: str) -> str:
                # Remove literal placeholder quotes that sometimes slip through from optional slots
                s = s.replace('""', "").replace("''", "")
                s = re.sub(r",\s*,", ",", s)
                s = re.sub(r"\s{2,}", " ", s).strip(" ,")
                # Common accidental duplicates
                s = re.sub(r"\bwith\s+with\b", "with", s, flags=re.IGNORECASE)
                s = re.sub(r"\bskin\s+skin\b", "skin", s, flags=re.IGNORECASE)
                # Split lines cleanup if sep contains newlines
                s = "\n".join([ln.strip(" ,") for ln in s.splitlines()]).strip()
                return s


            full_prompt = _clean_basic(full_prompt)
            negative_prompt = _clean_basic(negative_prompt)
            subject = _clean_basic(subject)
            scene = _clean_basic(scene)
            comp = _clean_basic(comp)

            full_prompt = _apply_safety_filter(full_prompt)
            negative_prompt = _apply_safety_filter(negative_prompt)
            if ctx.enable_synonym_normalize:
                full_prompt = _normalize_synonyms(full_prompt)
                negative_prompt = _normalize_synonyms(negative_prompt)

            cleanup_report = {}
            if apply_conflict_resolver:
                full_prompt, cleanup_report = conflict_resolve_prompt(full_prompt, html_unescape=html_unescape)
                if subject:
                    subject, _ = conflict_resolve_prompt(subject, html_unescape=html_unescape)
                if scene:
                    scene, _ = conflict_resolve_prompt(scene, html_unescape=html_unescape)
                if comp:
                    comp, _ = conflict_resolve_prompt(comp, html_unescape=html_unescape)

            
            def _normalize_danbooru(s: str) -> str:
                """
                Normalize prompt strings into Danbooru-friendly tag style:
                - lower-case
                - spaces -> underscores
                - normalize separators to commas
                - strip empty tokens
                """
                if not s:
                    return ""
                # unify separators
                s2 = s.replace("\n", ",")
                raw = [t.strip(" ,") for t in s2.split(",")]
                out = []
                seen = set()
                for t in raw:
                    if not t:
                        continue
                    # keep meta tags if any slipped through
                    if t.startswith("meta:"):
                        tok = t
                    else:
                        tok = t.strip()
                        # collapse internal whitespace and convert spaces to underscores
                        tok = re.sub(r"\s+", " ", tok)
                        tok = tok.lower().replace(" ", "_")
                        # remove accidental double-underscores
                        tok = re.sub(r"_+", "_", tok).strip("_")
                    if not tok:
                        continue
                    if dedupe_tags:
                        if tok in seen:
                            continue
                        seen.add(tok)
                    out.append(tok)
                return ", ".join(out).strip(" ,")

            if danbooru_normalize:
                full_prompt = _normalize_danbooru(full_prompt)
                negative_prompt = _normalize_danbooru(negative_prompt)
                subject = _normalize_danbooru(subject)
                scene = _normalize_danbooru(scene)
                comp = _normalize_danbooru(comp)

            meta_tags = sorted([t for t in ctx.active_tags if t.startswith("meta:")])
            ppg_json = json.dumps({
                "preset_folder": preset_folder,
                "entry_file": entry_file,
                "entry_key": entry_key,
                "scenario": None if scenario == "<none>" else scenario,
                "locks": locks,
                "seed": seed,
                "separator_mode": separator_mode,
                "sep_text": sep_text2,
                "meta_tags": meta_tags,
                "sections": {"subject": subject, "scene": scene, "composition": comp},
                "prompt": {"positive": full_prompt, "negative": negative_prompt},
                "cleanup": cleanup_report,
            }, ensure_ascii=False)

            debug_report = ""
            if debug:
                debug_report = "\n".join(ctx.debug_lines)
                debug_report += "\n\nActive meta tags:\n" + ", ".join(meta_tags)

            return (full_prompt, negative_prompt, subject, scene, comp, ppg_json, debug_report, json.dumps(cleanup_report, ensure_ascii=False))

        except Exception as e:
            dbg = "\n".join(ctx.debug_lines) if debug else ""
            raise RuntimeError(f"ProceduralPromptGraphV2 failed: {e}\n\nDebug trace:\n{dbg}")


class PPGConflictResolver:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"prompt": ("STRING", {"multiline": True, "default": ""}), "html_unescape": ("BOOLEAN", {"default": True})}}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("clean_prompt", "cleanup_report")
    FUNCTION = "resolve"
    CATEGORY = "prompt/ppg"

    def resolve(self, prompt: str, html_unescape: bool):
        clean, report = conflict_resolve_prompt(prompt, html_unescape=html_unescape)
        return (clean, json.dumps(report, ensure_ascii=False))


class PPGPromptSections:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"ppg_json": ("STRING", {"multiline": True, "default": ""})}}
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "subject_prompt", "scene_prompt", "composition_prompt", "meta_json")
    FUNCTION = "split"
    CATEGORY = "prompt/ppg"

    def split(self, ppg_json: str):
        try:
            data = json.loads(ppg_json) if ppg_json else {}
        except Exception:
            data = {}
        positive = (data.get("prompt", {}) or {}).get("positive", "") if isinstance(data, dict) else ""
        sections = data.get("sections", {}) if isinstance(data, dict) else {}
        subject = sections.get("subject", "") if isinstance(sections, dict) else ""
        scene = sections.get("scene", "") if isinstance(sections, dict) else ""
        comp = sections.get("composition", "") if isinstance(sections, dict) else ""
        meta = json.dumps({
            "preset_folder": data.get("preset_folder") if isinstance(data, dict) else None,
            "scenario": data.get("scenario") if isinstance(data, dict) else None,
            "meta_tags": data.get("meta_tags") if isinstance(data, dict) else [],
            "locks": data.get("locks") if isinstance(data, dict) else [],
            "seed": data.get("seed") if isinstance(data, dict) else None,
        }, ensure_ascii=False)
        return (positive, subject, scene, comp, meta)
