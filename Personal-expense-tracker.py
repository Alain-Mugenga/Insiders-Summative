import json
import mysql.connector
from mysql.connector import Error
from prettytable import PrettyTable
import getpass
from datetime import datetime
from decimal import Decimal

# Function to create a connection to the MySQL database
def create_conn():
    conn = None
    try:
        conn = mysql.connector.connect(
            host='01e489f6c6f8.1009380b.alu-cod.online',
            port='37443',
            database='sample',
            user='attorney',
            password='1234'
    )
    if conn.is_connected():
        print('Connected to MySQL database')
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return conn

def create_tables(connection):
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        budget BIGINT DEFAULT 0
    );
    """
    
    create_expenses_table = """
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        category VARCHAR(50),
        amount INT(100),
        date DATE,
        description TEXT,
        payment_method VARCHAR(50),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """

    cursor = connection.cursor()
    cursor.execute(create_users_table)
    cursor.execute(create_expenses_table)
    connection.commit()

    # Add the budget column if it doesn't exist
    add_budget_column_if_not_exists(connection)

def add_budget_column_if_not_exists(connection):
    cursor = connection.cursor()
    # This is the statement to Check if the budget column exists
    cursor.execute("SHOW COLUMNS FROM users LIKE 'budget';")
    result = cursor.fetchone()
    if not result:
        # Add the budget column if it does not exist
        cursor.execute("ALTER TABLE users ADD COLUMN budget BIGINT DEFAULT 0;")
        connection.commit()
