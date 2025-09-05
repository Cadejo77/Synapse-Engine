"""
Synapse Engine - Advanced Prompt Generation for ComfyUI

This module provides a sophisticated prompt generation system with rich descriptions
and advanced regional prompting capabilities including wild divide technology.
"""

from .synapse_node import NODE_CLASS_MAPPINGS as SYNAPSE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SYNAPSE_DISPLAY_MAPPINGS
from .regional_synapse_node import NODE_CLASS_MAPPINGS as REGIONAL_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as REGIONAL_DISPLAY_MAPPINGS
from .wild_divide_regional_node import NODE_CLASS_MAPPINGS as WILD_DIVIDE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as WILD_DIVIDE_DISPLAY_MAPPINGS

# Combine mappings from all nodes
NODE_CLASS_MAPPINGS = {**SYNAPSE_MAPPINGS, **REGIONAL_MAPPINGS, **WILD_DIVIDE_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**SYNAPSE_DISPLAY_MAPPINGS, **REGIONAL_DISPLAY_MAPPINGS, **WILD_DIVIDE_DISPLAY_MAPPINGS}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']