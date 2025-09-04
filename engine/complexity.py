"""
Complexity budget management
"""
from typing import Dict, Any, Optional

def get_cost(entry: Dict[str, Any], complexity_rules: Dict[str, Any]) -> int:
    """Get the complexity cost for an entry"""
    # Check if entry has explicit complexity_cost
    if 'complexity_cost' in entry:
        return entry['complexity_cost']
    
    # Use default cost from rules
    complexity_data = complexity_rules.get('complexity', {})
    return complexity_data.get('default_cost', 1)

def get_rarity_budget(rarity: str, complexity_rules: Dict[str, Any]) -> int:
    """Get the complexity budget for a given rarity"""
    complexity_data = complexity_rules.get('complexity', {})
    budgets = complexity_data.get('rarity_budgets', {})
    
    return budgets.get(rarity, budgets.get('common', 8))

def check_budget_available(context: Dict[str, Any], cost: int, complexity_rules: Dict[str, Any]) -> bool:
    """Check if there's enough budget remaining for the given cost"""
    used = context.get('complexity_used', 0)
    budget = context.get('budget', get_rarity_budget(context.get('rarity', 'common'), complexity_rules))
    
    return used + cost <= budget

def consume_budget(context: Dict[str, Any], cost: int) -> None:
    """Consume budget for a selected item"""
    context['complexity_used'] = context.get('complexity_used', 0) + cost