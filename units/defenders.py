# units/defenders.py
def get_defenders():
    return {
        "5x Assault Intercessors": {
            'name': '5x Assault Intercessors',
            'models': 5,
            'toughness': 4,
            'save': 3,
            'wounds_per_model': 2,
            'invuln_save': None,
        },
        "Chaos Rhino": {
            'name': 'Chaos Rhino',
            'models': 1,
            'toughness': 9,
            'save': 3,
            'wounds_per_model': 10,
            'invuln_save': None,
        },
        "Test Target Squad": {
            'name': 'Test Target Squad',
            'models': 10,
            'toughness': 4,
            'save': 3,
            'wounds_per_model': 3,
            'invuln_save': None,
        },
        # Add more metagame defenders here later
    }