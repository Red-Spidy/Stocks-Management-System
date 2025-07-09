import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Red_Spidy",
            database="Stock_Management"
        )
    except Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None