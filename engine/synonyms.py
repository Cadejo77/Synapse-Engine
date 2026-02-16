"""
Synonym normalization and token replacement
"""
from typing import List, Dict, Any

def normalize_all(tokens: List[str], synonyms_config: Dict[str, Any]) -> List[str]:
    """Normalize tokens using synonym mappings"""
    synonyms_data = synonyms_config.get('synonyms', {})
    normalization = synonyms_config.get('normalization', {})
    
    if not synonyms_data:
        return tokens
    
    result = []
    for token in tokens:
        normalized_token = token
        
        # Apply normalization settings
        if normalization.get('lowercase', False):
            normalized_token = normalized_token.lower()
        
        if normalization.get('replace_spaces_with_underscores', False):
            normalized_token = normalized_token.replace(' ', '_')
        
        # Apply synonym mapping
        found_synonym = False
        for canonical, synonyms in synonyms_data.items():
            if normalized_token in synonyms or normalized_token == canonical:
                result.append(canonical)
                found_synonym = True
                break
        
        if not found_synonym:
            result.append(normalized_token)
    
    return result