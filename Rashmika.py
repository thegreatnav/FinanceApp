import json
import os
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

class MoneyManager:
    def __init__(self, filename='transactions.json'):
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

    def add_transaction(self, description, amount):
        transaction = {'description': description, 'amount': amount}
        self.transactions.append(transaction)
        self.save_transactions()

    def view_balance(self):
        balance = sum(transaction['amount'] for transaction in self.transactions)
        return balance

    def view_transactions(self):
        return self.transactions

class MoneyManagerApp:
    def __init__(self, root):
        self.manager = MoneyManager()
        self.root = root
        self.login_page()  # Show the login page initially
        self.login_attempts = 0  # Counter for login attempts

    def login_page(self):
        self.root.title("Login - Personal Money Management App")
        self.root.geometry("400x200")
        self.root.configure(background='navy blue')

        label_username = Label(self.root, text="Username:")
        label_username.pack()

        self.entry_username = Entry(self.root)
        self.entry_username.pack()

        label_password = Label(self.root, text="Password:")
        label_password.pack()

        self.entry_password = Entry(self.root, show="*")
        self.entry_password.pack()

        button_login = Button(self.root, text="Login", command=self.validate_login)
        button_login.pack()

        button_register = Button(self.root, text="Register", command=self.register)
        button_register.pack()

    def create_widgets(self):
        self.label_description = Label(self.root, text="Description:")
        self.label_description.pack()

        self.entry_description = Entry(self.root)
        self.entry_description.pack()

        self.label_amount = Label(self.root, text="Amount:")
        self.label_amount.pack()

        self.entry_amount = Entry(self.root)
        self.entry_amount.pack()

        self.button_add = Button(self.root, text="Add Transaction", command=self.add_transaction)
        self.button_add.pack()

        self.button_balance = Button(self.root, text="View Balance", command=self.view_balance)
        self.button_balance.pack()

        self.button_transactions = Button(self.root, text="View Transactions", command=self.view_transactions)
        self.button_transactions.pack()

        self.button_exit = Button(self.root, text="Exit", command=self.root.destroy)
        self.button_exit.pack()

    def register(self):
        new_username = simpledialog.askstring("Register", "Enter a new username:")
        new_password = simpledialog.askstring("Register", "Enter a new password:")
        
        if new_username and new_password:
            user_data = {
                "username": new_username,
                "password": new_password
            }
            with open("user_data.json", "w") as file:
                json.dump(user_data, file)
        else:
            messagebox.showerror("Registration Failed", "Please enter both username and password.")

    def validate_login(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()
        
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
            
        if entered_username == user_data.get("username") and entered_password == user_data.get("password"):
            self.root.title("Personal Money Management App")
            self.root.geometry("600x400")
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_widgets()
        else:
            self.login_attempts += 1
            if self.login_attempts < 3:
                messagebox.showerror("Login Failed", f"Invalid username or password. You have {3 - self.login_attempts} attempts left.")
                # Clear the username and password fields
                self.entry_username.delete(0, END)
                self.entry_password.delete(0, END)
            else:
                messagebox.showerror("Login Failed", "You have reached the maximum number of login attempts.")
                self.root.destroy()

    def add_transaction(self):
        description = self.entry_description.get()
        amount = float(self.entry_amount.get())

        if description and amount:
            self.manager.add_transaction(description, amount)
            messagebox.showinfo("Success", "Transaction added successfully!")
        else:
            messagebox.showerror("Error", "Please enter both description and amount.")

    def view_balance(self):
        balance = self.manager.view_balance()
        messagebox.showinfo("Balance", f"Your current balance: ${balance:.2f}")

    def view_transactions(self):
        transactions = self.manager.view_transactions()

        if transactions:
            transaction_text = "\n".join(
                [f"{transaction['description']}: ${transaction['amount']:.2f}" for transaction in transactions])
            messagebox.showinfo("Transaction History", transaction_text)
        else:
            messagebox.showinfo("Transaction History", "No transactions yet")

if __name__ == "__main__":
    root = Tk()
    app = MoneyManagerApp(root)
    root.mainloop()
