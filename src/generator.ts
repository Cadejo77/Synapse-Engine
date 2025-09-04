import type {
  GenerationContext,
  Rarity,
  WeightedEntry,
  PipelineConfig,
  ComplexityRules,
  SelectionResult,
  LoadedConfig
} from './types.js';
import { weightedRandom } from './utils/random.js';
import { applyRarityAndGenreFilters, applyVibeBias, applyOverrides } from './weighting.js';
import { getCost } from './complexity.js';
import { applySpeciesArchetype, applyArchetypePower, applyBiomeStructure, applyVibePalette } from './relations.js';
import { applyConflictRules } from './conflicts.js';
import { assemblePrompt, assembleStyle, makeTagsHeader } from './promptAssembler.js';
import { categorizeTokens, violatesPolicy } from './safety.js';
import { normalizeAll } from './synonyms.js';

type GenrePick = { weight: number; token: string };
type RarityPick = { weight: number; rarity: Rarity };
type VibePick = { weight: number; token: string };
type ContentTypePick = { weight: number; type: 'figure' | 'landscape' | 'hybrid' };

function extractArray(pools: any, key: string): WeightedEntry[] {
  const pf = pools[key];
  if (!pf) return [];
  const possibleKeys = [key, key.replace(/s$/, '')];
  for (const k of Object.keys(pf)) {
    if (Array.isArray(pf[k]) && possibleKeys.includes(k)) {
      return pf[k];
    }
  }
  for (const v of Object.values(pf)) {
    if (Array.isArray(v)) return v as WeightedEntry[];
  }
  return [];
}

function cloneEntries(entries: WeightedEntry[]): WeightedEntry[] {
  return entries.map(e => ({ ...e }));
}

function weightedSample(entries: WeightedEntry[]): WeightedEntry | undefined {
  if (!entries.length) return undefined;
  const total = entries.reduce((a, b) => a + b.weight, 0);
  let r = Math.random() * total;
  for (const e of entries) {
    r -= e.weight;
    if (r <= 0) return e;
  }
  return entries[entries.length - 1];
}

export class PromptGenerator {
  constructor(private readonly cfg: LoadedConfig) {}

  private pickGenre(): string {
    const g = weightedRandom<GenrePick>(this.cfg.meta.genres.genres as GenrePick[]);
    return g.token;
  }
  private pickRarity(): Rarity {
    const r = weightedRandom<RarityPick>(this.cfg.meta.rarities.rarities as RarityPick[]);
    return r.rarity;
  }
  private pickVibe(): string {
    const v = weightedRandom<VibePick>(this.cfg.meta.vibes.vibes as VibePick[]);
    return v.token;
  }
  private pickContentType(): 'figure' | 'landscape' | 'hybrid' {
    const ct = weightedRandom<ContentTypePick>(this.cfg.meta.content_types.content_types as ContentTypePick[]);
    return ct.type;
  }

  private chooseFromPool(
    ctx: GenerationContext,
    dim: string,
    required: boolean,
    complexity: ComplexityRules
  ): void {
    const raw = extractArray(this.cfg.pools, dim);
    if (!raw.length) {
      if (required) ctx.warnings.push(`Empty required dimension ${dim}`);
      return;
    }
    let candidates = cloneEntries(raw);
    candidates = applyRarityAndGenreFilters(candidates, ctx.rarity, ctx.genre);
    applyVibeBias(candidates, ctx.vibe, 1.2);
    applyOverrides(candidates, this.cfg.meta.rarity_overrides.overrides || [], dim);

    if (dim === 'archetypes') {
      ctx.relationsApplied.push(
        ...applySpeciesArchetype(ctx.tokens.species?.[0], candidates, this.cfg.relations.species_archetype)
      );
    }
    if (dim === 'power_sources') {
      ctx.relationsApplied.push(
        ...applyArchetypePower(ctx.tokens.archetypes?.[0], candidates, this.cfg.relations.archetype_power_source)
      );
    }
    if (dim === 'structures') {
      ctx.relationsApplied.push(
        ...applyBiomeStructure(ctx.tokens.biomes?.[0], candidates, this.cfg.relations.biome_structure)
      );
    }
    if (dim === 'palettes') {
      ctx.relationsApplied.push(
        ...applyVibePalette(ctx.vibe, candidates, this.cfg.relations.vibe_palette)
      );
    }

    const conflictData = this.cfg.relations.conflicts.conflicts || [];
    const chosenTokensFlat = Object.values(ctx.tokens).flat();
    applyConflictRules(chosenTokensFlat, candidates, conflictData, ctx.genre);
    candidates = candidates.filter(c => c.weight > 0);
    if (!candidates.length) {
      if (required) ctx.warnings.push(`All candidates filtered out for required ${dim}`);
      return;
    }

    const meta = (this.cfg.pools[dim]?.metadata) || {};
    const chooseMin = meta.choose_min ?? (required ? 1 : 0);
    const chooseMax = meta.choose_max ?? 1;
    const probability = meta.choose_probability ?? 1;
    const secondChance = meta.second_pick_chance ?? 0;
    const diminishingFactor = meta.diminishing_factor
      ?? this.cfg.meta.complexity.complexity.modifier_cost_scale?.diminishing_factor
      ?? 0.65;

    if (Math.random() > probability) return;

    const chosen: string[] = [];
    let attempts = 0;
    while (chosen.length < chooseMax && attempts < chooseMax * 6) {
      attempts++;
      const candCopy = candidates.map(c => ({ ...c }));
      if (chosen.length > 0 && chooseMax > 1) {
        for (const c of candCopy) {
          c.weight = Math.max(1, Math.round(c.weight * Math.pow(diminishingFactor, chosen.length)));
        }
      }
      const pick = weightedSample(candCopy);
      if (!pick) break;
      const cost = pick.complexity_cost ?? this.cfg.meta.complexity.complexity.default_cost;
      if (ctx.complexityUsed + cost > ctx.budget) break;
      chosen.push(pick.token || pick.name || '');
      ctx.complexityUsed += cost;
      candidates = candidates.filter(c => c.token !== pick.token && c.name !== pick.name);
      if (chosen.length >= chooseMin) {
        if (chosen.length < chooseMax) {
          if (Math.random() > secondChance) break;
        }
      }
      if (!candidates.length) break;
    }

    if (chosen.length) ctx.tokens[dim] = chosen;
    else if (required) ctx.warnings.push(`Failed to select required items for ${dim}`);
  }

