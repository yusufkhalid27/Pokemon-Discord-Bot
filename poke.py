import requests
import random
import sqlite3

class PokemonBattle:

    def __init__(self):
        self.pokemon_list = self.load_pokemon_list()
        self.effectiveness_data = {
        'Normal': {
            'immunes': ['Ghost'],
            'weaknesses': ['Rock', 'Steel'],
            'strengths': []
        },
        'Fire': {
            'immunes': [],
            'weaknesses': ['Fire', 'Water', 'Rock', 'Dragon'],
            'strengths': ['Grass', 'Ice', 'Bug', 'Steel']
        },
        'Water': {
            'immunes': [],
            'weaknesses': ['Water', 'Grass', 'Dragon'],
            'strengths': ['Fire', 'Ground', 'Rock']
        },
        'Electric': {
            'immunes': ['Ground'],
            'weaknesses': ['Electric', 'Grass', 'Dragon'],
            'strengths': ['Water', 'Flying']
        },
        'Grass': {
            'immunes': [],
            'weaknesses': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel'],
            'strengths': ['Water', 'Ground', 'Rock']
        },
        'Ice': {
            'immunes': [],
            'weaknesses': ['Fire', 'Water', 'Ice', 'Steel'],
            'strengths': ['Grass', 'Ground', 'Flying', 'Dragon']
        },
        'Fighting': {
            'immunes': ['Ghost'],
            'weaknesses': ['Poison', 'Flying', 'Psychic', 'Bug', 'Fairy'],
            'strengths': ['Normal', 'Ice', 'Rock', 'Dark', 'Steel']
        },
        'Poison': {
            'immunes': ['Steel'],
            'weaknesses': ['Poison', 'Ground', 'Rock', 'Ghost'],
            'strengths': ['Grass', 'Fairy']
        },
        'Ground': {
            'immunes': ['Flying'],
            'weaknesses': ['Grass', 'Bug'],
            'strengths': ['Fire', 'Electric', 'Poison', 'Rock', 'Steel']
        },
        'Flying': {
            'immunes': [],
            'weaknesses': ['Electric', 'Rock', 'Steel'],
            'strengths': ['Grass', 'Fighting', 'Bug']
        },
        'Psychic': {
            'immunes': ['Dark'],
            'weaknesses': ['Psychic', 'Steel'],
            'strengths': ['Fighting', 'Poison']
        },
        'Bug': {
            'immunes': [],
            'weaknesses': ['Fire', 'Fighting', 'Poison', 'Flying', 'Ghost', 'Steel', 'Fairy'],
            'strengths': ['Grass', 'Psychic', 'Dark']
        },
        'Rock': {
            'immunes': [],
            'weaknesses': ['Fighting', 'Ground', 'Steel'],
            'strengths': ['Fire', 'Ice', 'Flying', 'Bug']
        },
        'Ghost': {
            'immunes': ['Normal'],
            'weaknesses': ['Dark'],
            'strengths': ['Psychic', 'Ghost']
        },
        'Dragon': {
            'immunes': ['Fairy'],
            'weaknesses': ['Steel'],
            'strengths': ['Dragon']
        },
        'Dark': {
            'immunes': [],
            'weaknesses': ['Fighting', 'Dark', 'Fairy'],
            'strengths': ['Psychic', 'Ghost']
        },
        'Steel': {
            'immunes': [],
            'weaknesses': ['Fire', 'Water', 'Electric', 'Steel'],
            'strengths': ['Ice', 'Rock', 'Fairy']
        },
        'Fairy': {
            'immunes': [],
            'weaknesses': ['Fire', 'Poison', 'Steel'],
            'strengths': ['Fighting', 'Dragon', 'Dark']
        }
    }
        
    def load_pokemon_list(self):
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=1000')
        return response.json()['results']

    def get_pokemon_data(self, pokemon_name):
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}')

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # Handle non-200 responses
            raise Exception(f'Failed to fetch data for {pokemon_name}. Status Code: {response.status_code}, Response: {response.text}')

    def get_pokemon_photo(self, pokemon_name):
        """Return the URL of the Pokémon's sprite image."""
        pokemon_data = self.get_pokemon_data(pokemon_name)
        # Accessing the sprite image
        return pokemon_data['sprites']['front_default']  # Returns the default front sprite

    def get_pokemon_types(self, pokemon_name):
        """Return the types of the Pokémon."""
        pokemon_data = self.get_pokemon_data(pokemon_name)
        # Extracting the types (capitalized to match effectiveness_data keys)
        types = [type_info['type']['name'].title() for type_info in pokemon_data['types']]
        return types
    
    def calculate_advantage(self, pokemon1_types, pokemon2_types):
        
        # Is Pokémon 2 immune to one of Pokémon 1's types?
        for type1 in pokemon1_types:
            for type2 in pokemon2_types:
                if type2 in self.effectiveness_data[type1]['immunes']:
                    return 2  # Pokémon 2 wins due to immunity

        # Is Pokémon 1 immune to one of Pokémon 2's types?
        for type2 in pokemon2_types:
            for type1 in pokemon1_types:
                if type1 in self.effectiveness_data[type2]['immunes']:
                    return 1  # Pokémon 1 wins due to immunity

        
        effectiveness_1_vs_2 = 1  
        effectiveness_2_vs_1 = 1  

        for type1 in pokemon1_types:
            for type2 in pokemon2_types:
                if type2 in self.effectiveness_data[type1]['strengths']:
                    effectiveness_1_vs_2 = 2  # Effective
                elif type2 in self.effectiveness_data[type1]['weaknesses']:
                    effectiveness_1_vs_2 = 0.5  # Not effective

        for type2 in pokemon2_types:
            for type1 in pokemon1_types:
                if type1 in self.effectiveness_data[type2]['strengths']:
                    effectiveness_2_vs_1 = 2  # Effective
                elif type1 in self.effectiveness_data[type2]['weaknesses']:
                    effectiveness_2_vs_1 = 0.5  # Not effective

        if effectiveness_1_vs_2 > effectiveness_2_vs_1:
            return 1
        elif effectiveness_1_vs_2 < effectiveness_2_vs_1:
            return 2
        else:
            return 0