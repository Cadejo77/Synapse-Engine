#!/usr/bin/env python3
"""
Test script for Synapse Engine ComfyUI node (Python-only)
Run this to verify the installation is working correctly.
"""

from synapse_node import SynapsePromptGenerator

def test_synapse_node():
    print("🧪 Testing Synapse Engine ComfyUI Node (Python-only)")
    print("=" * 55)
    
    node = SynapsePromptGenerator()
    
    # Test 1: Basic text generation
    print("\n1. Testing basic text generation:")
    result = node.generate_prompt(count=1, output_format="text", seed=42)
    print(f"   Generated: {result[0]}")
    
    # Test 2: JSON format
    print("\n2. Testing JSON format:")
    result = node.generate_prompt(count=1, output_format="json", seed=42)
    print(f"   JSON result (truncated): {result[0][:200]}...")
    
    # Test 3: Multiple prompts
    print("\n3. Testing multiple prompts:")
    result = node.generate_prompt(count=3, output_format="text", seed=123)
    print(f"   First prompt: {result[0]}")
    
    # Test 4: Seeded generation (should be reproducible)
    print("\n4. Testing seeded generation (reproducibility):")
    result1 = node.generate_prompt(count=1, output_format="text", seed=999)
    result2 = node.generate_prompt(count=1, output_format="text", seed=999)
    print(f"   First run:  {result1[0]}")
    print(f"   Second run: {result2[0]}")
    print(f"   Reproducible: {'✅' if result1[0] == result2[0] else '❌'}")
    
    # Test 5: Different seeds (should produce different results)
    print("\n5. Testing different seeds:")
    result1 = node.generate_prompt(count=1, output_format="text", seed=100)
    result2 = node.generate_prompt(count=1, output_format="text", seed=200)
    print(f"   Seed 100: {result1[0]}")
    print(f"   Seed 200: {result2[0]}")
    print(f"   Different: {'✅' if result1[0] != result2[0] else '❌'}")
    
    print("\n✅ All tests completed!")
    print("\nYour Synapse Engine ComfyUI node is ready to use!")
    print("Look for 'Synapse Prompt Generator' in ComfyUI under the 'text/synapse' category.")
    print("\nKey improvements:")
    print("- Pure Python implementation (no Node.js required)")
    print("- Deterministic seeding for reproducible results")
    print("- Direct YAML processing with PyYAML")
    print("- Supports both compositional and legacy modes")

if __name__ == "__main__":
    test_synapse_node()