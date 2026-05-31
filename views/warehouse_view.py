# -*- coding: utf-8 -*-
"""
views/warehouse_view.py
Vista de Tarjeta de Almacén de Materias Primas.
Permite el control de inventario utilizando el Método de Costo Promedio Ponderado (CPP).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
import models
import database

class WarehouseView(tk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=config.COLOR_BG)
        self.main_window = main_window
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # 1. Cabecera
        header_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, padx=25, pady=20)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        header_label = tk.Label(header_frame, 
                                text="TARJETA DE ALMACÉN DE MATERIAS PRIMAS", 
                                font=config.FONT_TITLE, 
                                fg=config.COLOR_TEXT_LIGHT, 
                                bg=config.COLOR_PRIMARY)
        header_label.pack(anchor="w")
        
        subheader_label = tk.Label(header_frame, 
                                   text="Valuación de Inventarios en Tiempo Real - Método de Costo Promedio Ponderado", 
                                   font=config.FONT_BODY, 
                                   fg=config.COLOR_GOLD, 
                                   bg=config.COLOR_PRIMARY)
        subheader_label.pack(anchor="w", pady=(2, 0))
        
        # 2. Panel de Indicadores Clave (KPIs)
        self.kpi_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=10)
        self.kpi_frame.grid(row=1, column=0, sticky="ew")
        
        self.build_kpis()
        
        # 3. Formulario de Transacciones (Mitad Izquierda) y Explicación (Mitad Derecha)
        middle_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=10)
        middle_frame.grid(row=2, column=0, sticky="ew")
        
        # Formulario
        form_frame = tk.LabelFrame(middle_frame, 
                                   text=" Registrar Movimiento de Almacén ", 
                                   font=config.FONT_SUBTITLE, 
                                   fg=config.COLOR_SECONDARY, 
                                   bg=config.COLOR_CARD, 
                                   bd=1, 
                                   padx=15, 
                                   pady=10)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Inputs
        tk.Label(form_frame, text="Fecha:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = ttk.Entry(form_frame, font=config.FONT_BODY)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        self.reset_date()
        
        tk.Label(form_frame, text="Tipo Movimiento:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=0, column=2, sticky="w", pady=5, padx=(15, 0))
        self.type_combo = ttk.Combobox(form_frame, values=["Entrada (Compra)", "Salida (Consumo)"], state="readonly", width=18, font=config.FONT_BODY)
        self.type_combo.current(0)
        self.type_combo.grid(row=0, column=3, sticky="w", pady=5, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        
        tk.Label(form_frame, text="Concepto:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=1, column=0, sticky="w", pady=5)
        self.concept_entry = ttk.Entry(form_frame, width=22, font=config.FONT_BODY)
        self.concept_entry.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        tk.Label(form_frame, text="Cantidad (Unidades):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=1, column=2, sticky="w", pady=5, padx=(15, 0))
        self.qty_entry = ttk.Entry(form_frame, width=12, font=config.FONT_BODY)
        self.qty_entry.grid(row=1, column=3, sticky="w", pady=5, padx=5)
        
        tk.Label(form_frame, text="Costo Unitario ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).grid(row=2, column=0, sticky="w", pady=5)
        self.cost_entry = ttk.Entry(form_frame, width=15, font=config.FONT_BODY)
        self.cost_entry.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        # Botón de Registro
        reg_btn = tk.Button(form_frame, 
                            text="💾  Registrar en Almacén", 
                            font=config.FONT_BODY_BOLD, 
                            fg=config.COLOR_TEXT_LIGHT, 
                            bg=config.COLOR_SECONDARY, 
                            activebackground=config.COLOR_HOVER, 
                            activeforeground=config.COLOR_TEXT_LIGHT,
                            bd=0, 
                            padx=15, 
                            pady=6,
                            command=self.save_transaction)
        reg_btn.grid(row=2, column=2, columnspan=2, sticky="e", pady=5, padx=5)
        
        # Tarjeta explicativa de Fórmulas
        formula_frame = tk.LabelFrame(middle_frame, 
                                      text=" Fórmulas Contables Aplicadas ", 
                                      font=config.FONT_SUBTITLE, 
                                      fg=config.COLOR_GOLD_DARK, 
                                      bg=config.COLOR_CARD, 
                                      bd=1, 
                                      padx=15, 
                                      pady=10,
                                      width=380)
        formula_frame.pack_propagate(False)
        formula_frame.pack(side="right", fill="both")
        
        formula_text = (
            "1. Entrada: Aumenta la existencia y el saldo.\n"
            "   Costo Unitario es el precio de adquisición.\n\n"
            "2. Costo Promedio Ponderado:\n"
            "   Costo Promedio = Saldo Valores Total / Existencia Total\n\n"
            "3. Salida: Disminuye la existencia y el saldo.\n"
            "   Valuación al último Costo Promedio calculado."
        )
        tk.Label(formula_frame, text=formula_text, font=("Segoe UI", 9), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD, justify="left").pack(anchor="w")
        
        # 4. Tabla de Tarjeta de Almacén (Fila 3)
        table_frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=10)
        table_frame.grid(row=3, column=0, sticky="nsew")
        
        cols = ("Fecha", "Concepto", "Movimiento", "Cant. E/S", "Costo Unitario", "Debe", "Haber", "Existencia", "Saldo Valores", "Costo Promedio")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        # Ancho y alineaciones de columnas
        column_widths = {
            "Fecha": 80, "Concepto": 150, "Movimiento": 80, "Cant. E/S": 80,
            "Costo Unitario": 90, "Debe": 100, "Haber": 100, "Existencia": 80,
            "Saldo Valores": 110, "Costo Promedio": 100
        }
        column_aligns = {
            "Fecha": "center", "Concepto": "w", "Movimiento": "center", "Cant. E/S": "center",
            "Costo Unitario": "e", "Debe": "e", "Haber": "e", "Existencia": "center",
            "Saldo Valores": "e", "Costo Promedio": "e"
        }
        
        for col in cols:
            self.tree.column(col, width=column_widths[col], anchor=column_aligns[col])
            self.tree.heading(col, text=col)
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def build_kpis(self):
        """Dibuja las tarjetas KPI de Almacén con bordes dorados."""
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()
            
        kpis = [
            ("EXISTENCIA ACTUAL", "0 unidades", "existencia", config.COLOR_PRIMARY),
            ("COSTO PROMEDIO CPP", "$ 0.00", "cpp", config.COLOR_GOLD_DARK),
            ("VALOR TOTAL EN ALMACÉN", "$ 0.00", "valor", config.COLOR_SECONDARY)
        ]
        
        self.kpi_labels = {}
        
        for title, value, key, color in kpis:
            card = tk.Frame(self.kpi_frame, bg=config.COLOR_CARD, highlightbackground=config.COLOR_GOLD, highlightthickness=1, padx=20, pady=10)
            card.pack(side="left", fill="both", expand=True, padx=5)
            
            lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD)
            lbl_title.pack(anchor="w")
            
            lbl_val = tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), fg=color, bg=config.COLOR_CARD)
            lbl_val.pack(anchor="w", pady=(2, 0))
            
            self.kpi_labels[key] = lbl_val
            
    def reset_date(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
    def on_type_change(self, event=None):
        """Habilita o deshabilita la caja de costo unitario según el tipo de movimiento."""
        mov_type = self.type_combo.get()
        if "Salida" in mov_type:
            self.cost_entry.delete(0, tk.END)
            # Mostrar último costo promedio si existe
            data = database.load_db()
            if data["almacen"]:
                cpp = data["almacen"][-1]["costo_promedio"]
                self.cost_entry.insert(0, f"{cpp:.2f}")
            else:
                self.cost_entry.insert(0, "0.00")
            self.cost_entry.configure(state="disabled")
        else:
            self.cost_entry.configure(state="normal")
            self.cost_entry.delete(0, tk.END)
            
    def save_transaction(self):
        """Valida y guarda la transacción de almacén, actualizando la base de datos."""
        fecha = self.date_entry.get().strip()
        concepto = self.concept_entry.get().strip()
        mov_type = self.type_combo.get()
        qty_str = self.qty_entry.get().strip()
        cost_str = self.cost_entry.get().strip()
        
        # Validaciones de entrada
        if not concepto:
            messagebox.showerror("Error de Entrada", "Debes ingresar un Concepto para la transacción.")
            return
            
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError("La cantidad debe ser un entero positivo.")
        except ValueError:
            messagebox.showerror("Error de Entrada", "Cantidad inválida. Debe ser un número entero mayor a cero.")
            return
            
        data = database.load_db()
        
        try:
            if "Entrada" in mov_type:
                try:
                    cost = float(cost_str)
                    if cost <= 0:
                        raise ValueError("El costo debe ser positivo.")
                except ValueError:
                    messagebox.showerror("Error de Entrada", "Costo Unitario inválido. Debe ser un número decimal mayor a cero.")
                    return
                
                models.registrar_entrada_almacen(data, fecha, concepto, qty, cost)
                messagebox.showinfo("Registro Exitoso", f"Entrada registrada: {qty} un. de '{concepto}' a ${cost:.2f} c/u.")
            else:
                # Salida
                models.registrar_salida_almacen(data, fecha, concepto, qty)
                messagebox.showinfo("Registro Exitoso", f"Salida contable registrada: {qty} un. de '{concepto}' consumida en producción.")
                
            # Limpiar formulario
            self.concept_entry.delete(0, tk.END)
            self.qty_entry.delete(0, tk.END)
            self.on_type_change() # Reset de estado del costo
            
            # Recargar ventana entera
            self.main_window.refresh_all_views()
            
        except Exception as e:
            messagebox.showerror("Error Contable", str(e))
            
    def update_data(self):
        """Refresca la tarjeta de almacén y las tarjetas KPI."""
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = database.load_db()
        almacen = data.get("almacen", [])
        
        for item in almacen:
            cant_str = f"+{item['cantidad']}" if item["tipo"] == "Entrada" else f"-{item['cantidad']}"
            debe_str = f"$ {item['debe']:,.2f}" if item["debe"] > 0 else "-"
            haber_str = f"$ {item['haber']:,.2f}" if item["haber"] > 0 else "-"
            cost_str = f"$ {item['costo_unitario']:,.2f}"
            saldo_str = f"$ {item['saldo_valores']:,.2f}"
            prom_str = f"$ {item['costo_promedio']:,.4f}"
            
            self.tree.insert("", "end", values=(
                item["fecha"],
                item["concepto"],
                item["tipo"],
                cant_str,
                cost_str,
                debe_str,
                haber_str,
                item["existencia"],
                saldo_str,
                prom_str
            ))
            
        # Actualizar KPIs
        if almacen:
            last = almacen[-1]
            self.kpi_labels["existencia"].configure(text=f"{last['existencia']:,} unidades")
            self.kpi_labels["cpp"].configure(text=f"$ {last['costo_promedio']:,.4f}")
            self.kpi_labels["valor"].configure(text=f"$ {last['saldo_valores']:,.2f}")
        else:
            self.kpi_labels["existencia"].configure(text="0 unidades")
            self.kpi_labels["cpp"].configure(text="$ 0.0000")
            self.kpi_labels["valor"].configure(text="$ 0.00")
            
        # Asegurar alineación correcta del formulario
        self.reset_date()
