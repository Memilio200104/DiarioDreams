import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import time
import threading

PALETA = {
    "espejismo": "#1C1F3B",
    "martinica": "#282C4D",
    "fjord": "#3C3F68",
    "bahi_aeste": "#4D4D80",
    "gris_medio": "#606271",
    "panel": "#0F1225"
}

def lerp_color(a_hex, b_hex, t: float):
    a = tuple(int(a_hex[i:i+2], 16) for i in (1,3,5))
    b = tuple(int(b_hex[i:i+2], 16) for i in (1,3,5))
    r = int(a[0] + (b[0]-a[0])*t)
    g = int(a[1] + (b[1]-a[1])*t)
    bb = int(a[2] + (b[2]-a[2])*t)
    return f"#{r:02x}{g:02x}{bb:02x}"

class LoginView(tk.Toplevel):
    MASTER_USER = "admin"
    MASTER_PASS = "dr3am$"

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login - Diario de Dreams")
        self.geometry("480x380")
        self.configure(bg=PALETA["espejismo"])
        self.resizable(False, False)
        self.grab_set()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480)//2
        y = (self.winfo_screenheight() - 380)//2
        self.geometry(f"+{x}+{y}")

        # Estos es pa el panel central
        panel = tk.Frame(self, bg=PALETA["panel"], bd=0)
        panel.place(relx=0.06, rely=0.08, relwidth=0.88, relheight=0.84)

        tk.Label(panel, text="Bienvenido a tu Diario de Dreams", font=('Times New Roman', 14, 'bold'),
                 bg=PALETA["panel"], fg=PALETA["bahi_aeste"]).pack(pady=(14,6))

        tk.Label(panel, text="Introduce tus credenciales", bg=PALETA["panel"], fg=PALETA["gris_medio"]).pack()

        frm = tk.Frame(panel, bg=PALETA["panel"])
        frm.pack(pady=18, padx=18, fill="x")

        tk.Label(frm, text="Usuario:", bg=PALETA["panel"], fg=PALETA["gris_medio"]).grid(row=0, column=0, sticky="w", pady=6)
        self.ent_user = ttk.Entry(frm, width=36)
        self.ent_user.grid(row=0, column=1, pady=6)
        self.ent_user.focus_set()

        tk.Label(frm, text="Contraseña:", bg=PALETA["panel"], fg=PALETA["gris_medio"]).grid(row=1, column=0, sticky="w", pady=6)
        self.ent_pass = ttk.Entry(frm, show="*", width=36)
        self.ent_pass.grid(row=1, column=1, pady=6)

        # Aquí es pa mostrar/ocultar contraseña con un pequeño toggle
        self.show_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(frm, text="Mostrar", bg=PALETA["panel"], fg=PALETA["gris_medio"],
                            variable=self.show_var, command=self._toggle_show)
        cb.grid(row=1, column=2, padx=(6,0))

        btn_frame = tk.Frame(panel, bg=PALETA["panel"])
        btn_frame.pack(pady=8)

        self.login_btn = tk.Button(btn_frame, text="Entrar", bd=0, padx=14, pady=8, bg=PALETA["bahi_aeste"], fg="white")
        self.login_btn.pack(side="left", padx=8)
        self.login_btn.bind("<Button-1>", self._on_login)
        self._bind_hover(self.login_btn, PALETA["bahi_aeste"], PALETA["fjord"])

        self.cancel_btn = tk.Button(btn_frame, text="Cancelar", bd=0, padx=14, pady=8, bg=PALETA["martinica"], fg="white")
        self.cancel_btn.pack(side="left", padx=8)
        self.cancel_btn.bind("<Button-1>", lambda e: self.destroy())
        self._bind_hover(self.cancel_btn, PALETA["martinica"], PALETA["fjord"])

        tk.Label(panel, text="Nota al usuario: el usuario master es 'admin'.", font=('Times New Roman', 9),
                 bg=PALETA["panel"], fg=PALETA["gris_medio"]).pack(side="bottom", pady=10)
        
        self.bind("<Return>", lambda e: self._on_login())

    def _toggle_show(self):
        if self.show_var.get():
            self.ent_pass.config(show="")
        else:
            self.ent_pass.config(show="*")

    def _on_login(self, event=None):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()

        if user == LoginView.MASTER_USER and pwd == LoginView.MASTER_PASS:
            try:
                self.destroy()
            except Exception:
                pass
            try:
                self.parent.show_dashboard()
            except Exception:
                pass
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos. Intenta de nuevo.")
            self._shake()

    def _shake(self):
        def do_shake():
            try:
                x = self.winfo_x()
                for dx in [-12, 12, -8, 8, -4, 4, 0]:
                    self.geometry(f"+{x+dx}+{self.winfo_y()}")
                    time.sleep(0.02)
            except Exception:
                pass
        threading.Thread(target=do_shake, daemon=True).start()
        
    def _bind_hover(self, widget, base_color, hover_color):
        widget._anim_after = None
        widget._hover_progress = 0.0
        widget._base_color = base_color
        widget._hover_color = hover_color
        widget.bind("<Enter>", lambda e, w=widget: self._start_hover(w, enter=True))
        widget.bind("<Leave>", lambda e, w=widget: self._start_hover(w, enter=False))

    def _start_hover(self, widget, enter=True, step=0.09):
        def stepfn():
            p = widget._hover_progress
            if enter:
                p = min(1.0, p + step)
            else:
                p = max(0.0, p - step)
            widget._hover_progress = p
            col = lerp_color(widget._base_color, widget._hover_color, p)
            try:
                widget.config(bg=col)
            except tk.TclError:
                pass
            if (enter and p < 1.0) or (not enter and p > 0.0):
                widget._anim_after = widget.after(30, stepfn)
            else:
                widget._anim_after = None
        if getattr(widget, "_anim_after", None):
            widget.after_cancel(widget._anim_after)
            widget._anim_after = None
        stepfn()
