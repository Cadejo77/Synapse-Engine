#!/usr/bin/env python3
"""
Demonstration of the Universal Format and Regional Node workflow
Shows how to use both nodes together for advanced prompting
"""

from synapse_node import SynapsePromptGenerator
from regional_synapse_node import RegionalSynapseNode

def demonstration():
    print("🎨 SYNAPSE ENGINE - UNIVERSAL FORMAT + REGIONAL NODE DEMO")
    print("=" * 70)
    print("Demonstrating the new simplified workflow...")
    print()
    
    # Initialize nodes
    main_node = SynapsePromptGenerator()
    regional_node = RegionalSynapseNode()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Epic Fantasy Battle",
            "user_prompt": "dragon knight fighting ancient wyrm in mystical forest",
            "seed": 12345
        },
        {
            "name": "Cyberpunk Scene", 
            "user_prompt": "neon-lit hacker in futuristic city with flying cars",
            "seed": 54321
        },
        {
            "name": "Artistic Portrait",
            "user_prompt": "elegant Victorian lady in ornate ballroom",
            "seed": 99999
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎯 Scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        # Step 1: Generate universal format prompt
        positive, negative, metadata = main_node.generate_prompt(
            count=1,
            output_format="text",
            seed=scenario['seed'],
            user_prompt=scenario['user_prompt'],
            genre_control="random"
        )
        
        print(f"User Input: {scenario['user_prompt']}")
        print(f"Generated: {positive}")
        print(f"Negative: {negative}")
        print(f"Metadata: {metadata}")
        print()
        
        # Step 2: Parse with regional node
        print("📍 Regional Breakdown:")
        quality, subject, background, supporting, second_subject = regional_node.split_regional_prompt(
            main_prompt=positive,
            enable_second_subject=True
        )
        
        print(f"  🏷️  Quality Tags: {quality}")
        print(f"  👤 Subject: {subject}")
        print(f"  🏞️  Background: {background}")
        print(f"  ✨ Supporting: {supporting}")
        if second_subject:
            print(f"  👥 Second Subject: {second_subject}")
        print()
        
        # Step 3: Show structured format as well
        positive_struct, negative_struct, metadata_struct = main_node.generate_prompt(
            count=1,
            output_format="structured",
            seed=scenario['seed'],
            user_prompt=scenario['user_prompt']
        )
        
        print("📋 Structured Format:")
        print(positive_struct)
        print()
        print("=" * 70)
        print()

def workflow_example():
    print("🔄 TYPICAL WORKFLOW EXAMPLE")
    print("=" * 50)
    print("Here's how you would use both nodes in a ComfyUI workflow:")
    print()
    
    print("1️⃣ Main Synapse Node Configuration:")
    print("   - count: 1")
    print("   - output_format: text")
    print("   - seed: 42")
    print("   - user_prompt: 'epic space marine battle'")
    print("   - genre_control: sci_fi")
    print()
    
    print("2️⃣ Connect Main Node output to Regional Node input:")
    print("   - main_prompt: [Connected from Main Node]")
    print("   - enable_second_subject: True")
    print("   - custom_quality_tags: (optional override)")
    print()
    
    print("3️⃣ Use Regional Node outputs for different purposes:")
    print("   - quality_tags → Quality enhancement node")
    print("   - subject_description → Character/object conditioning")
    print("   - background_location → Environment conditioning")
    print("   - supporting_tags → Style/atmosphere conditioning") 
    print("   - second_subject → Secondary character conditioning")
    print()

if __name__ == "__main__":
    try:
        demonstration()
        workflow_example()
        
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print()
        print("📋 KEY BENEFITS:")
        print("• Single universal format works with all AI models")
        print("• No more model-specific complexity")
        print("• Regional node provides granular control")
        print("• Predictable, organized prompt structure")
        print("• Easy to integrate into existing workflows")
        print("• Maintains all original functionality")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()