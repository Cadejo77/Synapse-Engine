"""
Regional Synapse Node - Works with the main Synapse node to provide regional prompt outputs
Splits the universal prompt into organized sections for advanced prompting techniques
"""
import re
from typing import List, Dict, Any

class RegionalSynapseNode:
    """
    A ComfyUI custom node that takes a Synapse-generated prompt and splits it into regions.
    Designed to work in connection with the main SynapsePromptGenerator node.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "main_prompt": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "enable_second_subject": ("BOOLEAN", {"default": False}),
                "custom_quality_tags": ("STRING", {"default": "", "multiline": True}),
                "custom_background": ("STRING", {"default": "", "multiline": True}),
                "custom_supporting": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("quality_tags", "subject_description", "background_location", "supporting_tags", "second_subject")
    FUNCTION = "split_regional_prompt"
    CATEGORY = "text/synapse"
    
    def split_regional_prompt(self, main_prompt, enable_second_subject=False, 
                            custom_quality_tags="", custom_background="", custom_supporting=""):
        """
        Split the main prompt into regional components following the requested structure:
        1. Quality tags
        2. Subject description  
        3. Background/location description
        4. Supporting tags (atmosphere, weather, vibe, color palette, style)
        5. Optional second subject
        """
        try:
            # Parse the main prompt parts
            if not main_prompt or not main_prompt.strip():
                return ("", "", "", "", "")
            
            # Split by comma and clean
            parts = [part.strip() for part in main_prompt.split(',') if part.strip()]
            
            if not parts:
                return ("", "", "", "", "")
            
            # Initialize output lists
            quality_parts = []
            subject_parts = []
            background_parts = []
            supporting_parts = []
            second_subject_parts = []
            
            # Quality tag indicators (usually at the beginning)
            quality_indicators = ['masterpiece', 'best quality', 'high resolution', 'amazing quality', 'very aesthetic']
            
            # Subject indicators
            subject_indicators = [
                'knight', 'warrior', 'mage', 'wizard', 'sorceress', 'battlemage', 'shadowblade',
                'elf', 'dwarf', 'human', 'orc', 'character', 'person', 'figure', 'barbarian',
                'rogue', 'paladin', 'archer', 'fighter', 'spellcaster', 'adventurer', 'hero',
                'dragon', 'beast', 'creature', 'demon', 'angel', 'spirit', 'ghost'
            ]
            
            # Background/location indicators
            background_indicators = [
                'forest', 'mountain', 'castle', 'temple', 'landscape', 'glade', 'chapel', 'tower',
                'cathedral', 'overpass', 'cityscape', 'environment', 'background', 'scene',
                'clearing', 'alleyway', 'dungeon', 'cavern', 'ruins', 'village', 'city', 'plains',
                'desert', 'ocean', 'river', 'lake', 'valley', 'cliff', 'bridge', 'palace',
                'interior', 'exterior', 'room', 'hall', 'chamber', 'courtyard', 'garden'
            ]
            
            # Supporting tag indicators (atmosphere, effects, style)  
            supporting_indicators = [
                'mist', 'fog', 'rain', 'storm', 'overcast', 'dawn', 'dusk', 'night', 'sunset',
                'lighting', 'chiaroscuro', 'texture', 'embers', 'sparks', 'glow', 'shadow',
                'atmospheric', 'dramatic', 'ancient', 'mystical', 'grim', 'dark', 'bright',
                'whimsical', 'serene', 'treasure', 'adventurous', 'heroic', 'epic', 'magical',
                'desaturated', 'oversaturated', 'tone', 'style', 'art', 'painting', 'cinematic'
            ]
            
            # Track subject count for second subject detection
            subject_count = 0
            
            # Categorize each part
            for part in parts:
                part_lower = part.lower()
                categorized = False
                
                # Check for quality tags first
                if any(indicator in part_lower for indicator in quality_indicators):
                    quality_parts.append(part)
                    categorized = True
                
                # Check for subjects
                elif any(indicator in part_lower for indicator in subject_indicators):
                    subject_count += 1
                    if enable_second_subject and subject_count > 1:
                        second_subject_parts.append(part)
                    else:
                        subject_parts.append(part)
                    categorized = True
                
                # Check for background/location
                elif any(indicator in part_lower for indicator in background_indicators):
                    background_parts.append(part)
                    categorized = True
                
                # Check for supporting tags
                elif any(indicator in part_lower for indicator in supporting_indicators):
                    supporting_parts.append(part)
                    categorized = True
                
                # If not categorized, try to make educated guesses
                if not categorized:
                    # Adjectives and descriptors typically go to supporting
                    if len(part.split()) == 1 and not part.isnumeric():
                        supporting_parts.append(part)
                    # Multi-word phrases might be subjects or backgrounds
                    elif len(part.split()) > 1:
                        # Check if it contains "with" or prepositions (likely subject descriptor)
                        if any(word in part_lower for word in ['with', 'wearing', 'holding', 'carrying']):
                            if enable_second_subject and subject_count > 0:
                                second_subject_parts.append(part)
                            else:
                                subject_parts.append(part)
                        # Otherwise assume supporting
                        else:
                            supporting_parts.append(part)
                    else:
                        supporting_parts.append(part)
            
            # Apply custom overrides
            if custom_quality_tags.strip():
                custom_quality = [part.strip() for part in custom_quality_tags.split(',') if part.strip()]
                quality_parts = custom_quality
            
            if custom_background.strip():
                custom_bg = [part.strip() for part in custom_background.split(',') if part.strip()]
                background_parts = custom_bg
                
            if custom_supporting.strip():
                custom_supp = [part.strip() for part in custom_supporting.split(',') if part.strip()]
                supporting_parts = custom_supp
            
            # Format outputs
            quality_output = ', '.join(quality_parts) if quality_parts else ""
            subject_output = ', '.join(subject_parts) if subject_parts else ""
            background_output = ', '.join(background_parts) if background_parts else ""
            supporting_output = ', '.join(supporting_parts) if supporting_parts else ""
            second_subject_output = ', '.join(second_subject_parts) if second_subject_parts else ""
            
            return (quality_output, subject_output, background_output, supporting_output, second_subject_output)
            
        except Exception as e:
            print(f"[Regional Synapse Node][ERROR] Exception in split_regional_prompt: {e}")
            return (f"Error: {e}", "", "", "", "")


NODE_CLASS_MAPPINGS = {
    "RegionalSynapseNode": RegionalSynapseNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegionalSynapseNode": "Regional Synapse Node"
}