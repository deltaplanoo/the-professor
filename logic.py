import dao, os
from datetime import datetime
import math, discord, random, re, time, qrcode

# Constants
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
        await message.channel.send(f'{message.author.mention} you have already redeemed your daily coins today. Please try again in {math.floor(remaining)} h and {math.floor((remaining - math.floor(remaining))*60)} min.')
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
  start = time.perf_counter()
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
  end = time.perf_counter()
  elapsed = end - start
  print(f"{username}, !bet: {elapsed:.2f} sec")

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

# FIXME: ping forest role!!!.
async def forest(message):
  token = message.content.split("token=")[-1]
  if token:
    length, tree_name = extract_info(message.content)
    if length is None or tree_name is None:
      await message.reply(f"Invalid format. Please use the format: '...to plant a X-minute {tree_name} with me!'")
      return
    title = f"🌲 Forest session 🌲"
    embed = discord.Embed(title=title, description=f"Created by {message.author.mention}", colour=discord.Colour.green())
    url = f"https://www.forestapp.cc/join-room?token={token}"
    embed.url = url
    embed.set_thumbnail(url="https://www.forestapp.cc/img/icon.png")
    forest_role = message.guild.get_role(1366696611216097281)
    
    embed.add_field(name="🌲Tree", value=tree_name)
    embed.add_field(name="⏳Time", value=f"{length} minutes")
    embed.add_field(name="🔑Token", value=f"`{token}`")
    
    img = qrcode.make(url)
    img = img.resize((150, 150))
    
    img.save(f"{token}.png", format="PNG")
    file = discord.File(f"{token}.png", filename=f"{token}.png")
    #FIXME: delete image after session starts

    await message.delete()
    await message.channel.send(f"New {forest_role.mention} session available! Join now!", file=file)
    sent_message = await message.channel.send(embed=embed)
    await sent_message.add_reaction('🌲')
    os.remove(f"{token}.png")


  else:
    await message.reply(f"The token you provided is invalid. Please provide a valid token.")

async def send(message):
  sender = message.author.name
  sender_balance = dao.get_user_balance(sender)
  #parse the command: !send @receiver <amount>
  parts = message.content.split()
  
  if len(parts) != 3:
    await message.reply("Usage: `!send @receiver <amount>`")
    return

  command, receiver_mention, amount_str = parts

  # 2. Validate receiver mention
  # check if mentioned user is already registered
  if len(message.mentions) == 0:
    await message.reply("You need to mention a user to send coins to, like this -> `!send @receiver <amount>`")
    return
  receiver = message.mentions[0].name
  if sender == receiver:
    await message.reply("You cannot send coins to yourself dumbass!")
    return
  receiver_balance = dao.get_user_balance(receiver)
  if receiver_balance is None:
    await message.reply(f"That bitch is not registered yet. Please ask them to register by redeeming their first coins with `!redeem`.")
    return
  
  # 3. Validate amount
  try:
    amount = int(amount_str)
    if amount <= 0:
      await message.reply("Amount must be a positive number.")
      return
  except ValueError:
    await message.reply("Invalid amount. Please provide a number.")
    return

  # 4. Check if sender has enough money
  if sender_balance < amount:
    await message.reply(f"You only have {sender_balance} coins, which is not enough to send {amount}.")
    return

  # 5. Perform the transfer
  # Decrement sender's balance
  dao.set_user_balance(sender, sender_balance - amount)
  dao.set_user_balance(receiver, receiver_balance + amount)
  
  # 6. Confirmation message
  await message.reply(f"You sent {amount} coins to {receiver_mention}. Yyour new balance is {sender_balance - amount}!")
