import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class LoginView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Iniciar Sesión")
        self.configure(bg="#F5F5DC")
        
        '''ToDo -Emix
         En Tkinter puro, puedes usar tk.Label y tk.Button y configurarlos
         O usar ttk.Label y ttk.Button y aprovechar el estilo global.
        '''
        
        tk.Label(self, text="Diario de Sueños", 
                 bg="#36454F", 
                 fg="white", 
                 font=('Times New Roman', 
                       18, 'bold'), 
                 padx=20, 
                 pady=10).grid(
                     row=0, 
                     column=0, 
                     columnspan=2, 
                     pady=(0, 20), 
                     sticky="ew")

        self.label_user = ttk.Label(self, text="Usuario:")
        self.entry_user = ttk.Entry(self)
        self.label_pass = ttk.Label(self, text="Contraseña:")
        self.entry_pass = ttk.Entry(self, show="*") 
        
        self.btn_login = ttk.Button(self, text="Iniciar Sesión", command=self.attempt_login) 

        
        self.label_user.grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.entry_user.grid(row=1, column=1, padx=15, pady=8)
        self.label_pass.grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.entry_pass.grid(row=2, column=1, padx=15, pady=8)
        self.btn_login.grid(row=3, column=0, columnspan=2, pady=20)
        
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.parent = parent
        self.successful_login = False
        
    def attempt_login(self):
        
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if username == "admin" and password == "123":
            messagebox.showinfo("Éxito", "Sesión iniciada correctamente.")
            self.successful_login = True
            self.destroy() 
            self.parent.show_dashboard() 
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
    def destroy(self):
        if self.successful_login:
            self.parent.show_dashboard() 
            
        super().destroy()