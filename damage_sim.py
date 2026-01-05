import numpy as np
from itertools import permutations

from units.attackers import get_attackers
from units.defenders import get_defenders
from units.common import get_wound_threshold


attackers = get_attackers()
defenders = get_defenders()

# For now, pick one to test (we'll add CLI next)
selected_attacker = attackers["Test Unit (D1 D2 D3 D4)"]
selected_defender = defenders["Test Target Squad"]

# Units (example with multi-model target)
# attacker_config = { moved to attackers.py
#     'name': 'Test Unit (D1, D2, D4)',
#     'models_total': 10,  # arbitrary, adjust counts as needed
    
#     'melee_weapon_groups': [
#         {
#             'count': 5,  # e.g. many low-D
#             'weapon_name': 'D1 weapon',
#             'attacks': 4,
#             'ws': 3,
#             'strength': 4,
#             'ap': -1,
#             'damage': 1,
#             'abilities': [],
#         },
#         {
#             'count': 3,
#             'weapon_name': 'D2 weapon',
#             'attacks': 3,
#             'ws': 4,
#             'strength': 5,
#             'ap': -2,
#             'damage': 2,
#             'abilities': [],
#         },
#         {
#             'count': 2,
#             'weapon_name': 'D4 weapon',
#             'attacks': 2,
#             'ws': 4,
#             'strength': 8,
#             'ap': -3,
#             'damage': 4,
#             'abilities': [],
#         },
#         {
#             'count': 2,
#             'weapon_name': 'D3 weapon',
#             'attacks': 2,
#             'ws': 4,
#             'strength': 6,
#             'ap': -2,
#             'damage': 3,
#             'abilities': [],
#         },
#     ],
# }

# defender = { moved to defenders.py
#     'name': 'Test Target Squad',
#     'models': 10,  # large enough to avoid end-of-unit effects
#     'toughness': 4,
#     'save': 3,
#     'wounds_per_model': 3,  # W=3
#     'invuln_save': None,
# }

# def get_wound_threshold(s, t): moved to common.py
#     if s >= t * 2:     return 2
#     if s > t:          return 3
#     if s == t:         return 4
#     if s >= (t + 1) // 2: return 5
#     if s <= t // 2:    return 6
#     raise ValueError(f"Cannot determine wound roll for S{s} vs T{t}")

def allocate_damage(group_damage_lists, num_models, w_per_model):
    # Simulates forced focus on wounded models (rules: must allocate to wounded/allocation-received model first)
    # Starts with first model, finishes it before moving on (attacker optimal = defender forced focus)
    remaining = [w_per_model] * num_models
    destroyed = 0
    applied = 0
    current_target = 0
    
    for group_damages in group_damage_lists:
        for dmg in group_damages:
            if current_target >= num_models:
                break
            # Apply to current target (wounded or allocated)
            dmg_applied = min(dmg, remaining[current_target])
            remaining[current_target] -= dmg_applied  # excess lost
            applied += dmg_applied
            if remaining[current_target] <= 0:
                destroyed += 1
                current_target += 1  # move to next model
                if current_target >= num_models:
                    break
    
    # Partial on the last wounded model
    partial = 0
    if current_target < num_models and remaining[current_target] < w_per_model:
        partial = w_per_model - remaining[current_target]
    
    return destroyed, partial, applied

