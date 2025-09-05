#!/usr/bin/env python3
"""
Comprehensive test for the complete enhanced regional prompting system
Tests main node, regional node, and wild divide node integration
"""

from synapse_node import SynapsePromptGenerator
from regional_synapse_node import RegionalSynapseNode
from wild_divide_regional_node import WildDivideRegionalNode

def test_complete_workflow():
    """Test the complete enhanced workflow from main node through regional processing"""
    print("🔥 COMPLETE ENHANCED WORKFLOW TEST")
    print("=" * 70)
    
    # Initialize all nodes
    main_node = SynapsePromptGenerator()
    regional_node = RegionalSynapseNode()
    wild_divide_node = WildDivideRegionalNode()
    
    # Test scenario: Complex battle scene
    user_prompt = "epic armored dragon knight wielding flaming sword battling shadow demon lord in crumbling ancient cathedral with stained glass windows"
    
    print(f"📝 Input Scenario: {user_prompt}")
    print("-" * 70)
    
    # Step 1: Generate rich prompt with main node
    print("🎨 STEP 1: Main Synapse Node (Rich Descriptions)")
    main_prompt, main_negative, main_metadata = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=777777,
        user_prompt=user_prompt,
        genre_control="dark_fantasy",
        enable_rich_descriptions=True
    )
    
    print(f"Main Output: {main_prompt}")
    print(f"Main Negative: {main_negative}")
    print(f"Main Metadata: {main_metadata}")
    print()
    
    # Step 2: Process with Regional Node
    print("🏗️ STEP 2: Regional Synapse Node (Advanced Regional)")
    full, negative, region_1, region_2, region_3, quality, metadata = regional_node.generate_regional_prompt(
        main_prompt=main_prompt,
        regional_mode=True,
        enable_second_subject=True,
        enable_third_region=True,
        subject_weight=1.2,
        background_weight=0.9,
        region_separator="BREAK"
    )
    
    print(f"Regional Full: {full}")
    print(f"Regional Negative: {negative}")
    print(f"Region 1 (Primary Subject): {region_1}")
    print(f"Region 2 (Background): {region_2}")
    print(f"Region 3 (Second Subject): {region_3}")
    print(f"Quality Tags: {quality}")
    print(f"Regional Metadata: {metadata}")
    print()
    
    # Step 3: Process with Wild Divide Node
    print("⚡ STEP 3: Wild Divide Regional Node (Advanced Composition)")
    composed, foreground, background, atmosphere, attention, wild_metadata = wild_divide_node.generate_wild_divide(
        main_prompt=main_prompt,
        divide_mode="wild_divide",
        composition_style="cinematic",
        subject_emphasis=1.3,
        background_emphasis=0.8,
        atmosphere_weight=1.1,
        enable_attention_layers=True,
        use_break_syntax=True
    )
    
    print(f"Wild Divide Composed: {composed}")
    print(f"Foreground Region: {foreground}")
    print(f"Background Region: {background}")
    print(f"Atmosphere Region: {atmosphere}")
    print(f"Attention Map: {attention}")
    print(f"Wild Divide Metadata: {wild_metadata}")
    print()

def test_different_divide_modes():
    """Test different divide modes in the wild divide node"""
    print("🎭 WILD DIVIDE MODES COMPARISON")
    print("=" * 70)
    
    wild_divide_node = WildDivideRegionalNode()
    main_node = SynapsePromptGenerator()
    
    # Generate a test prompt
    test_prompt, _, _ = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=123456,
        user_prompt="cyberpunk street samurai with neon katana fighting corporate drones in rain-soaked alley",
        genre_control="cyberpunk",
        enable_rich_descriptions=True
    )
    
    print(f"Test Prompt: {test_prompt}")
    print("-" * 70)
    
    divide_modes = [
        ("wild_divide", "Complex layering with wild weighting"),
        ("clean_divide", "Simple clean separation"),
        ("weighted_blend", "Gradual transitions with overlaps"),
        ("layered_composition", "Style-specific layered approach")
    ]
    
    for mode, description in divide_modes:
        print(f"🎨 {mode.upper()} - {description}")
        print("-" * 50)
        
        composed, foreground, background, atmosphere, attention, metadata = wild_divide_node.generate_wild_divide(
            main_prompt=test_prompt,
            divide_mode=mode,
            composition_style="cinematic",
            subject_emphasis=1.2,
            background_emphasis=0.8,
            atmosphere_weight=1.0
        )
        
        print(f"Composed: {composed}")
        print(f"Foreground: {foreground}")
        print(f"Background: {background}")
        print(f"Atmosphere: {atmosphere}")
        print(f"Metadata: {metadata}")
        print()

def test_composition_styles():
    """Test different composition styles"""
    print("🎬 COMPOSITION STYLES TEST")
    print("=" * 70)
    
    wild_divide_node = WildDivideRegionalNode()
    main_node = SynapsePromptGenerator()
    
    # Generate a versatile test prompt
    test_prompt, _, _ = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=654321,
        user_prompt="mysterious elven archer with enchanted bow in moonlit forest clearing with ancient ruins",
        genre_control="fantasy",
        enable_rich_descriptions=True
    )
    
    print(f"Test Prompt: {test_prompt}")
    print("-" * 70)
    
    composition_styles = [
        ("standard", "Standard balanced composition"),
        ("cinematic", "Film-like dramatic composition"),
        ("portrait", "Portrait-focused composition"),
        ("landscape", "Landscape-oriented composition"),
        ("action", "Action-oriented dynamic composition")
    ]
    
    for style, description in composition_styles:
        print(f"📸 {style.upper()} - {description}")
        print("-" * 50)
        
        composed, foreground, background, atmosphere, attention, metadata = wild_divide_node.generate_wild_divide(
            main_prompt=test_prompt,
            divide_mode="layered_composition",
            composition_style=style,
            subject_emphasis=1.2,
            background_emphasis=0.8,
            atmosphere_weight=1.0,
            enable_attention_layers=True
        )
        
        print(f"Composed: {composed}")
        print(f"Attention Map: {attention}")
        print(f"Metadata: {metadata}")
        print()

