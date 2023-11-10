import json
import os
from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt

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

    def add_expenditure(self, description, amount):
        transaction = {'description': description, 'amount': amount, 'type':'debit'}
        self.transactions.append(transaction)
        self.save_transactions()
    
    def add_income(self, description, amount):
        transaction = {'description': description, 'amount': amount, 'type':'credit'}
        self.transactions.append(transaction)
        self.save_transactions()

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

    def view_transactions(self):
        return self.transactions
    
    def reset_database(self):
        with open(self.filename, 'w') as file:
            self.transactions=[]
            json.dump({}, file)
            
                

class MoneyManagerApp:

    def __init__(self, root):       
        self.manager = MoneyManager()
        self.root = root
        self.create_login_page()
        self.create_widgets()

    def create_login_page(self):        
        self.root.title("Personal Money Management App")
        screen_width=root.winfo_screenwidth()-50
        screen_height=root.winfo_screenheight()-100
        self.root.geometry(str(screen_width)+"x"+str(screen_height)) 
        self.root.configure(background='navy blue')
        icon=PhotoImage(file="C:/Users/91949/Documents/VisualStudio/Finance_App/piggy-bank.png")
        self.root.iconphoto(False,icon)

        frame_titlebar=Frame(root,background='black')
        frame_titlebar.pack(expand=False,fill=BOTH)

        heading=Label(frame_titlebar,text='Bill Blitzer',font=('Algerian',25),foreground='white',background='navy blue')
        heading.pack(expand=False,fill=BOTH)

    def create_widgets(self):        
        self.label_description = Label(self.root, text="Description:")
        self.label_description.pack()

        self.entry_description = Entry(self.root)
        self.entry_description.pack()

        self.label_amount = Label(self.root, text="Amount:")
        self.label_amount.pack()

        self.entry_amount = Entry(self.root)
        self.entry_amount.pack()

        self.button_add_income = Button(self.root, text="Add Income", command=self.add_income)
        self.button_add_income.pack()

        self.button_totalincome = Button(self.root, text="View Total Income", command=self.view_income)
        self.button_totalincome.pack()

        self.button_add_expenditure = Button(self.root, text="Add Expenditure", command=self.add_expenditure)
        self.button_add_expenditure.pack()

        self.button_totalexpenditure = Button(self.root, text="View Total Expenditure", command=self.view_expenditure)
        self.button_totalexpenditure.pack()

        self.button_transactions = Button(self.root, text="View Transactions", command=self.view_transactions)
        self.button_transactions.pack()

        self.button_exit = Button(self.root, text="Exit", command=self.root.destroy)
        self.button_exit.pack()

        self.button_visualize = Button(self.root, text="Visualize Data", command=self.visualize_data)
        self.button_visualize.pack()

        self.button_reset = Button(self.root, text="Reset Database", command=self.reset_database)
        self.button_reset.pack()

    def reset_database(self):
        result = messagebox.askokcancel("Reset Database", "Are you sure you want to reset the database?")
        if result:
            self.manager.reset_database()
            messagebox.showinfo("Database Reset", "Database has been reset.")
            
    def visualize_data(self):
        transactions = self.manager.view_transactions()

        if transactions:
            descriptions = [transaction['description'] for transaction in transactions]
            amounts = [transaction['amount'] for transaction in transactions]

            fig,ax = plt.subplots()
            ax.bar(descriptions, amounts)
            ax.set_xlabel('Transaction Descriptions')
            ax.set_ylabel('Amounts')
            ax.set_title('Transaction Data Visualization')
            plt.show()
        else:
            messagebox.showinfo("Visualization", "No transactions yet.")
    
    def add_expenditure(self):
        description = self.entry_description.get()
        amount = float(self.entry_amount.get())

        if description and amount:
            self.manager.add_expenditure(description, amount)
            messagebox.showinfo("Success", "Transaction added successfully!")
            
            self.entry_amount.delete(0,END)
        else:
            messagebox.showerror("Error", "Please enter both description and amount.")

    def add_income(self):
        description = self.entry_description.get()
        amount = float(self.entry_amount.get())

        if description and amount:
            self.manager.add_income(description, amount)
            messagebox.showinfo("Success", "Transaction added successfully!")
            self.entry_description.delete(0,END)
            self.entry_amount.delete(0,END)
        else:
            messagebox.showerror("Error", "Please enter both description and amount.")

    def view_expenditure(self):
        amt = self.manager.view_totalamountspent()
        messagebox.showinfo("Expenditure", f"You have spent in total : ₹{amt:.2f}")

    def view_income(self):
        amt=self.manager.view_totalamountgained()
        messagebox.showinfo("Income",f"You have gained in total : ₹{amt:.2f}")

    def view_transactions(self):
        transactions = self.manager.view_transactions()

        if transactions:
            transaction_text = "\n".join([f"{transaction['description']}: ({transaction['type']}) ₹{transaction['amount']:.2f}" for transaction in transactions])
            messagebox.showinfo("Transaction History", transaction_text)
        else:
            messagebox.showinfo("Transaction History", "No transactions yet.")

if __name__ == "__main__":
    root = Tk()
    app = MoneyManagerApp(root)
    root.mainloop()