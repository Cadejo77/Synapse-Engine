"""
Safety filtering and content moderation
"""
from typing import List, Dict, Any, Set

def categorize_tokens(tokens: List[str], safety_config: Dict[str, Any]) -> Dict[str, List[str]]:
    """Categorize tokens according to safety flags"""
    flags = safety_config.get('flags', {})
    categorized = {}
    
    for category, category_tokens in flags.items():
        categorized[category] = []
        for token in tokens:
            if token in category_tokens:
                categorized[category].append(token)
    
    return categorized

def violates_policy(safety_map: Dict[str, List[str]], safety_config: Dict[str, Any]) -> bool:
    """Check if the current token combination violates safety policy"""
    policy = safety_config.get('policy', {})
    
    # Check for blocked combinations
    block_combinations = policy.get('block_if_combination', [])
    for combination in block_combinations:
        # Check if all categories in the combination have tokens
        violation = True
        for category in combination:
            if not safety_map.get(category):
                violation = False
                break
        
        if violation:
            return True
    
    return False

def apply_safety_filter(tokens: List[str], context: Dict[str, Any], 
                       safety_config: Dict[str, Any]) -> List[str]:
    """Apply safety filtering to remove problematic tokens"""
    policy = safety_config.get('policy', {})
    optional_strip_categories = policy.get('optional_strip_categories', [])
    
    if not optional_strip_categories:
        return tokens
    
    # Get current safety categorization
    safety_map = categorize_tokens(tokens, safety_config)
    
    # If we have a safety violation, try stripping optional categories
    if violates_policy(safety_map, safety_config):
        flags = safety_config.get('flags', {})
        filtered_tokens = []
        
        for token in tokens:
            should_keep = True
            # Check if token belongs to an optional strip category
            for category in optional_strip_categories:
                if token in flags.get(category, []):
                    should_keep = False
                    context.setdefault('warnings', []).append(
                        f"Removed {token} from {category} for safety"
                    )
                    break
            
            if should_keep:
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    return tokens