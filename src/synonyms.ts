import { SynonymsConfig } from './types.js';

export function normalizeToken(token: string, cfg: SynonymsConfig): string {
  let t = token;
  if (cfg.normalization?.lowercase) t = t.toLowerCase();
  if (cfg.normalization?.replace_spaces_with_underscores) {
    t = t.replace(/\s+/g, '_');
  }
  for (const [canon, variants] of Object.entries(cfg.synonyms || {})) {
    if (canon === t) return canon;
    if (variants.includes(t)) return canon;
  }
  return t;
}

export function normalizeAll(tokens: string[], cfg: SynonymsConfig): string[] {
  return tokens.map(t => normalizeToken(t, cfg));
}