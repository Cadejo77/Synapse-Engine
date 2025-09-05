#!/usr/bin/env python3
"""
Test the enhanced Synapse Engine with rich descriptions and advanced regional prompting
"""

from synapse_node import SynapsePromptGenerator
from regional_synapse_node import RegionalSynapseNode

def test_rich_descriptions():
    """Test the enhanced rich description functionality"""
    print("=== Testing Rich Descriptions ===")
    
    node = SynapsePromptGenerator()
    
    # Test rich descriptions enabled (default)
    positive_rich, negative_rich, metadata_rich = node.generate_prompt(
        count=1,
        output_format="text",
        seed=12345,
        user_prompt="epic dragon knight battle",
        genre_control="fantasy",
        enable_rich_descriptions=True
    )
    
    print(f"Rich Descriptions ENABLED:")
    print(f"Positive: {positive_rich}")
    print(f"Negative: {negative_rich}")
    print(f"Metadata: {metadata_rich}")
    print()
    
    # Test rich descriptions disabled
    positive_basic, negative_basic, metadata_basic = node.generate_prompt(
        count=1,
        output_format="text", 
        seed=12345,
        user_prompt="epic dragon knight battle",
        genre_control="fantasy",
        enable_rich_descriptions=False
    )
    
    print(f"Rich Descriptions DISABLED:")
    print(f"Positive: {positive_basic}")
    print(f"Negative: {negative_basic}")
    print(f"Metadata: {metadata_basic}")
    print()
    
    return positive_rich

def test_regional_format():
    """Test the new regional output format"""
    print("=== Testing Regional Output Format ===")
    
    node = SynapsePromptGenerator()
    
    # Test regional format with regional prompting enabled
    regional_output, negative, metadata = node.generate_prompt(
        count=1,
        output_format="regional",
        seed=54321,
        user_prompt="cyberpunk hacker in neon city with flying cars",
        genre_control="cyberpunk",
        regional_prompting=True
    )
    
    print(f"Regional Format Output:")
    print(f"Main: {regional_output}")
    print(f"Negative: {negative}")
    print(f"Metadata: {metadata}")
    print()

def test_advanced_regional_node(main_prompt):
    """Test the redesigned advanced regional node"""
    print("=== Testing Advanced Regional Node ===")
    
    regional_node = RegionalSynapseNode()
    
    # Test basic regional mode
    full, negative, region_1, region_2, region_3, quality, metadata = regional_node.generate_regional_prompt(
        main_prompt=main_prompt,
        regional_mode=True,
        enable_second_subject=False,
        enable_third_region=False
    )
    
    print(f"Basic Regional Mode:")
    print(f"Full Prompt: {full}")
    print(f"Negative: {negative}")
    print(f"Region 1 (Subject): {region_1}")
    print(f"Region 2 (Background): {region_2}")
    print(f"Region 3: {region_3}")
    print(f"Quality Tags: {quality}")
    print(f"Metadata: {metadata}")
    print()
    
    # Test with second subject and third region
    full2, negative2, region_1_2, region_2_2, region_3_2, quality2, metadata2 = regional_node.generate_regional_prompt(
        main_prompt=main_prompt,
        regional_mode=True,
        enable_second_subject=True,
        enable_third_region=True,
        subject_weight=1.2,
        background_weight=0.8,
        region_separator="BREAK"
    )
    
    print(f"Advanced Regional Mode (Second Subject + Third Region):")
    print(f"Full Prompt: {full2}")
    print(f"Negative: {negative2}")
    print(f"Region 1 (Primary Subject): {region_1_2}")
    print(f"Region 2 (Background): {region_2_2}")
    print(f"Region 3 (Second Subject/Additional): {region_3_2}")
    print(f"Quality Tags: {quality2}")
    print(f"Metadata: {metadata2}")
    print()
    
    # Test non-regional mode for comparison
    full3, negative3, region_1_3, region_2_3, region_3_3, quality3, metadata3 = regional_node.generate_regional_prompt(
        main_prompt=main_prompt,
        regional_mode=False
    )
    
    print(f"Non-Regional Mode (Simple Split):")
    print(f"Full Prompt: {full3}")
    print(f"Region 1 (Subject): {region_1_3}")
    print(f"Region 2 (Background): {region_2_3}")
    print(f"Metadata: {metadata3}")
    print()

