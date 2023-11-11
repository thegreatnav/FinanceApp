from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class MoneyManager:
    def __init__(self, filename='transactions2.json'):
        self.filename = filename
        self.transactions = self.load_transactions()

    def load_transactions(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_transactions(self):
        with open(self.filename, 'w') as file:
            json.dump(self.transactions, file)

    def add_transaction(self, username, description, amount, crdb,category):
        if username not in self.transactions:
            self.transactions[username] = []
        transaction = {'description': description, 'amount': amount, 'type': crdb, 'category':category}
        self.transactions[username].append(transaction)
        self.save_transactions()


    def view_balance(self,username):
        total_amt_spent=0
        if username in self.transactions:
            for transaction in self.transactions[username]:
                if 'type' in transaction and transaction['type']=='debit':
                    total_amt_spent=total_amt_spent+transaction['amount']
        return total_amt_spent

    def view_transactions(self, username):
        if username in self.transactions:
            return self.transactions[username]
        else:
            return []

    def view_totalamountspent(self,username):
        sum = 0
        for transaction in self.transactions[username]:
            if transaction['type'] == 'debit':
                sum = sum + transaction['amount']
        return sum

    def view_totalamountgained(self,username):
        sum = 0
        for transaction in self.transactions[username]:
            if transaction['type'] == 'credit':
                sum = sum + transaction['amount']
        return sum

    def reset_database(self):
        with open(self.filename, 'w') as file:
            self.transactions = {}
            json.dump({}, file)

    def register_user(self, username, password):
        # Load existing user data from the file
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as file:
                user_data = json.load(file)
        else:
            user_data = []

        # Check if the username already exists
        for user_entry in user_data:
            if user_entry['username'] == username:
                flash('Username already exists. Please choose a different one.', 'error')
                return

        # Add a new user entry to the user_data list
        new_user_entry = {'username': username, 'password': password}
        user_data.append(new_user_entry)

        # Write the updated user_data back to the file
        with open("user_data.json", "w") as file:
            json.dump(user_data, file)

        flash('Registration successful! You can now log in.', 'success')


    def validate_login(self, entered_username, entered_password):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        for user_entry in user_data:
            if user_entry.get("username") == entered_username and user_entry.get("password") == entered_password:
                return True

        return False

    
manager = MoneyManager()

def create_expenses_chart(balance, budget,username):
    fig, ax = Figure(), FigureCanvas(Figure())
    ax = fig.add_subplot(111)
    transactions = get_user_transactions(username)
    descriptions = [transaction['description'] for transaction in transactions if transaction['type']=='debit']
    amounts = [transaction['amount'] for transaction in transactions if transaction['type']=='debit']      
    ax.pie(amounts, labels=descriptions, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Expenses Overview')
    image_stream = BytesIO()
    fig.savefig(image_stream, format='png')
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')       
    return encoded_image

def create_income_chart(balance, budget,username):
    fig, ax = Figure(), FigureCanvas(Figure())
    ax = fig.add_subplot(111)
    transactions = get_user_transactions(username)
    descriptions = [transaction['description'] for transaction in transactions if transaction['type']=='credit']
    amounts = [transaction['amount'] for transaction in transactions if transaction['type']=='credit']      
    ax.pie(amounts, labels=descriptions, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title('Expenses Overview')
    image_stream = BytesIO()
    fig.savefig(image_stream, format='png')
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')       
    return encoded_image

def get_user_transactions(username):
    with open('transactions2.json', 'r') as file:
        data = json.load(file)
        return data.get(username,[])

def create_overview_plots(balance,budget,username):
    transactions = get_user_transactions(username)
    # Extracting expense, budget, and income data
    expenses = [transaction["amount"] for transaction in transactions if transaction.get("type") == "debit"]
    budget = 200000  # Replace with your actual budget value
    income = [transaction["amount"] for transaction in transactions if transaction.get("type") == "credit"]

    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Plot Expense Overview
    axs[0].pie([sum(expenses), budget - sum(expenses)], labels=["Spent", "Remaining"], autopct='%1.1f%%', startangle=90, colors=['red', 'green'])
    axs[0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    axs[0].set_title('Budget Overview')
    
    # Plot Expenses Overview
    descriptions1 = [transaction['description'] for transaction in transactions if transaction['type']=='debit']
    amounts1 = [transaction['amount'] for transaction in transactions if transaction['type']=='debit']
    axs[1].bar(descriptions1, amounts1)
    axs[1].set_title('Expenses Overview')

    # Plot Income Overview
    descriptions = [transaction['description'] for transaction in transactions if transaction['type']=='credit']
    amounts = [transaction['amount'] for transaction in transactions if transaction['type']=='credit']
    axs[2].bar(descriptions, amounts)
    axs[2].set_title('Income Overview')

    image_stream = BytesIO()
    fig.savefig(image_stream, format='png')
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')       
    return encoded_image

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        if new_username and new_password:
            manager.register_user(new_username, new_password)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Please enter both username and password.', 'error')

    return render_template('register.html')

@app.route('/visualization')
def visualization():
    budget = 50000
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    balance = manager.view_balance(session['username'])
    chart_image = create_overview_plots(balance, budget,session['username'])
    return render_template('visualization.html', chart_image=chart_image)

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']

        if 'register' in request.form:
            return render_template('register.html')
        else:
            # Login user
            if manager.validate_login(entered_username, entered_password):
                session['username'] = entered_username
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/')
def firstpage():
    return render_template('firstpage.html', redirect_url=url_for('login'))

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('loading.html')
    else:
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    budget = 1000
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))
    
    balance = manager.view_balance(session['username'])
    chart_image = create_overview_plots(balance, budget,session['username'])
    return render_template('dashboard.html', balance=balance, chart_image=chart_image)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username=session['username']
        description = request.form['description']
        amount = float(request.form['amount'])
        crdb = request.form['crdb']
        category = request.form.get('category')

        if category is not None and amount and crdb:
            # Your code to handle the category
            manager.add_transaction(username, description, amount, crdb, category)
            flash('Transaction added successfully!', 'success')
        else:
            flash('Category is missing in the form data.', 'error')

    return render_template('add_transaction.html')


@app.route('/view_balance')
def view_balance():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    balance = manager.view_balance(session['username'])
    return render_template('dashboard.html', balance=balance)


@app.route('/view_transactions')
def view_transactions():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    transactions = manager.view_transactions(session['username'])
    return render_template('view_transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)
