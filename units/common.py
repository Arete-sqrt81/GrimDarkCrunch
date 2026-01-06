import numpy as np

# units/common.py
def get_wound_threshold(s, t):
    if s >= t * 2:     return 2
    if s > t:          return 3
    if s == t:         return 4
    if s >= (t + 1) // 2: return 5
    if s <= t // 2:    return 6
    raise ValueError(f"Cannot determine wound roll for S{s} vs T{t}")

import re

def roll_damage(damage_str, count=1):
    """Roll damage for a string like 'D6+2', '2', 'D3', etc."""
    if isinstance(damage_str, (int, float)):
        return damage_str * count  # fixed damage

    # Parse string: e.g. 'D6+2', 'D3', '2D6'
    match = re.match(r'(\d*)D(\d+)([+-]?\d*)', damage_str)
    if match:
        num_dice = int(match.group(1) or 1)
        die_size = int(match.group(2))
        modifier = int(match.group(3) or 0)
        total = 0
        for _ in range(num_dice * count):
            total += np.random.randint(1, die_size + 1)
        total += modifier * count
        return total
    else:
        # Fallback: try to interpret as fixed
        try:
            return float(damage_str) * count
        except ValueError:
            raise ValueError(f"Invalid damage format: {damage_str}")
        
def get_average_damage(damage):
    if isinstance(damage, (int, float)):
        return float(damage)
    if damage == 'D6+2':
        return 5.5  # average of 1-6 + 2
    # Add more cases later as needed (e.g. 'D3' → 2, '2D6' → 7, etc.)
    try:
        return float(damage)  # fallback for numbers-as-strings
    except (ValueError, TypeError):
        return 1.0  # safe fallback so order doesn't crash