from .procedural_prompt_graph import ProceduralPromptGraphV2
from .synapse_regions import SynapseRegionConditioning, SynapseRegionPreview
from .synapse_palette_driver import SynapseColorPaletteDriver
from .synapse_lora_mixer import SynapseLoRAStyleMixer

NODE_CLASS_MAPPINGS = {
    "ProceduralPromptGraphV2": ProceduralPromptGraphV2,
    "SynapseRegionConditioning": SynapseRegionConditioning,
    "SynapseRegionPreview": SynapseRegionPreview,
    "SynapseColorPaletteDriver": SynapseColorPaletteDriver,
    "SynapseLoRAStyleMixer": SynapseLoRAStyleMixer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ProceduralPromptGraphV2": "Procedural Prompt Graph v2 (Synapse)",
    "SynapseRegionConditioning": "Synapse Region Conditioning",
    "SynapseRegionPreview": "Synapse Region Preview",
    "SynapseColorPaletteDriver": "Synapse Color Palette Driver",
    "SynapseLoRAStyleMixer": "Synapse LoRA Style Mixer",
}
