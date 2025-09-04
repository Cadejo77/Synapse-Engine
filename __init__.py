"""
Synapse Engine - Advanced Prompt Generation for ComfyUI

This module provides a sophisticated prompt generation system using YAML-based
dimensional composition and legacy templates.
"""

from .synapse_node import NODE_CLASS_MAPPINGS as SYNAPSE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SYNAPSE_DISPLAY_MAPPINGS
from .regional_synapse_node import NODE_CLASS_MAPPINGS as REGIONAL_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as REGIONAL_DISPLAY_MAPPINGS

# Combine mappings from both nodes
NODE_CLASS_MAPPINGS = {**SYNAPSE_MAPPINGS, **REGIONAL_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**SYNAPSE_DISPLAY_MAPPINGS, **REGIONAL_DISPLAY_MAPPINGS}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']