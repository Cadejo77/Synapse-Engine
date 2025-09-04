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
    """Apply safety filtering to remove problematic tokens based on content rating"""
    policy = safety_config.get('policy', {})
    optional_strip_categories = policy.get('optional_strip_categories', [])
    content_ratings = policy.get('content_ratings', {})
    
    # Get current content rating from context
    current_rating = context.get('content_rating', 'safe')
    allowed_categories = content_ratings.get(current_rating, [])
    
    if not optional_strip_categories and not content_ratings:
        return tokens
    
    # Get current safety categorization
    safety_map = categorize_tokens(tokens, safety_config)
    
    # Filter tokens based on content rating
    filtered_tokens = []
    flags = safety_config.get('flags', {})
    
    for token in tokens:
        should_include = True
        
        # Check if token belongs to a restricted category for this rating
        for category, category_tokens in flags.items():
            if token in category_tokens:
                if category not in allowed_categories and category not in ['franchise']:  # franchise can be optionally stripped
                    should_include = False
                    context.setdefault('warnings', []).append(
                        f"Token '{token}' filtered due to content rating '{current_rating}'"
                    )
                    break
        
        if should_include:
            filtered_tokens.append(token)
    
    
    # Check for policy violations with the filtered tokens
    filtered_safety_map = categorize_tokens(filtered_tokens, safety_config)
    if violates_policy(filtered_safety_map, safety_config):
        # Try stripping optional categories
        flags = safety_config.get('flags', {})
        final_tokens = []
        
        for token in filtered_tokens:
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
                final_tokens.append(token)
        
        return final_tokens
    
    return filtered_tokens