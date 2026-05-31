# -*- coding: utf-8 -*-
"""
views/automation_view.py
Vista de automatización de ciclos de costos. Permite ejecutar el ciclo contable
completo (traspasos de MPD, aplicación de MOD, GIF, traspaso a PT y Costo de Ventas)
con base en parámetros objetivo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import models
import database

class AutomationView(tk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=config.COLOR_BG)
        self.main_window = main_window
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabecera
        header_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, padx=25, pady=20)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        header_label = tk.Label(header_frame, 
                                text="AUTOMATIZACIÓN DEL CICLO DE COSTOS", 
                                font=config.FONT_TITLE, 
                                fg=config.COLOR_TEXT_LIGHT, 
                                bg=config.COLOR_PRIMARY)
        header_label.pack(anchor="w")
        
        subheader_label = tk.Label(header_frame, 
                                   text="Simulador Inteligente: Ejecuta traspasos de producción y determina costos unitarios de forma automática", 
                                   font=config.FONT_BODY, 
                                   fg=config.COLOR_GOLD, 
                                   bg=config.COLOR_PRIMARY)
        subheader_label.pack(anchor="w", pady=(2, 0))
        
        # 2. Parámetros de Simulación (Fila 1)
        params_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=15)
        params_frame.grid(row=1, column=0, sticky="ew")
        
        # Tarjeta de parámetros
        config_card = tk.LabelFrame(params_frame, 
                                    text=" Parámetros del Proyecto de Producción Objetivo ", 
                                    font=config.FONT_SUBTITLE, 
                                    fg=config.COLOR_SECONDARY, 
                                    bg=config.COLOR_CARD, 
                                    bd=1, 
                                    padx=20, 
                                    pady=15)
        config_card.pack(fill="x", expand=True)
        
        # Contenedor inputs
        inputs_row = tk.Frame(config_card, bg=config.COLOR_CARD)
        inputs_row.pack(fill="x", pady=5)
        
        # Objetivo de Producción (Unidades)
        tk.Label(inputs_row, text="Producción Objetivo (un.):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_target_qty = ttk.Entry(inputs_row, width=12, font=config.FONT_BODY)
        self.entry_target_qty.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        
        # Precio de Venta
        tk.Label(inputs_row, text="Precio de Venta Unitario ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.entry_price = ttk.Entry(inputs_row, width=12, font=config.FONT_BODY)
        self.entry_price.grid(row=0, column=3, sticky="w", pady=5, padx=10)
        
        # MOD unitario
        tk.Label(inputs_row, text="Costo Unitario MOD ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_mod = ttk.Entry(inputs_row, width=12, font=config.FONT_BODY)
        self.entry_mod.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        
        # GIF unitario
        tk.Label(inputs_row, text="Costo Unitario GIF ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.entry_gif = ttk.Entry(inputs_row, width=12, font=config.FONT_BODY)
        self.entry_gif.grid(row=1, column=3, sticky="w", pady=5, padx=10)
        
        # Cargar valores por defecto
        self.reset_defaults()
        
        # Botón de Automatización (Estilo Vantti POS: Dorado con texto oscuro)
        self.auto_btn = tk.Button(config_card, 
                                  text="⚡  Autocompletar Ciclo de Costos", 
                                  font=config.FONT_BODY_BOLD, 
                                  fg=config.COLOR_PRIMARY, 
                                  bg=config.COLOR_GOLD, 
                                  activebackground="#F59E0B", 
                                  activeforeground=config.COLOR_PRIMARY,
                                  bd=0, 
                                  padx=25, 
                                  pady=14,
                                  command=self.run_automation)
        self.auto_btn.pack(side="bottom", anchor="e", pady=(15, 0))
        
        # 3. Diagrama Visual del Flujo de Costos (Fila 2)
        flow_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=10)
        flow_frame.grid(row=2, column=0, sticky="nsew")
        
        lbl_flow_title = tk.Label(flow_frame, text="Diagrama de Flujo del Costo Contable (Proceso Industrial)", font=config.FONT_SUBTITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG)
        lbl_flow_title.pack(anchor="w", pady=(0, 10))
        
        # Contenedor gráfico del diagrama
        self.diagram_canvas = tk.Frame(flow_frame, bg=config.COLOR_CARD, bd=1, highlightbackground=config.COLOR_GOLD, highlightthickness=1)
        self.diagram_canvas.pack(fill="both", expand=True)
        
        self.build_flow_diagram()
        
    def reset_defaults(self):
        """Restablece los inputs a los valores del caso práctico académico."""
        self.entry_target_qty.delete(0, tk.END)
        self.entry_target_qty.insert(0, "500")
        
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, "350.00")
        
        self.entry_mod.delete(0, tk.END)
        self.entry_mod.insert(0, "40.00")
        
        self.entry_gif.delete(0, tk.END)
        self.entry_gif.insert(0, "20.00")
        
    def run_automation(self):
        """Ejecuta la lógica del ciclo de costos automático en los modelos contables."""
        qty_str = self.entry_target_qty.get().strip()
        price_str = self.entry_price.get().strip()
        mod_str = self.entry_mod.get().strip()
        gif_str = self.entry_gif.get().strip()
        
        # Validar entradas
        try:
            qty = int(qty_str)
            price = float(price_str)
            mod = float(mod_str)
            gif = float(gif_str)
            
            if qty <= 0 or price <= 0 or mod <= 0 or gif <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Parámetros", "Todos los parámetros deben ser números válidos mayores a cero.\nLa cantidad debe ser entera.")
            return
            
        data = database.load_db()
        
        # Validar si el proyecto está cargado (necesitamos la MP del Proyecto de Práctica)
        if not data.get("practice_project_loaded", False):
            # Cargar de forma automática el caso de práctica para evitar que truene
            models.cargar_proyecto_practica(data)
            
        try:
            # Ejecutar ciclo
            models.autocompletar_ciclo_costos(data, qty, price, mod, gif)
            
            messagebox.showinfo("Ciclo Completado", 
                                f"¡Ciclo de Costos finalizado con éxito para {qty} unidades!\n\n"
                                "Asientos automáticos registrados en el Diario:\n"
                                " 1. Consumo de MPD (Almacén MP ➔ Producción Proceso)\n"
                                " 2. Aplicación de Mano de Obra (MOD)\n"
                                " 3. Aplicación de Gastos Indirectos (GIF)\n"
                                " 4. Traspaso a Producto Terminado (PP ➔ Almacén PT)\n"
                                " 5. Venta del periodo e ingreso a Bancos\n"
                                " 6. Costo de lo Vendido registrado")
            
            self.main_window.refresh_all_views()
            # Navegar a la pestaña de reportes de inmediato para ver los resultados!
            self.main_window.show_view("reports")
            
        except Exception as e:
            messagebox.showerror("Error de Ejecución", str(e))
            
    def build_flow_diagram(self):
        """Construye el diagrama visual usando cajones y flechas en un layout responsivo."""
        # Limpiar
        for widget in self.diagram_canvas.winfo_children():
            widget.destroy()
            
        # Contenedor central
        container = tk.Frame(self.diagram_canvas, bg=config.COLOR_CARD, pady=40)
        container.pack(expand=True)
        
        # Definición de cajas del flujo contable industrial (Textos ultra simplificados y limpios)
        steps = [
            ("1. COMPRA MP", "Almacén de MP\n(1151)", "Inventario inicial y\ncompras de materias primas", config.COLOR_PRIMARY),
            ("➔", "Traspaso MPD\n(Consumo)", "Costo Promedio", config.COLOR_GOLD_DARK),
            ("2. PRODUCCIÓN", "Producción en Proceso\n(1152)", "Consumo acumulado +\nnómina MOD + cargos GIF", config.COLOR_SECONDARY),
            ("➔", "Traspaso PT\n(Costo Terminado)", "Costo Unitario real", config.COLOR_GOLD_DARK),
            ("3. PRODUCTO FIN", "Almacén de PT\n(1153)", "Almacenamiento de\nproductos terminados", config.COLOR_PRIMARY),
            ("➔", "Costo de Ventas\n(Salida PT)", "Valuación de salidas", config.COLOR_GOLD_DARK),
            ("4. REPORTES", "Costo de lo Vendido\n(5101)", "Reflejado en el Estado\nde Resultados final", config.COLOR_SECONDARY)
        ]
        
        for idx, (label, title, desc, col) in enumerate(steps):
            if label == "➔":
                # Flecha indicadora
                arrow_frame = tk.Frame(container, bg=config.COLOR_CARD)
                arrow_frame.pack(side="left", padx=10)
                
                tk.Label(arrow_frame, text=label, font=("Segoe UI", 24, "bold"), fg=col, bg=config.COLOR_CARD).pack()
                tk.Label(arrow_frame, text=title, font=("Segoe UI", 7, "bold"), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD).pack()
            else:
                # Caja de paso del costo
                box = tk.Frame(container, bg=config.COLOR_CARD, bd=1, highlightbackground=config.COLOR_BORDER, highlightthickness=1, width=170, height=140)
                box.pack(side="left", padx=5)
                box.pack_propagate(False)
                
                # Cabecera de la caja
                tk.Label(box, text=label, font=("Segoe UI", 8, "bold"), fg=config.COLOR_TEXT_LIGHT, bg=col, pady=4).pack(fill="x")
                
                # Título (Cuenta contable)
                tk.Label(box, text=title, font=("Segoe UI", 10, "bold"), fg=config.COLOR_TEXT_DARK, bg=config.COLOR_CARD, pady=8).pack()
                
                # Descripción técnica
                tk.Label(box, text=desc, font=("Segoe UI", 8), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD, justify="center", wraplength=150).pack()
                
        # Nota explicativa de MOD/GIF
        notes_frame = tk.Frame(self.diagram_canvas, bg=config.COLOR_CARD, pady=10)
        notes_frame.pack(fill="x", side="bottom")
        
        tk.Label(notes_frame, 
                 text="💡 Nota: Los cargos de Mano de Obra Directa (MOD) y Cargos Indirectos (GIF) se inyectan directamente en el paso '2. PRODUCCIÓN' para acumular el Costo de Fabricación.", 
                 font=("Segoe UI", 9, "italic"), 
                 fg=config.COLOR_TEXT_MUTED, 
                 bg=config.COLOR_CARD).pack()
                 
    def update_data(self):
        """Actualiza la vista recuperando la configuración actual en la base de datos."""
        data = database.load_db()
        config_costos = data.get("config_costos", {})
        
        if config_costos:
            # Rellenar con los últimos valores guardados
            self.entry_target_qty.delete(0, tk.END)
            self.entry_target_qty.insert(0, str(config_costos.get("produccion_objetivo", 500)))
            
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, f"{config_costos.get('precio_venta', 350.0):.2f}")
            
            # Nota: MOD y GIF los dejamos estables o prellenados en base a lo que se tenga en el caso
            # para no recalcular variables no guardadas.
