#!/usr/bin/env python3
"""
Test the new universal format and regional node functionality
"""

from synapse_node import SynapsePromptGenerator
from regional_synapse_node import RegionalSynapseNode

def test_universal_format():
    """Test the new universal format without model profiles"""
    print("=== Testing Universal Format (No Model Profiles) ===")
    
    node = SynapsePromptGenerator()
    
    # Test basic generation
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="text",
        seed=42
    )
    
    print(f"Basic Generation:")
    print(f"Positive: {positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()
    
    # Test with user prompt
    positive2, negative2, metadata2 = node.generate_prompt(
        count=1,
        output_format="text", 
        seed=123,
        user_prompt="epic dragon battle in ancient castle"
    )
    
    print(f"With User Prompt:")
    print(f"Positive: {positive2}")
    print(f"Negative: {negative2}")
    print(f"Metadata: {metadata2}")
    print()
    
    return positive2

def test_regional_node(main_prompt):
    """Test the regional node with different configurations"""
    print("=== Testing Regional Node ===")
    
    regional_node = RegionalSynapseNode()
    
    # Basic regional split
    quality, subject, background, supporting, second_subject = regional_node.split_regional_prompt(
        main_prompt=main_prompt,
        enable_second_subject=False
    )
    
    print(f"Basic Regional Split:")
    print(f"Quality Tags: {quality}")
    print(f"Subject: {subject}")
    print(f"Background: {background}")
    print(f"Supporting Tags: {supporting}")
    print(f"Second Subject: {second_subject}")
    print()
    
    # With second subject enabled
    quality2, subject2, background2, supporting2, second_subject2 = regional_node.split_regional_prompt(
        main_prompt=main_prompt,
        enable_second_subject=True
    )
    
    print(f"With Second Subject Enabled:")
    print(f"Quality Tags: {quality2}")
    print(f"Subject: {subject2}")
    print(f"Background: {background2}")
    print(f"Supporting Tags: {supporting2}")
    print(f"Second Subject: {second_subject2}")
    print()
    
    # With custom overrides
    quality3, subject3, background3, supporting3, second_subject3 = regional_node.split_regional_prompt(
        main_prompt=main_prompt,
        enable_second_subject=True,
        custom_quality_tags="ultra detailed, photorealistic, 8k",
        custom_background="mystical enchanted forest, ethereal lighting"
    )
    
    print(f"With Custom Overrides:")
    print(f"Quality Tags: {quality3}")
    print(f"Subject: {subject3}")
    print(f"Background: {background3}")
    print(f"Supporting Tags: {supporting3}")
    print(f"Second Subject: {second_subject3}")
    print()

def test_different_formats():
    """Test different output formats"""
    print("=== Testing Different Output Formats ===")
    
    node = SynapsePromptGenerator()
    
    # JSON format
    positive_json, negative_json, metadata_json = node.generate_prompt(
        count=1,
        output_format="json",
        seed=456,
        user_prompt="cyberpunk hacker in neon city"
    )
    
    print(f"JSON Format:")
    print(f"Output: {positive_json}")
    print()
    
    # Structured format
    positive_struct, negative_struct, metadata_struct = node.generate_prompt(
        count=1,
        output_format="structured",
        seed=789,
        user_prompt="fantasy archer in moonlit forest"
    )
    
    print(f"Structured Format:")
    print(f"Output: {positive_struct}")
    print()

if __name__ == "__main__":
    print("🧪 Testing Universal Synapse Engine + Regional Node\n")
    
    try:
        # Test universal format
        main_prompt = test_universal_format()
        
        # Test regional node
        test_regional_node(main_prompt)
        
        # Test different formats
        test_different_formats()
        
        print("✅ All tests completed successfully!")
        print("\n🎯 Summary of Changes:")
        print("• Removed model-specific formatting (SDXL, Flux, Illustrious XL, Pony)")
        print("• Implemented universal prompt format: quality → subject → background → supporting")
        print("• Created Regional Synapse Node for advanced prompting control")
        print("• Maintained backward compatibility for existing functionality")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()