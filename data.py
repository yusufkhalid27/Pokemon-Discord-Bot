import sqlite3

class PokemonDatabase:
    def __init__(self, db_name='my_database.db'):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()

        # Create user_pokemon table with 6 slots for Pokémon
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_pokemon (
                user_id INTEGER PRIMARY KEY,
                slot1 TEXT,
                slot2 TEXT,
                slot3 TEXT,
                slot4 TEXT,
                slot5 TEXT,
                slot6 TEXT
            )
        ''')

        self.connection.commit()

    def close(self):
        self.connection.close()

    def check_and_add_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM user_pokemon WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()

        # Add a new user with empty slots if the user does not exist
        if user is None:
            cursor.execute('''
                INSERT INTO user_pokemon (user_id, slot1, slot2, slot3, slot4, slot5, slot6)
                VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL)
            ''', (user_id,))
            self.connection.commit()


    def user_exists(self, user_id):
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1 FROM user_pokemon WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None


    def get_user_pokemon(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT slot1, slot2, slot3, slot4, slot5, slot6 FROM user_pokemon WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        if result is None:
            return [None] * 6
        return result

    def add_pokemon(self, user_id, pokemon_name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT slot1, slot2, slot3, slot4, slot5, slot6 FROM user_pokemon WHERE user_id = ?', (user_id,))
        slots = cursor.fetchone()

        # Find the first empty slot
        for i in range(6):
            if slots[i] is None:
                cursor.execute(f'UPDATE user_pokemon SET slot{i+1} = ? WHERE user_id = ?', (pokemon_name, user_id))
                self.connection.commit()
                return

        # If all slots are full, raise an error
        raise Exception("All slots are full. Cannot add more Pokémon.")

    def remove_pokemon(self, user_id, pokemon_name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT slot1, slot2, slot3, slot4, slot5, slot6 FROM user_pokemon WHERE user_id = ?', (user_id,))
        slots = cursor.fetchone()

        # Find the slot with the given Pokémon name and set it to NULL
        for i in range(6):
            if slots[i] == pokemon_name:
                cursor.execute(f'UPDATE user_pokemon SET slot{i+1} = NULL WHERE user_id = ?', (user_id,))
                self.connection.commit()
                return

        # If the Pokémon is not found, raise an error
        raise Exception("Pokémon not found in user's team.")