def simulate_melee(attacker, defender, num_sims=1000):  # Low for dev, change to 200_000 later
    rng = np.random.default_rng()
    
    total_models_destroyed = np.zeros(num_sims, dtype=float)
    total_partial_damage = np.zeros(num_sims, dtype=float)
    total_wounds_inflicted = np.zeros(num_sims, dtype=float)
    
    w_value = defender['wounds_per_model']
    
    # Step 0: Compute fixed weapon order upfront (before any rolls)
    groups = attacker['melee_weapon_groups']
    num_groups = len(groups)
    
    # Create list of (index, D) for sorting
    indexed_groups = [(i, g['damage']) for i, g in enumerate(groups)]
    
    # Rule 1 & 2: Collect all groups where D >= w_value (one-shot capable)
    high_d_groups = [idx for idx, d in indexed_groups if d >= w_value]
    
    # Rule 3: Collect remaining groups (D < w_value), sort by increasing D
    low_d_groups = [idx for idx, d in indexed_groups if d < w_value]
    low_d_groups.sort(key=lambda idx: groups[idx]['damage'])
    
    # Final order: high-D first (agnostic among them → keep original relative order), then low-D in increasing D
    fixed_order_indices = high_d_groups + low_d_groups
    
    # Debug: show chosen order
    print(f"Chosen weapon order (indices): {fixed_order_indices}")
    print(f"Weapon names in order: {[groups[i]['weapon_name'] for i in fixed_order_indices]}")
    
    for sim in range(num_sims):
        group_damage_lists = [[] for _ in range(num_groups)]
        
        # Generate damage lists (same as before)
        for g_idx, g in enumerate(groups):
            count = g['count']
            attacks_per = g['attacks']
            total_attacks = count * attacks_per
            
            if total_attacks == 0:
                continue
            
            hit_rolls = rng.integers(1, 7, total_attacks)
            hits = np.sum(hit_rolls >= g['ws'])
            
            if hits == 0:
                continue
            
            s = g['strength']
            t = defender['toughness']
            wound_threshold = get_wound_threshold(s, t)
            
            wound_rolls = rng.integers(1, 7, hits)
            wounds = np.sum(wound_rolls >= wound_threshold)
            
            if wounds == 0:
                continue
            
            ap = g['ap']
            save_rolls = rng.integers(1, 7, wounds)
            modified_rolls = save_rolls + ap
            effective_sv = max(defender['save'], 2)
            auto_fail_mask = (save_rolls == 1)
            normal_fail_mask = (modified_rolls < effective_sv)
            failed_saves = np.sum(auto_fail_mask | normal_fail_mask)
            
            group_damages = [g['damage'] for _ in range(failed_saves)]
            group_damage_lists[g_idx] = group_damages
        
        # Apply damage in the fixed order
        ordered_damage_lists = [group_damage_lists[i] for i in fixed_order_indices if group_damage_lists[i]]
        
        destroyed, partial, applied = allocate_damage(ordered_damage_lists, defender['models'], defender['wounds_per_model'])
        
        total_models_destroyed[sim] = destroyed
        total_partial_damage[sim] = partial
        total_wounds_inflicted[sim] = applied
        
        # Debug for first 5 sims (low sim count only)
        if sim < 5 and num_sims <= 1000:
            print(f"Sim {sim}: Group damage lists (original): {group_damage_lists}")
            print(f"Applied in order: {ordered_damage_lists}")
            print(f"Result: destroyed {destroyed}, partial {partial}, inflicted {applied}")
    
    # Aggregate
    avg_models_destroyed = total_models_destroyed.mean()
    avg_partial_damage = total_partial_damage.mean()
    avg_wounds_inflicted = total_wounds_inflicted.mean()
    destroy_prob = (total_models_destroyed > 0).mean() * 100
    
    return {
        'num_sims': num_sims,
        'avg_models_destroyed': avg_models_destroyed,
        'avg_partial_damage': avg_partial_damage,
        'avg_wounds_inflicted': avg_wounds_inflicted,
        'destroy_probability_%': destroy_prob
    }
# Run
results = simulate_melee(selected_attacker, selected_defender, num_sims=1000)

print(f"Simulating {selected_attacker['name']} vs {selected_defender['name']} (T{selected_defender['toughness']}, Sv{selected_defender['save']}+, W{selected_defender['wounds_per_model']}x{selected_defender['models']})")
print(f"({results['num_sims']:,} simulations)")
print(f"Avg models destroyed: {results['avg_models_destroyed']:.2f}")
print(f"Avg partial damage on surviving model: {results['avg_partial_damage']:.2f}")
print(f"Avg wounds inflicted: {results['avg_wounds_inflicted']:.2f}")
print(f"Probability of destroying at least one: {results['destroy_probability_%']:.2f}%")