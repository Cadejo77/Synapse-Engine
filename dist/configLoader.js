import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
function readYaml(filePath) {
    if (!fs.existsSync(filePath))
        throw new Error(`Missing YAML: ${filePath}`);
    const content = fs.readFileSync(filePath, 'utf-8');
    return yaml.load(content);
}
function ensureArray(value) {
    return Array.isArray(value) ? value : [];
}
export function loadAllConfig(rootDir) {
    const metaDir = path.join(rootDir, 'config/meta');
    const styleDir = path.join(rootDir, 'config/style');
    const subjectsDir = path.join(rootDir, 'config/subjects');
    const envDir = path.join(rootDir, 'config/environments');
    const compositionDir = path.join(rootDir, 'config/composition');
    const relationsDir = path.join(metaDir, 'relations');
    const plansDir = path.join(rootDir, 'plans');
    const dataDir = path.join(rootDir, 'data');
    const meta = {
        genres: readYaml(path.join(metaDir, 'genre_selector.yaml')),
        rarities: readYaml(path.join(metaDir, 'rarity_tiers.yaml')),
        rarity_overrides: readYaml(path.join(metaDir, 'rarity_overrides.yaml')),
        content_types: readYaml(path.join(metaDir, 'content_type_selector.yaml')),
        vibes: readYaml(path.join(metaDir, 'vibe_selector.yaml')),
        safety: readYaml(path.join(metaDir, 'safety_flags.yaml')),
        synonyms: readYaml(path.join(metaDir, 'synonyms.yaml')),
        complexity: readYaml(path.join(metaDir, 'complexity_rules.yaml')),
    };
    const relations = {
        species_archetype: readYaml(path.join(relationsDir, 'species_archetype_bias.yaml')),
        archetype_power_source: readYaml(path.join(relationsDir, 'archetype_power_source_bias.yaml')),
        biome_structure: readYaml(path.join(relationsDir, 'biome_structure_bias.yaml')),
        vibe_palette: readYaml(path.join(relationsDir, 'vibe_palette_bias.yaml')),
        conflicts: readYaml(path.join(relationsDir, 'negative_conflicts.yaml')),
    };
    const poolFiles = {
        species: 'species.yaml',
        archetypes: 'archetypes.yaml',
        physiques: 'physiques.yaml',
        emotions: 'emotions.yaml',
        conditions: 'conditions.yaml',
        power_sources: 'power_sources.yaml',
        gear_primary: 'gear_primary.yaml',
        gear_secondary: 'gear_secondary.yaml',
        modifiers: 'modifiers_general.yaml',
        biomes: 'biomes.yaml',
        structures: 'structures.yaml',
        atmosphere_mood: 'atmosphere_mood.yaml',
        weather: 'weather.yaml',
        time_of_day: 'time_of_day.yaml',
        special_fx: 'special_fx.yaml',
        palettes: 'color_palettes.yaml',
        lighting: 'lighting_styles.yaml',
        camera: 'camera_styles.yaml',
        media: 'medium_textures.yaml',
        depth_effects: 'depth_effects.yaml',
        framing: 'framing.yaml',
        focus_styles: 'focus_styles.yaml',
        quality_combo: 'style_quality_combo.yaml'
    };
    const pools = {};
    for (const [key, filename] of Object.entries(poolFiles)) {
        const baseDir = ['biomes', 'structures', 'atmosphere_mood', 'weather', 'time_of_day', 'special_fx'].includes(key) ? envDir :
            ['palettes', 'lighting', 'camera', 'media', 'depth_effects', 'framing', 'focus_styles', 'quality_combo'].includes(key) ? styleDir :
                ['species', 'archetypes', 'physiques', 'emotions', 'conditions', 'power_sources', 'gear_primary', 'gear_secondary', 'modifiers'].includes(key) ? subjectsDir :
                    compositionDir;
        pools[key] = readYaml(path.join(baseDir, filename));
    }
    const pipeline = readYaml(path.join(plansDir, 'generation_pipeline.yaml'));
    const hybrid = readYaml(path.join(plansDir, 'hybrid_subject_selector.yaml'));
    const legacySubjectsRaw = readYaml(path.join(dataDir, 'subject_core_legacy.yaml'));
    const legacyLandRaw = readYaml(path.join(dataDir, 'landscape_core_legacy.yaml'));
    const legacyFinRaw = readYaml(path.join(dataDir, 'env_style_finish_legacy.yaml'));
    const legacy = {
        subjects: ensureArray(legacySubjectsRaw.subjects),
        landscapes: ensureArray(legacyLandRaw.landscapes),
        finishers: ensureArray(legacyFinRaw.finishers)
    };
    return {
        rootDir,
        meta,
        relations,
        pools,
        pipeline,
        hybrid: hybrid.hybrid_plan,
        legacy
    };
}
