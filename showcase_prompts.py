#!/usr/bin/env python3
"""
Showcase the richness and variety of enhanced Synapse Engine prompts
"""

from synapse_node import SynapsePromptGenerator

def showcase_variety():
    """Show various types of prompts the system can generate"""
    
    print("🎨 SYNAPSE ENGINE - ENHANCED PROMPT VARIETY SHOWCASE")
    print("=" * 70)
    
    node = SynapsePromptGenerator()
    
    examples = [
        {
            "name": "SDXL Fantasy Portrait",
            "params": {
                "seed": 1001,
                "model_profile": "sdxl",
                "genre_control": "fantasy",
                "user_prompt": "elegant elven sorceress",
                "explicit_content": "artistic_only"
            }
        },
        {
            "name": "Flux Cyberpunk Scene", 
            "params": {
                "seed": 1002,
                "model_profile": "flux",
                "genre_control": "cyberpunk",
                "user_prompt": "rain-soaked neon cityscape at night"
            }
        },
        {
            "name": "Illustrious XL Dark Fantasy",
            "params": {
                "seed": 1003,
                "model_profile": "illustrious_xl",
                "genre_control": "dark_fantasy",
                "user_prompt": "ancient cathedral ruins"
            }
        },
        {
            "name": "Pony Steampunk Character",
            "params": {
                "seed": 1004,
                "model_profile": "pony", 
                "genre_control": "steampunk",
                "user_prompt": "clockwork engineer with goggles"
            }
        },
        {
            "name": "SDXL Landscape (Random Genre)",
            "params": {
                "seed": 1005,
                "model_profile": "sdxl",
                "user_prompt": "vast mountain landscape with dramatic lighting"
            }
        },
        {
            "name": "Regional Prompting Example",
            "params": {
                "seed": 1006,
                "model_profile": "sdxl",
                "output_format": "regional",
                "genre_control": "sci_fi",
                "user_prompt": "space marine in alien jungle"
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print("-" * 50)
        
        params = example["params"]
        output_fmt = params.pop("output_format", "text")
        positive, negative, metadata = node.generate_prompt(
            count=1,
            output_format=output_fmt,
            **params
        )
        
        if example['name'] == "Regional Prompting Example":
            print(f"Regional Format:\n{positive}")
        else:
            print(f"Positive: {positive}")
        
        if negative:
            print(f"Negative: {negative}")
        print(f"Details: {metadata}")
    
    print(f"\n{'='*70}")
    print("🌟 Key Features Demonstrated:")
    print("• Model-specific formatting (SDXL tags vs Flux prose)")
    print("• Genre control (fixed vs random)")
    print("• User prompt integration")
    print("• Automatic negative prompt generation")  
    print("• Regional prompting format")
    print("• R-rated artistic content options")
    print("• Rich compositional variety (portraits, landscapes, scenes)")
    print("• Quality tags and model-specific tokens")

if __name__ == "__main__":
    showcase_variety()