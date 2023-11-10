import tkinter as tk
from tkinter import messagebox
import json
import os
from tkinter import *

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

    def add_transaction(self, description, amount,crdb):
        
        transaction = {'description': description, 'amount': amount,'type':crdb}
        self.transactions.append(transaction)
        self.save_transactions()

    def view_balance(self):
        balance = sum(transaction['amount'] for transaction in self.transactions)
        return balance
    
    def view_transactions(self):
        return self.transactions

    def view_totalamountspent(self):
        sum=0
        for transaction in self.transactions:
            if transaction['type']=='debit':
                sum=sum+transaction['amount']
        return sum

    def view_totalamountgained(self):
        sum=0
        for transaction in self.transactions:
            if transaction['type']=='credit':
                sum=sum+transaction['amount']
        return sum

    def reset_database(self):
        with open(self.filename, 'w') as file:
            self.transactions=[]
            json.dump({}, file)

class MoneyManagerApp:

    def __init__(self, root):

        self.manager = MoneyManager()
        self.root = root
        self.root.title("Personal Money Management App")
        self.pages = {}
        self.current_page = None
        self.create_pages()
        self.show_page("MainPage")

    def create_pages(self):
        main_page = MainPage(self.root, self)
        add_transaction_page = AddTransactionPage(self.root, self)
        view_balance_page = ViewBalancePage(self.root, self)
        view_transactions_page = ViewTransactionsPage(self.root, self)

        self.pages["MainPage"] = main_page
        self.pages["AddTransactionPage"] = add_transaction_page
        self.pages["ViewBalancePage"] = view_balance_page
        self.pages["ViewTransactionsPage"] = view_transactions_page

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack()

class MainPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        label = Label(self, text="Welcome to the Money Manager App")
        label.pack(pady=10)

        add_transaction_button = Button(self, text="Add Transaction", command=lambda: controller.show_page("AddTransactionPage"))
        add_transaction_button.pack()

        view_balance_button = Button(self, text="View Balance", command=lambda: controller.show_page("ViewBalancePage"))
        view_balance_button.pack()

        view_transactions_button = Button(self, text="View Transactions", command=lambda: controller.show_page("ViewTransactionsPage"))
        view_transactions_button.pack()

class AddTransactionPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        label = Label(self, text="Add a Transaction")
        label.pack(pady=10)

        self.label_description = Label(self, text="Description:")
        self.label_description.pack()

        self.entry_description = Entry(self)
        self.entry_description.pack()

        self.label_amount = Label(self, text="Amount:")
        self.label_amount.pack()

        self.entry_amount = Entry(self)
        self.entry_amount.pack()

        self.button_addincome = Button(self, text="Add Income", command=lambda:self.add_transaction("credit"))
        self.button_addincome.pack()

        self.button_addexpense = Button(self, text="Add Expense", command=lambda:self.add_transaction("debit"))
        self.button_addexpense.pack()

        self.button_exit = Button(self, text="Exit", command=lambda:controller.show_page("MainPage"))
        self.button_exit.pack()

    def add_transaction(self,crdb):
        
        description = self.entry_description.get()
        amount = float(self.entry_amount.get())

        if description and amount:
            self.controller.manager.add_transaction(description, amount,crdb)
            messagebox.showinfo("Success", "Transaction added successfully!")
        else:
            messagebox.showerror("Error", "Please enter both description and amount.")
    
class ViewBalancePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        label = Label(self, text="View Balance")
        label.pack(pady=10)

        self.button_balance = Button(self, text="View Balance", command=self.view_balance)
        self.button_balance.pack()

        self.button_totalincome = Button(self, text="View Total Income", command=self.view_income)
        self.button_totalincome.pack()

        self.button_totalexpenditure = Button(self, text="View Total Expenditure", command=self.view_expenditure)
        self.button_totalexpenditure.pack()

        self.button_exit = Button(self, text="Exit", command=lambda:controller.show_page("MainPage"))
        self.button_exit.pack()
    
    def view_balance(self):
        balance = self.controller.manager.view_balance()
        messagebox.showinfo("Balance", f"Your current balance: ${balance:.2f}")

    def view_expenditure(self):
        amt = MoneyManager().view_totalamountspent()
        messagebox.showinfo("Expenditure", f"You have spent in total : ₹{amt:.2f}")

    def view_income(self):
        amt=MoneyManager().view_totalamountgained()
        messagebox.showinfo("Income",f"You have gained in total : ₹{amt:.2f}")

class ViewTransactionsPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        label = Label(self, text="View Transactions")
        label.pack(pady=10)

        self.button_transactions = Button(self, text="View Transactions", command=self.view_transactions)
        self.button_transactions.pack()

        self.button_exit = Button(self, text="Exit", command=lambda:controller.show_page("MainPage"))
        self.button_exit.pack()
    
    def view_transactions(self):
        transactions = self.controller.manager.view_transactions()

        if transactions:
            transaction_text = "\n".join([f"{transaction['description']}: ({transaction['type']}) ₹{transaction['amount']:.2f}" for transaction in transactions])
            messagebox.showinfo("Transaction History", transaction_text)
        else:
            messagebox.showinfo("Transaction History", "No transactions yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MoneyManagerApp(root)
    root.mainloop()