def test_workflow_integration():
    """Test the complete workflow integration"""
    print("=== Testing Complete Workflow Integration ===")
    
    main_node = SynapsePromptGenerator()
    regional_node = RegionalSynapseNode()
    
    # Generate rich prompt with main node
    main_prompt, main_negative, main_metadata = main_node.generate_prompt(
        count=1,
        output_format="text",
        seed=99999,
        user_prompt="mystical forest wizard battling shadow demon near ancient temple",
        genre_control="dark_fantasy",
        enable_rich_descriptions=True
    )
    
    print(f"Main Node Output:")
    print(f"Prompt: {main_prompt}")
    print(f"Negative: {main_negative}")
    print(f"Metadata: {main_metadata}")
    print()
    
    # Process with regional node for advanced control
    full, negative, region_1, region_2, region_3, quality, metadata = regional_node.generate_regional_prompt(
        main_prompt=main_prompt,
        regional_mode=True,
        enable_second_subject=True,
        enable_third_region=True,
        subject_weight=1.1,
        background_weight=1.0,
        region_separator="BREAK",
        custom_quality_tags="8k, ultra detailed, photorealistic, award winning"
    )
    
    print(f"Regional Node Processing:")
    print(f"Full Prompt: {full}")
    print(f"Regional Negative: {negative}")
    print(f"Region 1 (Wizard): {region_1}")
    print(f"Region 2 (Environment): {region_2}")
    print(f"Region 3 (Shadow Demon): {region_3}")
    print(f"Custom Quality: {quality}")
    print(f"Regional Metadata: {metadata}")
    print()

def test_different_genres_and_styles():
    """Test rich descriptions across different genres"""
    print("=== Testing Different Genres and Styles ===")
    
    node = SynapsePromptGenerator()
    
    test_cases = [
        {
            "name": "Fantasy Epic",
            "prompt": "armored paladin with holy sword fighting undead horde",
            "genre": "fantasy",
            "seed": 11111
        },
        {
            "name": "Cyberpunk Scene", 
            "prompt": "neon-enhanced cyborg assassin infiltrating corporate tower",
            "genre": "cyberpunk",
            "seed": 22222
        },
        {
            "name": "Steampunk Adventure",
            "prompt": "brass-goggled inventor piloting mechanical airship",
            "genre": "steampunk", 
            "seed": 33333
        },
        {
            "name": "Dark Fantasy Horror",
            "prompt": "blood-soaked necromancer summoning skeletal army in cursed graveyard",
            "genre": "dark_fantasy",
            "seed": 44444
        }
    ]
    
    for case in test_cases:
        print(f"🎨 {case['name']}:")
        print("-" * 50)
        
        prompt, negative, metadata = node.generate_prompt(
            count=1,
            output_format="text",
            seed=case["seed"],
            user_prompt=case["prompt"],
            genre_control=case["genre"],
            enable_rich_descriptions=True
        )
        
        print(f"Rich Prompt: {prompt}")
        print(f"Negative: {negative}")
        print(f"Metadata: {metadata}")
        print()

if __name__ == "__main__":
    print("🧪 Testing Enhanced Synapse Engine - Rich Descriptions & Advanced Regional Prompting\n")
    
    try:
        # Test rich descriptions
        main_prompt = test_rich_descriptions()
        
        # Test regional output format
        test_regional_format()
        
        # Test advanced regional node
        test_advanced_regional_node(main_prompt)
        
        # Test complete workflow
        test_workflow_integration()
        
        # Test different genres
        test_different_genres_and_styles()
        
        print("✅ All enhanced tests completed successfully!")
        print("\n🎯 Summary of Enhancements:")
        print("• Rich, detailed prompt generation with comprehensive quality tags")
        print("• Enhanced universal formatter utilizing full token metadata")
        print("• Advanced regional prompting with subject/background separation")
        print("• Multiple regional modes (2-3 regions) with weighting support")
        print("• Toggle switch for regional vs non-regional prompting")
        print("• Improved negative prompts organized by categories")
        print("• Full workflow integration between main and regional nodes")
        print("• Genre-specific quality enhancements and styling")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()