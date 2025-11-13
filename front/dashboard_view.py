import tkinter as tk
import threading
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import random, math, time
import re
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

PALETA = {
    "espejismo": "#1C1F3B",
    "martinica": "#282C4D",
    "fjord": "#3C3F68",
    "bahi_aeste": "#4D4D80",
    "gris_medio": "#606271",
    "panel": "#0F1225"
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def lerp_color(a_hex, b_hex, t: float):
    a = hex_to_rgb(a_hex)
    b = hex_to_rgb(b_hex)
    r = int(a[0] + (b[0] - a[0]) * t)
    g = int(a[1] + (b[1] - a[1]) * t)
    b_ = int(a[2] + (b[2] - a[2]) * t)
    return rgb_to_hex((r, g, b_))

class Star:
    def __init__(self, canvas, x, y, size, vx, vy, twinkle_speed):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.vx = vx
        self.vy = vy
        self.twinkle_speed = twinkle_speed
        self.phase = random.random()*2*math.pi
        self.item = canvas.create_oval(x, y, x+size, y+size, fill="#ffffff", outline="")
        canvas.tag_raise(self.item)

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy
        self.phase += self.twinkle_speed
        if self.x < -10: self.x = w + 5
        if self.x > w + 10: self.x = -5
        if self.y < -10: self.y = h + 5
        if self.y > h + 10: self.y = -5

        brightness = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(self.phase))
        v = int(255 * brightness)
        color = f"#{v:02x}{v:02x}{v:02x}"
        self.canvas.coords(self.item, self.x, self.y, self.x + self.size, self.y + self.size)
        try:
            self.canvas.itemconfigure(self.item, fill=color)
            self.canvas.tag_raise(self.item)
        except tk.TclError:
            pass


