"""
Wild Divide Regional Node - Advanced regional prompting with wild divide functionality
Provides complex subject/background separation with multiple composition techniques
"""
from typing import List, Dict, Any, Tuple

class WildDivideRegionalNode:
    """
    Advanced regional prompting node with wild divide functionality for complex scene composition.
    Separates subjects from backgrounds using various composition techniques and weighting strategies.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "main_prompt": ("STRING", {"forceInput": True}),
                "divide_mode": (["wild_divide", "clean_divide", "weighted_blend", "layered_composition"], {"default": "wild_divide"}),
                "composition_style": (["standard", "cinematic", "portrait", "landscape", "action"], {"default": "standard"}),
            },
            "optional": {
                "subject_emphasis": ("FLOAT", {"default": 1.2, "min": 0.5, "max": 3.0, "step": 0.1}),
                "background_emphasis": ("FLOAT", {"default": 0.8, "min": 0.3, "max": 2.0, "step": 0.1}),
                "atmosphere_weight": ("FLOAT", {"default": 1.0, "min": 0.3, "max": 2.0, "step": 0.1}),
                "enable_attention_layers": ("BOOLEAN", {"default": True}),
                "use_break_syntax": ("BOOLEAN", {"default": True}),
                "custom_separator": ("STRING", {"default": "BREAK"}),
                "foreground_elements": ("STRING", {"default": "", "multiline": True}),
                "background_elements": ("STRING", {"default": "", "multiline": True}),
                "atmospheric_elements": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("composed_prompt", "foreground_region", "background_region", "atmosphere_region", "attention_map", "metadata")
    FUNCTION = "generate_wild_divide"
    CATEGORY = "text/synapse"
    
    def generate_wild_divide(self, main_prompt, divide_mode="wild_divide", composition_style="standard",
                           subject_emphasis=1.2, background_emphasis=0.8, atmosphere_weight=1.0,
                           enable_attention_layers=True, use_break_syntax=True, custom_separator="BREAK",
                           foreground_elements="", background_elements="", atmospheric_elements=""):
        """
        Generate advanced regional prompts using wild divide methodology for complex compositions.
        
        Args:
            main_prompt: Input prompt from main Synapse node
            divide_mode: Method of regional division (wild_divide, clean_divide, weighted_blend, layered_composition)
            composition_style: Overall composition approach (standard, cinematic, portrait, landscape, action)
            subject_emphasis: Weight for foreground subjects (0.5-3.0)
            background_emphasis: Weight for background elements (0.3-2.0)
            atmosphere_weight: Weight for atmospheric elements (0.3-2.0)
            enable_attention_layers: Use attention-based layering
            use_break_syntax: Use BREAK syntax for regional separation
            custom_separator: Custom separator for regions
            foreground_elements: Custom foreground override
            background_elements: Custom background override
            atmospheric_elements: Custom atmospheric override
            
        Returns:
            Tuple of (composed_prompt, foreground_region, background_region, atmosphere_region, attention_map, metadata)
        """
        try:
            if not main_prompt or not main_prompt.strip():
                return ("", "", "", "", "", "")
            
            # Parse the prompt into semantic components
            components = self._parse_semantic_components(main_prompt)
            
            # Apply custom overrides
            if foreground_elements.strip():
                components['subjects'] = [elem.strip() for elem in foreground_elements.split(',') if elem.strip()]
            if background_elements.strip():
                components['backgrounds'] = [elem.strip() for elem in background_elements.split(',') if elem.strip()]
            if atmospheric_elements.strip():
                components['atmosphere'] = [elem.strip() for elem in atmospheric_elements.split(',') if elem.strip()]
            
            # Generate regions based on divide mode
            if divide_mode == "wild_divide":
                regions = self._generate_wild_divide_regions(components, composition_style, 
                                                          subject_emphasis, background_emphasis, atmosphere_weight)
            elif divide_mode == "clean_divide":
                regions = self._generate_clean_divide_regions(components, subject_emphasis, background_emphasis)
            elif divide_mode == "weighted_blend":
                regions = self._generate_weighted_blend_regions(components, subject_emphasis, background_emphasis, atmosphere_weight)
            else:  # layered_composition
                regions = self._generate_layered_composition_regions(components, composition_style, 
                                                                   subject_emphasis, background_emphasis, atmosphere_weight)
            
            # Build attention map if enabled
            attention_map = ""
            if enable_attention_layers:
                attention_map = self._generate_attention_map(components, composition_style, divide_mode)
            
            # Compose final prompt with appropriate syntax
            composed_prompt = self._compose_final_prompt(regions, use_break_syntax, custom_separator)
            
            # Generate metadata
            metadata = self._generate_metadata(divide_mode, composition_style, subject_emphasis, 
                                             background_emphasis, atmosphere_weight, len(components['subjects']), 
                                             len(components['backgrounds']))
            
            return (
                composed_prompt,
                regions.get('foreground', ''),
                regions.get('background', ''),
                regions.get('atmosphere', ''),
                attention_map,
                metadata
            )
            
        except Exception as e:
            print(f"[Wild Divide Regional Node][ERROR] Exception: {e}")
            return (f"Error: {e}", "", "", "", "", "")
    
    def _parse_semantic_components(self, prompt: str) -> Dict[str, List[str]]:
        """Parse prompt into semantic components with enhanced categorization"""
        
        parts = [part.strip() for part in prompt.split(',') if part.strip()]
        
        components = {
            'quality': [],
            'subjects': [],
            'backgrounds': [],
            'atmosphere': [],
            'technical': [],
            'composition': []
        }
        
        # Enhanced semantic indicators
        quality_indicators = [
            'masterpiece', 'best quality', 'high resolution', 'ultra detailed', 'award winning',
            'professional', '8k', '4k', 'photorealistic', 'highly detailed', 'exceptional'
        ]
        
        subject_indicators = [
            'knight', 'warrior', 'mage', 'wizard', 'character', 'person', 'figure', 'hero',
            'dragon', 'creature', 'beast', 'demon', 'angel', 'elemental', 'spirit',
            'wielding', 'holding', 'carrying', 'wearing', 'armed with', 'dressed in'
        ]
        
        background_indicators = [
            'forest', 'castle', 'temple', 'landscape', 'environment', 'scene', 'setting',
            'dungeon', 'cavern', 'ruins', 'city', 'village', 'palace', 'tower', 'mountain',
            'in', 'at', 'within', 'inside', 'outside', 'near', 'by', 'surrounded by'
        ]
        
        atmosphere_indicators = [
            'lighting', 'shadows', 'glow', 'dramatic', 'ethereal', 'mystical', 'dark', 'bright',
            'fog', 'mist', 'rain', 'storm', 'particles', 'effects', 'aura', 'energy',
            'moody', 'atmospheric', 'cinematic', 'epic', 'serene', 'intense'
        ]
        
        composition_indicators = [
            'shot', 'angle', 'view', 'perspective', 'composition', 'framing', 'focus',
            'close-up', 'wide shot', 'portrait', 'full body', 'centered', 'diagonal'
        ]
        
        technical_indicators = [
            'style', 'art', 'painting', 'digital', 'rendering', 'texture', 'detailed'
        ]
        
        # Categorize parts
        for part in parts:
            part_lower = part.lower()
            categorized = False
            
            # Check each category
            for category, indicators in [
                ('quality', quality_indicators),
                ('subjects', subject_indicators), 
                ('backgrounds', background_indicators),
                ('atmosphere', atmosphere_indicators),
                ('composition', composition_indicators),
                ('technical', technical_indicators)
            ]:
                if any(indicator in part_lower for indicator in indicators):
                    components[category].append(part)
                    categorized = True
                    break
            
            # Default categorization for uncategorized parts
            if not categorized:
                if len(part.split()) == 1:
                    components['atmosphere'].append(part)  # Single words usually atmospheric
                else:
                    components['subjects'].append(part)  # Multi-word phrases usually subjects
        
        return components
    
    def _generate_wild_divide_regions(self, components: Dict[str, List[str]], composition_style: str,
                                    subject_emphasis: float, background_emphasis: float, 
                                    atmosphere_weight: float) -> Dict[str, str]:
        """Generate wild divide style regions with complex layering"""
        
        regions = {}
        
        # Foreground: Quality + Subjects with emphasis
        foreground_parts = []
        foreground_parts.extend(components['quality'])
        
        # Apply wild divide weighting to subjects
        if components['subjects']:
            emphasized_subjects = []
            for subject in components['subjects'][:3]:  # Limit to 3 main subjects
                if subject_emphasis != 1.0:
                    emphasized_subjects.append(f"({subject}:{subject_emphasis:.1f})")
                else:
                    emphasized_subjects.append(subject)
            foreground_parts.extend(emphasized_subjects)
        
        # Add composition elements for foreground
        if composition_style == "cinematic":
            foreground_parts.extend(["cinematic composition", "dramatic framing"])
        elif composition_style == "portrait":
            foreground_parts.extend(["portrait composition", "focused framing"])
        elif composition_style == "action":
            foreground_parts.extend(["dynamic composition", "action pose"])
        
        regions['foreground'] = ', '.join(foreground_parts)
        
        # Background: Environment + some atmosphere with emphasis
        background_parts = []
        
        if components['backgrounds']:
            emphasized_backgrounds = []
            for bg in components['backgrounds'][:2]:  # Limit backgrounds
                if background_emphasis != 1.0:
                    emphasized_backgrounds.append(f"({bg}:{background_emphasis:.1f})")
                else:
                    emphasized_backgrounds.append(bg)
            background_parts.extend(emphasized_backgrounds)
        
        # Add some atmospheric elements to background
        bg_atmosphere = components['atmosphere'][:2]  # Take first 2 atmospheric elements
        background_parts.extend(bg_atmosphere)
        
        regions['background'] = ', '.join(background_parts)
        
        # Atmosphere: Remaining atmosphere + technical + composition
        atmosphere_parts = []
        
        # Remaining atmospheric elements with weighting
        remaining_atmosphere = components['atmosphere'][2:]  # Skip those used in background
        if remaining_atmosphere and atmosphere_weight != 1.0:
            weighted_atmosphere = [f"({atm}:{atmosphere_weight:.1f})" for atm in remaining_atmosphere]
            atmosphere_parts.extend(weighted_atmosphere)
        else:
            atmosphere_parts.extend(remaining_atmosphere)
        
        atmosphere_parts.extend(components['technical'])
        atmosphere_parts.extend(components['composition'])
        
        regions['atmosphere'] = ', '.join(atmosphere_parts)
        
        return regions
    
    def _generate_clean_divide_regions(self, components: Dict[str, List[str]], 
                                     subject_emphasis: float, background_emphasis: float) -> Dict[str, str]:
        """Generate clean divide style regions with simple separation"""
        
        regions = {}
        
        # Clean foreground: Quality + Subjects only
        foreground_parts = []
        foreground_parts.extend(components['quality'])
        
        if components['subjects'] and subject_emphasis != 1.0:
            emphasized_subjects = [f"({subj}:{subject_emphasis:.1f})" for subj in components['subjects']]
            foreground_parts.extend(emphasized_subjects)
        else:
            foreground_parts.extend(components['subjects'])
        
        regions['foreground'] = ', '.join(foreground_parts)
        
        # Clean background: Backgrounds only
        background_parts = []
        
        if components['backgrounds'] and background_emphasis != 1.0:
            emphasized_backgrounds = [f"({bg}:{background_emphasis:.1f})" for bg in components['backgrounds']]
            background_parts.extend(emphasized_backgrounds)
        else:
            background_parts.extend(components['backgrounds'])
        
        regions['background'] = ', '.join(background_parts)
        
        # Clean atmosphere: Everything else
        atmosphere_parts = []
        atmosphere_parts.extend(components['atmosphere'])
        atmosphere_parts.extend(components['technical'])
        atmosphere_parts.extend(components['composition'])
        
        regions['atmosphere'] = ', '.join(atmosphere_parts)
        
        return regions
    
    def _generate_weighted_blend_regions(self, components: Dict[str, List[str]], 
                                       subject_emphasis: float, background_emphasis: float,
                                       atmosphere_weight: float) -> Dict[str, str]:
        """Generate weighted blend regions with gradual transitions"""
        
        regions = {}
        
        # Blended approach with overlapping elements
        all_elements = []
        all_elements.extend(components['quality'])
        all_elements.extend(components['subjects'])
        all_elements.extend(components['backgrounds'])
        all_elements.extend(components['atmosphere'])
        all_elements.extend(components['technical'])
        all_elements.extend(components['composition'])
        
        # Split into thirds with weighted overlaps
        third = len(all_elements) // 3
        
        # Foreground: First third + some from second third
        foreground_elements = all_elements[:third + 1]
        if subject_emphasis != 1.0:
            foreground_elements = [f"({elem}:{subject_emphasis:.1f})" for elem in foreground_elements[:3]] + foreground_elements[3:]
        regions['foreground'] = ', '.join(foreground_elements)
        
        # Background: Second third + some overlap
        background_elements = all_elements[third-1:2*third+1] 
        if background_emphasis != 1.0:
            background_elements = [f"({elem}:{background_emphasis:.1f})" for elem in background_elements[:2]] + background_elements[2:]
        regions['background'] = ', '.join(background_elements)
        
        # Atmosphere: Final third + some overlap  
        atmosphere_elements = all_elements[2*third-1:]
        if atmosphere_weight != 1.0:
            atmosphere_elements = [f"({elem}:{atmosphere_weight:.1f})" for elem in atmosphere_elements[:2]] + atmosphere_elements[2:]
        regions['atmosphere'] = ', '.join(atmosphere_elements)
        
        return regions
    
    def _generate_layered_composition_regions(self, components: Dict[str, List[str]], composition_style: str,
                                            subject_emphasis: float, background_emphasis: float,
                                            atmosphere_weight: float) -> Dict[str, str]:
        """Generate layered composition with style-specific arrangements"""
        
        regions = {}
        
        # Layer-based composition
        if composition_style == "cinematic":
            # Cinematic: Strong foreground, detailed background, atmospheric mood
            regions['foreground'] = ', '.join(components['quality'] + 
                                            [f"({s}:{subject_emphasis:.1f})" for s in components['subjects'][:2]] +
                                            ["cinematic lighting", "dramatic composition"])
            
            regions['background'] = ', '.join([f"({bg}:{background_emphasis:.1f})" for bg in components['backgrounds']] +
                                            components['atmosphere'][:2] +
                                            ["cinematic depth"])
            
            regions['atmosphere'] = ', '.join([f"({atm}:{atmosphere_weight:.1f})" for atm in components['atmosphere'][2:]] +
                                            components['technical'] +
                                            ["film grain", "anamorphic"])
            
        elif composition_style == "portrait":
            # Portrait: Focus on subject details, minimal background
            regions['foreground'] = ', '.join(components['quality'] +
                                            [f"({s}:{subject_emphasis:.1f})" for s in components['subjects']] +
                                            ["portrait lighting", "shallow depth of field"])
            
            regions['background'] = ', '.join([f"({bg}:{background_emphasis * 0.7:.1f})" for bg in components['backgrounds'][:1]] +
                                            ["blurred background", "bokeh"])
            
            regions['atmosphere'] = ', '.join([f"({atm}:{atmosphere_weight:.1f})" for atm in components['atmosphere']] +
                                            components['technical'])
            
        else:  # Standard layered
            regions['foreground'] = ', '.join(components['quality'] + 
                                            [f"({s}:{subject_emphasis:.1f})" for s in components['subjects']])
            regions['background'] = ', '.join([f"({bg}:{background_emphasis:.1f})" for bg in components['backgrounds']])
            regions['atmosphere'] = ', '.join([f"({atm}:{atmosphere_weight:.1f})" for atm in components['atmosphere']] +
                                            components['technical'] + components['composition'])
        
        return regions
    
    def _generate_attention_map(self, components: Dict[str, List[str]], composition_style: str, 
                              divide_mode: str) -> str:
        """Generate attention-based weighting map for complex compositions"""
        
        attention_elements = []
        
        # Primary attention (highest weight)
        if components['subjects']:
            primary_subject = components['subjects'][0] if components['subjects'] else ""
            attention_elements.append(f"PRIMARY: ({primary_subject}:1.3)")
        
        # Secondary attention (medium weight)
        if len(components['subjects']) > 1:
            secondary_subjects = components['subjects'][1:3]
            for subj in secondary_subjects:
                attention_elements.append(f"SECONDARY: ({subj}:1.1)")
        
        # Background attention (lower weight)
        if components['backgrounds']:
            main_bg = components['backgrounds'][0] if components['backgrounds'] else ""
            attention_elements.append(f"BACKGROUND: ({main_bg}:0.9)")
        
        # Atmospheric attention (subtle weight)
        if components['atmosphere']:
            main_atmosphere = components['atmosphere'][0] if components['atmosphere'] else ""
            attention_elements.append(f"ATMOSPHERE: ({main_atmosphere}:0.8)")
        
        return ' | '.join(attention_elements)
    
    def _compose_final_prompt(self, regions: Dict[str, str], use_break_syntax: bool, 
                            custom_separator: str) -> str:
        """Compose the final prompt with appropriate syntax"""
        
        prompt_parts = []
        
        separator = f" {custom_separator} " if use_break_syntax else " | "
        
        # Add non-empty regions
        for region_name in ['foreground', 'background', 'atmosphere']:
            region_content = regions.get(region_name, '')
            if region_content.strip():
                prompt_parts.append(region_content)
        
        return separator.join(prompt_parts)
    
    def _generate_metadata(self, divide_mode: str, composition_style: str, subject_emphasis: float,
                         background_emphasis: float, atmosphere_weight: float, subject_count: int,
                         background_count: int) -> str:
        """Generate metadata about the regional configuration"""
        
        return (f"Mode: {divide_mode}, Style: {composition_style}, "
                f"Subjects: {subject_count} (weight: {subject_emphasis:.1f}), "
                f"Backgrounds: {background_count} (weight: {background_emphasis:.1f}), "
                f"Atmosphere Weight: {atmosphere_weight:.1f}")


NODE_CLASS_MAPPINGS = {
    "WildDivideRegionalNode": WildDivideRegionalNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildDivideRegionalNode": "Wild Divide Regional Node"
}