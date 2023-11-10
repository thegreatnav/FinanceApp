from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
import matplotlib.pyplot as plt

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
            return []

    def save_transactions(self):
        with open(self.filename, 'w') as file:
            json.dump(self.transactions, file)

    def add_transaction(self, description, amount, crdb):
        transaction = {'description': description, 'amount': amount, 'type': crdb}
        self.transactions.append(transaction)
        self.save_transactions()

    def view_balance(self):
        balance = sum(transaction['amount'] for transaction in self.transactions)
        return balance

    def view_transactions(self):
        return self.transactions

    def view_totalamountspent(self):
        sum = 0
        for transaction in self.transactions:
            if transaction['type'] == 'debit':
                sum = sum + transaction['amount']
        return sum

    def view_totalamountgained(self):
        sum = 0
        for transaction in self.transactions:
            if transaction['type'] == 'credit':
                sum = sum + transaction['amount']
        return sum

    def reset_database(self):
        with open(self.filename, 'w+') as file:
            self.transactions = []
            json.dump({}, file)

    def register_user(self, username, password):
        user_data = {'username': username, 'password': password}
        with open("user_data.json", "w+") as file:
            json.dump(user_data, file)

    def validate_login(self, entered_username, entered_password):
        file_path = os.path.join(os.path.dirname(__file__), "user_data.json")

        try:
            with open(file_path, "r") as file:
                user_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
        # Return False if the file doesn't exist or is empty
            return False

        return entered_username == user_data.get("username") and entered_password == user_data.get("password")



# Initialize the MoneyManager outside of the route functions
manager = MoneyManager()


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

@app.route('/', methods=['GET', 'POST'])
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
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/index')
def index():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    transactions = manager.view_transactions()
    if transactions:
        descriptions = [transaction['description'] for transaction in transactions]
        amounts = [transaction['amount'] for transaction in transactions]

        fig, ax = plt.subplots()
        ax.bar(descriptions, amounts)
        ax.set_xlabel('Transaction Descriptions')
        ax.set_ylabel('Amounts')
        ax.set_title('Transaction Data Visualization')
        plt.show()

    return render_template('dashboard.html')


@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        crdb = request.form['crdb']

        if description and amount:
            manager.add_transaction(description, amount, crdb)
            flash('Transaction added successfully!', 'success')
        else:
            flash('Please enter both description and amount.', 'error')

    return render_template('add_transaction.html')


@app.route('/view_balance')
def view_balance():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    balance = manager.view_balance()
    return render_template('view_balance.html', balance=balance)


@app.route('/view_transactions')
def view_transactions():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    transactions = manager.view_transactions()
    return render_template('view_transactions.html', transactions=transactions)

  # Use the relative path to the templates folder

@app.route('/new_page')
def another_page():
    return render_template('add_transaction.html')


if __name__ == '__main__':
    app.run(debug=True)
