from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from itertools import groupby
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

class MoneyManager:

    def update_budget(self, username, new_budget):
        budget_data = self.load_budget_data()
        if username in budget_data:
            budget_data[username]['budget'] = new_budget
            self.save_budget_data(budget_data)
        else:
            budget_data[username] = {'budget': 0}
            self.save_budget_data(budget_data)

    def view_budget(self, username):
        budget_data = self.load_budget_data()
        if username in budget_data:
            return budget_data[username].get('budget')
        else:
            return 0
        
    def load_budget_data(self):
        budget_file = 'budgets.json'
        if os.path.exists(budget_file):
            with open(budget_file, 'r') as file:
                return json.load(file)
        else:
            return {}
        
    def save_budget_data(self, budget_data):
        budget_file = 'budgets.json'
        with open(budget_file, 'w') as file:
            json.dump(budget_data, file)
        
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

    def add_transaction(self, username, description, amount, crdb,category,date):
        if username not in self.transactions:
            self.transactions[username] = []
        date_string = date.strftime('%Y-%m-%d %H:%M:%S')
        transaction = {'description': description, 'amount': amount, 'type': crdb, 'category':category,'date':date_string}
        self.transactions[username].append(transaction)
        self.save_transactions()


    def view_total_expenditure(self,username):
        total_amt_spent=0
        if username in self.transactions:
            for transaction in self.transactions[username]:
                if 'type' in transaction and transaction['type']=='debit':
                    total_amt_spent=total_amt_spent+transaction['amount']
            return total_amt_spent
        else:
            return 0

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
        total_amt_gained=0
        if username in self.transactions:
            for transaction in self.transactions[username]:
                if 'type' in transaction and transaction['type']=='credit':
                    total_amt_gained=total_amt_gained+transaction['amount']
            return total_amt_gained
        else:
            return 0
       

    def reset_database(self):
        with open(self.filename, 'w') as file:
            self.transactions = {}
            json.dump({}, file)

    def register_user(self, username, password):
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as file:
                user_data = json.load(file)
        else:
            user_data = []
        for user_entry in user_data:
            if user_entry['username'] == username:
                flash('Username already exists. Please choose a different one.', 'error')
                return
        
        #hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user_entry = {'username': username, 'password': password}
        user_data.append(new_user_entry)
        with open("user_data.json", "w") as file:
            json.dump(user_data, file)
        flash('Registration successful! You can now log in.', 'success')

    def validate_login(self, entered_username, entered_password):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        for user_entry in user_data:
            #if user_entry.get("username") == entered_username and bcrypt.check_password_hash(user_entry.get("password"), entered_password):
            if user_entry.get("username") == entered_username and user_entry.get("password")==entered_password:
                return True
        return False
        
manager = MoneyManager()

def create_expenses_chart(balance, budget, username):
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#010408')  # Set the size and background color
    transactions = get_user_transactions(username)
    descriptions = [transaction['description'] for transaction in transactions if transaction['type'] == 'debit']
    amounts = [transaction['amount'] for transaction in transactions if transaction['type'] == 'debit']    
    explode = (0.1,) * len(amounts)  # Explode all slices slightly for emphasis    
    colors = plt.cm.Paired(range(len(descriptions)))  # Use a color map for variety    
    ax.pie(amounts, labels=descriptions, autopct='%1.1f%%', startangle=90, explode=explode, colors=colors, labeldistance=1.05, textprops={'color': 'white'})
    centre_circle = plt.Circle((0, 0), 0.70, fc='none')
    ax.add_patch(centre_circle)    
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Expenses Overview', fontsize=16, color='#ffffff')  # Set title color to white
    image_stream = BytesIO()
    fig.savefig(image_stream, format='png', bbox_inches='tight', transparent=True)  # Set transparent background
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
    ax.set_title('Income Overview')
    image_stream = BytesIO()
    fig.savefig(image_stream, format='png')
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')       
    return encoded_image

def create_budget_chart(balance, budget, username):

    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#010408')
    transactions = get_user_transactions(username)
    expenses = [transaction["amount"] for transaction in transactions if transaction.get("type") == "debit"]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)
    if budget-sum(expenses)>0:
        ax.pie([sum(expenses), budget - sum(expenses)], labels=["Spent", "Remaining"],
            autopct='%1.1f%%', startangle=90, colors=colors, explode=explode,
            wedgeprops=dict(width=0.4, edgecolor='black'),textprops={'color': 'white','fontsize':14,'fontweight':'bold'})
    else:
        ax.pie([10, 0], labels=["Spent", "Remaining"],
            autopct='%1.1f%%', startangle=90, colors=colors, explode=explode,
            wedgeprops=dict(width=0.4, edgecolor='black'),textprops={'color': 'white','fontsize':14,'fontweight':'bold'})
        if budget>0:
            ax.text(0, 0, "YOU'RE BROKE!", ha='center', va='center', fontsize=20, color='red')
        else:
            ax.text(0, 0, "Please set your expenditure!", ha='center', va='center', fontsize=16, color='white')
    centre_circle = plt.Circle((0, 0), 0.50, fc='none')
    ax.add_patch(centre_circle)
    ax.axis('equal')
    ax.set_title('Budget Overview', fontsize=16, color='#ffffff')

    image_stream = BytesIO()
    fig.savefig(image_stream, format='png', bbox_inches='tight', transparent=True)  # Set transparent background
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')
    return encoded_image


def get_user_transactions(username):
    with open('transactions2.json', 'r') as file:
        data = json.load(file)
        return data.get(username,[])