  private legacyPick(ctx: GenerationContext): void {
    if (ctx.content_type === 'figure') {
      if (this.cfg.legacy.subjects.length) {
        ctx.chosenLegacy = this.weightedLegacyLine(this.cfg.legacy.subjects);
      }
    } else {
      if (this.cfg.legacy.landscapes.length) {
        ctx.chosenLegacy = this.weightedLegacyLine(this.cfg.legacy.landscapes);
      }
    }
    if (this.cfg.legacy.finishers.length && ctx.chosenLegacy) {
      const fin = this.pickFinisher();
      if (fin) ctx.chosenLegacy += " :: " + fin;
    }
  }

  private weightedLegacyLine(lines: string[]): string {
    const parsed = lines
      .map(l => {
        const m = l.match(/^\s*(\d+)\s*,\s*(.*)$/);
        if (!m) return null;
        return { weight: parseInt(m[1], 10), text: m[2] };
      })
      .filter(Boolean) as { weight: number; text: string }[];
    const total = parsed.reduce((a, b) => a + b.weight, 0);
    let r = Math.random() * total;
    for (const p of parsed) {
      r -= p.weight;
      if (r <= 0) return p.text;
    }
    return parsed[parsed.length - 1].text;
  }

  private pickFinisher(): string | undefined {
    const fins = this.cfg.legacy.finishers;
    if (!fins.length) return;
    const total = fins.reduce((a, b) => a + b.weight, 0);
    let r = Math.random() * total;
    for (const f of fins) {
      r -= f.weight;
      if (r <= 0) return f.text;
    }
    return fins[fins.length - 1].text;
  }

  private generateOne(): SelectionResult {
    const genre = this.pickGenre();
    const rarity = this.pickRarity();
    const vibe = this.pickVibe();
    const ct = this.pickContentType();
    const pipeline: PipelineConfig = this.cfg.pipeline.pipeline;
    const complexity: ComplexityRules = this.cfg.meta.complexity.complexity;

    const compositional = Math.random() < (pipeline.mode_selector?.compositional_chance ?? 0.7);

    const ctx: GenerationContext = {
      genre,
      rarity,
      vibe,
      content_type: ct,
      tokens: {},
      complexityUsed: 0,
      budget: complexity.rarity_budgets[rarity],
      warnings: [],
      relationsApplied: [],
      conflictsApplied: [],
      mode: compositional ? 'compositional' : 'legacy'
    };

    if (!compositional) {
      this.legacyPick(ctx);
    } else {
      if (ct === 'figure' || ct === 'hybrid') {
        for (const dim of pipeline.figure_dimensions.required) {
          this.chooseFromPool(ctx, dim, true, complexity);
        }
        for (const dim of pipeline.figure_dimensions.optional) {
          this.chooseFromPool(ctx, dim, false, complexity);
        }
      } else if (ct === 'landscape') {
        for (const dim of pipeline.landscape_dimensions.required) {
          this.chooseFromPool(ctx, dim, true, complexity);
        }
        for (const dim of pipeline.landscape_dimensions.optional) {
          this.chooseFromPool(ctx, dim, false, complexity);
        }
      }
      for (const dim of pipeline.style_dimensions.order) {
        this.chooseFromPool(ctx, dim, false, complexity);
      }
      if (rarity === 'epic' && pipeline.rarity_rules?.epic_adds_depth_effects) {
        if (!ctx.tokens.depth_effects || !ctx.tokens.depth_effects.length) {
          this.chooseFromPool(ctx, 'depth_effects', false, complexity);
        }
      }
    }

    const allTokens = Object.values(ctx.tokens).flat();
    const safetyMap = categorizeTokens(allTokens, this.cfg.meta.safety);
    if (violatesPolicy(safetyMap, this.cfg.meta.safety)) {
      ctx.warnings.push('Safety violation: blocked category combination');
    }

    for (const [k, arr] of Object.entries(ctx.tokens)) {
      ctx.tokens[k] = normalizeAll(arr, this.cfg.meta.synonyms);
    }

    let promptCore = assemblePrompt(ctx);
    if (compositional) {
      const styleStr = assembleStyle(ctx);
      if (styleStr) promptCore += ". " + styleStr;
    }

    const tagsHeader = makeTagsHeader(ctx);
    const fullPrompt = `${tagsHeader} ${promptCore}`.trim();

    return {
      prompt: fullPrompt,
      tagsHeader,
      metadata: ctx
    };
  }

  generate(count = 1): SelectionResult[] {
    const arr: SelectionResult[] = [];
    for (let i = 0; i < count; i++) arr.push(this.generateOne());
    return arr;
  }
}