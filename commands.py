from typing import Optional
import logic
import discord

daily_coins = 50

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if (message.content.startswith('!daily') or
      message.content.startswith('!redeem') or
      message.content.startswith('!claim')):
    username = message.author.name
    await logic.register(username, message)
    eligible = await logic.redeem_eligibility(username, message)
    if eligible:
      await logic.redeem(username, message)

  if message.content.startswith('!balance'):
    username = message.author.name
    await logic.check_balance(username, message)
  
  if message.content.startswith('!help'):
    await message.channel.send(
'''
- `!daily` - Redeem your daily coins (aliases: `!redeem`)
- `!balance` - Check your balance
- `!help` - Show this message
- `!gamble <amount>` - Gamble your coins (aliases: `!bet`, `!roll`)
''')

  if (message.content.startswith('!gamble') or
    message.content.startswith('!bet') or
    message.content.startswith('!roll')):
    await logic.gamble(message)

  if "69" in message.content and message.channel == "🔢-counting" and not message.content.startswith("http"):
    await message.add_reaction('😍')

  if message.content.startswith('!buy'):
    await logic.buy(message)

  if message.content.startswith('!give'):
    await logic.give(message)
