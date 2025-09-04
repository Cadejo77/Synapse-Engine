# Advanced Prompt Generation YAML System

This repository contains a fully decomposed, compositional prompt generation dataset plus legacy monolithic lines. The system supports:

1. Mode Selection:
   - Compositional (dimension-driven) vs Legacy (pre-fused line).
2. Conditional Gating:
   - rarity_min / rarity_max
   - allow_genres / block_genres
   - vibe_bias
3. Relational Weight Adjustments:
   - species ↔ archetype
   - archetype ↔ power_source
   - biome ↔ structure
   - vibe ↔ palette
4. Conflict Handling (negative_conflicts)
5. Complexity Budgeting (complexity_rules.yaml)
6. Style & Composition Layers
7. Safety Filtering (safety_flags.yaml)
8. Synonym Normalization (synonyms.yaml)
9. Rarity Overrides (rarity_overrides.yaml)
10. Tag Emission:
    - Final prompt can prepend /genre:.../ /rarity:.../ /vibe:.../ etc.

## Generation Flow (Recommended)
1. Pick genre (genre_selector)
2. Pick rarity (rarity_tiers)
3. Pick vibe (vibe_selector)
4. Pick content_type (content_type_selector)
5. If legacy fallback (prob from pipeline) → choose line from subject_core_legacy or landscape_core_legacy (+ optional finishers)
6. Else compositional:
   - For figure: choose species, archetype, physique, etc. respecting gating & complexity budget.
   - For landscape: choose biome, structure, atmosphere, etc.
   - Apply relation multipliers & conflict rules.
   - Apply rarity overrides & vibe/palette bias.
   - Add style layers (palette, lighting, camera, medium, depth, framing, focus, quality combo).
7. Safety Pass (remove offending optional tokens or re-roll).
8. Assemble textual prompt using template variants.
9. Emit /tag:value/ metadata prefix (optional).
10. Log choices (token usage, rarity, complexity load).

## Complexity Budget (Default)
Defined per rarity in complexity_rules.yaml. Each chosen token has complexity_cost (default 1 unless elevated). Stop adding optional pools when budget would be exceeded.

## Adding New Dimension Tokens
- Add an entry with weight + token
- If specialized: set rarity_min and/or allow_genres
- If it synergizes with others: add synergy_tags or a relation multiplier entry
- If it conflicts: add conflict rule in negative_conflicts.yaml or conflicts field directly

## Files Overview
See file tree in main answer. Each pool file ends with a metadata block showing version & selection parameters.

## Next Steps (Optional)
- Add composites (macro archetype bundles)
- Add faction/culture dimension
- Introduce usage_stats tracking & dynamic overrides
- Add template variants file for natural language assembly

Version: dataset_v1_full_decomposed