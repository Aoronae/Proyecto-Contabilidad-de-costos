# -*- coding: utf-8 -*-
"""
views/reports_view.py
Vista de Reportes Financieros y Análisis de Costos.
Genera el Estado de Costos de Producción y de lo Vendido, determina el Costo Unitario
y calcula el Punto de Equilibrio con una gráfica explicativa trazada en un Canvas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import models
import database

class ReportsView(tk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=config.COLOR_BG)
        self.main_window = main_window
        
        # Grid layout (Izquierda: Estado de Costos, Derecha: Punto de Equilibrio)
        self.grid_columnconfigure(0, weight=1) # Estado de Costos
        self.grid_columnconfigure(1, weight=1) # Punto de Equilibrio y Gráfico
        self.grid_rowconfigure(0, weight=1)
        
        # --- COLUMNA 1: ESTADO DE COSTOS (IZQUIERDA) ---
        left_panel = tk.Frame(self, bg=config.COLOR_BG, padx=15, pady=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        
        lbl_report_title = tk.Label(left_panel, text="📋  Estado de Costos de Producción y de lo Vendido", font=config.FONT_TITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG)
        lbl_report_title.pack(anchor="w", pady=(0, 10))
        
        # Tarjeta contenedora del reporte financiero formal
        self.report_card = tk.Frame(left_panel, bg=config.COLOR_CARD, bd=1, highlightbackground=config.COLOR_BORDER, highlightthickness=1, padx=20, pady=20)
        self.report_card.pack(fill="both", expand=True)
        
        # Dibujaremos las etiquetas del reporte contable dinámicamente
        self.report_rows = []
        
        # --- COLUMNA 2: PUNTO DE EQUILIBRIO Y GRÁFICA (DERECHA) ---
        right_panel = tk.Frame(self, bg=config.COLOR_BG, padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        lbl_pe_title = tk.Label(right_panel, text="📈  Análisis del Punto de Equilibrio", font=config.FONT_TITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG)
        lbl_pe_title.pack(anchor="w", pady=(0, 10))
        
        # Tarjeta de parámetros del Punto de Equilibrio
        pe_card = tk.LabelFrame(right_panel, 
                                 text=" Variables de Costo y Margen ", 
                                 font=config.FONT_SUBTITLE, 
                                 fg=config.COLOR_SECONDARY, 
                                 bg=config.COLOR_CARD, 
                                 bd=1, 
                                 padx=15, 
                                 pady=10)
        pe_card.pack(fill="x", pady=(0, 10))
        
        # Inputs del PE
        inputs_frame = tk.Frame(pe_card, bg=config.COLOR_CARD)
        inputs_frame.pack(fill="x")
        
        tk.Label(inputs_frame, text="Costos Fijos ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=0, sticky="w", pady=4)
        self.entry_fixed_costs = ttk.Entry(inputs_frame, width=12, font=config.FONT_BODY)
        self.entry_fixed_costs.grid(row=0, column=1, sticky="w", pady=4, padx=8)
        self.entry_fixed_costs.insert(0, "45000.00")
        
        tk.Label(inputs_frame, text="P. Venta Unitario ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=2, sticky="w", pady=4, padx=(15, 0))
        self.entry_unit_price = ttk.Entry(inputs_frame, width=12, font=config.FONT_BODY)
        self.entry_unit_price.grid(row=0, column=3, sticky="w", pady=4, padx=8)
        
        tk.Label(inputs_frame, text="C. Variable Unitario ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=1, column=0, sticky="w", pady=4)
        self.entry_var_cost = ttk.Entry(inputs_frame, width=12, font=config.FONT_BODY)
        self.entry_var_cost.grid(row=1, column=1, sticky="w", pady=4, padx=8)
        
        # Botón Calcular PE
        calc_btn = tk.Button(pe_card, 
                             text="📊  Calcular e Interpolar", 
                             font=config.FONT_BODY_BOLD, 
                             fg=config.COLOR_TEXT_LIGHT, 
                             bg=config.COLOR_SECONDARY, 
                             activebackground=config.COLOR_HOVER, 
                             activeforeground=config.COLOR_TEXT_LIGHT,
                             bd=0, 
                             padx=12, 
                             pady=4,
                             command=self.calculate_break_even)
        calc_btn.pack(side="right", pady=5)
        
        # Panel de Resultados PE
        self.results_frame = tk.Frame(pe_card, bg=config.COLOR_CARD, pady=5)
        self.results_frame.pack(fill="x", side="left")
        
        self.lbl_pe_units = tk.Label(self.results_frame, text="Pto. Equilibrio: -- unidades", font=config.FONT_BODY_BOLD, fg=config.COLOR_GOLD_DARK, bg=config.COLOR_CARD)
        self.lbl_pe_units.pack(anchor="w")
        
        self.lbl_pe_sales = tk.Label(self.results_frame, text="Ventas Requeridas: $ --", font=config.FONT_BODY_BOLD, fg=config.COLOR_PRIMARY, bg=config.COLOR_CARD)
        self.lbl_pe_sales.pack(anchor="w")
        
        # Tarjeta del Gráfico (Canvas de Tkinter estilizado)
        graph_card = tk.Frame(right_panel, bg=config.COLOR_CARD, bd=1, highlightbackground=config.COLOR_GOLD, highlightthickness=1)
        graph_card.pack(fill="both", expand=True)
        
        tk.Label(graph_card, text="Representación Gráfica del Punto de Equilibrio", font=("Segoe UI", 9, "bold"), fg=config.COLOR_PRIMARY, bg=config.COLOR_CARD, pady=5).pack()
        
        self.chart_canvas = tk.Canvas(graph_card, bg=config.COLOR_CARD, bd=0, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        
    def get_financial_data(self):
        """Calcula el estado de costos dinámico de la base de datos."""
        data = database.load_db()
        return models.obtener_estado_costos(data)
        
    def update_data(self):
        """Genera el estado financiero en la pantalla de la izquierda y actualiza los valores del PE."""
        # 1. Dibujar el Estado de Costos
        for widget in self.report_card.winfo_children():
            widget.destroy()
            
        data = database.load_db()
        est = models.obtener_estado_costos(data)
        
        # Renglones y formatos del reporte formal
        # Estructura: (Nombre, Valor, EsNegativo, Indentación, Negrita, DobleSubrayado)
        report_schema = [
            ("Inventario Inicial de Materias Primas", est["inv_ini_mp"], False, 0, False, False),
            ("(+) Compras de Materias Primas", est["compras_mp"], False, 0, False, False),
            ("(=) Materias Primas Disponibles", est["mp_disponible"], False, 1, True, False),
            ("(-) Inventario Final de Materias Primas", est["inv_fin_mp"], True, 0, False, False),
            ("(=) Materia Prima Directa Utilizada", est["mp_utilizada"], False, 1, True, False),
            ("(+) Mano de Obra Directa Aplicada", est["mod_aplicada"], False, 0, False, False),
            ("(+) Cargos Indirectos (GIF) Aplicados", est["gif_applied"] if "gif_applied" in est else est["gif_aplicado"], False, 0, False, False),
            ("(=) Costo de la Producción Procesada", est["costo_produccion_procesada"], False, 1, True, False),
            ("(+) Inventario Inicial de Producción en Proceso", est["inv_ini_pp"], False, 0, False, False),
            ("(-) Inventario Final de Producción en Proceso", est["inv_fin_pp"], True, 0, False, False),
            ("(=) Costo de la Producción Terminada", est["costo_production_terminada"] if "costo_production_terminada" in est else est["costo_produccion_terminada"], False, 2, True, False),
            ("(+) Inventario Inicial de Productos Terminados", est["inv_ini_pt"], False, 0, False, False),
            ("(-) Inventario Final de Productos Terminados", est["inv_fin_pt"], True, 0, False, False),
            ("(=) COSTO DE PRODUCCIÓN DE LO VENDIDO", est["costo_de_lo_vendido"], False, 2, True, True),
        ]
        
        # Título Contable Formal
        tk.Label(self.report_card, text="PROYECTO DE PRÁCTICA DE COSTOS INDUSTRIALES S.A.", font=("Segoe UI", 10, "bold"), fg=config.COLOR_PRIMARY, bg=config.COLOR_CARD).pack()
        tk.Label(self.report_card, text="Estado de Costos de Producción y de lo Vendido", font=("Segoe UI", 9, "bold"), fg=config.COLOR_TEXT_DARK, bg=config.COLOR_CARD).pack()
        tk.Label(self.report_card, text="Del 01 de Mayo al 30 de Mayo de 2026", font=("Segoe UI", 8, "italic"), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD).pack(pady=(0, 15))
        
        # Grid para alinear columnas perfectamente
        table_frame = tk.Frame(self.report_card, bg=config.COLOR_CARD)
        table_frame.pack(fill="x", expand=True)
        table_frame.columnconfigure(0, weight=1) # Concepto
        table_frame.columnconfigure(1, weight=0) # Signo
        table_frame.columnconfigure(2, weight=0) # Importe
        
        for idx, (label, val, is_neg, indent, is_bold, double_under) in enumerate(report_schema):
            font = config.FONT_BODY_BOLD if is_bold else config.FONT_BODY
            fg_col = config.COLOR_PRIMARY if is_bold else config.COLOR_TEXT_DARK
            
            # Sangría para identación
            pad_x = 10 * indent
            
            # Etiqueta Concepto
            lbl_concept = tk.Label(table_frame, text=label, font=font, fg=fg_col, bg=config.COLOR_CARD, anchor="w")
            lbl_concept.grid(row=idx, column=0, sticky="w", padx=(pad_x, 5), pady=2)
            
            # Signo matemático
            sign = "-" if is_neg else ""
            lbl_sign = tk.Label(table_frame, text=sign, font=font, fg=fg_col, bg=config.COLOR_CARD)
            lbl_sign.grid(row=idx, column=1, padx=5, pady=2)
            
            # Importe formateado
            val_str = f"$ {val:,.2f}"
            lbl_val = tk.Label(table_frame, text=val_str, font=font, fg=fg_col, bg=config.COLOR_CARD, anchor="e", width=14)
            lbl_val.grid(row=idx, column=2, sticky="e", padx=(5, 10), pady=2)
            
            if double_under:
                # Doble subrayado para total final
                lbl_val.configure(fg=config.COLOR_GOLD_DARK, font=("Segoe UI", 10, "bold"))
                lbl_concept.configure(fg=config.COLOR_SECONDARY, font=("Segoe UI", 10, "bold"))
                
        # Card del Costo Unitario al final del reporte
        unit_cost_frame = tk.Frame(self.report_card, bg=config.COLOR_BG, bd=1, highlightbackground=config.COLOR_GOLD, highlightthickness=1, pady=8, padx=15)
        unit_cost_frame.pack(fill="x", pady=(20, 0))
        
        prod_obj = data["config_costos"].get("produccion_objetivo", 500)
        tk.Label(unit_cost_frame, text=f"Volumen Producido: {prod_obj} unidades", font=("Segoe UI", 8, "bold"), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_BG).pack(side="left")
        
        cost_unitario = est.get("costo_unitario", 0.0)
        tk.Label(unit_cost_frame, text=f"COSTO UNITARIO DE PRODUCCIÓN: $ {cost_unitario:,.2f}", font=("Segoe UI", 9, "bold"), fg=config.COLOR_PRIMARY, bg=config.COLOR_BG).pack(side="right")
        
        # 2. Inicializar inputs de Punto de Equilibrio
        cfg = data.get("config_costos", {})
        self.entry_unit_price.delete(0, tk.END)
        self.entry_unit_price.insert(0, f"{cfg.get('precio_venta', 350.0):.2f}")
        
        self.entry_var_cost.delete(0, tk.END)
        # Por defecto, el costo variable es el Costo Unitario calculado de producción!
        self.entry_var_cost.insert(0, f"{cost_unitario:.2f}")
        
        # Calcular PE e Interpolar
        self.calculate_break_even()
        
    def calculate_break_even(self):
        """Realiza los cálculos del punto de equilibrio e invoca el renderizado de la gráfica."""
        try:
            fc = float(self.entry_fixed_costs.get())
            price = float(self.entry_unit_price.get())
            vc = float(self.entry_var_cost.get())
            
            if price <= vc:
                messagebox.showerror("Margen de Contribución Negativo", "El Precio de Venta debe ser mayor al Costo Variable Unitario.\nDe lo contrario, no existe un Punto de Equilibrio y la empresa incurrirá en pérdidas infinitas.")
                return
                
            margin = price - vc
            pe_units = fc / margin
            pe_sales = pe_units * price
            
            # Actualizar etiquetas
            self.lbl_pe_units.configure(text=f"Pto. Equilibrio: {pe_units:,.1f} unidades", fg=config.COLOR_GOLD_DARK)
            self.lbl_pe_sales.configure(text=f"Ventas Requeridas: $ {pe_sales:,.2f}")
            
            # Dibujar gráfica en el canvas
            self.draw_pe_chart(fc, price, vc, pe_units)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor introduce valores numéricos correctos para el cálculo.")
            
    def draw_pe_chart(self, fc, price, vc, pe_units):
        """Dibuja de forma gráfica y estilizada la gráfica del Punto de Equilibrio en el Canvas."""
        self.chart_canvas.delete("all")
        
        # Obtener dimensiones
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        
        if w < 50 or h < 50:
            # Fallback en caso de que no esté completamente montada la ventana en pixeles
            w = 400
            h = 280
            
        # Márgenes
        mx_left = 60
        mx_right = 30
        my_top = 20
        my_bottom = 45
        
        # Área de dibujo útil
        gw = w - mx_left - mx_right
        gh = h - my_top - my_bottom
        
        # Rango del eje X (desde 0 hasta PE * 1.8 para dar perspectiva)
        max_units = int(pe_units * 1.8) if pe_units > 0 else 1000
        if max_units == 0: max_units = 1000
        
        # Rango del eje Y (Ingresos totales al max_units)
        max_sales = max_units * price
        if max_sales == 0: max_sales = 100000
        
        # Funciones de conversión a píxeles en pantalla (origen abajo a la izquierda)
        def to_px(units, amount):
            px_x = mx_left + (units / max_units) * gw
            px_y = (my_top + gh) - (amount / max_sales) * gh
            return px_x, px_y
            
        # 1. Dibujar Cuadrícula y Ejes
        self.chart_canvas.create_line(mx_left, my_top, mx_left, my_top + gh, fill=config.COLOR_BORDER, width=2) # Eje Y
        self.chart_canvas.create_line(mx_left, my_top + gh, mx_left + gw, my_top + gh, fill=config.COLOR_BORDER, width=2) # Eje X
        
        # Etiquetas del Eje Y
        for i in range(5):
            val = (max_sales / 4) * i
            px_x, px_y = to_px(0, val)
            self.chart_canvas.create_text(px_x - 8, px_y, text=f"${val/1000:,.0f}k", anchor="e", font=("Segoe UI", 7), fill=config.COLOR_TEXT_MUTED)
            self.chart_canvas.create_line(mx_left, px_y, mx_left + gw, px_y, fill=config.COLOR_BG, width=1) # Rejilla horizontal
            
        # Etiquetas del Eje X
        for i in range(5):
            val = (max_units / 4) * i
            px_x, px_y = to_px(val, 0)
            self.chart_canvas.create_text(px_x, px_y + 12, text=f"{val:,.0f}", anchor="n", font=("Segoe UI", 7), fill=config.COLOR_TEXT_MUTED)
            self.chart_canvas.create_line(px_x, my_top, px_x, my_top + gh, fill=config.COLOR_BG, width=1) # Rejilla vertical
            
        # Nombre de los ejes
        self.chart_canvas.create_text(mx_left - 35, my_top + gh/2, text="Valores ($)", angle=90, anchor="center", font=("Segoe UI", 8, "bold"), fill=config.COLOR_TEXT_DARK)
        self.chart_canvas.create_text(mx_left + gw/2, my_top + gh + 28, text="Unidades de Producción", anchor="center", font=("Segoe UI", 8, "bold"), fill=config.COLOR_TEXT_DARK)
        
        # 2. Dibujar Líneas Financieras
        # A. Costo Fijo (Línea horizontal en color rojo o dorado)
        p1_cf = to_px(0, fc)
        p2_cf = to_px(max_units, fc)
        self.chart_canvas.create_line(p1_cf[0], p1_cf[1], p2_cf[0], p2_cf[1], fill="#94A3B8", width=2, dash=(4, 4))
        self.chart_canvas.create_text(p2_cf[0] - 5, p2_cf[1] - 8, text="Costos Fijos", anchor="e", font=("Segoe UI", 7, "bold"), fill="#64748B")
        
        # B. Ingreso Total (Ventas = Unidades * Precio de Venta) - Color Royal Blue
        p1_in = to_px(0, 0)
        p2_in = to_px(max_units, max_units * price)
        self.chart_canvas.create_line(p1_in[0], p1_in[1], p2_in[0], p2_in[1], fill=config.COLOR_SECONDARY, width=3)
        self.chart_canvas.create_text(p2_in[0] - 5, p2_in[1] - 10, text="Ventas", anchor="e", font=("Segoe UI", 8, "bold"), fill=config.COLOR_SECONDARY)
        
        # C. Costo Total (Costos Fijos + Unidades * Costo Variable) - Color Rojo/Slate
        p1_ct = to_px(0, fc)
        p2_ct = to_px(max_units, fc + (max_units * vc))
        self.chart_canvas.create_line(p1_ct[0], p1_ct[1], p2_ct[0], p2_ct[1], fill="#EF4444", width=3)
        self.chart_canvas.create_text(p2_ct[0] - 5, p2_ct[1] + 10, text="Costo Total", anchor="e", font=("Segoe UI", 8, "bold"), fill="#B91C1C")
        
        # 3. Marcar el Punto de Equilibrio (Intersección de Ventas y Costo Total)
        px_pe = to_px(pe_units, pe_units * price)
        
        # Líneas de referencia punteadas en dorado
        self.chart_canvas.create_line(px_pe[0], px_pe[1], px_pe[0], my_top + gh, fill=config.COLOR_GOLD, width=1, dash=(3, 3)) # Hacia abajo X
        self.chart_canvas.create_line(px_pe[0], px_pe[1], mx_left, px_pe[1], fill=config.COLOR_GOLD, width=1, dash=(3, 3)) # Hacia izquierda Y
        
        # Círculo destacado en Dorado
        r = 6
        self.chart_canvas.create_oval(px_pe[0]-r, px_pe[1]-r, px_pe[0]+r, px_pe[1]+r, fill=config.COLOR_GOLD, outline=config.COLOR_PRIMARY, width=2)
        
        # Globo de texto decorativo
        self.chart_canvas.create_text(px_pe[0] + 12, px_pe[1] - 15, text=f"PE ({pe_units:.0f} un.)", anchor="w", font=("Segoe UI", 9, "bold"), fill=config.COLOR_GOLD_DARK)
