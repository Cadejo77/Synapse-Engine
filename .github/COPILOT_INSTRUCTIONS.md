# GitHub Copilot Instructions for YAMLPromptMaster

## Project Overview

YAMLPromptMaster is a TypeScript-based compositional prompt generation system designed to produce rich structured prompts for AI image/content generation workflows (e.g., ComfyUI custom node integration). It uses a layered YAML configuration model with subjects, environments, style, meta configurations, relations, and conflicts.

## Architecture Overview

### Core Components

The system is organized into modular components:

- **`src/index.ts`**: CLI entry point - loads config, parses args (`--count`, `--json`, `--out`), invokes generator
- **`src/types.ts`**: Central domain model - rarity, weighting interfaces, complexity, safety, synonyms, relations, config shape, context
- **`src/configLoader.ts`**: Aggregates YAML into in-memory `LoadedConfig` - performs existence checks & basic transforms
- **`src/generator.ts`**: Core generation pipeline (mode selection, pool selection, relations, conflicts, safety, normalization, assembly)
- **`src/utils/random.ts`**: Weighted random + shuffle helpers (currently non-seeded)
- **`src/weighting.ts`**: Applies rarity filtering, genre allow/block, vibe bias, and overrides
- **`src/relations.ts`**: Weight multipliers based on synergy (species→archetype, archetype→power_source, etc.)
- **`src/conflicts.ts`**: Implements suppression/reduce_weight strategies
- **`src/complexity.ts`**: Budget enforcement, diminishing cost scaffolding
- **`src/safety.ts`**: Categorizes tokens into safety flags & policy check
- **`src/synonyms.ts`**: Normalization and canonical mapping
- **`src/promptAssembler.ts`**: Builds final string + style concatenation + tag header

### Data Flow

1. CLI selects count → loads YAML set
2. For each prompt:
   - Choose meta axes (genre, rarity, vibe, content_type)
   - Determine mode: compositional vs legacy
   - If compositional: process required pools, apply relations/conflicts, enforce complexity
   - If legacy: choose weighted line + finisher
   - Safety classification & optional warning creation
   - Synonym normalization
   - Prompt assembly (structured + style + header)
3. Collect output (optionally JSON)

## Configuration System

### Directory Structure
```
config/meta/*.yaml          # Core metadata configurations
config/meta/relations/*.yaml # Relationship rules
config/subjects/*.yaml       # Character/figure related pools
config/environments/*.yaml   # Environment/landscape pools
config/style/*.yaml          # Style and aesthetic pools
plans/*.yaml                # Generation pipelines and hybrid plans
data/*.yaml                 # Legacy prompt lines
```

### Pool File Pattern
All pool files follow this structure:
- Top-level `metadata:` section (choose_min, choose_max, second_pick_chance, diminishing_factor, choose_probability)
- Plural key array (e.g., `species:`, `modifiers:`, `lighting:`)
- Token objects with gating fields & optional complexity_cost

### Key Configuration Files
- `meta/genre_selector.yaml`: Genre definitions and weights
- `meta/rarity_tiers.yaml`: Rarity levels (common, rare, epic) and their probabilities
- `meta/complexity_rules.yaml`: Budget allocation per rarity level
- `meta/safety_flags.yaml`: Safety categorization rules
- `meta/synonyms.yaml`: Token normalization mappings
- `plans/generation_pipeline.yaml`: Generation flow configuration

## Development Guidelines

### Code Patterns

#### Type Safety
- All configurations use strongly typed interfaces defined in `types.ts`
- Use `LoadedConfig` interface for configuration objects
- Use `GenerationContext` for tracking generation state
- Use `SelectionResult` for final output

#### Random Selection
```typescript
// Use weightedSample for single selection
const pick = weightedSample(candidates);

// Use weightedSample multiple times for multiple picks
// Apply diminishing factor for repeated selections from same pool
```

#### Pool Processing
```typescript
// Standard pool processing pattern
const poolData = this.cfg.pools[poolName];
const candidates = applyWeighting(poolData, ctx);
applyRelations(candidates, ctx);
applyConflicts(candidates, ctx);
const selections = chooseFromPool(candidates, metadata);
```

#### Error Handling
- Missing YAML files throw immediately with descriptive error
- Pool processing adds warnings to context rather than failing
- Use `ctx.warnings.push()` for recoverable issues

### Testing Strategy

When adding tests, follow these patterns:

#### Unit Tests
- **Relations**: Test that species selection increases archetype weights
- **Conflicts**: Verify suppression/reduction strategies work correctly
- **Complexity**: Ensure budget enforcement prevents overspend
- **Safety**: Validate policy violation detection

#### Integration Tests
- Run multiple generations and verify statistical distribution
- Test end-to-end flow from config loading to prompt output
- Verify JSON output format consistency

#### Snapshot Tests
- Use fixed seeds for deterministic testing (future enhancement)
- Compare output stability across code revisions

### Configuration Management

