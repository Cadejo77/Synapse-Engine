import { SafetyConfig } from './types.js';

export function categorizeTokens(tokens: string[], safety: SafetyConfig): Record<string, string[]> {
  const map: Record<string, string[]> = {};
  for (const [category, words] of Object.entries(safety.flags)) {
    for (const token of tokens) {
      if (words.includes(token)) {
        if (!map[category]) map[category] = [];
        map[category].push(token);
      }
    }
  }
  return map;
}

export function violatesPolicy(catMap: Record<string, string[]>, safety: SafetyConfig): boolean {
  const combos = safety.policy.block_if_combination ?? [];
  for (const combo of combos) {
    if (combo.every(c => catMap[c] && catMap[c].length > 0)) {
      return true;
    }
  }
  return false;
}

export function stripOptionalCategories(
  tokens: string[],
  safety: SafetyConfig
): string[] {
  const stripCats = safety.policy.optional_strip_categories ?? [];
  if (!stripCats.length) return tokens;
  const forbidden = new Set<string>();
  for (const cat of stripCats) {
    const words = safety.flags[cat] || [];
    for (const w of words) forbidden.add(w);
  }
  return tokens.filter(t => !forbidden.has(t));
}