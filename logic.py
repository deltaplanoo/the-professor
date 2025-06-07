import dao, button
from datetime import datetime
import math, discord, random, re

redeem_coins = 50
threshold = 3 * 60 * 60  # 3 hours

def extract_info(text_string):
    """
    Extracts the length and tree name from a specific string format.
    Handles lengths that are 2 or 3 digits.

    Args:
        text_string (str): The input string in the format "to plant a XX-minute TreeName with me!".

    Returns:
        tuple: A tuple containing (length, tree_name).
               Returns (None, None) if the pattern is not found.
    """
    # Regex pattern to capture the number (2 or 3 digits) and the tree name
    # \s+                  : one or more whitespace characters
    # (\d{2,3})            : captures 2 or 3 digits (for the length)
    # -minute\s+           : matches "-minute" followed by one or more spaces
    # (.*?)                : captures any character non-greedily (the tree name)
    # \s*with me!          : matches " with me!"
    match = re.search(r'a\s+(\d{2,3})-minute\s+(.*?)\s*with me!', text_string)

    if match:
        length = int(match.group(1)) # Convert the captured digit string to an integer
        tree = match.group(2).strip() # Get the captured tree name and remove leading/trailing whitespace
        return length, tree
    else:
        return None, None

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
    balance += redeem_coins
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
    if elapsed_time.total_seconds() >= threshold:  # elapsed >= threshold -> redeem
      return True
    else:
      remaining = (threshold - elapsed_time.total_seconds()) / 60
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

# FIXME: ping forest role!!!
async def forest(message):
  token = message.content.split("token=")[-1]
  if token:
    length, tree_name = extract_info(message.content)
    if length is None or tree_name is None:
      await message.reply(f"Invalid format. Please use the format: '...to plant a X-minute {tree_name} with me!'")
      return
    title = f"🌲 Forest session 🌲"
    embed = discord.Embed(title=title, description=f"Created by {message.author.mention}", colour=discord.Colour.green())
    embed.url = f"https://www.forestapp.cc/join-room?token={token}"
    embed.set_thumbnail(url="https://www.forestapp.cc/img/icon.png")
    channel = message.channel
    forest_role = message.guild.get_role(1366696611216097281)
    
    embed.add_field(name="🌲Tree", value=tree_name)
    embed.add_field(name="⏳Time", value=f"{length} minutes")
    embed.add_field(name="🔑Token", value=f"`{token}`")

    initial_joined_count = 1
    embed.set_footer(text=f"Users in session: {initial_joined_count}")

    await message.delete()
    sent_message = await message.channel.send(embed=embed)
    view = button.ForestSessionView(initial_creator=message.author, session_message_id=sent_message.id)
    for item in view.children:
      if isinstance(item, discord.ui.Button) and item.custom_id.startswith("join_forest_session_"):
        item.callback = view.handle_join_button_click
        break
    await sent_message.edit(view=view)

  else:
    await message.reply(f"The token you provided is invalid. Please provide a valid token.")