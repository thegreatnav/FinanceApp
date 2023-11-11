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