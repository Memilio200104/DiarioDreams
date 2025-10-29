import tkinter as tk
from tkinter import ttk

class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.configure(bg="#F5F5DC")

        tk.Label(self, text="DIARIO DE DREAMS", bg="#36454F", fg="white", 
                 font=('Times New Roman', 20, 'bold'), padx=10, pady=10).pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=20, pady=10, fill="both", expand=True) 

        self.tab_registro = tk.Frame(self.notebook, bg="#F5F5DC")
        self.notebook.add(self.tab_registro, text="📝 Registrar Sueño")
        self._setup_registro_tab(self.tab_registro)

        self.tab_consulta = tk.Frame(self.notebook, bg="#F5F5DC")
        self.notebook.add(self.tab_consulta, text="🔍 Consultar/Buscar")
        self._setup_consulta_tab(self.tab_consulta)

        self.tab_visualizaciones = tk.Frame(self.notebook, bg="#F5F5DC")
        self.notebook.add(self.tab_visualizaciones, text="📊 Visualizaciones")
        self._setup_visualizaciones_tab(self.tab_visualizaciones)

        self.tab_exportar = tk.Frame(self.notebook, bg="#F5F5DC")
        self.notebook.add(self.tab_exportar, text="📤 Exportar/Reportes")
        self._setup_exportar_tab(self.tab_exportar)

        self.notebook.select(self.tab_registro)


    def _setup_registro_tab(self, tab):
        tab.configure(bg="#F5F5DC")
        font_style = ('Times New Roman', 12)
        
        ttk.Label(tab, text="Título del Sueño:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(tab, width=60).grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(tab, text="Contenido del Sueño:", font=('Times New Roman', 14, 'bold')).grid(
            row=1, column=0, padx=10, pady=10, sticky="nw")
        text_area_frame = ttk.Frame(tab, relief="sunken", borderwidth=1)
        text_area_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        text_widget = tk.Text(text_area_frame, width=60, height=15, wrap="word", 
                              bg="white", fg="#333333", font=font_style, padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        ttk.Button(tab, text="Guardar y Analizar Sueño").grid(
            row=2, column=1, padx=10, pady=20, sticky="e")
        tab.grid_columnconfigure(1, weight=1)

    def _setup_consulta_tab(self, tab):
        tab.configure(bg="#F5F5DC") 
        search_frame = ttk.Frame(tab, style="TLabel") 
        search_frame.pack(padx=20, pady=20, fill="x") 
        ttk.Label(search_frame, text="Buscar Sueño (Lenguaje Natural):").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ttk.Button(search_frame, text="Buscar", command=self._search_dreams).grid(
            row=0, column=2, padx=10, pady=10)
        search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(tab, text="--- Resultados de Búsqueda Semántica ---", 
                 bg="#36454F", fg="white", font=('Times New Roman', 12, 'bold')).pack(fill="x", padx=20, pady=(10, 0))
        
        self.results_text = tk.Text(tab, height=15, width=80, bg="white", fg="#333333", font=('Times New Roman', 12))
        self.results_text.pack(padx=20, pady=20, fill="both", expand=True) 
        
    def _search_dreams(self):
        query = self.search_entry.get()
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Buscando: '{query}'...\nLa implementación de la búsqueda semántica requiere la IA (Sprint 2).") 

    def _setup_visualizaciones_tab(self, tab):
        tab.configure(bg="#F5F5DC")
        tk.Label(tab, text="GRÁFICOS DE EVOLUCIÓN EMOCIONAL", 
                 font=('Times New Roman', 16, 'bold'), bg="#F5F5DC", fg="#333333").pack(pady=20)
        
        tk.Label(tab, text="Aquí se mostrarán: 1) Evolución emocional a lo largo del tiempo, 2) Nube de palabras clave, y 3) Conteo por categoría emocional.",
                 wraplength=700, justify=tk.LEFT, bg="#F5F5DC", fg="#36454F").pack(padx=30)
        
        # Placeholder para la gráfica (se implementará en Sprint 4) -Emix
        ttk.Frame(tab, width=600, height=350, relief="groove", borderwidth=2).pack(pady=20, padx=30, fill="both", expand=True)

    def _setup_exportar_tab(self, tab):
        tab.configure(bg="#F5F5DC")
        tk.Label(tab, text="EXPORTAR DATOS Y REPORTES", 
                 font=('Times New Roman', 16, 'bold'), bg="#F5F5DC", fg="#333333").pack(pady=20)

        export_frame = ttk.Frame(tab, style="TLabel")
        export_frame.pack(pady=20)
        
        ttk.Button(export_frame, text="Exportar Métricas a CSV").grid(row=0, column=0, padx=15, pady=10)
        ttk.Button(export_frame, text="Generar Reporte PDF").grid(row=0, column=1, padx=15, pady=10)
        
        tk.Label(tab, text="Esta función consolidará tus sueños y tendencias emocionales en un archivo de reporte.",
                 wraplength=500, justify=tk.LEFT, bg="#F5F5DC", fg="#36454F").pack(pady=10)