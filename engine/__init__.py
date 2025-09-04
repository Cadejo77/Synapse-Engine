"""
Synapse Engine - Python implementation of the compositional prompt generator
"""

from .generator import PromptGenerator
from .loader import load_all_config

__all__ = ['PromptGenerator', 'load_all_config']