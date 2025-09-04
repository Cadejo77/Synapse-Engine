import { GenerationContext } from './types.js';

const FIGURE_TEMPLATES = [
  "A {rarityAdj}{physique}{species} {archetype}{power_source}{modifiers} {gear_primary}{gear_secondary}, {emotion}{condition}",
  "{rarityAdj}{species} {archetype}{power_source}{modifiers}, bearing {gear_primary}{gear_secondary}, {emotion}{condition}"
];

const LANDSCAPE_TEMPLATES = [
  "A {rarityAdj}{biomes}{structures}{atmosphere_mood}{weather}{time_of_day}{special_fx}",
  "{rarityAdj}{biomes} scene{structures}{atmosphere_mood}{time_of_day}{special_fx}"
];

function listOrEmpty(ctx: GenerationContext, key: string, joiner = ", "): string {
  const arr = ctx.tokens[key] || [];
  return arr.length ? arr.join(joiner) : "";
}

function rarityAdjective(r: string): string {
  switch (r) {
    case 'rare': return "rare ";
    case 'epic': return "epic ";
    default: return "";
  }
}

export function assemblePrompt(ctx: GenerationContext): string {
  if (ctx.mode === 'legacy' && ctx.chosenLegacy) {
    return ctx.chosenLegacy;
  }

  if (ctx.content_type === 'figure' || ctx.content_type === 'hybrid') {
    const template = FIGURE_TEMPLATES[Math.floor(Math.random() * FIGURE_TEMPLATES.length)];
    const species = listOrEmpty(ctx, 'species', " ");
    const archetype = listOrEmpty(ctx, 'archetypes', " ");
    const physique = listOrEmpty(ctx, 'physiques', " ");
    const power = listOrEmpty(ctx, 'power_sources', " & ");
    const mods = listOrEmpty(ctx, 'modifiers', ", ");
    const gp = listOrEmpty(ctx, 'gear_primary', " & ");
    const gs = listOrEmpty(ctx, 'gear_secondary', " & ");
    const emotion = listOrEmpty(ctx, 'emotions', " ");
    const condition = listOrEmpty(ctx, 'conditions', " ");

    return template
      .replace("{rarityAdj}", rarityAdjective(ctx.rarity))
      .replace("{physique}", physique ? physique + " " : "")
      .replace("{species}", species)
      .replace("{archetype}", archetype ? " " + archetype : "")
      .replace("{power_source}", power ? " empowered by " + power : "")
      .replace("{modifiers}", mods ? " adorned with " + mods : "")
      .replace("{gear_primary}", gp ? gp : "")
      .replace("{gear_secondary}", gs ? " + " + gs : "")
      .replace("{emotion}", emotion ? emotion : "")
      .replace("{condition}", condition ? " (" + condition + ")" : "")
      .replace(/\s+/g, " ")
      .trim();
  } else {
    const template = LANDSCAPE_TEMPLATES[Math.floor(Math.random() * LANDSCAPE_TEMPLATES.length)];
    const biome = listOrEmpty(ctx, 'biomes', " ");
    const structure = listOrEmpty(ctx, 'structures', " ");
    const mood = listOrEmpty(ctx, 'atmosphere_mood', ", ");
    const weather = listOrEmpty(ctx, 'weather', " ");
    const tod = listOrEmpty(ctx, 'time_of_day', " ");
    const fx = listOrEmpty(ctx, 'special_fx', ", ");

    return template
      .replace("{rarityAdj}", rarityAdjective(ctx.rarity))
      .replace("{biomes}", biome)
      .replace("{structures}", structure ? " with " + structure : "")
      .replace("{atmosphere_mood}", mood ? " under " + mood : "")
      .replace("{weather}", weather ? " " + weather : "")
      .replace("{time_of_day}", tod ? " at " + tod : "")
      .replace("{special_fx}", fx ? " featuring " + fx : "")
      .replace(/\s+/g, " ")
      .trim();
  }
}

export function assembleStyle(ctx: GenerationContext): string {
  const parts: string[] = [];
  for (const key of ['palettes','lighting','camera','media','depth_effects','framing','focus_styles','quality_combo']) {
    if (ctx.tokens[key] && ctx.tokens[key].length) {
      parts.push(...ctx.tokens[key]);
    }
  }
  return parts.length ? "Style: " + parts.join(", ") : "";
}

export function makeTagsHeader(ctx: GenerationContext): string {
  const basePairs: [string,string][] = [
    ['genre', ctx.genre],
    ['rarity', ctx.rarity],
    ['vibe', ctx.vibe],
    ['mode', ctx.mode],
    ['type', ctx.content_type]
  ];
  const dimTags: string[] = [];
  for (const [k, arr] of Object.entries(ctx.tokens)) {
    for (const tok of arr) {
      dimTags.push(`/${k}:${tok}/`);
    }
  }
  const header = basePairs.map(([k,v]) => `/${k}:${v}/`).join(" ") + " " + dimTags.join(" ");
  return header.trim();
}