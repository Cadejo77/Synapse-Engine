export function applySpeciesArchetype(chosenSpecies, archetypeCandidates, rel) {
    const applied = [];
    if (!chosenSpecies)
        return applied;
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
export function applyArchetypePower(chosenArchetype, powerCandidates, rel) {
    const applied = [];
    if (!chosenArchetype)
        return applied;
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
export function applyBiomeStructure(chosenBiome, structureCandidates, rel) {
    const applied = [];
    if (!chosenBiome)
        return applied;
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
export function applyVibePalette(chosenVibe, paletteCandidates, rel) {
    const applied = [];
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
