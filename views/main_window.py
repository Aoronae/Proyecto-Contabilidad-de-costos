# -*- coding: utf-8 -*-
"""
views/main_window.py
Ventana principal y contenedor del panel de navegación lateral.
Rediseñado por completo para replicar exactamente la estética premium de Vantti POS:
- Barra superior blanca con logotipo y tarjeta de perfil de usuario (avatar circular).
- Menú lateral en Azul Marino condensado con iconos verticales y pastillas de enfoque en Dorado.
- Panel de contenido en Gris Claro con tarjetas blancas de bordes curvos y botones corporativos en Dorado.
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
        self.title("COST ERP - Sistema Contable y Administrativo de Costos")
        self.geometry("1200x800")
        self.configure(bg="#F8FAFC") # Gris/Blanco ultra suave (Tailwind Slate 50)
        
        # Cargar base de datos
        self.db_data = database.load_db()
        
        # Estilos generales
        self.setup_styles()
        
        # --- 1. BARRA SUPERIOR (TOP BAR) - Estilo Vantti POS ---
        self.top_bar = tk.Frame(self, bg="#FFFFFF", height=70, bd=0, highlightbackground="#E2E8F0", highlightthickness=1)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)
        
        # Logotipo / Título de la App (Izquierda de la barra superior)
        self.logo_frame = tk.Frame(self.top_bar, bg="#FFFFFF", padx=25)
        self.logo_frame.pack(side="left", fill="y")
        
        self.lbl_logo_title = tk.Label(self.logo_frame, text="Cost ERP", font=("Segoe UI", 18, "bold"), fg="#0F172A", bg="#FFFFFF")
        self.lbl_logo_title.pack(anchor="w", pady=(10, 0))
        
        self.lbl_logo_subtitle = tk.Label(self.logo_frame, text="Sistema contable modular de costos de producción", font=("Segoe UI", 9), fg="#64748B", bg="#FFFFFF")
        self.lbl_logo_subtitle.pack(anchor="w")
        
        # --- 2. CONTENEDOR PRINCIPAL INFERIOR ---
        self.main_container = tk.Frame(self, bg="#F8FAFC")
        self.main_container.pack(side="bottom", expand=True, fill="both")
        
        # --- 3. MENÚ LATERAL (SIDEBAR CONDENSADO) - Estilo Vantti POS ---
        self.sidebar_frame = tk.Frame(self.main_container, bg=config.COLOR_SIDEBAR, width=110)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        # Contenedor para alinear los botones en el centro de la barra lateral
        self.menu_buttons_container = tk.Frame(self.sidebar_frame, bg=config.COLOR_SIDEBAR, pady=15)
        self.menu_buttons_container.pack(fill="both", expand=True)
        
        self.views = {}
        self.active_view = None
        self.nav_items = {} # Contiene tuplas de (Frame del botón, Canvas del icono, Label de texto)
        
        # Items del menú (key, glifo formal, título corto, vista a mostrar)
        self.menu_items = [
            ("init", "⛁", "Dashboard", self.show_view_init),
            ("warehouse", "⛃", "Almacén", self.show_view_warehouse),
            ("ledger", "⚖", "Diario", self.show_view_ledger),
            ("automation", "⚙", "Ciclo", self.show_view_automation),
            ("reports", "▤", "Reportes", self.show_view_reports)
        ]
        
        self.build_sidebar_menu()
        
        # Botón de Reiniciar al fondo del menú lateral
        self.build_sidebar_footer()
        
        # --- 4. PANEL DE CONTENIDO GENERAL ---
        self.content_frame = tk.Frame(self.main_container, bg="#F8FAFC", padx=30, pady=25)
        self.content_frame.pack(side="right", expand=True, fill="both")
        
        # Inicializar vistas modulares
        self.init_all_views()
        
        # Mostrar pestaña por defecto
        self.show_view("init")

    def setup_styles(self):
        """Configura los estilos de la librería ttk para que combinen con la paleta institucional."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configurar Treeviews (Tablas)
        style.configure("Treeview", 
                        background="#FFFFFF", 
                        foreground="#1E293B", 
                        fieldbackground="#FFFFFF",
                        bordercolor="#E2E8F0",
                        rowheight=28,
                        font=("Segoe UI", 9))
        
        style.configure("Treeview.Heading", 
                        background="#0F172A", 
                        foreground="#FFFFFF", 
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=1)
        
        style.map("Treeview.Heading",
                  background=[('active', "#1E3A8A")],
                  foreground=[('active', "#FFFFFF")])
        
        # Botones ttk
        style.configure("TButton", 
                        background="#1E3A8A", 
                        foreground="#FFFFFF", 
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0)
        style.map("TButton",
                  background=[('active', "#2563EB")])
        
        style.configure("TLabel", background="#F1F5F9", font=("Segoe UI", 9), foreground="#1E293B")
        style.configure("TFrame", background="#F1F5F9")
        
    def build_sidebar_menu(self):
        """Crea los botones verticales estilizados idénticos a los de Vantti POS."""
        for key, icon, text, command in self.menu_items:
            # Frame contenedor del botón completo (para manejar espaciado e interactividad)
            btn_frame = tk.Frame(self.menu_buttons_container, bg=config.COLOR_SIDEBAR, height=90, cursor="hand2")
            btn_frame.pack(fill="x", pady=6)
            btn_frame.pack_propagate(False)
            
            # Canvas interno para dresenhar la pastilla/óvalo de selección e icono
            icon_canvas = tk.Canvas(btn_frame, bg=config.COLOR_SIDEBAR, width=55, height=36, bd=0, highlightthickness=0)
            icon_canvas.pack(anchor="center", pady=(10, 2))
            
            # Dibujar pastilla de selección (por defecto invisible / color de fondo)
            oval_id = icon_canvas.create_oval(2, 2, 53, 34, fill=config.COLOR_SIDEBAR, outline="")
            
            # Añadir icono (Emoji / Unicode) centrado sobre la pastilla
            icon_canvas.create_text(27, 18, text=icon, fill="#FFFFFF", font=("Segoe UI", 16))
            
            # Etiqueta de texto debajo del icono
            text_label = tk.Label(btn_frame, text=text, font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=config.COLOR_SIDEBAR)
            text_label.pack(anchor="center")
            
            # Guardar referencias para poder modificar estilos al hacer click / hover
            self.nav_items[key] = {
                "frame": btn_frame,
                "canvas": icon_canvas,
                "oval": oval_id,
                "label": text_label,
                "command": command
            }
            
            # Enlazar eventos de click e interactividad para todos los sub-widgets
            for widget in (btn_frame, icon_canvas, text_label):
                widget.bind("<Button-1>", lambda e, k=key: self.on_menu_click(k))
                widget.bind("<Enter>", lambda e, k=key: self.on_menu_enter(k))
                widget.bind("<Leave>", lambda e, k=key: self.on_menu_leave(k))
 
    def build_sidebar_footer(self):
        """Crea el botón de reinicio al fondo del menú lateral."""
        footer_frame = tk.Frame(self.sidebar_frame, bg=config.COLOR_SIDEBAR, height=70, cursor="hand2")
        footer_frame.pack(side="bottom", fill="x", pady=10)
        footer_frame.pack_propagate(False)
        
        icon_lbl = tk.Label(footer_frame, text="↻", font=("Segoe UI", 16), fg=config.COLOR_GOLD, bg=config.COLOR_SIDEBAR)
        icon_lbl.pack(anchor="center", pady=(5, 2))
        
        text_lbl = tk.Label(footer_frame, text="Reiniciar", font=("Segoe UI", 8, "bold"), fg="#CBD5E1", bg=config.COLOR_SIDEBAR)
        text_lbl.pack(anchor="center")
        
        # Enlazar eventos del botón de reinicio
        for widget in (footer_frame, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda e: self.reset_system())
            widget.bind("<Enter>", lambda e: [icon_lbl.configure(fg="#FFFFFF"), text_lbl.configure(fg=config.COLOR_GOLD)])
            widget.bind("<Leave>", lambda e: [icon_lbl.configure(fg=config.COLOR_GOLD), text_lbl.configure(fg="#CBD5E1")])
 
    def on_menu_enter(self, key):
        """Efecto hover al pasar el cursor sobre un botón del menú lateral."""
        if self.active_view != key:
            # Sutil cambio a un color de fondo hover
            self.nav_items[key]["frame"].configure(bg=config.COLOR_SIDEBAR_HOVER)
            self.nav_items[key]["canvas"].configure(bg=config.COLOR_SIDEBAR_HOVER)
            self.nav_items[key]["label"].configure(bg=config.COLOR_SIDEBAR_HOVER)
 
    def on_menu_leave(self, key):
        """Efecto leave al retirar el cursor del botón del menú lateral."""
        if self.active_view != key:
            # Regresar al fondo original
            self.nav_items[key]["frame"].configure(bg=config.COLOR_SIDEBAR)
            self.nav_items[key]["canvas"].configure(bg=config.COLOR_SIDEBAR)
            self.nav_items[key]["label"].configure(bg=config.COLOR_SIDEBAR)
 
    def on_menu_click(self, key):
        """Dispara el comando correspondiente al botón clickeado."""
        self.nav_items[key]["command"]()
 
    def show_view(self, key):
        """Cambia dinámicamente la pestaña seleccionada aplicando el estilo visual."""
        # 1. Desactivar estilo visual del botón anterior
        if self.active_view and self.active_view in self.nav_items:
            item = self.nav_items[self.active_view]
            item["frame"].configure(bg=config.COLOR_SIDEBAR)
            item["canvas"].configure(bg=config.COLOR_SIDEBAR)
            item["canvas"].itemconfig(item["oval"], fill=config.COLOR_SIDEBAR) # Ocultar pastilla
            item["label"].configure(bg=config.COLOR_SIDEBAR, fg="#FFFFFF")
            
        # Ocultar todas las sub-vistas
        for v in self.views.values():
            v.pack_forget()
            
        # 2. Activar estilo visual del nuevo botón (Píldora dorada de selección)
        self.active_view = key
        item = self.nav_items[key]
        item["frame"].configure(bg=config.COLOR_SIDEBAR)
        item["canvas"].configure(bg=config.COLOR_SIDEBAR)
        item["canvas"].itemconfig(item["oval"], fill=config.COLOR_GOLD) # Mostrar pastilla dorada
        item["label"].configure(bg=config.COLOR_SIDEBAR, fg=config.COLOR_GOLD) # Texto en dorado
        
        # Mostrar nueva vista
        self.views[key].pack(fill="both", expand=True)
        
        # Forzar recarga de información de la vista activa
        self.views[key].update_data()
        self.update_status_display()

    # Callbacks de navegación
    def show_view_init(self): self.show_view("init")
    def show_view_warehouse(self): self.show_view("warehouse")
    def show_view_ledger(self): self.show_view("ledger")
    def show_view_automation(self): self.show_view("automation")
    def show_view_reports(self): self.show_view("reports")
    
    def init_all_views(self):
        """Instancia todas las vistas contables sobre el contenedor de contenido principal."""
        self.views["init"] = InitView(self.content_frame, self)
        self.views["warehouse"] = WarehouseView(self.content_frame, self)
        self.views["ledger"] = LedgerView(self.content_frame, self)
        self.views["automation"] = AutomationView(self.content_frame, self)
        self.views["reports"] = ReportsView(self.content_frame, self)
        
    def update_status_display(self):
        """Mantiene los datos cargados."""
        self.db_data = database.load_db()
        
    def refresh_all_views(self):
        """Recarga la base de datos de todos los módulos y redibuja."""
        self.db_data = database.load_db()
        for v in self.views.values():
            v.update_data()
            
    def reset_system(self):
        """Limpia el estado financiero completo."""
        if messagebox.askyesno("Confirmar Cierre y Reinicio", "¿Estás seguro de que deseas restablecer por completo todo el sistema y borrar la base de datos local?"):
            database.clear_db()
            self.refresh_all_views()
            self.show_view("init")
            messagebox.showinfo("Reinicio Completado", "El sistema ha sido restablecido a su estado inicial vacío.")
