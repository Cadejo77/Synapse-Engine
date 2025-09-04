import {
  RelationSpeciesArchetype,
  RelationArchetypePower,
  RelationBiomeStructure,
  RelationVibePalette,
  WeightedEntry
} from './types.js';

export interface RelationData {
  species_archetype: { relations: RelationSpeciesArchetype[] };
  archetype_power_source: { relations: RelationArchetypePower[] };
  biome_structure: { relations: RelationBiomeStructure[] };
  vibe_palette: { relations: RelationVibePalette[] };
  conflicts: { conflicts: any[] };
}

export function applySpeciesArchetype(
  chosenSpecies: string | undefined,
  archetypeCandidates: WeightedEntry[],
  rel: RelationData['species_archetype']
): string[] {
  const applied: string[] = [];
  if (!chosenSpecies) return applied;
  for (const r of rel.relations) {
    if (r.species === chosenSpecies) {
      const match = archetypeCandidates.find(a => a.token === r.archetype);
      if (match) {
        match.weight = Math.max(1, Math.round(match.weight * r.weight_multiplier));
        applied.push(`species_archetype:${chosenSpecies}->${r.archetype} x${r.weight_multiplier}`);
      }
    }
  }
  return applied;
}

export function applyArchetypePower(
  chosenArchetype: string | undefined,
  powerCandidates: WeightedEntry[],
  rel: RelationData['archetype_power_source']
): string[] {
  const applied: string[] = [];
  if (!chosenArchetype) return applied;
  for (const r of rel.relations) {
    if (r.archetype === chosenArchetype) {
      const match = powerCandidates.find(p => p.token === r.power_source);
      if (match) {
        match.weight = Math.max(1, Math.round(match.weight * r.weight_multiplier));
        applied.push(`archetype_power:${chosenArchetype}->${r.power_source} x${r.weight_multiplier}`);
      }
    }
  }
  return applied;
}

export function applyBiomeStructure(
  chosenBiome: string | undefined,
  structureCandidates: WeightedEntry[],
  rel: RelationData['biome_structure']
): string[] {
  const applied: string[] = [];
  if (!chosenBiome) return applied;
  for (const r of rel.relations) {
    if (r.biome === chosenBiome) {
      const match = structureCandidates.find(s => s.token === r.structure);
      if (match) {
        match.weight = Math.max(1, Math.round(match.weight * r.weight_multiplier));
        applied.push(`biome_structure:${chosenBiome}->${r.structure} x${r.weight_multiplier}`);
      }
    }
  }
  return applied;
}

export function applyVibePalette(
  chosenVibe: string,
  paletteCandidates: WeightedEntry[],
  rel: RelationData['vibe_palette']
): string[] {
  const applied: string[] = [];
  for (const r of rel.relations) {
    if (r.vibe === chosenVibe) {
      const match = paletteCandidates.find(p => p.token === r.palette);
      if (match) {
        match.weight = Math.max(1, Math.round(match.weight * r.weight_multiplier));
        applied.push(`vibe_palette:${chosenVibe}->${r.palette} x${r.weight_multiplier}`);
      }
    }
  }
  return applied;
}