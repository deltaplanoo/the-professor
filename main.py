import commands
import dao
import json

with open('secrets.json') as f:
    data = json.load(f)
token = data["token"]

def main():
  """
  Main function to run the bot.
  """
  # Init DBs
  dao.create_users_table()
  dao.create_cards_table()

  commands.client.run(token)

if __name__ == "__main__":
  main()
