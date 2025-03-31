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
            user='insiders',
            password='1234'
        )
        if conn.is_connected():
            print('Connected to MySQL server')

        # Create the database if it doesn't exist
        create_database(conn)

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return conn

def create_database(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS personal_expense_tracker;")
        cursor.execute("USE personal_expense_tracker;")
        print("Database 'personal_expense_tracker' created or already exists.")
    except Error as e:
        print(f"Error while creating database: {e}")

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

    if expenses:
        table = PrettyTable()
        table.field_names = ["Category", "Amount", "Date", "Description", "Payment Method"]
        for expense in expenses:
            table.add_row(expense)
        print(table)

        # Calculate total expenses for the month
        total_expenses = sum(Decimal(expense[1]) for expense in expenses)
        print(f"\nTotal Expenses for {year_month}: {total_expenses} RWF")

        # Check budget status
        cursor.execute("SELECT budget FROM users WHERE user_id = %s", (user_id,))
        budget = cursor.fetchone()[0]
        remaining_budget = budget - total_expenses

        print("\nBudget Status:")
        if remaining_budget <= 0:
            print("Warning: You have no money left!")
        elif remaining_budget < (budget * Decimal('0.1')):
            print("Alert: You are about to finish your budget.")
        else:
            print("You are within your budget.")

    else:
        print("No expenses found for the specified month.")

class BudgetManager:
    def __init__(self, budget):
        """Initialize the budget and create an empty list for expenses."""
        self.budget = Decimal(budget)  # Total budget in Rwandan Francs (RWF)
        self.expenses = []  # List to store expense records

    def add_expense_local(self, amount, category, description=""):
        """Adds a new expense to the expense list and checks the budget."""
        if amount <= 0:
            print("Invalid amount. Expense should be greater than zero.")
            return

        # Append expense details as a dictionary to the expenses list
        self.expenses.append({"amount": Decimal(amount), "category": category, "description": description})
        self.check_budget()

    def get_total_expense(self):
        """Calculates and returns the total money spent."""
        return sum(Decimal(expense['amount']) for expense in self.expenses)

    def get_remaining_budget(self):
        """Calculates and returns the remaining budget."""
        return self.budget - self.get_total_expense()

    def check_budget(self):
        """Checks if the user is approaching or exceeding their budget."""
        total_spent = self.get_total_expense()
        remaining = self.get_remaining_budget()

        print(f"Total Spent: {total_spent} RWF | Remaining Budget: {remaining} RWF")

        # Notify the user if they have exceeded or are close to exceeding their budget
        if remaining <= 0:
            print("Warning: You have no money left!")
        elif remaining < (self.budget * Decimal('0.1')):
            print("Alert: You are about to finish your budget.")

    def save_data(self, filename="budget_data.json"):
        """Saves the budget and expense data to a JSON file."""
        data = {
            "budget": float(self.budget),  # Convert Decimal to float
            "expenses": [
                {"amount": float(expense['amount']), "category": expense['category'], "description": expense['description']}
                for expense in self.expenses
            ]
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print("Data saved successfully.")

    def load_data(self, filename="budget_data.json"):
        """Loads budget and expense data from a JSON file."""
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                self.budget = Decimal(data["budget"])  # Retrieve budget value
                self.expenses = [
                    {"amount": Decimal(str(expense['amount'])), "category": expense['category'], "description": expense['description']}
                    for expense in data["expenses"]
                ]  # Retrieve list of expenses
                print("Data loaded successfully.")
        except FileNotFoundError:
            print("No saved data found.")

def display_menu(language):
    if language == "en":
        return """
        Options:
        1. Log Expense
        2. View Expenses
        3. Monthly Report
        4. Check Budget
        5. Change Password
        6. Change Language
        7. Save & Exit
        0. Go Back
        00. Main Menu
        """
    elif language == "rw":
        return """
        Amahitamo:
        1. Kwandika ibyakoreshejwe
        2. Reba amafaranga yakoreshejwe
        3. Raporo ya buri kwezi
        4. Reba ingengo yimari
        5. Hindura Ijambo Banga
        6. Hindura Ururimi
        7. Gusohoka
        0. Subira Inyuma
        00. Ahabanza
        """
    elif language == "fr":
        return """
        Options:
        1. Enregistrer une dépense
        2. Voir les dépenses
        3. Rapport mensuel
        4. Vérifier le budget
        5. Changer le mot de passe
        6. Changer de langue
        7. Sauvegarder & Quitter
        0. Retour
        00. Menu Principal
        """

def display_login_menu(language):
    if language == "en":
        return """
        Options:
        1. Register
        2. Log In
        3. Exit
        """
    elif language == "rw":
        return """
        Ibyiciro:
        1. Kwiyandikisha
        2. Kwinjira
        3. Sohoka
        """
    elif language == "fr":
        return """
        Options:
        1. S'inscrire
        2. Se connecter
        3. Quitter
        """

def display_language_options(language):
    options = []
    if language != "en":
        options.append("1. English")
    if language != "rw":
        options.append("2. Kinyarwanda")
    if language != "fr":
        options.append("3. Français")
    return "\n".join(options)

def main():
    conn = create_conn()
    if conn is not None:
        # Create tables if they don't exist
        create_tables(conn)

        language = "en"
        logged_in = False
        user_id = None
        manager = None
        username = None

        print("\n********************************************************")
        print("*        Welcome to the Personal Expense Tracker!    *")
        print("********************************************************\n")

        while True:
            if not logged_in:
                print(display_login_menu(language))
                choice = input("Choose an option: ")

                if choice == '1':
                    username = input("Enter username: ")
                    email = input("Enter email: ")
                    password = getpass.getpass("Enter password: ")
                    budget = float(input("Enter your budget (RWF): "))
                    add_user(conn, username, email, password, budget)

                elif choice == '2':
                    username = input("Enter your username to log in: ")
                    password = getpass.getpass("Enter your password: ")
                    result = user_exists(conn, username, password)
                    if result:
                        user_id, username, budget = result
                        if budget == 0:
                            
                            budget = float(input("Enter your budget (RWF): "))
                            save_budget(conn, user_id, budget)
                        logged_in = True
                        print("\n********************************************************")
                        print(f"*                Welcome, {username}!                 *")
                        print("********************************************************\n")
                        manager = BudgetManager(budget)  # Create an instance of BudgetManager
                    else:
                        print("Invalid username or password. Please try again.")

                elif choice == '3':
                    print("Exiting the application.")
                    break

                else:
                    print("Invalid option. Please try again.")
            else:
                print(display_menu(language))
                choice = input("Choose an option: ")

                if choice == '1':
                    category = input("Enter expense category: ")
                    amount = Decimal(input("Enter amount: "))
                    date = input("Enter date (YYYY-MM-DD): ")
                    description = input("Enter description: ")
                    payment_method = input("Enter payment method: ")
                    add_expense(conn, user_id, category, amount, date, description, payment_method)
                    manager.add_expense_local(amount, category, description)

                elif choice == '2':
                    get_expenses(conn, user_id)

                elif choice == '3':
                    year_month = input("Enter year and month (YYYY-MM): ")
                    get_monthly_report(conn, user_id, year_month)

                elif choice == '4':
                    print(f"Remaining Budget: {manager.get_remaining_budget()} RWF")

                elif choice == '5':
                    new_password = getpass.getpass("Enter new password: ")
                    change_password(conn, user_id, new_password)

                elif choice == '6':
                    print("Choose a language:")
                    print(display_language_options(language))
                    lang_choice = input("Enter your choice: ")
                    if lang_choice == '1':
                        language = "en"
                    elif lang_choice == '2':
                        language = "rw"
                    elif lang_choice == '3':
                        language = "fr"
                    else:
                        print("Invalid choice. Language remains unchanged.")
                    print(f"Language changed to {'English' if language == 'en' else 'Kinyarwanda' if language == 'rw' else 'Français'}.")

                elif choice == '7':
                    save_budget(conn, user_id, manager.budget)
                    manager.save_data()
                    logged_in = False
                    user_id = None
                    print("Logged out successfully.")

                elif choice == '0':
                    # Go back to the previous menu or action
                    print("Going back to the previous menu.")
                    continue

                elif choice == '00':
                    # Return to the main menu
                    logged_in = False
                    print("Returning to the main menu.")

                else:
                    print("Invalid option. Please try again.")

        conn.close()

if __name__ == "__main__":
    main()
