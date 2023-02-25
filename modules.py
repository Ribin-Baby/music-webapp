from uuid import uuid4
import sqlite3 as sql

def generate_uuid():
    unique_id = str(uuid4())
    return unique_id

# function to convert the seconds into readable format
def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

 # Create a specific current-user class/keeps log of user specific data
class Webuser():
    def __init__(self):
        self.uuid = ""
        self.username = ""
        self.myalbums = []

# SQL database manager code
class DB():
    def __init__(self, file):
        self.file = file
        
    def insert(self, table, data):
        # -> data = (username, uuid)
        # Connect to the database
        conn = sql.connect(self.file)
        
        no_p = len(data)
        value_space = "(" + "?" + ", ?"*(no_p - 1) + ")"
        # Insert a row into the table using string formatting
        query = f"INSERT INTO {table} VALUES {value_space}"
        conn.execute(query, (data))
        
        # Commit the changes to the database
        conn.commit()
        # Close the database connection
        conn.close()
    
    def read(self, table, data, many=False):
        # Connect to the database
        conn = sql.connect(self.file)
        
        if data and not many:
            # Retrieve a single row from the customers table
            query = "SELECT * FROM {} WHERE {} = ?".format(table, data[0])
            result = conn.execute(query, (data[1],)).fetchone()
        elif data and many:
            # Retrieve a single row from the customers table
            query = "SELECT * FROM {} WHERE {} = ?".format(table, data[0])
            result = conn.execute(query, (data[1],)).fetchall()
        if not data and many:
            query = "SELECT * FROM {}".format(table)
            result = conn.execute(query).fetchall()
        # print(result)  # prints the tuple containing the customer information
        
        # Close the database connection
        conn.close()
        return result
    
    def remove(self, table, data):
        # -> data = (column_name, row_value_to_delete)
        # Connect to the database
        conn = sql.connect(self.file)
        
        # Delete the rows
        query = "DELETE FROM {} WHERE {} = ?".format(table, data[0])
        conn.execute(query, (data[1],))
        
        # Commit the changes to the database
        conn.commit()
        # Close the database connection
        conn.close()
   
           
###--- TEST CODE ---###

# uuid = generate_uuid() # GENERATE - ID
# print(uuid)
# db = DB("./db/user_pwd.db") # LOAD
# db.insert("user_uuid", ("ribin", uuid)) # SAVE
# db.read("user_uuid", ("username", "ribin")) # READ
# db.remove("user_uuid", ("username", "ribin")) # DELETE