# Pokémon Discord Bot

A lightweight Discord bot where users can catch Pokémon in the wild and battle each other using type-advantage mechanics in a discord server. This bot is not hosted on Discord any longer, will return in the future.


## Commands

| Command | Description |
|---|---|
| `!wild` | Encounter a random wild Pokémon. Use `!throw` to catch it or `!run` to flee. |
| `!team` | View your current Pokémon team with sprites. |
| `!battle @user` | Challenge another user to a battle. |

## How It Works

**Catching** — Wild encounters give you a 35% chance to catch on each throw. The Pokémon can also escape (3 varieties with increasing suspense) or flee entirely. If your team is full (6 Pokémon), you'll be asked to release one to make room.

**Battling** — Each round is decided by type-advantage using the full 18-type effectiveness chart, including immunities. Losing Pokémon are replaced by the next in the team until one side runs out. Neutral matchups are decided by a coin flip.

## Files

- `main.py` — Bot setup and Discord commands
- `poke.py` — PokeAPI integration and type-effectiveness logic
- `data.py` — SQLite database for storing user teams