def create_overview_plots(balance,username):
    transactions = get_user_transactions(username)
    # Extracting expense, budget, and income data
    budget = manager.view_budget(session['username'])
    expenses = [transaction["amount"] for transaction in transactions if transaction.get("type") == "debit"]  # Replace with your actual budget value
    income = [transaction["amount"] for transaction in transactions if transaction.get("type") == "credit"]

    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), facecolor='none')  # Set the size and background color
    for ax in axs:
        for text in ax.get_xticklabels() + ax.get_yticklabels():
            text.set_color('#ffffff')

    # Plot Budget Overview
    axs[0].pie([sum(expenses), budget - sum(expenses)], labels=["Spent", "Remaining"], autopct='%1.1f%%', startangle=90, colors=['red', 'green'])
    axs[0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    axs[0].set_title('Budget Overview', fontsize=16, color='#ffffff')

    # Plot Expenses Overview
    descriptions1 = [transaction['description'] for transaction in transactions if transaction['type'] == 'debit']
    amounts1 = [transaction['amount'] for transaction in transactions if transaction['type'] == 'debit']
    axs[1].bar(descriptions1, amounts1, color='blue')  # Adjust color if needed
    axs[1].set_title('Expenses Overview', fontsize=16, color='#ffffff')

    # Plot Income Overview
    descriptions = [transaction['description'] for transaction in transactions if transaction['type'] == 'credit']
    amounts = [transaction['amount'] for transaction in transactions if transaction['type'] == 'credit']
    axs[2].bar(descriptions, amounts, color='green')  # Adjust color if needed
    axs[2].set_title('Income Overview', fontsize=16, color='#ffffff')

    for ax in axs:
        ax.title.set_color('#ffffff')  # Set title color to white
        ax.spines['bottom'].set_color('#ffffff')  # Set x-axis color to white
        ax.spines['top'].set_color('#ffffff')
        ax.spines['right'].set_color('#ffffff')
        ax.spines['left'].set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')  # Set y-axis label color to white
        ax.xaxis.label.set_color('#ffffff')

    plt.tight_layout(pad=3)  # Adjust the spacing between subplots

    image_stream = BytesIO()
    fig.savefig(image_stream, format='png', facecolor=fig.get_facecolor(), transparent=True)  # Set transparent background
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')
    return encoded_image

def string_to_datetime2(value):
    return datetime.strptime(value,'%Y-%m')

def string_to_datetime(value):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    pass

def format_datetime(value, format='%B %Y'):
    return value.strftime(format)

app.jinja_env.filters['string_to_datetime'] = string_to_datetime
app.jinja_env.filters['string_to_datetime2'] = string_to_datetime2
app.jinja_env.filters['strftime'] = format_datetime

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        if new_username and new_password:
            manager.register_user(new_username, new_password)
            return redirect(url_for('login'))
        else:
            flash('Please enter both username and password.', 'error')

    return render_template('register.html')

@app.route('/update_budget', methods=['POST'])
def update_budget():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_budget = float(request.form['monthly-budget'])
        manager.update_budget(session['username'], new_budget)

    return redirect(url_for('dashboard'))

@app.route('/visualization')
def visualization():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    balance = manager.view_total_expenditure(session['username'])
    chart_image = create_overview_plots(balance, session['username'])
    return render_template('visualization.html', chart_image=chart_image)

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']

        if 'register' in request.form:
            return render_template('register.html')
        else:
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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    budget = manager.view_budget(session['username'])   
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'update-budget' in request.form:
            new_budget = float(request.form['monthly-budget'])
            manager.update_budget(session['username'], new_budget)
            budget = manager.view_budget(session['username'])

    balance = manager.view_total_expenditure(session['username'])
    bal=budget-balance
    inc=manager.view_totalamountgained(session['username'])
    chart_image = create_budget_chart(balance, budget, session['username'])
    return render_template('dashboard.html', balance=balance, chart_image=chart_image, budget=budget,bal=bal,inc=inc)

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
        date_str=request.form.get('date')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD HH:MM:SS.', 'error')
            return redirect(url_for('add_transaction'))

        if category is not None and amount and crdb and date:
            manager.add_transaction(username, description, amount, crdb, category,date)
            flash('Transaction added successfully!', 'success')
        else:
            flash('Category is missing in the form data.', 'error')

    return render_template('add_transaction.html')


@app.route('/view_total_expenditure')
def view_total_expenditure():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    balance = manager.view_total_expenditure(session['username'])
    return render_template('dashboard.html', balance=balance)


@app.route('/view_transactions')
def view_transactions():
    if 'username' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    transactions = manager.view_transactions(session['username'])
    transactions_by_category = {}
    transactions_by_month={}
    transactions.sort(key=lambda x: x['category'])

    sort_option = request.args.get('sort_option', 'date')  # Default to sorting by date
    if sort_option == 'month':
        transactions.sort(key=lambda x: (int(x['date'].split('-')[0]), int(x['date'].split('-')[1])))
    elif sort_option == 'year':
        transactions.sort(key=lambda x: int(x['date'].split('-')[0]))
    elif sort_option == 'day':
        transactions.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'))

    for category, group in groupby(transactions, key=lambda x: x['category']):
        transactions_by_category[category] = list(group)
    for month,group in groupby(transactions,key=lambda x: x['date'][:7]):
            transactions_by_month[month] = list(group)
    return render_template('view_transactions.html', transactions_by_category=transactions_by_category,transactions_by_month=transactions_by_month,sort_option=sort_option)

if __name__ == '__main__':
    app.run(debug=True)
