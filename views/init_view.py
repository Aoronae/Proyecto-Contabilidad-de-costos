# -*- coding: utf-8 -*-
"""
views/init_view.py
Vista de inicialización del sistema. Muestra el Catálogo de Cuentas Contables y 
alberga el botón para cargar el Proyecto de Práctica con datos simulados.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import models
import database

class InitView(tk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=config.COLOR_BG)
        self.main_window = main_window
        
        # Margen general
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabecera de la Vista
        header_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, padx=25, pady=20)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        header_label = tk.Label(header_frame, 
                                text="INICIALIZACIÓN DEL SISTEMA Y CATÁLOGO DE CUENTAS", 
                                font=config.FONT_TITLE, 
                                fg=config.COLOR_TEXT_LIGHT, 
                                bg=config.COLOR_PRIMARY)
        header_label.pack(anchor="w")
        
        subheader_label = tk.Label(header_frame, 
                                   text="Configura los saldos iniciales del ERP o carga un caso práctico de simulación", 
                                   font=config.FONT_BODY, 
                                   fg=config.COLOR_GOLD, 
                                   bg=config.COLOR_PRIMARY)
        subheader_label.pack(anchor="w", pady=(2, 0))
        
        # 2. Panel Informativo y Acciones (Fila 1)
        actions_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=15)
        actions_frame.grid(row=1, column=0, sticky="ew")
        
        # Tarjeta de Carga de Proyecto de Práctica (Aesthetics: Card con borde dorado)
        practice_card = tk.LabelFrame(actions_frame, 
                                      text=" Caso Práctico Académico / Profesional ", 
                                      font=config.FONT_SUBTITLE, 
                                      fg=config.COLOR_SECONDARY, 
                                      bg=config.COLOR_CARD, 
                                      bd=2, 
                                      relief="groove", 
                                      padx=20, 
                                      pady=15)
        practice_card.pack(fill="x", expand=True)
        
        # Nota explicativa simplificada y amigable
        explanation_text = (
            "¡Bienvenido a Cost ERP! Para comenzar a explorar las simulaciones de inmediato,\n"
            "presiona el botón de la derecha para cargar el caso práctico escolar preconfigurado."
        )
        explanation_label = tk.Label(practice_card, 
                                     text=explanation_text, 
                                     font=config.FONT_BODY, 
                                     fg=config.COLOR_TEXT_DARK, 
                                     bg=config.COLOR_CARD, 
                                     justify="left")
        explanation_label.pack(side="left", anchor="w", pady=5)
        
        # Botón Institucional de Carga (Estilo Vantti POS: Dorado con texto oscuro)
        self.load_btn = tk.Button(practice_card, 
                                  text="🚀  Cargar Proyecto de Práctica", 
                                  font=config.FONT_BODY_BOLD, 
                                  fg=config.COLOR_PRIMARY, 
                                  bg=config.COLOR_GOLD, 
                                  activebackground="#F59E0B", 
                                  activeforeground=config.COLOR_PRIMARY,
                                  bd=0, 
                                  padx=20, 
                                  pady=12,
                                  relief="flat",
                                  command=self.load_practice)
        self.load_btn.pack(side="right", padx=20)
        
        # 3. Catálogo de Cuentas (Fila 2 - Rellena el espacio)
        catalog_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=10)
        catalog_frame.grid(row=2, column=0, sticky="nsew")
        
        catalog_title = tk.Label(catalog_frame, 
                                 text="Catálogo de Cuentas Contables y Saldos en Tiempo Real", 
                                 font=config.FONT_SUBTITLE, 
                                 fg=config.COLOR_PRIMARY, 
                                 bg=config.COLOR_BG)
        catalog_title.pack(anchor="w", pady=(0, 5))
        
        # Tabla (Treeview)
        cols = ("Código", "Nombre de la Cuenta", "Tipo", "Naturaleza", "Saldo Actual")
        self.tree = ttk.Treeview(catalog_frame, columns=cols, show="headings", selectmode="browse")
        
        # Definir anchos y alineación
        self.tree.column("Código", width=80, anchor="center")
        self.tree.column("Nombre de la Cuenta", width=300, anchor="w")
        self.tree.column("Tipo", width=120, anchor="center")
        self.tree.column("Naturaleza", width=120, anchor="center")
        self.tree.column("Saldo Actual", width=150, anchor="e")
        
        # Cabeceras
        for col in cols:
            self.tree.heading(col, text=col)
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(catalog_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def load_practice(self):
        """Dispara la carga de datos simulados en la base de datos."""
        try:
            data = database.load_db()
            data = models.cargar_proyecto_practica(data)
            self.main_window.refresh_all_views()
            messagebox.showinfo("Éxito", "¡Caso práctico cargado correctamente!\nLos saldos y la tarjeta de almacén han sido inicializados.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al inicializar el proyecto: {e}")
            
    def update_data(self):
        """Refresca la tabla del catálogo con los saldos vigentes."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = database.load_db()
        saldos = data.get("saldos", {})
        
        # Ordenar cuentas por código
        for code in sorted(config.CATALOGO_CUENTAS.keys()):
            info = config.CATALOGO_CUENTAS[code]
            saldo = saldos.get(code, 0.0)
            saldo_str = f"$ {saldo:,.2f}" if saldo > 0 else "$ 0.00"
            
            # Insertar en tabla
            self.tree.insert("", "end", values=(
                code,
                info["nombre"],
                info["tipo"],
                info["naturaleza"],
                saldo_str
            ))
            
        # Si el proyecto de práctica ya está cargado, deshabilitar botón o cambiar texto
        if data.get("practice_project_loaded", False):
            self.load_btn.configure(text="✅  Proyecto de Práctica Cargado", bg=config.COLOR_PRIMARY, state="disabled")
        else:
            self.load_btn.configure(text="🚀  Cargar Proyecto de Práctica", bg=config.COLOR_GOLD, state="normal")
