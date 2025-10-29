# main.py (MODIFICADO PARA PRUEBAS)

import tkinter as tk
from tkinter import ttk 
from front.login_view import LoginView
from front.dashboard_view import DashboardView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diario de Sueños Inteligente con I.A.")
        self.geometry("800x600")
        
        style = ttk.Style(self)
        style.theme_use('clam') 

        style.configure("TNotebook", background="#F5F5DC")
        style.configure("TNotebook.Tab", 
                        background="#E89153", 
                        foreground="white", 
                        font=('Times New Roman', 10, 'bold'))
        style.map("TNotebook.Tab", 
                  background=[("selected", "#36454F")]) 
        
        self.configure(bg="#F5F5DC") 
        
        style.configure("TButton", 
                        font=('Times New Roman', 10), 
                        foreground="#333333",
                        background="#FDB887", 
                        padding=5)
        
        style.configure("TLabel", 
                        background="#F5F5DC", 
                        foreground="#333333", 
                        font=('Times New Roman', 12))

        self.current_view = None
         #ToDO: Habilitar login posteriormente -Emix
        self.withdraw() 
        # self.show_login()
        self.show_dashboard() 

    def show_login(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
            
        login_window = LoginView(self)
        login_window.grab_set() 
        self.wait_window(login_window)

    def show_dashboard(self):
        if self.current_view:
            self.current_view.destroy()
        
        self.deiconify()
        self.current_view = DashboardView(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()