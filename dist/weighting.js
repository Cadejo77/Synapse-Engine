export function applyRarityAndGenreFilters(entries, rarity, genre) {
    return entries.filter(e => {
        if (e.rarity_min && rarityRank(rarity) < rarityRank(e.rarity_min))
            return false;
        if (e.rarity_max && rarityRank(rarity) > rarityRank(e.rarity_max))
            return false;
        if (e.allow_genres && e.allow_genres.length && !e.allow_genres.includes(genre))
            return false;
        if (e.block_genres && e.block_genres.includes(genre))
            return false;
        return true;
    });
}
export function applyVibeBias(entries, vibe, multiplier = 1.2) {
    for (const e of entries) {
        if (e.vibe_bias && e.vibe_bias === vibe) {
            e.weight = Math.max(1, Math.round(e.weight * multiplier));
        }
    }
}
export function applyOverrides(entries, overrides, fieldName) {
    for (const ov of overrides) {
        if (ov.field !== fieldName)
            continue;
        if (ov.match_type === 'token_equals') {
            for (const e of entries) {
                if (e.token === ov.token || e.name === ov.token) {
                    e.weight = Math.max(1, Math.round(e.weight * ov.multiplier));
                }
            }
        }
    }
}
export function rarityRank(r) {
    switch (r) {
        case 'common': return 1;
        case 'rare': return 2;
        case 'epic': return 3;
    }
}
export function normalizeWeights(_entries) {
    // Optional normalization placeholder
}
