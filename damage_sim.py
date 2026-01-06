import numpy as np
from itertools import permutations
import argparse
from tabulate import tabulate
import csv
import os
import time
start_time = time.time()

from units.attackers import get_attackers
from units.defenders import get_defenders
from units.common import get_wound_threshold
from units.common import roll_damage
from units.common import get_average_damage


parser = argparse.ArgumentParser(description="Warhammer 40k melee damage simulator")
parser.add_argument(
    '--attackers',
    nargs='+',
    default=None,
    help="Space-separated list of attacker names to simulate (default: all available)"
)
parser.add_argument(
    '--defenders',
    nargs='+',
    default=None,
    help="Space-separated list of defender names (default: all)"
)
parser.add_argument(
    '--num-sims',
    type=int,
    default=1000,
    help="Number of simulations per matchup (default: 1000)"
)
args = parser.parse_args()


# Load units
attackers = get_attackers()
defenders = get_defenders()

# Select attackers
if args.attackers:
    selected_attackers = [name for name in args.attackers if name in attackers]
    if not selected_attackers:
        print("No valid attackers found in selection. Reverting to default (D1 D2 D3 D4).")
        selected_attackers = ["Test Unit (D1 D2 D3 D4)"]
else:
    # No flag → use default single test attacker
    print("No --attackers flag provided. Running default test attacker.")
    selected_attackers = ["Test Unit (D1 D2 D3 D4)"]

# Select defenders
if args.defenders:
    selected_defenders = [name for name in args.defenders if name in defenders]
    if not selected_defenders:
        print("No valid defenders found in selection. Reverting to default.")
        selected_defenders = ["Test Target Squad"]
else:
    # No flag → use default single test defender
    print("No --defenders flag provided. Running default test defender.")
    selected_defenders = ["Test Target Squad"]

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
    indexed_groups = [(i, get_average_damage(g['damage'])) for i, g in enumerate(groups)]
    
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
            
            # Save phase
            ap = g['ap']
            save_rolls = rng.integers(1, 7, wounds)
            modified_armour_rolls = save_rolls + ap
            effective_armour_sv = max(defender['save'], 2)

            armour_success = modified_armour_rolls >= effective_armour_sv
            armour_success[save_rolls == 1] = False  # unmodified 1 always fails

            saved = armour_success

            # Invuln if present
            if defender.get('invuln_save') is not None:
                invuln_sv = defender['invuln_save']
                invuln_success = save_rolls >= invuln_sv
                saved = armour_success | invuln_success

                # Debug print — only for first sim, and only if enabled
                if sim == 0 and os.getenv("DEBUG_INVULN", "0") == "1":
                    armour_saves = np.sum(armour_success)
                    invuln_saves = np.sum(invuln_success)
                    total_saved = np.sum(saved)
                    print(f"  Invuln debug (sim 0): Armour saves: {armour_saves}/{wounds}, "
                        f"Invuln saves: {invuln_saves}/{wounds}, Total saved: {total_saved}/{wounds}")
                    if invuln_saves > armour_saves:
                        print("  → Invuln was better in this roll batch")
                    elif invuln_saves == armour_saves:
                        print("  → Invuln and armour equal in this roll batch")
                    else:
                        print("  → Armour was better in this roll batch")
            else:
                saved = armour_success

            failed_saves = np.sum(~saved)
            
            #group_damages = [g['damage'] for _ in range(failed_saves)]
            damage_value = g['damage']
            group_damages = []
            for _ in range(failed_saves):
                rolled = roll_damage(damage_value)  # roll once per successful attack
                group_damages.append(rolled)
            
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

# Main loop: run for each selected attacker vs each defender
table_data = []
for att_name in selected_attackers:
    attacker = attackers[att_name]
    for def_name in selected_defenders:
        defender = defenders[def_name]
        print(f"  Running: {att_name} vs {def_name}")  # <--- ADD THIS
        results = simulate_melee(attacker, defender, args.num_sims)
        table_data.append([
            att_name,
            def_name,
            f"{results['avg_models_destroyed']:.2f}",
            f"{results['avg_partial_damage']:.2f}",
            f"{results['avg_wounds_inflicted']:.2f}",
            f"{results['destroy_probability_%']:.2f}%"
        ])

# Print results in a table
headers = ["Attacker", "Defender", "Avg Destroyed", "Avg Partial", "Avg Inflicted", "Destroy %"]
print(tabulate(table_data, headers=headers, tablefmt="grid"))

os.makedirs("output", exist_ok=True)
csv_path = "output/results.csv"

with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Attacker", "Defender", "Avg Destroyed", "Avg Partial", "Avg Inflicted", "Destroy %"])
    for row in table_data:
        writer.writerow(row)

print(f"\nResults saved to: {csv_path}")
print(f"\nCompleted {len(table_data)} matchups in {time.time() - start_time:.1f} seconds")