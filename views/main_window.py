# -*- coding: utf-8 -*-
"""
views/main_window.py
Ventana principal y contenedor del panel de navegación lateral.
Implementa el diseño de dashboard premium y coordina las diferentes vistas modulares.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import database

# Importaciones de las sub-vistas modulares
from views.init_view import InitView
from views.warehouse_view import WarehouseView
from views.ledger_view import LedgerView
from views.automation_view import AutomationView
from views.reports_view import ReportsView

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title("ERP Contabilidad de Costos - Premium Edition")
        self.geometry("1100x750")
        self.configure(bg=config.COLOR_BG)
        
        # Cargar base de datos inicial
        self.db_data = database.load_db()
        
        # Aplicar estilos globales de ttk
        self.setup_styles()
        
        # Estructura del Layout General:
        # Menú Lateral (Left) + Contenedor de Vistas (Right)
        self.sidebar_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, width=260)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        self.content_frame = tk.Frame(self, bg=config.COLOR_BG)
        self.content_frame.pack(side="right", expand=True, fill="both")
        
        # Construir menú lateral
        self.build_sidebar()
        
        # Diccionario para almacenar instancias de las vistas
        self.views = {}
        self.active_view = None
        
        # Inicializar vistas
        self.init_all_views()
        
        # Mostrar vista inicial
        self.show_view("init")
        
    def setup_styles(self):
        """Configura los estilos de la librería ttk para que combinen con la paleta institucional."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configurar Treeviews (Tablas)
        style.configure("Treeview", 
                        background=config.COLOR_CARD, 
                        foreground=config.COLOR_TEXT_DARK, 
                        fieldbackground=config.COLOR_CARD,
                        bordercolor=config.COLOR_BORDER,
                        rowheight=26,
                        font=config.FONT_BODY)
        
        style.configure("Treeview.Heading", 
                        background=config.COLOR_PRIMARY, 
                        foreground=config.COLOR_TEXT_LIGHT, 
                        font=config.FONT_BODY_BOLD,
                        borderwidth=1)
        
        style.map("Treeview.Heading",
                  background=[('active', config.COLOR_SECONDARY)],
                  foreground=[('active', config.COLOR_TEXT_LIGHT)])
        
        # Botones ttk
        style.configure("TButton", 
                        background=config.COLOR_SECONDARY, 
                        foreground=config.COLOR_TEXT_LIGHT, 
                        font=config.FONT_BODY_BOLD,
                        borderwidth=0,
                        focuscolor=config.COLOR_ACCENT)
        style.map("TButton",
                  background=[('active', config.COLOR_HOVER)],
                  foreground=[('active', config.COLOR_TEXT_LIGHT)])
        
        # Etiquetas / Frames ttk
        style.configure("TLabel", background=config.COLOR_BG, font=config.FONT_BODY, foreground=config.COLOR_TEXT_DARK)
        style.configure("TFrame", background=config.COLOR_BG)
        style.configure("Card.TFrame", background=config.COLOR_CARD, relief="flat", borderwidth=1)
        
    def build_sidebar(self):
        """Construye el menú lateral con diseño corporativo premium."""
        # Cabecera del Sistema (Logo / Título)
        logo_frame = tk.Frame(self.sidebar_frame, bg=config.COLOR_PRIMARY, pady=25)
        logo_frame.pack(fill="x")
        
        title_label = tk.Label(logo_frame, text="COST ERP", font=("Segoe UI", 20, "bold"), fg=config.COLOR_TEXT_LIGHT, bg=config.COLOR_PRIMARY)
        title_label.pack()
        
        subtitle_label = tk.Label(logo_frame, text="CONTABILIDAD DE COSTOS", font=("Segoe UI", 8, "bold"), fg=config.COLOR_GOLD, bg=config.COLOR_PRIMARY)
        subtitle_label.pack()
        
        # Línea divisoria decorativa
        divider = tk.Frame(self.sidebar_frame, bg=config.COLOR_GOLD, height=3)
        divider.pack(fill="x", padx=15, pady=5)
        
        # Frame contenedor de botones de navegación
        menu_frame = tk.Frame(self.sidebar_frame, bg=config.COLOR_PRIMARY, pady=20)
        menu_frame.pack(fill="both", expand=True)
        
        self.nav_buttons = {}
        
        # Botones de navegación con iconos unicode
        menu_items = [
            ("init", "🏢  Inicialización", self.show_view_init),
            ("warehouse", "📦  Tarjeta de Almacén", self.show_view_warehouse),
            ("ledger", "📖  Diario y Cuentas T", self.show_view_ledger),
            ("automation", "⚡  Autocompletar Ciclo", self.show_view_automation),
            ("reports", "📊  Reportes de Costos", self.show_view_reports)
        ]
        
        for key, text, command in menu_items:
            btn = tk.Button(menu_frame, 
                            text=text, 
                            font=config.FONT_BODY_BOLD, 
                            fg=config.COLOR_TEXT_LIGHT, 
                            bg=config.COLOR_PRIMARY, 
                            activebackground=config.COLOR_SECONDARY, 
                            activeforeground=config.COLOR_TEXT_LIGHT,
                            bd=0, 
                            padx=20, 
                            pady=14, 
                            anchor="w",
                            command=command)
            btn.pack(fill="x", padx=10, pady=4)
            
            # Efecto Hover
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self.on_leave(b, k))
            
            self.nav_buttons[key] = btn
            
        # Footer con estado e información del sistema
        footer_frame = tk.Frame(self.sidebar_frame, bg=config.COLOR_PRIMARY, pady=15)
        footer_frame.pack(side="bottom", fill="x")
        
        # Botón de reinicio completo
        reset_btn = tk.Button(footer_frame, 
                              text="🔄  Reiniciar Todo", 
                              font=("Segoe UI", 9, "bold"), 
                              fg="#F87171", 
                              bg=config.COLOR_PRIMARY, 
                              activebackground=config.COLOR_PRIMARY, 
                              activeforeground="#EF4444",
                              bd=0,
                              command=self.reset_system)
        reset_btn.pack(pady=5)
        
        self.status_label = tk.Label(footer_frame, 
                                     text="Estado: Sin inicializar", 
                                     font=("Segoe UI", 8, "italic"), 
                                     fg=config.COLOR_TEXT_MUTED, 
                                     bg=config.COLOR_PRIMARY)
        self.status_label.pack()
        self.update_status_display()
        
    def on_hover(self, btn):
        """Efecto al pasar el mouse por encima del botón."""
        if btn["bg"] != config.COLOR_SECONDARY:
            btn.configure(bg="#1E293B")
            
    def on_leave(self, btn, key):
        """Efecto al retirar el mouse del botón."""
        if self.active_view != key:
            btn.configure(bg=config.COLOR_PRIMARY)
        else:
            btn.configure(bg=config.COLOR_SECONDARY)
            
    def init_all_views(self):
        """Inicializa las sub-vistas modulares y las monta en el panel de contenido."""
        self.views["init"] = InitView(self.content_frame, self)
        self.views["warehouse"] = WarehouseView(self.content_frame, self)
        self.views["ledger"] = LedgerView(self.content_frame, self)
        self.views["automation"] = AutomationView(self.content_frame, self)
        self.views["reports"] = ReportsView(self.content_frame, self)
        
    def show_view(self, key):
        """Oculta la vista anterior y muestra la nueva pestaña seleccionada."""
        # Desactivar botón anterior
        if self.active_view and self.active_view in self.nav_buttons:
            self.nav_buttons[self.active_view].configure(bg=config.COLOR_PRIMARY, fg=config.COLOR_TEXT_LIGHT)
            
        # Ocultar todas las vistas
        for v in self.views.values():
            v.pack_forget()
            
        # Activar el nuevo botón
        self.active_view = key
        self.nav_buttons[key].configure(bg=config.COLOR_SECONDARY, fg=config.COLOR_GOLD)
        
        # Mostrar nueva vista
        self.views[key].pack(fill="both", expand=True)
        
        # Actualizar datos de la vista antes de pintar
        self.views[key].update_data()
        self.update_status_display()

    # Helpers de navegación
    def show_view_init(self): self.show_view("init")
    def show_view_warehouse(self): self.show_view("warehouse")
    def show_view_ledger(self): self.show_view("ledger")
    def show_view_automation(self): self.show_view("automation")
    def show_view_reports(self): self.show_view("reports")
    
    def update_status_display(self):
        """Actualiza el label indicador de la base de datos."""
        self.db_data = database.load_db()
        if self.db_data.get("practice_project_loaded", False):
            self.status_label.configure(text="✅  Caso de Práctica Activo", fg=config.COLOR_GOLD)
        else:
            self.status_label.configure(text="⚠️  Sin inicializar (Vacío)", fg="#94A3B8")
            
    def refresh_all_views(self):
        """Fuerza a todas las vistas del sistema a refrescar sus datos."""
        self.db_data = database.load_db()
        for v in self.views.values():
            v.update_data()
        self.update_status_display()
        
    def reset_system(self):
        """Limpia la base de datos JSON regresando al estado virgen en blanco."""
        if messagebox.askyesno("Confirmar Reinicio", "¿Estás seguro de que deseas limpiar todo el sistema y borrar todos los asientos y registros del almacén?"):
            database.clear_db()
            self.refresh_all_views()
            self.show_view("init")
            messagebox.showinfo("Reinicio Completado", "El sistema ha sido restablecido a su estado inicial vacío.")
