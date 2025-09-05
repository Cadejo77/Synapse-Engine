"""
Regional Synapse Node - Advanced regional prompting for ComfyUI
Provides proper regional prompting with subject/background separation and multiple regions
Designed for use with advanced prompting techniques like BREAK, AND, wild divide, etc.
"""
import re
from typing import List, Dict, Any, Tuple

class RegionalSynapseNode:
    """
    Advanced regional prompting node that splits prompts into multiple regions
    for complex scene composition with proper subject/background separation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "main_prompt": ("STRING", {"forceInput": True}),
                "regional_mode": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "enable_second_subject": ("BOOLEAN", {"default": False}),
                "enable_third_region": ("BOOLEAN", {"default": False}),
                "subject_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
                "background_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
                "region_separator": (["BREAK", "AND", "|", "::"], {"default": "BREAK"}),
                "custom_quality_tags": ("STRING", {"default": "", "multiline": True}),
                "custom_background": ("STRING", {"default": "", "multiline": True}),
                "custom_supporting": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("full_prompt", "negative_prompt", "region_1", "region_2", "region_3", "quality_tags", "metadata")
    FUNCTION = "generate_regional_prompt"
    CATEGORY = "text/synapse"
    
    def generate_regional_prompt(self, main_prompt, regional_mode=True, enable_second_subject=False, 
                               enable_third_region=False, subject_weight=1.0, background_weight=1.0,
                               region_separator="BREAK", custom_quality_tags="", custom_background="", 
                               custom_supporting=""):
        """
        Generate comprehensive regional prompting output with multiple regions for complex scenes.
        
        Args:
            main_prompt: The input prompt from main Synapse node
            regional_mode: Whether to enable regional prompting mode
            enable_second_subject: Enable detection and separation of secondary subjects
            enable_third_region: Enable third region for additional elements
            subject_weight: Weight for subject regions (1.0 = normal)
            background_weight: Weight for background region (1.0 = normal) 
            region_separator: Separator to use between regions (BREAK, AND, |, ::)
            custom_quality_tags: Custom quality override
            custom_background: Custom background override
            custom_supporting: Custom supporting tags override
            
        Returns:
            Tuple of (full_prompt, negative_prompt, region_1, region_2, region_3, quality_tags, metadata)
        """
        try:
            if not main_prompt or not main_prompt.strip():
                return ("", "", "", "", "", "", "")
            
            # Parse and categorize the prompt components
            quality_parts, subject_parts, background_parts, supporting_parts, second_subject_parts = self._parse_prompt_components(
                main_prompt, enable_second_subject, custom_quality_tags, custom_background, custom_supporting
            )
            
            # Generate the full non-regional prompt (fallback)
            full_prompt = self._build_full_prompt(quality_parts, subject_parts, background_parts, supporting_parts, second_subject_parts)
            
            # Generate basic negative prompt 
            negative_prompt = self._generate_negative_prompt()
            
            if not regional_mode:
                # Return simple split without regional formatting
                return (
                    full_prompt,
                    negative_prompt,
                    ', '.join(subject_parts) if subject_parts else "",
                    ', '.join(background_parts) if background_parts else "",
                    ', '.join(second_subject_parts) if second_subject_parts else "",
                    ', '.join(quality_parts) if quality_parts else "",
                    f"Mode: Simple, Regions: {2 if enable_second_subject else 1}"
                )
            
            # Build regional prompts with proper weighting and separation
            region_1, region_2, region_3 = self._build_regional_prompts(
                quality_parts, subject_parts, background_parts, supporting_parts, second_subject_parts,
                enable_second_subject, enable_third_region, subject_weight, background_weight, region_separator
            )
            
            # Metadata about the regional configuration
            metadata = self._build_metadata(enable_second_subject, enable_third_region, subject_weight, background_weight, region_separator)
            
                return (
                full_prompt,
                negative_prompt, 
                region_1,
                region_2,
                region_3,
                ', '.join(quality_parts) if quality_parts else "",
                metadata
            )
            
        except Exception as e:
            print(f"[Regional Synapse Node][ERROR] Exception in generate_regional_prompt: {e}")
            return (f"Error: {e}", "", "", "", "", "", "")
    
    def split_regional_prompt(self, main_prompt, enable_second_subject=False, 
                            custom_quality_tags="", custom_background="", custom_supporting=""):
        """
        Legacy method for backward compatibility.
        Split the main prompt into regional components following the old structure.
        """
        try:
            # Use the new method but return in old format
            full, negative, region_1, region_2, region_3, quality, metadata = self.generate_regional_prompt(
                main_prompt=main_prompt,
                regional_mode=False,  # Use simple mode for legacy compatibility
                enable_second_subject=enable_second_subject,
                custom_quality_tags=custom_quality_tags,
                custom_background=custom_background,
                custom_supporting=custom_supporting
            )
            
            # Convert to old format: (quality_tags, subject_description, background_location, supporting_tags, second_subject)
            return (quality, region_1, region_2, "", region_3)
            
        except Exception as e:
            print(f"[Regional Synapse Node][ERROR] Exception in split_regional_prompt: {e}")
            return (f"Error: {e}", "", "", "", "")
    
    def _parse_prompt_components(self, main_prompt: str, enable_second_subject: bool, 
                               custom_quality_tags: str, custom_background: str, custom_supporting: str) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        """Parse the main prompt into organized components"""
        
        # Split by comma and clean
        parts = [part.strip() for part in main_prompt.split(',') if part.strip()]
        
        if not parts:
            return ([], [], [], [], [])
        
        # Initialize component lists
        quality_parts = []
        subject_parts = []
        background_parts = []
        supporting_parts = []
        second_subject_parts = []
        
        # Enhanced indicators for better categorization
        quality_indicators = [
            'masterpiece', 'best quality', 'high resolution', 'ultra detailed', 'amazing quality',
            'very aesthetic', 'exceptional', 'award winning', 'professional', '8k', '4k', 'hd'
        ]
        
        subject_indicators = [
            # Characters and beings
            'knight', 'warrior', 'mage', 'wizard', 'sorceress', 'battlemage', 'shadowblade',
            'elf', 'dwarf', 'human', 'orc', 'character', 'person', 'figure', 'barbarian',
            'rogue', 'paladin', 'archer', 'fighter', 'spellcaster', 'adventurer', 'hero',
            'dragon', 'beast', 'creature', 'demon', 'angel', 'spirit', 'ghost', 'elemental',
            'assassin', 'berserker', 'cleric', 'druid', 'monk', 'necromancer', 'psion',
            # Descriptive phrases
            'wielding', 'armed with', 'carrying', 'wearing', 'dressed in', 'adorned with',
            'holding', 'grasping', 'brandishing', 'equipped with'
        ]
        
        background_indicators = [
            # Locations and environments
            'forest', 'mountain', 'castle', 'temple', 'landscape', 'glade', 'chapel', 'tower',
            'cathedral', 'overpass', 'cityscape', 'environment', 'background', 'scene',
            'clearing', 'alleyway', 'dungeon', 'cavern', 'ruins', 'village', 'city', 'plains',
            'desert', 'ocean', 'river', 'lake', 'valley', 'cliff', 'bridge', 'palace',
            'interior', 'exterior', 'room', 'hall', 'chamber', 'courtyard', 'garden',
            'battlefield', 'arena', 'wasteland', 'sanctuary', 'library', 'laboratory',
            'throne room', 'great hall', 'underground', 'surface', 'sky', 'clouds',
            # Locational prepositions
            'in', 'at', 'within', 'inside', 'outside', 'beneath', 'above', 'beyond',
            'surrounded by', 'standing in', 'walking through', 'emerging from'
        ]
        
        supporting_indicators = [
            # Lighting and atmosphere
            'lighting', 'shadows', 'glow', 'illuminated', 'dramatic', 'soft', 'harsh',
            'ambient', 'rim light', 'backlighting', 'volumetric', 'god rays', 'sunbeams',
            'candlelight', 'firelight', 'moonlight', 'starlight', 'neon', 'magical glow',
            # Mood and atmosphere
            'moody', 'atmospheric', 'ethereal', 'mystical', 'dark', 'bright', 'vibrant',
            'muted', 'saturated', 'desaturated', 'warm', 'cool', 'ominous', 'peaceful',
            'intense', 'serene', 'chaotic', 'orderly', 'ancient', 'modern', 'timeless',
            # Weather and effects
            'fog', 'mist', 'rain', 'storm', 'snow', 'wind', 'dust', 'smoke', 'steam',
            'particles', 'sparks', 'embers', 'energy', 'magic', 'aura', 'ripples',
            # Style and technical
            'cinematic', 'photorealistic', 'stylized', 'detailed', 'intricate', 'ornate',
            'composition', 'perspective', 'depth', 'focus', 'blur', 'sharp', 'texture'
        ]
        
        # Track subject count for multiple subject detection
        subject_count = 0
        
        # Categorize each part with enhanced logic
        for part in parts:
            part_lower = part.lower()
            categorized = False
            
            # Check for quality tags first
            if any(indicator in part_lower for indicator in quality_indicators):
                quality_parts.append(part)
                categorized = True
            
            # Check for subjects with multi-subject detection
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
            
            # Enhanced fallback categorization
            if not categorized:
                # Complex multi-word subject descriptions
                if len(part.split()) > 2 and any(word in part_lower for word in ['with', 'wearing', 'holding', 'carrying', 'wielding', 'dressed', 'adorned']):
                    if enable_second_subject and subject_count > 0:
                        second_subject_parts.append(part)
                    else:
                        subject_parts.append(part)
                # Location descriptions with prepositions
                elif any(prep in part_lower for prep in ['in the', 'at the', 'near the', 'by the', 'on the', 'under the']):
                    background_parts.append(part)
                # Single descriptive words typically go to supporting
                elif len(part.split()) == 1:
                    supporting_parts.append(part)
                # Default to supporting for unmatched multi-word phrases
                else:
                    supporting_parts.append(part)
        
        # Apply custom overrides
        if custom_quality_tags.strip():
            quality_parts = [part.strip() for part in custom_quality_tags.split(',') if part.strip()]
        
        if custom_background.strip():
            background_parts = [part.strip() for part in custom_background.split(',') if part.strip()]
        
        if custom_supporting.strip():
            supporting_parts = [part.strip() for part in custom_supporting.split(',') if part.strip()]
        
        return (quality_parts, subject_parts, background_parts, supporting_parts, second_subject_parts)
    
    def _build_full_prompt(self, quality_parts: List[str], subject_parts: List[str], 
                         background_parts: List[str], supporting_parts: List[str], 
                         second_subject_parts: List[str]) -> str:
        """Build the complete non-regional prompt"""
        all_parts = []
        all_parts.extend(quality_parts)
        all_parts.extend(subject_parts)
        all_parts.extend(second_subject_parts)
        all_parts.extend(background_parts)
        all_parts.extend(supporting_parts)
        return ', '.join(all_parts)
    
    def _build_regional_prompts(self, quality_parts: List[str], subject_parts: List[str], 
                              background_parts: List[str], supporting_parts: List[str], 
                              second_subject_parts: List[str], enable_second_subject: bool,
                              enable_third_region: bool, subject_weight: float, background_weight: float,
                              region_separator: str) -> Tuple[str, str, str]:
        """Build the regional prompts with proper weighting and separation"""
        
        regions = []
        
        # Region 1: Primary subject with quality and relevant supporting elements
        region_1_parts = []
        region_1_parts.extend(quality_parts)
        
        if subject_parts:
            # Apply weighting to subjects if not default
            if subject_weight != 1.0:
                weighted_subjects = [f"({subject}:{subject_weight:.1f})" for subject in subject_parts]
                region_1_parts.extend(weighted_subjects)
            else:
                region_1_parts.extend(subject_parts)
        
        # Add relevant supporting elements to region 1
        subject_supporting = [part for part in supporting_parts if any(keyword in part.lower() 
                            for keyword in ['pose', 'expression', 'stance', 'action', 'movement'])]
        region_1_parts.extend(subject_supporting)
        
        regions.append(', '.join(region_1_parts) if region_1_parts else "")
        
        # Region 2: Background/environment with atmospheric elements
        region_2_parts = []
        
        if background_parts:
            # Apply weighting to background if not default
            if background_weight != 1.0:
                weighted_backgrounds = [f"({bg}:{background_weight:.1f})" for bg in background_parts]
                region_2_parts.extend(weighted_backgrounds)
            else:
                region_2_parts.extend(background_parts)
        
        # Add environmental supporting elements to region 2
        env_supporting = [part for part in supporting_parts if part not in subject_supporting]
        region_2_parts.extend(env_supporting[:3])  # Limit to avoid overcrowding
        
        regions.append(', '.join(region_2_parts) if region_2_parts else "")
        
        # Region 3: Second subject or additional elements  
        region_3_parts = []
        
        if enable_second_subject and second_subject_parts:
            # Second subject with same weight as primary
            if subject_weight != 1.0:
                weighted_second_subjects = [f"({subj}:{subject_weight:.1f})" for subj in second_subject_parts]
                region_3_parts.extend(weighted_second_subjects)
            else:
                region_3_parts.extend(second_subject_parts)
        elif enable_third_region:
            # Additional atmospheric or technical elements
            remaining_supporting = env_supporting[3:] if len(env_supporting) > 3 else []
            region_3_parts.extend(remaining_supporting)
        
        regions.append(', '.join(region_3_parts) if region_3_parts else "")
        
        return tuple(regions)
    
    def _generate_negative_prompt(self) -> str:
        """Generate comprehensive negative prompt for regional use"""
        negatives = [
            "worst quality", "low quality", "lowres", "blurry", "bad anatomy", 
            "bad hands", "malformed", "deformed", "extra limbs", "missing limbs",
            "bad proportions", "disfigured", "extra fingers", "missing fingers",
            "watermark", "text", "signature", "username", "error", "artifacts"
        ]
        return ', '.join(negatives)
    
    def _build_metadata(self, enable_second_subject: bool, enable_third_region: bool,
                       subject_weight: float, background_weight: float, region_separator: str) -> str:
        """Build metadata string describing the regional configuration"""
        return (f"Regional Mode: Enabled, "
                f"Second Subject: {'Yes' if enable_second_subject else 'No'}, "
                f"Third Region: {'Yes' if enable_third_region else 'No'}, "
                f"Subject Weight: {subject_weight:.1f}, "
                f"Background Weight: {background_weight:.1f}, "
                f"Separator: {region_separator}")


NODE_CLASS_MAPPINGS = {
    "RegionalSynapseNode": RegionalSynapseNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegionalSynapseNode": "Regional Synapse Node (Advanced)"
}