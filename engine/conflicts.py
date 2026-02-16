"""
Conflict resolution between incompatible tokens
"""
from typing import List, Dict, Any
import copy

def apply_conflict_rules(entries: List[Dict[str, Any]], context: Dict[str, Any],
                        relations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply conflict rules to filter out incompatible combinations"""
    conflicts_data = relations.get('conflicts', {}).get('rules', [])
    if not conflicts_data:
        return entries
    
    # Get all currently selected tokens
    all_tokens = []
    for dim_tokens in context.get('tokens', {}).values():
        all_tokens.extend(dim_tokens)
    
    all_tokens_set = set(all_tokens)
    
    result = []
    for entry in entries:
        entry_copy = copy.deepcopy(entry)
        token = entry_copy.get('token') or entry_copy.get('name', '')
        
        # Check each conflict rule
        should_include = True
        for rule in conflicts_data:
            rule_tokens = set(rule.get('tokens', []))
            strategy = rule.get('strategy', 'suppress_second')
            factor = rule.get('factor', 0.5)
            
            # Check if this entry's token is part of a conflict rule
            if token in rule_tokens:
                # Check if any other tokens from the same rule are already selected
                conflicting_tokens = rule_tokens.intersection(all_tokens_set)
                
                if conflicting_tokens:
                    if strategy == 'suppress_second':
                        # Don't include this token
                        should_include = False
                        context.setdefault('conflicts_applied', []).append(
                            f"Suppressed {token} due to conflict with {list(conflicting_tokens)}"
                        )
                        break
                    elif strategy == 'reduce_weight':
                        # Reduce weight by factor
                        entry_copy['weight'] = int(entry_copy.get('weight', 1) * factor)
                        context.setdefault('conflicts_applied', []).append(
                            f"Reduced weight of {token} to {entry_copy['weight']} due to conflict"
                        )
                    elif strategy == 'allow_if_genre_multi':
                        # Only allow if genre is 'multi'
                        if context.get('genre') != 'multi':
                            should_include = False
                            context.setdefault('conflicts_applied', []).append(
                                f"Suppressed {token} (not multi-genre) due to conflict"
                            )
                            break
        
        if should_include:
            result.append(entry_copy)
    
    return result