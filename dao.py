import sqlite3
import os
from typing import Optional


current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(current_dir, "users.db")

# Create the database and table (if they don't exist)
def create_users_table():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    coins INTEGER NOT NULL DEFAULT 0,
                    last_redeem DATETIME
                )
            """)
            conn.commit()
        print("Users table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating users table: {e}")

def create_cards_table():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    rarity INTEGER NOT NULL
                    path INTEGER NOT NULL UNIQUE,
                )
            """)
            conn.commit()
        print("Cards table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating cards table: {e}")


def insert_user(username: str, coins: int = 0) -> Optional[int]:
    """
    Inserts a new user into the 'users' table.

    Args:
        username (str): The username of the user.
        coins (int, optional): The initial coin balance of the user. Defaults to 0.

    Returns:
        Optional[int]: The ID of the newly inserted user, or None on error.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, coins)
                VALUES (?, ?)
            """, (username, coins))
            conn.commit()
            return cursor.lastrowid  # Return the ID of the newly inserted user
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        return None  # Return None to indicate failure

def get_user_id(username: str) -> Optional[int]:
    """
    Retrieves the ID of a user from the 'users' table.
    Args:
        username (str): The username of the user.
        Returns:
        Optional[int]: The ID of the user, or None if the user is not found or an error occurs.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id
                FROM users
                WHERE username = ?
            """, (username,))
            result = cursor.fetchone()  # Fetch a single result
            if result:
                return result[0]  # Return the user ID (the first element of the tuple)
            else:
                return None  # User not found
    except sqlite3.Error as e:
        print(f"Error retrieving user ID: {e}")
        return None

def set_last_redeem(username: str, last_redeem: str) -> bool:
    """
    Sets the last redeem time of a user in the 'users' table.
    Args:
        username (str): The username of the user.
        last_redeem (str): The new last redeem time of the user.
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET last_redeem = ?
                WHERE username = ?
            """, (last_redeem, username))
            conn.commit()
            return cursor.rowcount > 0  # Return True if at least one row was updated
    except sqlite3.Error as e:
        print(f"Error setting last redeem time: {e}")
        return False                    # Return False to indicate failure

def get_last_redeem(username: str) -> Optional[str]:
    """
    Retrieves the last redeem time of a user from the 'users' table.
    Args:
        username (str): The username of the user.
    Returns:
        Optional[str]: The last redeem time of the user, or None if the user is not found or an error occurs.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_redeem
                FROM users
                WHERE username = ?
            """, (username,))
            result = cursor.fetchone()  # Fetch a single result
            if result:
                return result[0]  # Return the last redeem time (the first element of the tuple)
            else:
                return None  # User not found
    except sqlite3.Error as e:
        print(f"Error retrieving last redeem time: {e}")
        return None

def get_user_balance(username: str) -> Optional[int]:
    """
    Retrieves the coin balance of a user from the 'users' table.

    Args:
        username (str): The username of the user.

    Returns:
        Optional[int]: The coin balance of the user, or None if the user is not found or an error occurs.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT coins
                FROM users
                WHERE username = ?
            """, (username,))
            result = cursor.fetchone()  # Fetch a single result
            if result:
                return result[0]  # Return the coin balance (the first element of the tuple)
            else:
                return None  # User not found
    except sqlite3.Error as e:
        print(f"Error retrieving user balance: {e}")
        return None  # Return None to indicate failure


def set_user_balance(username: str, coins: int) -> bool:
    """
    Sets the coin balance of a user in the 'users' table.
    Args:
        username (str): The username of the user.
        coins (int): The new coin balance of the user.
        Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET coins = ?
                WHERE username = ?
            """, (coins, username))
            conn.commit()
            return cursor.rowcount > 0  # Return True if at least one row was updated
    except sqlite3.Error as e:
        print(f"Error setting user balance: {e}")
        return False  # Return False to indicate failure


if __name__ == "__main__":
    create_users_table()

    # Example usage of insert_user:
    new_user_id = insert_user("TestUser", 100)
    if new_user_id:
        print(f"New user inserted with ID: {new_user_id}")
    else:
        print("Failed to insert new user.")
