export type Rarity = 'common' | 'rare' | 'epic';

export interface WeightedEntry {
  weight: number;
  token?: string;
  name?: string;
  text?: string;
  rarity_min?: Rarity;
  rarity_max?: Rarity;
  allow_genres?: string[];
  block_genres?: string[];
  vibe_bias?: string;
  alias?: string;
  tags?: string[];
  synergy_tags?: string[];
  complexity_cost?: number;
}

export interface GenreEntry { token: string; weight: number; }
export interface VibeEntry { token: string; weight: number; }
export interface RarityEntry { rarity: Rarity; weight: number; }
export interface ContentTypeEntry { type: string; weight: number; }

export interface RarityOverride {
  match_type: 'token_equals';
  field: string;
  token: string;
  multiplier: number;
  reason?: string;
}

export interface RelationSpeciesArchetype {
  species: string;
  archetype: string;
  weight_multiplier: number;
}
export interface RelationArchetypePower {
  archetype: string;
  power_source: string;
  weight_multiplier: number;
}
export interface RelationBiomeStructure {
  biome: string;
  structure: string;
  weight_multiplier: number;
}
export interface RelationVibePalette {
  vibe: string;
  palette: string;
  weight_multiplier: number;
}

export interface ConflictRule {
  tokens: string[];
  strategy: 'suppress_second' | 'allow_if_genre_multi' | 'reduce_weight';
  factor?: number;
  reason?: string;
}

export interface ComplexityRules {
  rarity_budgets: Record<Rarity, number>;
  default_cost: number;
  modifier_cost_scale: { diminishing_factor: number };
  overflow_strategy: 'truncate_optionals';
}

export interface SafetyFlags {
  [category: string]: string[];
}

export interface SafetyPolicy {
  block_if_combination?: string[][];
  optional_strip_categories?: string[];
}

export interface SafetyConfig {
  flags: SafetyFlags;
  policy: SafetyPolicy;
}

export interface SynonymsConfig {
  synonyms: Record<string, string[]>;
  normalization?: {
    lowercase?: boolean;
    replace_spaces_with_underscores?: boolean;
  };
}

export interface PipelineConfig {
  mode_selector: { compositional_chance: number };
  order: string[];
  figure_dimensions: {
    required: string[];
    optional: string[];
  };
  landscape_dimensions: {
    required: string[];
    optional: string[];
  };
  style_dimensions: {
    order: string[];
  };
  constraints: {
    max_modifiers?: number;
    max_special_fx?: number;
  };
  rarity_rules?: {
    rare_allows_extra_modifier?: boolean;
    epic_adds_depth_effects?: boolean;
  };
}

export interface HybridPlan {
  steps: ({ pool: string; weight: number } | { action: string; weight: number })[];
  max_steps: number;
  allow_early_stop: boolean;
}

export interface GenerationContext {
  genre: string;
  rarity: Rarity;
  vibe: string;
  content_type: 'figure' | 'landscape' | 'hybrid';
  tokens: Record<string, string[]>;
  complexityUsed: number;
  budget: number;
  chosenLegacy?: string;
  warnings: string[];
  relationsApplied: string[];
  conflictsApplied: string[];
  mode: 'legacy' | 'compositional';
}

export interface PoolFile {
  metadata?: any;
  [key: string]: any;
}

export interface SelectionResult {
  prompt: string;
  tagsHeader: string;
  metadata: GenerationContext;
}

export interface LoadedConfig {
  rootDir: string;
  meta: {
    genres: any;
    rarities: any;
    rarity_overrides: any;
    content_types: any;
    vibes: any;
    safety: any;
    synonyms: any;
    complexity: any;
  };
  relations: {
    species_archetype: any;
    archetype_power_source: any;
    biome_structure: any;
    vibe_palette: any;
    conflicts: any;
  };
  pools: Record<string, any>;
  pipeline: any;
  hybrid: any;
  legacy: {
    subjects: string[];
    landscapes: string[];
    finishers: { text: string; weight: number }[];
  };
}