def test_regional_vs_non_regional():
    """Test the regional vs non-regional toggle functionality"""
    print("🔄 REGIONAL VS NON-REGIONAL COMPARISON")
    print("=" * 70)
    
    main_node = SynapsePromptGenerator()
    regional_node = RegionalSynapseNode()
    
    # Test prompt
    test_prompt = "steampunk inventor with brass goggles piloting mechanical airship above Victorian city"
    
    # Generate base prompt
    base_prompt, base_negative, base_metadata = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=999999,
        user_prompt=test_prompt,
        genre_control="steampunk",
        enable_rich_descriptions=True
    )
    
    print(f"Base Prompt: {base_prompt}")
    print("-" * 70)
    
    # Test with regional mode ON
    print("🟢 REGIONAL MODE: ENABLED")
    print("-" * 30)
    full_on, neg_on, r1_on, r2_on, r3_on, q_on, meta_on = regional_node.generate_regional_prompt(
        main_prompt=base_prompt,
        regional_mode=True,
        enable_second_subject=False,
        enable_third_region=False
    )
    
    print(f"Full: {full_on}")
    print(f"Region 1: {r1_on}")
    print(f"Region 2: {r2_on}")
    print(f"Metadata: {meta_on}")
    print()
    
    # Test with regional mode OFF  
    print("🔴 REGIONAL MODE: DISABLED")
    print("-" * 30)
    full_off, neg_off, r1_off, r2_off, r3_off, q_off, meta_off = regional_node.generate_regional_prompt(
        main_prompt=base_prompt,
        regional_mode=False
    )
    
    print(f"Full: {full_off}")
    print(f"Region 1: {r1_off}")
    print(f"Region 2: {r2_off}")
    print(f"Metadata: {meta_off}")
    print()

def test_weighting_system():
    """Test the weighting system across different emphasis values"""
    print("⚖️ WEIGHTING SYSTEM TEST")
    print("=" * 70)
    
    wild_divide_node = WildDivideRegionalNode()
    main_node = SynapsePromptGenerator()
    
    # Generate test prompt
    test_prompt, _, _ = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=111222,
        user_prompt="battle-scarred orc warrior with massive war axe charging through burning village",
        genre_control="fantasy",
        enable_rich_descriptions=True
    )
    
    print(f"Test Prompt: {test_prompt}")
    print("-" * 70)
    
    weight_tests = [
        (0.8, 0.6, 0.8, "Subtle weighting"),
        (1.0, 1.0, 1.0, "Balanced weighting"),
        (1.5, 0.7, 1.2, "Strong subject emphasis"),
        (1.2, 1.3, 0.9, "Strong background emphasis"),
        (2.0, 0.5, 1.5, "Extreme subject focus")
    ]
    
    for subj_weight, bg_weight, atm_weight, description in weight_tests:
        print(f"🎚️ {description}: Subject({subj_weight}) | Background({bg_weight}) | Atmosphere({atm_weight})")
        print("-" * 60)
        
        composed, foreground, background, atmosphere, attention, metadata = wild_divide_node.generate_wild_divide(
            main_prompt=test_prompt,
            divide_mode="wild_divide",
            composition_style="action",
            subject_emphasis=subj_weight,
            background_emphasis=bg_weight,
            atmosphere_weight=atm_weight,
            enable_attention_layers=True
        )
        
        print(f"Foreground: {foreground}")
        print(f"Background: {background}")
        print(f"Atmosphere: {atmosphere}")
        print(f"Attention: {attention}")
        print()

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE ENHANCED REGIONAL PROMPTING SYSTEM TEST")
    print("=" * 80)
    print()
    
    try:
        # Run all comprehensive tests
        test_complete_workflow()
        print("\n" + "=" * 80 + "\n")
        
        test_different_divide_modes()
        print("\n" + "=" * 80 + "\n")
        
        test_composition_styles()
        print("\n" + "=" * 80 + "\n")
        
        test_regional_vs_non_regional()
        print("\n" + "=" * 80 + "\n")
        
        test_weighting_system()
        
        print("=" * 80)
        print("✅ ALL COMPREHENSIVE TESTS COMPLETED SUCCESSFULLY!")
        print("\n🎯 COMPLETE SYSTEM SUMMARY:")
        print("• Main Synapse Node: Rich, detailed prompt generation")
        print("• Regional Synapse Node: Advanced regional prompting with 3 regions")
        print("• Wild Divide Regional Node: Complex composition with attention mapping")
        print("• Multiple divide modes: wild_divide, clean_divide, weighted_blend, layered_composition")
        print("• Multiple composition styles: standard, cinematic, portrait, landscape, action")
        print("• Advanced weighting system for subjects, backgrounds, and atmosphere")
        print("• Regional vs non-regional toggle functionality")
        print("• Full integration between all nodes for complex workflows")
        print("• Attention-based layering for professional-grade prompts")
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()