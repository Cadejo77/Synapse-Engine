#!/usr/bin/env python3
"""
Enhanced test script for Synapse Engine with new functionality
"""

from synapse_node import SynapsePromptGenerator
import json

def test_enhanced_synapse_node():
    print("🎨 Testing Enhanced Synapse Engine Node")
    print("=" * 60)
    
    node = SynapsePromptGenerator()
    
    # Test 1: Model-specific formatting
    print("\n1. Testing Model-Specific Formatting:")
    print("-" * 40)
    
    models = ["sdxl", "flux", "illustrious_xl", "pony"]
    for model in models:
        result = node.generate_prompt(1, "full_prompt", 200, model, "random", "safe", "beautiful portrait")
        print(f"{model.upper():12}: {result[0][:80]}...")
        print(f"{'NEGATIVE':12}: {result[1]}")
        print()
    
    # Test 2: Content Rating System
    print("2. Testing Content Rating System:")
    print("-" * 40)
    
    ratings = ["safe", "mature", "artistic_r"]
    for rating in ratings:
        result = node.generate_prompt(1, "full_prompt", 300, "auto", "random", rating)
        print(f"{rating.upper():12}: {result[0][:80]}...")
        print()
    
    # Test 3: Regional Prompting
    print("3. Testing Regional Prompting:")
    print("-" * 40)
    
    result = node.generate_prompt(1, "regional_components", 200, "sdxl", "random", "safe", "epic fantasy scene")
    print(result[0])
    print()
    
    # Test 4: Genre Control
    print("4. Testing Genre Control:")
    print("-" * 40)
    
    genres = ["fantasy", "cyberpunk", "dark_fantasy"]
    for genre in genres:
        result = node.generate_prompt(1, "full_prompt", 400, "auto", "fixed", "safe", "", "", genre)
        print(f"{genre.upper():12}: {result[0][:80]}...")
        print()
    
    # Test 5: Rich Variety Showcase
    print("5. Rich Variety Showcase (10 different prompts):")
    print("-" * 40)
    
    for i, seed in enumerate(range(500, 510), 1):
        result = node.generate_prompt(1, "full_prompt", seed, "auto", "random", "safe")
        print(f"#{i:2}: {result[0][:90]}...")
    
    print("\n✅ Enhanced Synapse Engine tests completed!")
    print("\nKey New Features:")
    print("- Model-specific formatting (SDXL, Flux, Illustrious XL, Pony)")
    print("- Content rating system with artistic R support")
    print("- Regional prompting for advanced workflows")
    print("- Genre control (fixed/random)")
    print("- User prompt integration")
    print("- Enhanced variety and richness")
    print("- Dual positive/negative prompt outputs")

if __name__ == "__main__":
    test_enhanced_synapse_node()