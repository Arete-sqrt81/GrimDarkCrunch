# GrimDarkCrunch

Warhammer 40k damage simulator (melee focus).

## Folder structure
- `damage_sim.py`: Main script + CLI
- `units/`: All unit data
  - `attackers.py`: Attacker configs
  - `defenders.py`: Defender configs
  - `common.py`: Shared helpers
- `output/`: Results (CSV, etc.)

## How to add a unit
1. Open `units/attackers.py` or `defenders.py`
2. Add a new entry to the dict returned by `get_attackers()` / `get_defenders()`
3. Use the same dict format as existing entries

## Run examples
python damage_sim.py --attackers "10x Assault Intercessors" "Test Unit (D1 D2 D3 D4)"