#### Adding New Tokens
1. Add entries with appropriate weights to relevant pool files
2. Set `rarity_min`/`rarity_max` if specialized
3. Add `allow_genres`/`block_genres` for genre-specific tokens
4. Consider complexity_cost for resource management
5. Add relations in appropriate relation files if synergies exist
6. Add conflict rules if incompatibilities exist

#### Pool Metadata
```yaml
metadata:
  choose_min: 1           # Minimum selections (0 for optional pools)
  choose_max: 2           # Maximum selections
  choose_probability: 0.8 # Probability of selecting from this pool
  second_pick_chance: 0.3 # Probability of additional picks beyond minimum
  diminishing_factor: 0.65 # Weight reduction for additional picks
```

### Relations System

Relations create synergistic weight multipliers:

```yaml
# species_archetype_bias.yaml
relations:
  - species: "elf"
    archetype: "mage"
    weight_multiplier: 2.5
```

**Application Order**: Relations must be applied before conflicts. Prerequisites must be selected first.

### Conflicts System

Conflicts handle incompatible token combinations:

```yaml
# negative_conflicts.yaml
conflicts:
  - tokens: ["holy_aura", "cursed_energy"]
    strategy: "suppress_second"
    reason: "Religious conflict"
  
  - tokens: ["fire_elemental", "ice_magic"]
    strategy: "reduce_weight"
    factor: 0.3
```

**Strategies**:
- `suppress_second`: Set conflicting token weight to 0
- `reduce_weight`: Multiply weight by factor (default 0.5)
- `allow_if_genre_multi`: Only apply conflict if genre is not "multi"

### Safety System

Current implementation uses substring matching:

```typescript
// Categorize all tokens by safety flags
const safetyMap = categorizeTokens(allTokens, this.cfg.meta.safety);

// Check for policy violations
if (violatesPolicy(safetyMap, this.cfg.meta.safety)) {
  ctx.warnings.push('Safety violation: blocked category combination');
}
```

**Future Enhancement**: Move to token-level safety annotations instead of substring scanning.

### Complexity Budget

Each rarity level has a complexity budget:
- **Common**: Lower budget, fewer tokens
- **Rare**: Medium budget, allows extra modifiers
- **Epic**: High budget, enables depth effects

Tokens can specify `complexity_cost` or use the default cost from complexity rules.

## Common Tasks

### Adding a New Dimension

1. Create new YAML file in appropriate config directory
2. Add pool name to `configLoader.ts` mapping
3. Update generation pipeline in `generator.ts`
4. Add to prompt assembly templates if needed
5. Consider relations and conflicts with existing dimensions

### Implementing New Relation Type

1. Add interface to `types.ts`
2. Create YAML file in `config/meta/relations/`
3. Add loading logic to `configLoader.ts`
4. Implement application logic in `relations.ts`
5. Update generator to apply the new relation type

### Adding Safety Rules

1. Update `safety_flags.yaml` with new category/tokens
2. Add policy rules to prevent harmful combinations
3. Test with various token combinations
4. Consider adding optional strip categories for automatic cleanup

## Known Technical Debt

### High Priority
- **Non-deterministic RNG**: Add `--seed` parameter for reproducible runs
- **No schema validation**: Implement JSON Schema validation for YAML files
- **Missing tests**: Add comprehensive unit and integration test suite

### Medium Priority
- **Order sensitivity**: Relations require prerequisite selection order
- **Simple conflict resolution**: Single-pass logic may miss complex scenarios
- **Limited error aggregation**: Individual file failures stop entire load process

### Future Enhancements
- **Pluggable extensions**: API for custom dimension modules
- **Advanced conflict engine**: Constraint solver approach
- **Performance optimization**: Caching and precomputed adjacency maps

## CLI Usage

```bash
# Basic generation
node dist/index.js --count 5

# JSON output
node dist/index.js --count 10 --json --out results.json

# Custom config directory
node dist/index.js --root ./custom-config --count 3
```

## Build & Development

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Development with ts-node
npm run dev

# Production run
npm run gen
```

## Contributing Guidelines

1. **Types First**: Define interfaces in `types.ts` before implementing features
2. **Minimal Changes**: Make surgical modifications, avoid large refactors
3. **Test Coverage**: Add tests for new relation types and conflict strategies
4. **Configuration Validation**: Run builds and basic generation tests before PRs
5. **Documentation**: Update this file when adding new patterns or significant features

## Debugging Tips

### Generation Issues
- Check `ctx.warnings` for selection problems
- Verify pool file naming matches plural expectations
- Ensure metadata sections are properly formatted
- Test individual pools in isolation

### Weight/Selection Problems
- Add debug logging to see candidate counts after filtering
- Verify rarity gating isn't too restrictive
- Check for conflicts suppressing all candidates
- Validate complexity budget isn't too low

### Configuration Loading
- Check YAML syntax with online validators
- Verify file paths match expected directory structure
- Ensure all referenced relations/conflicts files exist
- Test with minimal configuration first

## Version Management

- **Config versions**: Tag configuration changes separately (`config-v1.2.0`)
- **Engine versions**: Tag code releases (`engine-v1.2.0`)
- **Breaking changes**: Major version increments for schema or algorithm changes
- **Compatibility**: Maintain backward compatibility within major versions