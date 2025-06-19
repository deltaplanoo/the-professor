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

  if (message.content.startswith('!redeem') or
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
    await message.reply(
'''
Here are the available commands:
- `!redeem` - Redeem your coins (aliases: `!claim`)
- `!balance` - Check your balance
- `!gamble <amount>` - Gamble your coins (aliases: `!bet`, `!roll`)
- `!send @receiver <amount>` - Send coins to another user
- `!help` - Show this message
''')

  if (message.content.startswith('!gamble') or
    message.content.startswith('!bet') or
    message.content.startswith('!roll')):
    await logic.gamble(message)

  if "69" in message.content and not message.content.startswith("http"):
    await message.add_reaction('😍')

  if message.content.startswith('!buy'):
    await logic.buy(message)

  #if message.content.startswith('!give'):
  #  await logic.give(message)

  if "forestapp.cc/join-room?token=" in message.content:
    await logic.forest(message)

  if message.content.startswith('!send'):
    await logic.send(message)