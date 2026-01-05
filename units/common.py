# units/common.py
def get_wound_threshold(s, t):
    if s >= t * 2:     return 2
    if s > t:          return 3
    if s == t:         return 4
    if s >= (t + 1) // 2: return 5
    if s <= t // 2:    return 6
    raise ValueError(f"Cannot determine wound roll for S{s} vs T{t}")