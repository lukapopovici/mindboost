
# Password hashing logic (bcrypt via passlib)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend/sql_app.db'))

def list_tables_and_contents():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables in database:')
    for table in tables:
        table_name = table[0]
        print(f'\nTable: {table_name}')
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        # Get column names
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in cursor.fetchall()]
        print(' | '.join(columns))
        for row in rows:
            print(' | '.join(str(item) for item in row))
    conn.close()

def insert_data(table_name, data_dict):
    """
    Insert data into a table.
    Args:
        table_name (str): Name of the table.
        data_dict (dict): Dictionary of column-value pairs to insert.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?' for _ in data_dict])
    values = tuple(data_dict.values())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    print(f"Inserted into {table_name}: {data_dict}")

if __name__ == '__main__':
    # Insert test users with hashed passwords


    test_users = [
        {"email": "test1@example.com", "password": "password123"},
        {"email": "test2@example.com", "password": "letmein456"},
        {"email": "test3@example.com", "password": "qwerty789"}
    ]

    for user in test_users:
        hashed = get_password_hash(user["password"])
        data_dict = {
            "email": user["email"],
            "hashed_password": hashed,
            "is_active": 1
        }
        try:
            insert_data("users", data_dict)
            print(f"Inserted user: {user['email']} | password: {user['password']}")
        except Exception as e:
            print(f"Could not insert user {user['email']}: {e}")

    # Show contents after insert
    print("\nDatabase contents after inserting test users:")
    list_tables_and_contents()


