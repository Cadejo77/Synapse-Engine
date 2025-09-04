#!/usr/bin/env python3
"""
Test the enhanced Synapse Engine functionality
"""

from synapse_node import SynapsePromptGenerator

def test_basic_generation():
    """Test basic prompt generation"""
    print("=== Testing Basic Generation ===")
    
    node = SynapsePromptGenerator()
    
    # Test with new parameters
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="text", 
        seed=42,
        model_profile="sdxl"
    )
    
    print(f"Positive: {positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_user_prompt():
    """Test with user prompt input"""
    print("=== Testing User Prompt Input ===")
    
    node = SynapsePromptGenerator()
    
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="text",
        seed=123,
        model_profile="flux",
        user_prompt="a mystical forest wizard"
    )
    
    print(f"Positive: {positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_genre_control():
    """Test fixed genre control"""
    print("=== Testing Genre Control ===")
    
    node = SynapsePromptGenerator()
    
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="text",
        seed=456,
        model_profile="illustrious_xl",
        genre_control="cyberpunk"
    )
    
    print(f"Positive: {positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_explicit_content():
    """Test explicit content generation"""
    print("=== Testing Explicit Content ===")
    
    node = SynapsePromptGenerator()
    
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="text",
        seed=789,
        model_profile="sdxl",
        explicit_content="artistic_only",
        genre_control="fantasy"
    )
    
    print(f"Positive: {positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_regional_format():
    """Test regional prompting format"""
    print("=== Testing Regional Format ===")
    
    node = SynapsePromptGenerator()
    
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="regional",
        seed=101112,
        model_profile="sdxl",
        user_prompt="epic battle scene"
    )
    
    print(f"Regional Output:\n{positive}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_structured_output():
    """Test structured output format"""
    print("=== Testing Structured Output ===")
    
    node = SynapsePromptGenerator()
    
    positive, negative, metadata = node.generate_prompt(
        count=1,
        output_format="structured",
        seed=131415,
        model_profile="pony",
        user_prompt="anime character portrait",
        custom_negative="bad anatomy, deformed"
    )
    
    print(f"Structured Output:\n{positive}")
    print()

if __name__ == "__main__":
    print("🧪 Testing Enhanced Synapse Engine Features\n")
    
    try:
        test_basic_generation()
        test_user_prompt()
        test_genre_control()
        test_explicit_content()
        test_regional_format()
        test_structured_output()
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()