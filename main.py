import discord
from discord.ext import commands
import random
from data import PokemonDatabase
from poke import PokemonBattle
import asyncio
import os

# ééé


async def add_or_release(pokemon_name, ctx, user_id):
     
    user_pokemon = Database.get_user_pokemon(user_id)  

    user_pokemon_names = [name for name in user_pokemon if name]
    if len(user_pokemon_names) < 6:
        # If the user has less than 6 Pokémon, add the new one
        Database.add_pokemon(user_id, pokemon_name)
        await ctx.send(f"You have caught {pokemon_name.title()} and added it to your team!")
    else:
        # If the user has 6 Pokémon, list them and ask for action
        await ctx.send("You already have 6 Pokémon in your team. Here they are:")
        await ctx.send(", ".join(user_pokemon_names))
        await ctx.send("Which Pokémon would you like to release? Type the name of the Pokémon to release it, or type 'keep' to keep your current team.")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30)  

            if msg.content.lower() == 'keep':
                await ctx.send("You chose to keep your current team.")
            elif msg.content in user_pokemon_names:
                # Remove the specified Pokémon from the user's team
                Database.remove_pokemon(user_id, msg.content)
                Database.add_pokemon(user_id, pokemon_name)
                await ctx.send(f"You have released {msg.content.title()} from your team and added {pokemon_name}.")
            else:
                await ctx.send("Invalid input. Please type the name of a Pokémon you want to release or 'keep'.")

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Your team remains unchanged.")


def wild_encounter_odds():
    outcomes = ['caught', 'escape1', 'escape2', 'escape3', 'flee']
    weights = [0.35, 0.16, 0.16, 0.16, 0.16]
    return random.choices(outcomes, weights=weights, k=1)[0]

async def wild_encounter(Battler, ctx, user_id):
    encounter = random.choice(Battler.pokemon_list)  # Get a random Pokemon
    pokemon_name = encounter['name'].title()
    photo_url = Battler.get_pokemon_photo(encounter['name'])
    caught = False
    fled = False
    ran = False
    await ctx.send(f"{photo_url}")
    await ctx.send(f"A wild {pokemon_name} appeared! What will you do? Type !run to flee or !throw to catch it.")

    while not caught and not fled and not ran:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ['!run', '!throw']

        try:
            msg = await bot.wait_for('message', check=check, timeout=120)

            if msg.content == '!throw':
                await ctx.send(f"{msg.author} threw a Pokéball!")
                outcome = wild_encounter_odds()  # Get the outcome
                print(f"Outcome: {outcome}")
                if outcome == 'caught':
                    caught = True
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send("Gotcha!")
                    await ctx.send(f"{pokemon_name} was caught!")

                elif outcome == 'flee':
                    fled = True
                    await ctx.send(f"{pokemon_name} dodged and fled!")

                elif outcome == 'escape1':
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(f"The {pokemon_name} escaped the Pokéball!")

                elif outcome == 'escape2':
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(f"The {pokemon_name} escaped the Pokéball!")

                elif outcome == 'escape3':
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(".")
                    await asyncio.sleep(1)
                    await ctx.send(f"The {pokemon_name} escaped the Pokéball!")

            elif msg.content == '!run':
                ran = True
                await ctx.send(f"{msg.author} ran away from the wild encounter.")

        except asyncio.TimeoutError:
            await ctx.send(f"{msg.author} took too long to respond! The wild Pokémon escaped!")
            break  # Exit the loop if the user doesn't respond in time
            
        # Resends for loop repetition    
        if not caught and not fled and not ran:
            await ctx.send(f"{photo_url}")
            await ctx.send(f"What will you do? Type !run to flee or !throw to catch it.")
    
    if caught:
        await add_or_release(encounter['name'], ctx, user_id)





Battler = PokemonBattle()
Database = PokemonDatabase()


intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Create a bot instance with the specified intents and command prefix (e.g., "!")
bot = commands.Bot(command_prefix='!', intents=intents)

# Event to notify when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def team(ctx):
    user_id = ctx.author.id 
    user_pokemon = Database.get_user_pokemon(user_id)

    if user_pokemon:
        await ctx.send(f"{ctx.author}'s Pokémon:")
        for pokemon_name in user_pokemon:
            if pokemon_name: 
                photo_url = Battler.get_pokemon_photo(pokemon_name)  
                await ctx.send(f"{pokemon_name.title()}:")
                await ctx.send(photo_url)

    else:
        await ctx.send(f"User {ctx.author} has no Pokémon.")

@bot.command()
async def wild(ctx):
    user_id = ctx.author.id  # Get the user's ID
    Database.check_and_add_user(user_id)
    await wild_encounter(Battler, ctx, user_id)



@bot.command()
async def battle(ctx,  opponent: discord.User = None):
    
    if opponent is None:
        await ctx.send("Please mention a user to battle! (e.g., \"!battle @username\")")
        return

    member = ctx.guild.get_member(opponent.id)

    if member is None:
        await ctx.send(f"{opponent.name} is not in this server.")
        return

    if opponent == ctx.author:
        await ctx.send("You cannot battle yourself!")
        return

    if not Database.user_exists(opponent.id):
        await ctx.send(f"{opponent.name} is not registered in the Pokémon database.")  
        return
    else:
        await ctx.send(f'{ctx.author.mention} has challenged {opponent.mention} to a battle!')

    # Get each player's team, filter out empty slots, and shuffle the order
    player1_pokemon = [name for name in Database.get_user_pokemon(ctx.author.id) if name]
    player2_pokemon = [name for name in Database.get_user_pokemon(opponent.id) if name]

    if not player1_pokemon:
        await ctx.send(f"{ctx.author.mention} has no Pokémon to battle with!")
        return
    if not player2_pokemon:
        await ctx.send(f"{opponent.mention} has no Pokémon to battle with!")
        return

    random.shuffle(player1_pokemon)
    random.shuffle(player2_pokemon)

    player1_active = player1_pokemon.pop()
    player2_active = player2_pokemon.pop()

    await ctx.send(
        f"{ctx.author.mention} sends out {player1_active} and "
        f"{opponent.mention} sends out {player2_active}!"
    )

    battle_winner = None

    while (True):
        await asyncio.sleep(1)

        round_winner = Battler.calculate_advantage(Battler.get_pokemon_types(player1_active), Battler.get_pokemon_types(player2_active))
        # Randomize for neutral case 
        if round_winner == 0:
            round_winner = random.choice([1, 2])


        if round_winner == 1:
            
            await ctx.send(f"{player1_active} vs. {player2_active}")

            if player2_pokemon:
                fainted = player2_active
                player2_active = player2_pokemon.pop()
                await ctx.send(f"{fainted} fainted! {opponent.name} sends out {player2_active}")
            else:
                battle_winner = ctx.author
                break
            
        else:

            await ctx.send(f"{player1_active} vs. {player2_active}")

            if player1_pokemon:
                fainted = player1_active
                player1_active = player1_pokemon.pop()
                await ctx.send(f"{fainted} fainted! {ctx.author.name} sends out {player1_active}")

            else:
                battle_winner = opponent
                break
            

        


    await ctx.send(f"{battle_winner.mention} wins this round!")



BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "DISCORD_BOT_TOKEN environment variable not set. "
        "Set it before running the bot, e.g.:\n"
        "  export DISCORD_BOT_TOKEN=your_token_here   (Linux/Mac)\n"
        "  set DISCORD_BOT_TOKEN=your_token_here       (Windows cmd)\n"
        "Or place it in a .env file and load it with python-dotenv."
    )

bot.run(BOT_TOKEN)

