# units/attackers.py
from .common import get_wound_threshold  # if needed later

def get_attackers():
    return {
        "10x Assault Intercessors": {
            'name': '10x Assault Intercessors',
            'models_total': 10,
            'melee_weapon_groups': [
                {
                    'count': 9,
                    'weapon_name': 'Astartes chainsword',
                    'attacks': 4,
                    'ws': 3,
                    'strength': 4,
                    'ap': -1,
                    'damage': 1,
                    'abilities': [],
                },
                {
                    'count': 1,
                    'weapon_name': 'Thunder hammer',
                    'attacks': 3,
                    'ws': 4,
                    'strength': 8,
                    'ap': -2,
                    'damage': 2,
                    'abilities': [],
                },
            ],
        },
        "Test Unit (D1 D2 D3 D4)": {
            'name': 'Test Unit (D1 D2 D3 D4)',
            'models_total': 10,
            'melee_weapon_groups': [
                {'count': 3, 'weapon_name': 'D1 weapon', 'attacks': 4, 'ws': 3, 'strength': 4, 'ap': -1, 'damage': 1, 'abilities': []},
                {'count': 3, 'weapon_name': 'D2 weapon', 'attacks': 3, 'ws': 4, 'strength': 5, 'ap': -2, 'damage': 2, 'abilities': []},
                {'count': 2, 'weapon_name': 'D3 weapon', 'attacks': 2, 'ws': 4, 'strength': 6, 'ap': -2, 'damage': 3, 'abilities': []},
                {'count': 2, 'weapon_name': 'D4 weapon', 'attacks': 2, 'ws': 4, 'strength': 8, 'ap': -3, 'damage': 4, 'abilities': []},
            ],
        },
        # Add more later (e.g. Bloodthirster, Maulerfiend, etc.)
    }