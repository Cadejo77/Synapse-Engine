export function applyConflictRules(chosen, pendingPool, rules, genre) {
    const outcome = { reduced: [], suppressed: [], notes: [] };
    for (const rule of rules) {
        const [a, b] = rule.tokens;
        const hasA = chosen.includes(a);
        const hasB = chosen.includes(b) || pendingPool.some(p => p.token === b);
        if (!(hasA && hasB))
            continue;
        switch (rule.strategy) {
            case 'suppress_second': {
                for (const p of pendingPool) {
                    if (p.token === b) {
                        p.weight = 0;
                        outcome.suppressed.push(b);
                        outcome.notes.push(`suppressed ${b} due to conflict with ${a}`);
                    }
                }
                break;
            }
            case 'allow_if_genre_multi': {
                if (genre !== 'multi') {
                    for (const p of pendingPool) {
                        if (p.token === b) {
                            p.weight = Math.round(p.weight * 0.4);
                            outcome.reduced.push(`${b}*0.4`);
                        }
                    }
                    outcome.notes.push(`reduced ${b} (genre not multi) conflict ${a}-${b}`);
                }
                break;
            }
            case 'reduce_weight': {
                const factor = rule.factor ?? 0.5;
                for (const p of pendingPool) {
                    if (p.token === b) {
                        p.weight = Math.max(1, Math.round(p.weight * factor));
                        outcome.reduced.push(`${b}*${factor}`);
                    }
                }
                outcome.notes.push(`reduced ${b} factor ${rule.factor ?? 0.5} due to ${a}`);
                break;
            }
        }
    }
    return outcome;
}
