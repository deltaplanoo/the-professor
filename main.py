import commands
import dao
import asyncio

def main():
  """
  Main function to run the bot.
  """
  # Init db
  dao.create_users_table()
  
  token = "MTM3Mjk5NzgwNDE3MTE5ODYxNQ.Gd47q0.Ic7YIIRHAfVpfwcT5qM0RCeM1lDex3hT0lmGqs"
  commands.client.run(token)

if __name__ == "__main__":
  main()
