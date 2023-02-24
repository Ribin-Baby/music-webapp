import sqlite3

# Connect to the database (creates a new database if it doesn't exist)
# 1.
conn = sqlite3.connect('./db/user_pwd.db')

# Create a table
# 1. creating table 1
conn.execute('''CREATE TABLE user_uuid
                (username TEXT PRIMARY KEY NOT NULL,
                 uuid TEXT NOT NULL)''')

# 2. creating table 2
conn.execute('''CREATE TABLE uuid_pwd
                (uuid TEXT PRIMARY KEY NOT NULL,
                 pwd TEXT NOT NULL)''')

conn.close()
print("created DB succesfully")