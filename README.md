# Advanced Prompt Generation YAML System

This repository contains a fully decomposed, compositional prompt generation dataset plus legacy monolithic lines. 

**❓ [See FAQ.md](FAQ.md) for common questions, including "What's the difference between this and regular chat?"**

**🚀 Quick Demo:** Run `./demo.sh` to see the system in action!

The system supports:

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

## Why Use This System vs Regular Chat?

This structured YAML-based approach offers several key advantages over simply asking an AI to generate prompts through conversation:

### 1. **Consistency & Repeatability**
- **Structured System**: Generates prompts following consistent patterns and quality standards every time
- **Regular Chat**: Each conversation produces different results, quality varies based on how you phrase requests

### 2. **Comprehensive Coverage**
- **Structured System**: Systematically covers all aspects (species, archetypes, gear, lighting, composition, etc.) based on predefined taxonomies
- **Regular Chat**: May miss important details or focus inconsistently on different aspects

### 3. **Balanced Relationships**
- **Structured System**: Automatically applies weighted relationships (e.g., certain species work better with specific archetypes) and handles conflicts intelligently
- **Regular Chat**: Relies on AI's training patterns, which may not always produce optimal combinations

### 4. **Complexity Control**
- **Structured System**: Uses complexity budgets to prevent prompt overload while ensuring minimum quality thresholds
- **Regular Chat**: No built-in mechanism to control prompt complexity or ensure balanced detail levels

### 5. **Systematic Variation**
- **Structured System**: Produces controlled variation through weighted randomization across multiple dimensions
- **Regular Chat**: Variation depends on how you phrase requests and AI creativity limits

### 6. **Quality Assurance**
- **Structured System**: Built-in safety filtering, conflict resolution, and synonym normalization
- **Regular Chat**: No systematic quality control or filtering mechanisms

### 7. **Scalability & Automation**
- **Structured System**: Can generate hundreds of high-quality prompts in seconds without manual intervention
- **Regular Chat**: Requires individual conversations and manual quality checking for each prompt

### 8. **Customization & Control**
- **Structured System**: Fine-tune weights, add new dimensions, modify relationships, and adjust complexity rules through YAML configuration
- **Regular Chat**: Limited ability to systematically customize AI behavior beyond conversation techniques

### Example Comparison

**Regular Chat Approach:**
```
User: "Create a fantasy character prompt"
AI: "A brave elven warrior with magical powers"
```

**Structured System Output:**
```
/genre:dark_fantasy/ /rarity:epic/ /vibe:serene/ /mode:compositional/ 
/type:figure/ /species:tiefling_ember/ /archetypes:stormcaller/ 
/physiques:sturdy/ /emotions:introspective/ /conditions:sand_scoured/ 
/power_sources:arcane/ /gear_primary:longsword/ 
/gear_secondary:grapnel_spool/ /modifiers:living_ink_tattoos/ 

A epic sturdy tiefling_ember stormcaller empowered by arcane 
adorned with living_ink_tattoos longsword + grapnel_spool, 
introspective (sand_scoured). 

Style: volcanic_ember_char, rim_high_contrast, digital_paint, 
subtle_depth_of_field, centered_subject
```

The structured approach provides rich detail, consistent quality, and systematic coverage that would be difficult to achieve reliably through conversation alone.

---

Version: dataset_v1_full_decomposed