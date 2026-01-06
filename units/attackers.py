# units/attackers.py

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
        "Bloodthirster (Great Axe of Khorne - Strike)": {
            'name': 'Bloodthirster (Great Axe of Khorne - Strike)',
            'models_total': 1,
            'melee_weapon_groups': [
                {
                    'count': 1,
                    'weapon_name': 'Great Axe of Khorne (strike)',
                    'attacks': 7,
                    'ws': 2,
                    'strength': 16,
                    'ap': -4,
                    'damage': 'D6+2',  # ← string instead of number
                    'abilities': ['devastating wounds'],
                },
            ],
        },
        "Bloodthirster (Great Axe of Khorne - Sweep)": {
            'name': 'Bloodthirster (Great Axe of Khorne - Sweep)',
            'models_total': 1,
            'melee_weapon_groups': [
                {
                    'count': 1,
                    'weapon_name': 'Great Axe of Khorne (sweep)',
                    'attacks': 14,
                    'ws': 2,
                    'strength': 10,
                    'ap': -2,
                    'damage': 2,
                    'abilities': ['devastating wounds'],
                },
            ],
        },
        "Chaos Chosen + Chaos Lord": {
            'name': 'Chaos Chosen + Chaos Lord',
            'models_total': 10,  # 10 Chosen + 1 Lord
            'melee_weapon_groups': [
                # Chaos Lord
                {
                    'count': 1,
                    'weapon_name': 'Power fist (Lord)',
                    'attacks': 5,
                    'ws': 2,
                    'strength': 8,
                    'ap': -2,
                    'damage': 2,
                    'abilities': [],
                },
                # Chaos Chosen
                {
                    'count': 2,
                    'weapon_name': 'Paired accursed weapons (Chosen)',
                    'attacks': 5,
                    'ws': 3,
                    'strength': 5,
                    'ap': -2,
                    'damage': 1,
                    'abilities': ['twin-linked'],
                },
                {
                    'count': 2,
                    'weapon_name': 'Power Fist (Chosen)',
                    'attacks': 4,
                    'ws': 3,
                    'strength': 8,
                    'ap': -2,
                    'damage': 2,
                    'abilities': [],
                },
                {
                    'count': 6,
                    'weapon_name': 'Accursed weapons (Chosen)',
                    'attacks': 4,
                    'ws': 3,
                    'strength': 5,
                    'ap': -2,
                    'damage': 1,
                    'abilities': [],
                },
            ],
        },
    }