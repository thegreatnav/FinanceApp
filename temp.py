from tkinter import messagebox
import json
import os
from tkinter import *
from PIL import Image

class MoneyManager:
    def __init__(self, file='transactions2.json'):
        self.filename = file
        self.transactions_arr = self.load_transactions()

    def load_transactions(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return []

    def save_transactions(self):
        with open(self.filename, 'w') as file:
            json.dump(self.transactions_arr, file)

    def add_transaction(self, description, amount, crdb):        
        transaction = {'description': description, 'amount': amount,'type':crdb}
        self.transactions_arr.append(transaction)
        self.save_transactions()
    
    def view_transactions(self):
        return self.transactions_arr

    def view_totalamountspent(self):
        sum=0
        for transaction in self.transactions_arr:
            if transaction['type']=='debit':
                sum=sum+transaction['amount']
        return sum

    def view_totalamountgained(self):
        sum=0
        for transaction in self.transactions_arr:
            if transaction['type']=='credit':
                sum=sum+transaction['amount']
        return sum

    def reset_database(self):
        with open(self.filename, 'w') as file:
            self.transactions_arr=[]
            json.dump({}, file)

class MoneyManagerApp:

    def __init__(self,root_param):
        self.manager_instance = MoneyManager()
        self.root = root_param
        screen_width=self.root.winfo_screenwidth()-200
        screen_height=self.root.winfo_screenheight()-300
        self.root.geometry(str(screen_width)+"x"+str(screen_height))
        self.root.title("Quiz Application")
        self.root.configure(background='#88c0fa')
        self.create_pages(self.root)
    
    def create_pages(self,root):
        self.create_main_page(root)
        self.create_add_transaction_page(root)
        self.create_view_balance_page(root)
        self.create_view_transactions_page(root)

    def create_main_page(self,root):
        main_page=Frame(root)
        main_page.pack()

        frame_titlebar=Frame(main_page)
        frame_titlebar.pack(expand=True,fill=BOTH)

        heading=Label(frame_titlebar,text='Bill Blitzer',font=('Algerian',25),foreground='white',bg='#88c0fa')
        heading.pack(side=LEFT,expand=False,fill=BOTH)

        img1=Image.open('C:\\Users\\91949\\Downloads\\Kaun_Banega_Crorepati.jpg')
        img1=img1.resize((100,100))
        img=PhotoImage(file=img1)
        logo=Label(frame_titlebar,image=img,background='navy blue')
        logo.pack(side=LEFT,expand=True,fill=BOTH)

    def create_add_transaction_page(self,root):
        add_transaction_page = Frame(root)
        add_transaction_page.pack()
    
    def create_view_balance_page(self,root):
        view_balance_page = Frame(root)
        view_balance_page.pack()

    def create_view_transactions_page(self,root):
        view_transactions_page = Frame(root)
        view_transactions_page.pack()

if __name__ == "__main__":
    root = Tk()
    app = MoneyManagerApp(root)
    root.mainloop()