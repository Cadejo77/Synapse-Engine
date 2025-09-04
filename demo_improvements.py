#!/usr/bin/env python3
"""
Demonstrate model-specific prompt formatting and quality improvements
"""

from synapse_node import SynapsePromptGenerator

def demonstrate_model_differences():
    """Show how the same concept is formatted differently for each model"""
    
    print("🔬 MODEL-SPECIFIC FORMATTING COMPARISON")
    print("=" * 70)
    print("Generating the same concept for different AI models...")
    print()
    
    node = SynapsePromptGenerator()
    
    # Use same seed and concept for fair comparison
    base_concept = "mystical forest sorceress with glowing staff"
    seed = 12345
    
    models = [
        ("SDXL", "sdxl"),
        ("Flux.1", "flux"), 
        ("Illustrious XL", "illustrious_xl"),
        ("Pony Diffusion", "pony")
    ]
    
    for model_name, profile in models:
        print(f"🎯 {model_name}")
        print("-" * 40)
        
        positive, negative, metadata = node.generate_prompt(
            count=1,
            output_format="text",
            seed=seed,
            model_profile=profile,
            user_prompt=base_concept,
            negative_prompts=True
        )
        
        print(f"Positive: {positive}")
        if negative:
            print(f"Negative: {negative}")
        else:
            print("Negative: (None - model doesn't use negatives)")
        print(f"Details: {metadata}")
        print()

def demonstrate_variety_improvements():
    """Show the variety and richness of generated content"""
    
    print("🌟 CONTENT VARIETY & RICHNESS SHOWCASE")
    print("=" * 70)
    
    node = SynapsePromptGenerator()
    
    scenarios = [
        {
            "name": "Epic Landscape",
            "prompt": "dramatic mountain vista at sunset",
            "genre": "fantasy"
        },
        {
            "name": "Character Portrait", 
            "prompt": "battle-worn warrior with scars",
            "genre": "dark_fantasy"
        },
        {
            "name": "Architectural Scene",
            "prompt": "ancient temple with mystical lighting", 
            "genre": "fantasy"
        },
        {
            "name": "Urban Environment",
            "prompt": "neon-lit cyberpunk alleyway",
            "genre": "cyberpunk"
        },
        {
            "name": "Artistic Study",
            "prompt": "elegant figure in classical pose",
            "genre": "fantasy",
            "explicit": "artistic_only"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print("-" * 30)
        
        positive, negative, metadata = node.generate_prompt(
            count=1,
            output_format="text",
            seed=1000 + i,
            model_profile="sdxl",
            user_prompt=scenario['prompt'],
            genre_control=scenario['genre'],
            explicit_content=scenario.get('explicit', 'disabled')
        )
        
        print(f"Generated: {positive}")
        print(f"Metadata: {metadata}")
        print()

def demonstrate_regional_prompting():
    """Show regional prompting for complex scenes"""
    
    print("🏗️ REGIONAL PROMPTING FOR COMPLEX SCENES")
    print("=" * 70)
    
    node = SynapsePromptGenerator()
    
    complex_scenes = [
        "epic dragon battle over medieval castle",
        "futuristic cityscape with flying vehicles", 
        "enchanted forest clearing with fairy lights"
    ]
    
    for i, scene in enumerate(complex_scenes, 1):
        print(f"{i}. Regional Breakdown: {scene}")
        print("-" * 50)
        
        regional, negative, metadata = node.generate_prompt(
            count=1,
            output_format="regional",
            seed=2000 + i,
            model_profile="sdxl",
            user_prompt=scene
        )
        
        print(regional)
        print(f"Negative: {negative}")
        print()

if __name__ == "__main__":
    print("🎨 SYNAPSE ENGINE - MODEL OPTIMIZATION & QUALITY DEMO")
    print("=" * 80)
    print()
    
    try:
        demonstrate_model_differences()
        print("\n" + "=" * 80 + "\n")
        demonstrate_variety_improvements()
        print("\n" + "=" * 80 + "\n") 
        demonstrate_regional_prompting()
        
        print("=" * 80)
        print("✨ SUMMARY OF IMPROVEMENTS:")
        print("• Model-specific formatting ensures optimal prompt structure")
        print("• Rich compositional variety from portraits to landscapes") 
        print("• Advanced controls for content, genre, and style")
        print("• Professional output formats including regional prompting")
        print("• Automatic negative prompts for quality control")
        print("• Seamless user prompt integration")
        print("• Graduated explicit content controls with artistic options")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()