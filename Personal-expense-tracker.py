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

def user_exists(connection, username, password):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, username, budget FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    return result if result else None

def add_user(connection, username, email, password, budget):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, email, password, budget) VALUES (%s, %s, %s, %s)",
                   (username, email, password, budget))
    connection.commit()
    print("User registered successfully! Please log in to access all services.")

def change_password(connection, user_id, new_password):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user_id))
    connection.commit()
    print("Password changed successfully!")

def save_budget(connection, user_id, budget):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET budget = %s WHERE user_id = %s", (budget, user_id))
    connection.commit()
    print("Budget saved successfully!")

def add_expense(connection, user_id, category, amount, date, description, payment_method):
    try:
        datetime.strptime(date, '%Y-%m-%d')

        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO expenses (user_id, category, amount, date, description, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, category, amount, date, description, payment_method))
        connection.commit()
        print("Expense logged successfully!")
    except ValueError:
        print("Invalid date format. Please enter the date in the format YYYY-MM-DD.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def get_expenses(connection, user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT category, amount, date, description, payment_method FROM expenses WHERE user_id = %s", (user_id,))
    expenses = cursor.fetchall()

    if expenses:
        table = PrettyTable()
        table.field_names = ["Category", "Amount", "Date", "Description", "Payment Method"]
        for expense in expenses:
            table.add_row(expense)
        print(table)
    else:
        print("No expenses found for the specified user.")

def get_monthly_report(connection, user_id, year_month):
    cursor = connection.cursor()
    query = """
    SELECT category, amount, date, description, payment_method FROM expenses
    WHERE user_id = %s AND DATE_FORMAT(date, '%Y-%m') = %s
    """
    cursor.execute(query, (user_id, year_month))
    expenses = cursor.fetchall()