class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)
        self.configure(bg=PALETA["espejismo"])

        self.ia_service = None
        self.ia_error = None
        self._ia_ready = False

        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_image = None
        self._make_background_image(width=1200, height=800)
        self.stars = []
        self._create_stars(45)

        self.panel = tk.Frame(self, bg=PALETA["panel"], bd=0)
        self.panel.place(relx=0.03, rely=0.03, relwidth=0.94, relheight=0.94)


        header = tk.Frame(self.panel, bg=PALETA["panel"])
        header.pack(fill="x", padx=16, pady=12)
        tk.Label(header, text="Diario de Dreams", font=('Times New Roman', 22, 'bold'),
                 bg=PALETA["panel"], fg=PALETA["bahi_aeste"]).pack(side="left")
        tk.Label(header, text="Un lugar para registrar y soñar",
                 font=('Times New Roman', 11, 'italic'),
                 bg=PALETA["panel"], fg=PALETA["gris_medio"]).pack(side="left", padx=10)


        self.loading_frame = tk.Frame(self.panel, bg=PALETA["panel"])
        self.loading_frame.pack(fill="both", expand=True, padx=40, pady=40)
        self.loading_label = tk.Label(self.loading_frame, text="Cargando el motor de I.A. — esto puede tardar unos segundos...",
                                      bg=PALETA["panel"], fg=PALETA["gris_medio"], font=('Times New Roman', 12))
        self.loading_label.pack(pady=10)
        self.loading_dots = tk.Label(self.loading_frame, text="", bg=PALETA["panel"], fg=PALETA["gris_medio"], font=('Times New Roman', 18))
        self.loading_dots.pack(pady=6)
        self._loading_dots_phase = 0
        self._animate_loading_dots()

        self.bind("<Configure>", self._on_resize)

        threading.Thread(target=self._init_ia_service_background, daemon=True).start()

        self._animate()


    def _animate_loading_dots(self):
        phases = ["", ".", "..", "...", "..", "."]
        self._loading_dots_phase = (self._loading_dots_phase + 1) % len(phases)
        try:
            self.loading_dots.config(text=phases[self._loading_dots_phase])
        except Exception:
            pass
        if not self._ia_ready:
            self.after(400, self._animate_loading_dots)

    def _init_ia_service_background(self):
        try:
            from back.ia_services import IAService
            ia = IAService()  
            self.ia_service = ia
            self.ia_error = None
        except Exception as e:
            self.ia_service = None
            self.ia_error = e
        try:
            self.after(50, self._on_ia_initialized)
        except Exception:
            pass

    def _on_ia_initialized(self):
        self._ia_ready = True
        try:
            self.loading_frame.destroy()
        except Exception:
            pass

        if self.ia_error:
            import traceback
            tb = traceback.format_exception_only(type(self.ia_error), self.ia_error)
            msg = "Error al inicializar IA:\n" + "".join(tb)
            err_label = tk.Label(self.panel, text=msg, fg="orange", bg=PALETA["panel"], wraplength=600, justify="left")
            err_label.pack(padx=20, pady=10)
            btn_retry = tk.Button(self.panel, text="Reintentar inicialización de IA", command=self._retry_init_ia,
                                  bg=PALETA["bahi_aeste"], fg="white", bd=0, padx=10, pady=8)
            btn_retry.pack(pady=6)
            self._bind_hover(btn_retry, PALETA["bahi_aeste"], PALETA["fjord"])
            return

        try:
            self.notebook = ttk.Notebook(self.panel)
            self.notebook.pack(padx=16, pady=8, fill="both", expand=True)

            self.tab_registro = tk.Frame(self.notebook, bg=PALETA["panel"])
            self.notebook.add(self.tab_registro, text="📝 Registrar Sueño")
            self._setup_registro_tab(self.tab_registro)

            self.tab_consulta = tk.Frame(self.notebook, bg=PALETA["panel"])
            self.notebook.add(self.tab_consulta, text="🔍 Consultar/Buscar")
            self._setup_consulta_tab(self.tab_consulta)

            self.tab_visual = tk.Frame(self.notebook, bg=PALETA["panel"])
            self.notebook.add(self.tab_visual, text="📊 Visualizaciones")
            self._setup_visualizaciones_tab(self.tab_visual)

            threading.Thread(target=self._load_dreams_list_safe, daemon=True).start()

        except Exception as e:
            tk.Label(self.panel, text=f"Error preparando UI: {e}", fg="orange", bg=PALETA["panel"]).pack(padx=10, pady=10)

    def _retry_init_ia(self):
        for w in self.panel.winfo_children():
            w.destroy()
        header = tk.Frame(self.panel, bg=PALETA["panel"])
        header.pack(fill="x", padx=16, pady=12)
        tk.Label(header, text="Diario de Dreams", font=('Times New Roman', 22, 'bold'),
                 bg=PALETA["panel"], fg=PALETA["bahi_aeste"]).pack(side="left")
        self.loading_frame = tk.Frame(self.panel, bg=PALETA["panel"])
        self.loading_frame.pack(fill="both", expand=True, padx=40, pady=40)
        self.loading_label = tk.Label(self.loading_frame, text="Reintentando inicialización de I.A....",
                                      bg=PALETA["panel"], fg=PALETA["gris_medio"], font=('Times New Roman', 12))
        self.loading_label.pack(pady=10)
        self.loading_dots = tk.Label(self.loading_frame, text="", bg=PALETA["panel"], fg=PALETA["gris_medio"])
        self.loading_dots.pack(pady=6)
        self._ia_ready = False
        self._animate_loading_dots()
        threading.Thread(target=self._init_ia_service_background, daemon=True).start()

    def _load_dreams_list_safe(self):
        try:
            rows = []
            if self.ia_service and getattr(self.ia_service, "db_manager", None):
                try:
                    rows = self.ia_service.db_manager.fetch_all_dreams()
                except Exception:
                    rows = []
            else:
                rows = []
            def update_tree():
                try:
                    if not hasattr(self, "tree"):
                        cols = ("id", "title", "date", "emotion", "format")
                        self.tree = ttk.Treeview(self.tab_consulta, columns=cols, show="headings", height=8)
                        for c in cols:
                            self.tree.heading(c, text=c.capitalize())
                            self.tree.column(c, width=140)
                        self.tree.pack(fill="both", expand=False, padx=8, pady=8)
                        self.tree.bind("<Double-1>", self._on_row_double)
                    for r in self.tree.get_children():
                        self.tree.delete(r)
                    for d in rows:
                        self.tree.insert("", "end", values=(d['id'], d['title'], d['date_recorded'], d['emotion_tag'], d.get('creative_format','')))
                except Exception:
                    pass
            self.after(10, update_tree)
        except Exception:
            pass

    def _make_background_image(self, width=1200, height=800):
        img = Image.new('RGB', (width, height), color=PALETA["martinica"])
        draw = ImageDraw.Draw(img)

        top = hex_to_rgb(PALETA["martinica"])
        mid = hex_to_rgb(PALETA["fjord"])
        bottom = hex_to_rgb(PALETA["bahi_aeste"])

        for y in range(height):
            t = y / float(height - 1)
            if t < 0.6:
                t2 = t / 0.6
                color = (
                    int(top[0] + (mid[0] - top[0]) * t2),
                    int(top[1] + (mid[1] - top[1]) * t2),
                    int(top[2] + (mid[2] - top[2]) * t2)
                )
            else:
                t2 = (t - 0.6) / 0.4
                color = (
                    int(mid[0] + (bottom[0] - mid[0]) * t2),
                    int(mid[1] + (bottom[1] - mid[1]) * t2),
                    int(mid[2] + (bottom[2] - mid[2]) * t2)
                )
            draw.line([(0, y), (width, y)], fill=color)

        for i in range(12):
            ellipse_w = random.randint(int(width*0.2), int(width*0.6))
            ellipse_h = random.randint(int(height*0.08), int(height*0.25))
            x = random.randint(-int(width*0.2), int(width*0.8))
            y = random.randint(-int(height*0.1), int(height*0.9))
            overlay = Image.new('RGBA', (width, height), (0,0,0,0))
            odraw = ImageDraw.Draw(overlay)
            col = hex_to_rgb(PALETA["espejismo"])
            odraw.ellipse([x, y, x+ellipse_w, y+ellipse_h], fill=(col[0], col[1], col[2], 18))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)

        img = img.filter(ImageFilter.GaussianBlur(radius=8))
        self.bg_pil = img.convert('RGB')
        self.bg_image = ImageTk.PhotoImage(self.bg_pil)
        self.bg_canvas.delete("bg_img")
        self.bg_canvas.create_image(0, 0, image=self.bg_image, anchor='nw', tags="bg_img")
        self.bg_canvas.lower("bg_img")
        self.bg_canvas.update()
        
    def _create_stars(self, n=30):
        self.bg_canvas.delete("star")
        self.stars = []
        w = self.winfo_width() or 1200
        h = self.winfo_height() or 800
        for _ in range(n):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            size = random.uniform(1.2, 3.8)
            vx = random.uniform(-0.15, 0.15)
            vy = random.uniform(-0.3, -0.05)
            tw = random.uniform(0.05, 0.2)
            s = Star(self.bg_canvas, x, y, size, vx, vy, tw)
            self.bg_canvas.addtag_withtag("star", s.item)
            self.stars.append(s)
        self.bg_canvas.tag_raise("star")

    def _on_resize(self, event):
        w = max(600, event.width)
        h = max(400, event.height)
        self._make_background_image(width=w, height=h)
        if len(self.stars) < 5:
            self._create_stars(45)

    def _animate(self):
        w = self.winfo_width() or 1200
        h = self.winfo_height() or 800
        for s in self.stars:
            s.update(w, h)
        if random.random() < 0.012:
            x0 = random.uniform(0, w)
            y0 = random.uniform(0, h)
            size = random.uniform(2.5, 6.0)
            item = self.bg_canvas.create_oval(x0, y0, x0+size, y0+size, fill="#ffffff", outline="")
            self.bg_canvas.lift(item)
            self.bg_canvas.after(380, lambda it=item: self.bg_canvas.delete(it))
        self.after(33, self._animate)

    def _setup_registro_tab(self, tab):
        tab.configure(bg=PALETA["panel"])
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frame, text="Título del Sueño:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.entry_titulo = ttk.Entry(frame, width=60)
        self.entry_titulo.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Label(frame, text="Contenido:").grid(row=1, column=0, sticky="nw", padx=6, pady=6)
        self.text_contenido = tk.Text(frame, width=60, height=10, wrap="word")
        self.text_contenido.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)

        ttk.Label(frame, text="Formato Creativo:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.combo_formato = ttk.Combobox(frame, values=["Poema", "Historia Corta", "Guion Corto"], state="readonly", width=30)
        self.combo_formato.set("Poema")
        self.combo_formato.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        btn_frame = tk.Frame(frame, bg=PALETA["panel"])
        btn_frame.grid(row=3, column=1, sticky="e", pady=10)
        self.save_btn = tk.Button(btn_frame, text="Guardar y Analizar Sueño", bd=0, padx=10, pady=8,
                                bg=PALETA["bahi_aeste"], fg="white", activebackground=PALETA["fjord"])
        self.save_btn.pack(side="right", padx=6)
        self.save_btn.bind("<Button-1>", lambda e: self._handle_guardar_sueno())
        self._bind_hover(self.save_btn, PALETA["bahi_aeste"], PALETA["fjord"])

        hist_btn = tk.Button(btn_frame, text="Abrir Historial", bd=0, padx=10, pady=8,
                            bg=PALETA["martinica"], fg="white")
        hist_btn.pack(side="right", padx=6)
        hist_btn.bind("<Button-1>", lambda e: self.notebook.select(self.tab_consulta))
        self._bind_hover(hist_btn, PALETA["martinica"], PALETA["fjord"])

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        result_box = tk.Frame(tab, bg=PALETA["panel"])
        result_box.pack(fill="x", padx=12, pady=(6,12))
        tk.Label(result_box, text="Resultado Creativo", bg=PALETA["panel"], fg=PALETA["gris_medio"]).pack(anchor="w")
        self.text_creativo = tk.Text(result_box, height=6, wrap="word")
        self.text_creativo.pack(fill="both", expand=True, pady=(6,0))

        analysis_box = tk.Frame(tab, bg=PALETA["panel"])
        analysis_box.pack(fill="x", padx=12, pady=(6,12))
        tk.Label(analysis_box, text="Análisis / Significado", bg=PALETA["panel"], fg=PALETA["gris_medio"]).pack(anchor="w")
        self.text_analysis = tk.Text(analysis_box, height=6, wrap="word")
        self.text_analysis.pack(fill="both", expand=True, pady=(6,0))

    def _handle_guardar_sueno(self):
        titulo = self.entry_titulo.get().strip()
        contenido = self.text_contenido.get("1.0", tk.END).strip()
        formato = self.combo_formato.get()
        if not titulo or not contenido:
            messagebox.showerror("Error de Entrada", "Título y contenido no pueden estar vacíos.")
            return

        if not self._ia_ready or not self.ia_service:
            messagebox.showwarning("IA no lista", "El motor de IA aún no está listo. Intenta de nuevo en unos segundos o presiona 'Reintentar' en la pestaña de consulta.")
            return

        try:
            emocion, creativo, analisis = self.ia_service.process_and_save_dream(titulo, contenido, formato)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar el sueño: {e}")
            return

        self.text_creativo.delete("1.0", tk.END)
        self.text_creativo.insert(tk.END, creativo if creativo else "(No generado)")

        self.text_analysis.delete("1.0", tk.END)
        self.text_analysis.insert(tk.END, self._extract_interpretation_and_advice(analisis))

        try:
            self._update_creative_label(formato)
        except Exception:
            pass

        if isinstance(emocion, str) and ("Error" in emocion or "Error" in creativo or "Error" in analisis):
            messagebox.showerror("Error de Servidor", "Ocurrió un error al procesar o guardar el sueño. Revisa la terminal y tu conexión a MySQL/OpenAI.")
        else:
            messagebox.showinfo("Éxito", f"Sueño guardado y analizado.\nEmoción: {emocion}.\nAnálisis generado en el campo de abajo.")

            try:
                threading.Thread(target=self._load_dreams_list_safe, daemon=True).start()
            except Exception:
                pass

    def _setup_consulta_tab(self, tab):
        tab.configure(bg=PALETA["panel"])
        top = tk.Frame(tab, bg=PALETA["panel"])
        top.pack(fill="x", padx=8, pady=8)
        tk.Label(top, text="Buscar:", bg=PALETA["panel"]).pack(side="left", padx=6)
        self.search_entry = ttk.Entry(top)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=6)
        search_btn = tk.Button(top, text="Buscar sueño", bd=0, padx=8, pady=6, bg=PALETA["bahi_aeste"], fg="white")
        search_btn.pack(side="left", padx=6)
        search_btn.bind("<Button-1>", lambda e: self._perform_semantic_search())
        self._bind_hover(search_btn, PALETA["bahi_aeste"], PALETA["fjord"])
        ttk.Button(top, text="Refrescar Lista", command=lambda: threading.Thread(target=self._load_dreams_list_safe, daemon=True).start()).pack(side="left", padx=6)

        cols = ("id", "title", "date", "emotion", "format")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=140)
        self.tree.pack(fill="both", expand=False, padx=8, pady=8)
        self.tree.bind("<Double-1>", self._on_row_double)

        detail = tk.Frame(tab, bg=PALETA["panel"])
        detail.pack(fill="both", expand=True, padx=8, pady=(0,8))
        tk.Label(detail, text="Contenido Completo:", bg=PALETA["panel"]).pack(anchor="w")
        self.detail_content = tk.Text(detail, height=6, wrap="word")
        self.detail_content.pack(fill="both", expand=True, pady=6)
        tk.Label(detail, text="Creativo Guardado:", bg=PALETA["panel"]).pack(anchor="w")
        self.detail_creative = tk.Text(detail, height=6, wrap="word")
        self.detail_creative.pack(fill="both", expand=True, pady=6)
        
        tk.Label(detail, text="Análisis del Sueño:", bg=PALETA["panel"]).pack(anchor="w", pady=(8,0))
        self.detail_analysis = tk.Text(detail, height=6, wrap="word")
        self.detail_analysis.pack(fill="both", expand=True, pady=6)

        threading.Thread(target=self._load_dreams_list_safe, daemon=True).start()

    def _load_dreams_list(self):
        threading.Thread(target=self._load_dreams_list_safe, daemon=True).start()

    def _on_row_double(self, event):
        sel = self.tree.focus()
        if not sel:
            return
        vals = self.tree.item(sel, "values")
        try:
            did = int(vals[0])
        except Exception:
            messagebox.showerror("Error", "ID inválido seleccionado.")
            return

        if not self.ia_service or not getattr(self.ia_service, "db_manager", None):
            messagebox.showwarning("BD no disponible", "La base de datos no está disponible (IA/DB no inicializadas).")
            return

        dream = self.ia_service.db_manager.fetch_dream_by_id(did)
        if not dream:
            messagebox.showerror("Error", "No se pudo cargar el sueño.")
            return

        self.detail_content.delete("1.0", tk.END)
        self.detail_content.insert(tk.END, dream.get("content", ""))

        self.detail_creative.delete("1.0", tk.END)
        creative_text = dream.get("creative_text") or "(Sin creativo guardado)"
        self.detail_creative.insert(tk.END, f"Formato: {dream.get('creative_format','')}\n\n{creative_text}")

        self.detail_analysis.delete("1.0", tk.END)
        analysis_raw = dream.get("analysis_text") or "(Sin análisis guardado)"
        self.detail_analysis.insert(tk.END, self._extract_interpretation_and_advice(analysis_raw))

    def _perform_semantic_search(self):
        q = self.search_entry.get().strip()
        if not q:
            messagebox.showwarning("Aviso", "Escribe algo para buscar.")
            return

        if not self._ia_ready or not self.ia_service:
            messagebox.showwarning("IA no lista", "El motor de IA aún no está listo.")
            return

        try:
            res = self.ia_service.semantic_search(q)
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {e}")
            return
        
        self.detail_content.delete("1.0", tk.END)
        self.detail_creative.delete("1.0", tk.END)
        self.detail_analysis.delete("1.0", tk.END)
        self.detail_content.insert(tk.END, res)

    def _setup_visualizaciones_tab(self, tab):
        tab.configure(bg=PALETA["panel"])
        main_frame = ttk.Frame(tab, style='TFrame')
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame, bg=PALETA["panel"], highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.charts_container = tk.Frame(scrollable_frame, bg=PALETA["panel"])
        self.charts_container.pack(fill="x", padx=15, pady=15)
        
        tk.Label(self.charts_container, text="📊 Resumen Emocional Histórico", 
                 font=('Times New Roman', 18, 'bold'), bg=PALETA["panel"], fg=PALETA["bahi_aeste"]).pack(pady=10)

        btn_refresh = tk.Button(self.charts_container, text="Actualizar Gráficos", bd=0, padx=12, pady=8,
                                bg=PALETA["bahi_aeste"], fg="white")
        btn_refresh.pack(pady=10)
        btn_refresh.bind("<Button-1>", lambda e: self._load_visualizations_safe())
        self._bind_hover(btn_refresh, PALETA["bahi_aeste"], PALETA["fjord"])

        self.visual_status_label = tk.Label(self.charts_container, text="Presiona 'Actualizar Gráficos' para cargar datos.", 
                                            bg=PALETA["panel"], fg=PALETA["gris_medio"])
        self.visual_status_label.pack(pady=5)
        
        self.chart_frame = tk.Frame(self.charts_container, bg=PALETA["panel"])
        self.chart_frame.pack(fill="x", expand=False, pady=15)


    def _load_visualizations_safe(self):
        self.visual_status_label.config(text="Cargando datos y dibujando gráficos, por favor espera...", fg="yellow")
        
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        threading.Thread(target=self._draw_all_charts, daemon=True).start()


    def _draw_all_charts(self):
        try:
            emotion_counts, evolution_data, wordcloud_text = self.ia_service.get_visual_metrics()

            if isinstance(emotion_counts, str):
                self.after(0, lambda: self.visual_status_label.config(text=emotion_counts, fg="red"))
                return

            self.after(0, lambda: self._draw_emotion_pie(emotion_counts))
            self.after(0, lambda: self._draw_emotion_evolution(evolution_data)) 
            self.after(0, lambda: self._draw_wordcloud(wordcloud_text))
            
            self.after(0, lambda: self.visual_status_label.config(text="Gráficos actualizados con éxito.", fg="lime green"))

        except Exception as e:
            self.after(0, lambda: self.visual_status_label.config(text=f"Error fatal al dibujar gráficos: {e}", fg="red"))


    def _draw_emotion_pie(self, emotion_counts):
        colors = ['#4D4D80', '#282C4D', '#3C3F68', '#606271', '#7A7D94'] 
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        labels = [k for k, v in emotion_counts.items() if v > 0]
        sizes = [v for v in emotion_counts.values() if v > 0]
        
        if not sizes:
             ax.text(0.5, 0.5, 'No hay datos de sueños para graficar.', ha='center', va='center', color='gray')
        else:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)], textprops={'color': 'white'})
            ax.axis('equal') 
        
        ax.set_title("Distribución de Emociones", color='white')
        fig.patch.set_facecolor(PALETA["panel"])
        ax.set_facecolor(PALETA["panel"])

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="x", expand=True, padx=10, pady=20, side=tk.TOP)
        canvas.draw()


    def _draw_wordcloud(self, text):
            import matplotlib.pyplot as plt 
            from wordcloud import WordCloud 
            
            for widget in self.chart_frame.winfo_children():
                if widget.winfo_ismapped() and isinstance(widget, tk.Label):
                    if hasattr(widget, 'wordcloud_marker'):
                        widget.destroy()

            if not text.strip():
                label = tk.Label(self.chart_frame, text="No hay suficiente texto para la Nube de Palabras.", 
                                bg=PALETA["panel"], fg="gray")
                label.pack(side=tk.TOP, padx=10, pady=10)
                return

            wc = WordCloud(width=800, 
                        height=400, 
                        background_color=PALETA["panel"], 
                        colormap='plasma', 
                        min_font_size=10,
                        normalize_plurals=False).generate(text)
            
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off") 
            fig.patch.set_facecolor(PALETA["panel"])
            plt.tight_layout(pad=0) 


            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas_widget = canvas.get_tk_widget()
            
            canvas_widget.pack(fill="x", expand=True, padx=10, pady=20, side=tk.TOP) 
            

            canvas_widget.wordcloud_marker = True 
            canvas.draw()

    def _bind_hover(self, widget, base_color, hover_color):
        widget._anim_after = None
        widget._hover_progress = 0.0
        widget._base_color = base_color
        widget._hover_color = hover_color
        widget.bind("<Enter>", lambda e, w=widget: self._start_hover(w, enter=True))
        widget.bind("<Leave>", lambda e, w=widget: self._start_hover(w, enter=False))

    def _start_hover(self, widget, enter=True, step=0.08):
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

    def _setup_hover_effects(self):
        pass


    def _update_creative_label(self, formato):
        try:
            print(f"[UI] formato creativo: {formato}")
        except Exception:
            pass


    def _extract_interpretation_and_advice(self, analysis_text: str) -> str:
        if not analysis_text:
            return "(Sin análisis guardado)"

        try:
            if isinstance(analysis_text, dict):
                data = analysis_text
                interp = data.get("interpretation") or data.get("interpret") or data.get("meaning") or data.get("interpretación")
                advice = data.get("advice") or data.get("recommendation") or data.get("consejo")
                parts = []
                if interp:
                    parts.append("Interpretación:\n" + str(interp).strip())
                if advice:
                    parts.append("Consejo:\n" + str(advice).strip())
                if parts:
                    return "\n\n".join(parts)
        except Exception:
            pass

        txt = analysis_text.strip()

        try:
            data = json.loads(txt)
            interp = data.get("interpretation") or data.get("interpret") or data.get("meaning") or data.get("interpretación")
            advice = data.get("advice") or data.get("recommendation") or data.get("consejo")
            parts = []
            if interp:
                parts.append("Interpretación:\n" + str(interp).strip())
            if advice:
                parts.append("Consejo:\n" + str(advice).strip())
            if parts:
                return "\n\n".join(parts)
        except Exception:
            pass

        m = re.search(r'\{.*\}', txt, flags=re.DOTALL)
        if m:
            candidate = m.group(0)
            candidate_norm = candidate.replace('“', '"').replace('”', '"').replace("’", "'").replace("‘", "'")
            if candidate_norm.count("'") >= candidate_norm.count('"'):
                candidate_norm = candidate_norm.replace("'", '"')
            try:
                data = json.loads(candidate_norm)
                interp = data.get("interpretation") or data.get("interpret") or data.get("meaning") or data.get("interpretación")
                advice = data.get("advice") or data.get("recommendation") or data.get("consejo")
                parts = []
                if interp:
                    parts.append("Interpretación:\n" + str(interp).strip())
                if advice:
                    parts.append("Consejo:\n" + str(advice).strip())
                if parts:
                    return "\n\n".join(parts)
            except Exception:
                cand2 = candidate_norm.replace('\\"', '"').replace('\\\'', "'")
                try:
                    data = json.loads(cand2)
                    interp = data.get("interpretation") or data.get("interpret") or data.get("meaning") or data.get("interpretación")
                    advice = data.get("advice") or data.get("recommendation") or data.get("consejo")
                    parts = []
                    if interp:
                        parts.append("Interpretación:\n" + str(interp).strip())
                    if advice:
                        parts.append("Consejo:\n" + str(advice).strip())
                    if parts:
                        return "\n\n".join(parts)
                except Exception:
                    pass
        lines = txt.splitlines()
        interp_lines = []
        advice_lines = []
        for ln in lines:
            low = ln.lower()
            if "interpret" in low or "interpretación" in low or "meaning" in low:
                interp_lines.append(ln.strip())
            if "advice" in low or "consejo" in low or "recommend" in low:
                advice_lines.append(ln.strip())

        if interp_lines or advice_lines:
            parts = []
            if interp_lines:
                parts.append("Interpretación:\n" + " ".join(interp_lines))
            if advice_lines:
                parts.append("Consejo:\n" + " ".join(advice_lines))
            return "\n\n".join(parts)
        
        if len(txt) > 2000:
            return txt[:2000] + "\n\n...(texto demasiado largo, ver consola para JSON completo)"
        return txt

    def _draw_emotion_evolution(self, evolution_data):
        import pandas as pd
        import matplotlib.dates as mdates
        
        EMOTION_COLORS = {
            "Alegría": '#4D4D80', 
            "Calma": '#3C3F68',
            "Tristeza": '#606271', 
            "Miedo": '#B2B2B2', 
            "Ira": '#C93C3C',
            "Indefinida": '#333333'
        }

        df = pd.DataFrame(evolution_data, columns=['date', 'emotion'])
        df['date'] = pd.to_datetime(df['date'])

        df_counts = df.groupby(['date', 'emotion']).size().reset_index(name='count')
        
        df_pivot = df_counts.pivot(index='date', columns='emotion', values='count').fillna(0)
        
        fig = Figure(figsize=(12, 5), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor(PALETA["panel"])
        ax.set_facecolor(PALETA["panel"])
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        
        ax.set_title("Evolución de Frecuencia Emocional", color='white')
        ax.set_xlabel("Fecha", color='white')
        ax.set_ylabel("Frecuencia Diaria", color='white')

        if df_pivot.empty:
            ax.text(0.5, 0.5, 'No hay datos suficientes para la evolución temporal.', ha='center', va='center', color='gray')
        else:
            for emotion in df_pivot.columns:
                ax.plot(df_pivot.index, df_pivot[emotion], label=emotion, 
                        color=EMOTION_COLORS.get(emotion, '#FFFFFF'), linewidth=2)
            
            ax.legend(loc='upper left', frameon=False, labelcolor='white')

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            fig.autofmt_xdate(rotation=45) 

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="x", expand=True, padx=10, pady=10, side=tk.TOP)
        canvas.draw()
