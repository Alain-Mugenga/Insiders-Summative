Personal Expense Tracker

Overview

The Personal Expense Tracker is a command-line application designed to help users manage their expenses efficiently. It allows users to log expenses, view their spending history, generate monthly reports, and monitor their budget. The application supports multiple languages, including English, Kinyarwanda, and French.

Features

- User registration and login
- Log expenses with categories, amounts, dates, descriptions, and payment methods
- View a list of all logged expenses
- Generate monthly expense reports
- Monitor and update budget
- Change password
- Multi-language support (English, Kinyarwanda, French)

Prerequisites

- Python 3.x
- MySQL Server
- Virtual Environment (optional but recommended)

                                        Setup Instructions

1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone <repository-url>
cd Personal_expense-Tracker
```

2. Create a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies. Create and activate a virtual environment using the following commands:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install mysql-connector-python prettytable
```

4. Set Up the Database

Ensure your MySQL server is running. The application will automatically create the necessary database and tables if they don't exist. Update the database connection details in the `create_conn` function if needed.

5. Run the Application

Run the application using the following command:

```bash
python Insiders-Summative/Personal_expense-Tracker.py
```

Usage Instructions

1. Register or Log In

- When you first run the application, you will be prompted to register or log in.
- Follow the on-screen instructions to create a new user account or log in with existing credentials.

2. Main Menu

Once logged in, you will be presented with the main menu, which includes the following options:

- Log Expense: Enter details of a new expense, including category, amount, date, description, and payment method.
- View Expenses: Display a list of all logged expenses.
- Monthly Report: Generate a report of expenses for a specific month.
- Check Budget: View the remaining budget and check if you are within your spending limits.
- Change Password: Update your account password.
- Change Language: Switch the application language between English, Kinyarwanda, and French.
- Save & Exit: Save your data and log out of the application.

3. Navigating the Application

- Use the numeric options to navigate through the menus and perform actions.
- Follow the prompts to enter required information when logging expenses or generating reports.

Notes

- Ensure that your MySQL server is running and accessible with the provided credentials.
- The application uses a local JSON file to save and load budget data. Make sure the file is writable.
- For security reasons, avoid hardcoding sensitive information such as database passwords in your code. Consider using environment variables or configuration files.
