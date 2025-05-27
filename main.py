import commands
import dao
import asyncio
import json

with open('secrets.json') as f:
    data = json.load(f)
token = data["token"]

def main():
  """
  Main function to run the bot.
  """
  # Init db
  dao.create_users_table()
  
  commands.client.run(token)

if __name__ == "__main__":
  main()
