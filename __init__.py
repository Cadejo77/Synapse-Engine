from .procedural_prompt_graph import (
    ProceduralPromptGraph,
    ProceduralPromptGraphV2,
    PPGConflictResolver,
    PPGPromptSections,
    PPGRegionPlanBuilder,
)

NODE_CLASS_MAPPINGS = {
    "ProceduralPromptGraph": ProceduralPromptGraph,
    "ProceduralPromptGraphV2": ProceduralPromptGraphV2,
    "PPGConflictResolver": PPGConflictResolver,
    "PPGPromptSections": PPGPromptSections,
    "PPGRegionPlanBuilder": PPGRegionPlanBuilder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ProceduralPromptGraph": "Procedural Prompt Graph (YAML)",
    "ProceduralPromptGraphV2": "Procedural Prompt Graph v2 (scenarios + sections)",
    "PPGConflictResolver": "PPG Conflict Resolver",
    "PPGPromptSections": "PPG Prompt Sections (from JSON)",
    "PPGRegionPlanBuilder": "PPG Region Plan Builder",
}
