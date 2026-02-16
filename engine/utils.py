"""
Utility functions for random selection with deterministic seeding
"""
import random
from typing import List, TypeVar, Dict, Any

T = TypeVar('T')

class DeterministicRandom:
    """Wrapper around random.Random for deterministic generation"""
    
    def __init__(self, seed: int = None):
        self._rng = random.Random(seed)
    
    def random(self) -> float:
        return self._rng.random()
    
    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)
    
    def choice(self, seq):
        return self._rng.choice(seq)
    
    def shuffle(self, seq):
        return self._rng.shuffle(seq)

def weighted_random(items: List[Dict[str, Any]], rng: DeterministicRandom) -> Dict[str, Any]:
    """Select a weighted random item from a list"""
    if not items:
        return None
    
    total = sum(item.get('weight', 1) for item in items)
    if total <= 0:
        return items[-1] if items else None
    
    r = rng.random() * total
    for item in items:
        r -= item.get('weight', 1)
        if r <= 0:
            return item
    
    return items[-1]

def shuffle(arr: List[T], rng: DeterministicRandom) -> List[T]:
    """Shuffle an array using the deterministic RNG"""
    result = arr.copy()
    for i in range(len(result) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        result[i], result[j] = result[j], result[i]
    return result