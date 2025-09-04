export function getCost(entry, rules) {
    return entry.complexity_cost ?? rules.default_cost;
}
export function canAccept(current, entry, rules, budget) {
    return current + getCost(entry, rules) <= budget;
}
export function applyDiminishing(chosenCount, baseWeight, dimFactor) {
    if (chosenCount === 0)
        return baseWeight;
    return Math.max(1, Math.round(baseWeight * Math.pow(dimFactor, chosenCount)));
}
