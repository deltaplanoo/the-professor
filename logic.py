import dao
from datetime import datetime
import math, discord, random, re

daily_coins = 50

async def register(username, message):
  user_id = dao.get_user_id(username)
  if user_id is None:
    user_id = dao.insert_user(username)
    await message.channel.send(f'Welcome to the game {message.author.mention}!')
    await message.channel.send("Don't forget to redeem your daily coins with !redeem. Take a look at the commands with !help.")
    return True

async def redeem(username, message):
  balance = dao.get_user_balance(username)
  if isinstance(balance, int):
    balance += daily_coins
    dao.set_user_balance(username, balance)
    await message.channel.send(f'{message.author.mention} you received your daily coins! Your new balance is {balance}.')
    dao.set_last_redeem(username, datetime.now().isoformat())
    return True

async def redeem_eligibility(username, message) -> bool:
  last_redeem = dao.get_last_redeem(username)
  if last_redeem is None:
    return True
  else:
    elapsed_time = datetime.now() - datetime.fromisoformat(last_redeem)
    print(elapsed_time.total_seconds())
    if elapsed_time.total_seconds() >= 24 * 60 * 60:  # elapsed >= 24h -> redeem
      return True
    else:
      remaining = (24 * 60 * 60 - elapsed_time.total_seconds()) / 60
      if remaining > 60:
        remaining = remaining / 60
        await message.channel.send(f'{message.author.mention} you have already redeemed your daily coins today. Please try again in {math.floor(remaining)} hours.')
        return False
      else:
        await message.channel.send(f'{message.author.mention} you have already redeemed your daily coins today. Please try again in {math.floor(remaining)} minutes.')
        return False

async def check_balance(username, message):
  balance = dao.get_user_balance(username)
  if isinstance(balance, int):
    await message.channel.send(f'{message.author.mention} your balance is {balance}.')
  else:
    await register(username, message)

async def gamble(message):
  username = message.author.name
  balance = dao.get_user_balance(username)
  amount = re.findall(r'\d+', message.content)
  try:
    amount = int(amount[0])
    if balance is None:
      await message.channel.send(f"{message.author.mention} chill lil bro, you're not even registered yet... But dw, I'll do that for you.")
      await register(username, message)
    elif balance < amount:
      await message.channel.send(f"{message.author.mention} you're broke af, go redeem some coins with !redeem.")
    elif balance >= amount:
      multiplier = random.randrange(0, 2) * 2 
      if multiplier==0:
        await message.channel.send(f"{message.author.mention} you lost {amount} coins! 😭")
        dao.set_user_balance(username, balance - amount)
      else:
        await message.channel.send(f"{message.author.mention} you won {amount*2} coins! 💸")
        dao.set_user_balance(username, balance + amount)
  except IndexError as e:
    await message.channel.send(f"{message.author.mention} you need to specify an amount to gamble.")

async def give(message):
  username = message.author.name
  balance = dao.get_user_balance(username)
  amount = re.findall(r'\d+', message.content)
  try:
    amount = int(amount[0])
    dao.set_user_balance(username, balance + amount)
    await message.channel.send(f"{message.author.mention} you received {amount}, your balance now is {balance + amount}.")
  except IndexError as e:
    await message.channel.send(f"{message.author.mention} you need to specify an amount to give.")

async def buy(message):
  balance = dao.get_user_balance(message.author.name)
  # TODO: add coins' logic here
  # TODO: add random pick loigc here
  cardname = "Card Name"
  rarity = "Rarity"
  embed = discord.Embed(title=cardname, description="Rarity: rarity", colour=discord.Colour.default())
  # embed.add_field(name="", value="")
  # embed.timestamp = datetime.utcnow()
  # embed.set_footer(text=f"")
  embed.set_image(url="https://cardotaku.com/cdn/shop/files/ex-card-4.png")
  await message.reply(embed=embed)

