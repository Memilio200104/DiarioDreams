import tkinter as tk
from tkinter import ttk, messagebox
import traceback
import os
import threading
import time
from front.login_view import LoginView
from front.dashboard_view import DashboardView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diario de Dreams")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.colors = {
            "bg_top": "#1C1F3B",
            "text_color": "#F2F6FF",
            "accent": "#4D4D80"
        }

        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure("TLabel", foreground=self.colors["text_color"], background=self.colors["bg_top"], font=('Times New Roman', 12))
        style.configure("TButton", foreground=self.colors["text_color"], font=('Times New Roman', 11, 'bold'))
        style.configure("TEntry", fieldbackground="#2B2F4A", foreground=self.colors["text_color"])
        style.map("TButton", background=[("active", self.colors["accent"])])
        
        style.configure("Treeview.Heading", 
                        font=('Times New Roman', 12, 'bold'),
                        foreground=self.colors["text_color"],  
                        background="#3C3F68")                 

        style.configure("Treeview", 
                        background="#282C4D",                  
                        fieldbackground="#282C4D",              
                        foreground=self.colors["text_color"],   
                        rowheight=25)                          
        
        style.map('Treeview', 
                  background=[('selected', self.colors["accent"])], 
                  foreground=[('selected', 'white')])

        self.withdraw()
        self.current_view = None

        try:
            self._open_login_and_ensure_dashboard()
        except Exception as e:
            messagebox.showerror("Error Fatal de Inicialización", f"Error al iniciar el login o dashboard: {e}")
            self.quit()

    def _open_login_and_ensure_dashboard(self):
        self.login_window = LoginView(self)
        self.wait_window(self.login_window) 
        if self.current_view is None:
            try:
                self.deiconify()
            except Exception:
                pass

    def show_dashboard(self):
        if self.current_view:
            try:
                self.deiconify()
            except Exception:
                pass
            return

        try:
            self.deiconify()
            self.current_view = DashboardView(self)
        except Exception:
            tb = traceback.format_exc()
            print("Error en show_dashboard():\n", tb)
            try:
                messagebox.showerror("Error", "No se pudo abrir el dashboard. Mira la consola para más info.")
            except Exception:
                pass
            try:
                self.deiconify()
            except Exception:
                pass

if __name__ == "__main__":
    # Cambiar aquí pal debug con logs de errores
    # os.environ.setdefault("DREAMS_APP", "1")
    app = App()
    app.mainloop()