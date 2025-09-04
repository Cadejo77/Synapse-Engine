import { ComplexityRules, WeightedEntry } from './types.js';

export function getCost(entry: WeightedEntry, rules: ComplexityRules): number {
  return entry.complexity_cost ?? rules.default_cost;
}

export function canAccept(
  current: number,
  entry: WeightedEntry,
  rules: ComplexityRules,
  budget: number
): boolean {
  return current + getCost(entry, rules) <= budget;
}

export function applyDiminishing(
  chosenCount: number,
  baseWeight: number,
  dimFactor: number
): number {
  if (chosenCount === 0) return baseWeight;
  return Math.max(1, Math.round(baseWeight * Math.pow(dimFactor, chosenCount)));
}