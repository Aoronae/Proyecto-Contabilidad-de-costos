# -*- coding: utf-8 -*-
"""
views/ledger_view.py
Vista de Libro Diario y Cuentas T.
Permite ingresar asientos contables con validación interactiva de partida doble,
visualizar el Libro Diario completo y ver la mayorización en esquemas de Cuentas T.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
import models
import database

class LedgerView(tk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=config.COLOR_BG)
        self.main_window = main_window
        
        # Grid layout para dividir en paneles (Izquierda: Diario, Derecha: Cuentas T)
        self.grid_columnconfigure(0, weight=4) # Libro Diario / Formulario
        self.grid_columnconfigure(1, weight=5) # Cuentas T (Mayor)
        self.grid_rowconfigure(0, weight=1)
        
        # --- COLUMNA 1: DIARIO Y FORMULARIO (IZQUIERDA) ---
        left_panel = tk.Frame(self, bg=config.COLOR_BG, padx=15, pady=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        
        # Título Sección Diario
        lbl_diario_title = tk.Label(left_panel, text="Libro Diario General", font=config.FONT_TITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG)
        lbl_diario_title.pack(anchor="w", pady=(0, 10))
        
        # Formulario de Registro de Asientos (Tarjeta)
        self.form_card = tk.LabelFrame(left_panel, 
                                       text=" Crear Asiento Contable (Partida Doble) ", 
                                       font=config.FONT_SUBTITLE, 
                                       fg=config.COLOR_SECONDARY, 
                                       bg=config.COLOR_CARD, 
                                       bd=1, 
                                       padx=15, 
                                       pady=10)
        self.form_card.pack(fill="x", pady=(0, 15))
        
        # Inputs del asiento (Cabecera)
        header_row = tk.Frame(self.form_card, bg=config.COLOR_CARD)
        header_row.pack(fill="x", pady=5)
        
        tk.Label(header_row, text="Fecha:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).pack(side="left")
        self.entry_date = ttk.Entry(header_row, width=12, font=config.FONT_BODY)
        self.entry_date.pack(side="left", padx=5)
        self.reset_date()
        
        tk.Label(header_row, text="Concepto:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).pack(side="left", padx=(15, 0))
        self.entry_concept = ttk.Entry(header_row, width=32, font=config.FONT_BODY)
        self.entry_concept.pack(side="left", padx=5, fill="x", expand=True)
        
        # Línea de Movimiento (Agregar Cargo/Abono)
        movement_row = tk.Frame(self.form_card, bg=config.COLOR_CARD, pady=10)
        movement_row.pack(fill="x")
        
        # Separador decorativo dorado
        divider = tk.Frame(movement_row, bg=config.COLOR_GOLD, height=1)
        divider.pack(fill="x", pady=(0, 8))
        
        input_subrow = tk.Frame(movement_row, bg=config.COLOR_CARD)
        input_subrow.pack(fill="x")
        
        tk.Label(input_subrow, text="Cuenta:", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).pack(side="left")
        
        # Armar lista para combobox de cuentas
        account_choices = [f"{code} - {info['nombre']}" for code, info in sorted(config.CATALOGO_CUENTAS.items())]
        self.combo_account = ttk.Combobox(input_subrow, values=account_choices, state="readonly", width=30, font=config.FONT_BODY)
        self.combo_account.pack(side="left", padx=5)
        self.combo_account.current(0)
        
        tk.Label(input_subrow, text="Debe ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).pack(side="left", padx=(10, 0))
        self.entry_debe = ttk.Entry(input_subrow, width=10, font=config.FONT_BODY)
        self.entry_debe.pack(side="left", padx=3)
        self.entry_debe.insert(0, "0.00")
        
        tk.Label(input_subrow, text="Haber ($):", bg=config.COLOR_CARD, font=config.FONT_BODY_BOLD).pack(side="left", padx=(10, 0))
        self.entry_haber = ttk.Entry(input_subrow, width=10, font=config.FONT_BODY)
        self.entry_haber.pack(side="left", padx=3)
        self.entry_haber.insert(0, "0.00")
        
        # Botón para agregar movimiento al borrador (Estilo Vantti POS: Dorado)
        add_btn = tk.Button(input_subrow, 
                            text="Agregar", 
                            font=config.FONT_BODY_BOLD, 
                            fg=config.COLOR_PRIMARY, 
                            bg=config.COLOR_GOLD, 
                            activebackground="#F59E0B", 
                            activeforeground=config.COLOR_PRIMARY,
                            bd=0, 
                            padx=15, 
                            pady=4,
                            command=self.add_draft_movement)
        add_btn.pack(side="right", padx=5)
        
        # Tabla borrador del asiento actual
        draft_table_frame = tk.Frame(self.form_card, bg=config.COLOR_CARD, pady=5)
        draft_table_frame.pack(fill="x")
        
        self.draft_tree = ttk.Treeview(draft_table_frame, columns=("Cuenta", "Debe", "Haber"), show="headings", height=4)
        self.draft_tree.column("Cuenta", width=220, anchor="w")
        self.draft_tree.column("Debe", width=90, anchor="e")
        self.draft_tree.column("Haber", width=90, anchor="e")
        
        self.draft_tree.heading("Cuenta", text="Cuenta Contable")
        self.draft_tree.heading("Debe", text="Cargo (Debe)")
        self.draft_tree.heading("Haber", text="Abono (Haber)")
        self.draft_tree.pack(side="left", fill="x", expand=True)
        
        draft_scroll = ttk.Scrollbar(draft_table_frame, orient="vertical", command=self.draft_tree.yview)
        self.draft_tree.configure(yscrollcommand=draft_scroll.set)
        draft_scroll.pack(side="right", fill="y")
        
        # Borrador footer (Totales de partida doble)
        self.draft_footer = tk.Frame(self.form_card, bg=config.COLOR_CARD, pady=5)
        self.draft_footer.pack(fill="x")
        
        self.lbl_sum_debe = tk.Label(self.draft_footer, text="Total Debe: $0.00", font=config.FONT_BODY_BOLD, fg=config.COLOR_DEBE, bg=config.COLOR_CARD)
        self.lbl_sum_debe.pack(side="left", padx=5)
        
        self.lbl_sum_haber = tk.Label(self.draft_footer, text="Total Haber: $0.00", font=config.FONT_BODY_BOLD, fg=config.COLOR_HABER, bg=config.COLOR_CARD)
        self.lbl_sum_haber.pack(side="left", padx=15)
        
        self.lbl_balance_status = tk.Label(self.draft_footer, text="Descuadrado", font=config.FONT_BODY_BOLD, fg=config.COLOR_GOLD_DARK, bg=config.COLOR_GOLD_LIGHT, padx=8)
        self.lbl_balance_status.pack(side="left", padx=10)
        
        # Eliminar línea y guardar asiento
        btn_action_frame = tk.Frame(self.form_card, bg=config.COLOR_CARD)
        btn_action_frame.pack(fill="x", pady=(5, 0))
        
        del_btn = tk.Button(btn_action_frame, 
                            text="Eliminar Fila", 
                            font=("Segoe UI", 9), 
                            fg="#EF4444", 
                            bg=config.COLOR_CARD, 
                            activebackground=config.COLOR_CARD, 
                            activeforeground="#B91C1C",
                            bd=0,
                            command=self.delete_draft_row)
        del_btn.pack(side="left")
        
        save_entry_btn = tk.Button(btn_action_frame, 
                                   text="Guardar Asiento Diario", 
                                   font=config.FONT_BODY_BOLD, 
                                   fg=config.COLOR_PRIMARY, 
                                   bg=config.COLOR_GOLD, 
                                   activebackground="#F59E0B", 
                                   activeforeground=config.COLOR_PRIMARY,
                                   bd=0, 
                                   padx=15, 
                                   pady=8,
                                   command=self.submit_asiento)
        save_entry_btn.pack(side="right")
        
        # Tabla Libro Diario Completo (Fila de abajo a la izquierda)
        diario_table_frame = tk.Frame(left_panel, bg=config.COLOR_BG)
        diario_table_frame.pack(fill="both", expand=True)
        
        tk.Label(diario_table_frame, text="Historial de Asientos Contables Registrados", font=config.FONT_SUBTITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG).pack(anchor="w", pady=(0, 5))
        
        cols = ("ID", "Fecha", "Concepto", "Cuentas/Movimientos", "Debe", "Haber")
        self.journal_tree = ttk.Treeview(diario_table_frame, columns=cols, show="headings")
        
        self.journal_tree.column("ID", width=40, anchor="center")
        self.journal_tree.column("Fecha", width=80, anchor="center")
        self.journal_tree.column("Concepto", width=180, anchor="w")
        self.journal_tree.column("Cuentas/Movimientos", width=180, anchor="w")
        self.journal_tree.column("Debe", width=80, anchor="e")
        self.journal_tree.column("Haber", width=80, anchor="e")
        
        for col in cols:
            self.journal_tree.heading(col, text=col)
            
        j_scroll = ttk.Scrollbar(diario_table_frame, orient="vertical", command=self.journal_tree.yview)
        self.journal_tree.configure(yscrollcommand=j_scroll.set)
        
        self.journal_tree.pack(side="left", fill="both", expand=True)
        j_scroll.pack(side="right", fill="y")
        
        # Borrador en memoria de movimientos del asiento actual
        self.draft_movements = []

        # --- COLUMNA 2: CUENTAS T (DERECHA) ---
        right_panel = tk.Frame(self, bg=config.COLOR_BG, padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        lbl_mayor_title = tk.Label(right_panel, text="Esquemas de Mayor (Cuentas T)", font=config.FONT_TITLE, fg=config.COLOR_PRIMARY, bg=config.COLOR_BG)
        lbl_mayor_title.pack(anchor="w", pady=(0, 10))
        
        # Contenedor con Scroll para Cuentas T (Canvas + Frame)
        self.scroll_canvas = tk.Canvas(right_panel, bg=config.COLOR_BG, bd=0, highlightthickness=0)
        self.scroll_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_content = tk.Frame(self.scroll_canvas, bg=config.COLOR_BG)
        
        # Configurar evento de scroll
        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            )
        )
        
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=self.scroll_scrollbar.set)
        
        # Enlazar ancho del frame con el canvas para asegurar responsividad
        self.scroll_canvas.bind('<Configure>', self.on_canvas_configure)
        
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_scrollbar.pack(side="right", fill="y")

    def on_canvas_configure(self, event):
        """Ajusta el ancho del panel contenedor interno para alinearse al Canvas."""
        self.scroll_canvas.itemconfig(self.canvas_window, width=event.width)
        
    def reset_date(self):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
    def add_draft_movement(self):
        """Agrega un cargo o abono temporal al borrador del asiento actual."""
        acct_str = self.combo_account.get()
        debe_str = self.entry_debe.get().strip()
        haber_str = self.entry_haber.get().strip()
        
        code = acct_str.split(" - ")[0]
        
        try:
            debe = round(float(debe_str), 2)
            haber = round(float(haber_str), 2)
            if debe < 0 or haber < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Los importes del Debe y Haber deben ser números válidos mayores o iguales a cero.")
            return
            
        if debe == 0 and haber == 0:
            messagebox.showerror("Error", "Debe ingresar un valor mayor a cero ya sea en el Debe o en el Haber.")
            return
            
        if debe > 0 and haber > 0:
            messagebox.showerror("Error", "Un mismo renglón no puede tener valores en el Debe y el Haber simultáneamente. Registre dos filas por separado.")
            return
            
        # Añadir al borrador
        mov = {"cuenta": code, "debe": debe, "haber": haber}
        self.draft_movements.append(mov)
        
        # Resetear campos de importes
        self.entry_debe.delete(0, tk.END)
        self.entry_debe.insert(0, "0.00")
        self.entry_haber.delete(0, tk.END)
        self.entry_haber.insert(0, "0.00")
        
        self.update_draft_ui()
        
    def delete_draft_row(self):
        """Elimina el elemento seleccionado en la tabla borradora."""
        selected = self.draft_tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un renglón del borrador para eliminar.")
            return
            
        for sel in selected:
            idx = self.draft_tree.index(sel)
            self.draft_movements.pop(idx)
            
        self.update_draft_ui()
        
    def update_draft_ui(self):
        """Refresca la UI del borrador y recalcula si está cuadrado."""
        # Limpiar
        for item in self.draft_tree.get_children():
            self.draft_tree.delete(item)
            
        total_debe = 0.0
        total_haber = 0.0
        
        data = database.load_db()
        catalogo = data.get("catalogo", config.CATALOGO_CUENTAS)
        
        for mov in self.draft_movements:
            cta_name = catalogo.get(mov["cuenta"], {}).get("nombre", "Cuenta Desconocida")
            cta_display = f"{mov['cuenta']} - {cta_name}"
            
            debe_display = f"$ {mov['debe']:,.2f}" if mov["debe"] > 0 else "-"
            haber_display = f"$ {mov['haber']:,.2f}" if mov["haber"] > 0 else "-"
            
            self.draft_tree.insert("", "end", values=(cta_display, debe_display, haber_display))
            
            total_debe += mov["debe"]
            total_haber += mov["haber"]
            
        self.lbl_sum_debe.configure(text=f"Total Debe: $ {total_debe:,.2f}")
        self.lbl_sum_haber.configure(text=f"Total Haber: $ {total_haber:,.2f}")
        
        # Validar cuadre
        if round(total_debe, 2) == round(total_haber, 2) and len(self.draft_movements) > 0:
            self.lbl_balance_status.configure(text="Cuadrado", fg=config.COLOR_TEXT_LIGHT, bg=config.COLOR_DEBE)
        else:
            self.lbl_balance_status.configure(text="Descuadrado", fg=config.COLOR_GOLD_DARK, bg=config.COLOR_GOLD_LIGHT)
            
    def submit_asiento(self):
        """Valida partida doble formalmente y guarda en el Libro Diario."""
        fecha = self.entry_date.get().strip()
        concepto = self.entry_concept.get().strip()
        
        if not concepto:
            messagebox.showerror("Error", "Debes especificar un Concepto o Glosa para el asiento.")
            return
            
        if not self.draft_movements:
            messagebox.showerror("Error", "El asiento contable no tiene ningún movimiento registrado.")
            return
            
        data = database.load_db()
        
        try:
            # Registrar
            models.registrar_asiento(data, fecha, concepto, self.draft_movements)
            messagebox.showinfo("Éxito", f"¡Asiento '{concepto}' guardado y mayorizado exitosamente!")
            
            # Limpiar
            self.draft_movements = []
            self.entry_concept.delete(0, tk.END)
            self.update_draft_ui()
            
            # Refrescar todo
            self.main_window.refresh_all_views()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación Contable", str(e))
            
    def update_data(self):
        """Carga los asientos en el diario general y redibuja las Cuentas T de mayor."""
        # 1. Actualizar Diario General
        for item in self.journal_tree.get_children():
            self.journal_tree.delete(item)
            
        data = database.load_db()
        diario = data.get("diario", [])
        catalogo = data.get("catalogo", config.CATALOGO_CUENTAS)
        
        # Actualizar opciones de cuentas contables del combobox dinámicamente
        account_choices = [f"{code} - {info['nombre']}" for code, info in sorted(catalogo.items())]
        self.combo_account.configure(values=account_choices)
        
        for asiento in diario:
            # Insertamos la fila principal
            first_row = True
            for m in asiento["movimientos"]:
                cta_name = catalogo.get(m["cuenta"], {}).get("nombre", "Cuenta Desconocida")
                cta_disp = f"   {m['cuenta']} - {cta_name}"
                
                debe_str = f"$ {m['debe']:,.2f}" if m["debe"] > 0 else ""
                haber_str = f"$ {m['haber']:,.2f}" if m["haber"] > 0 else ""
                
                if first_row:
                    self.journal_tree.insert("", "end", values=(
                        asiento["id"],
                        asiento["fecha"],
                        asiento["concepto"],
                        cta_disp,
                        debe_str,
                        haber_str
                    ))
                    first_row = False
                else:
                    self.journal_tree.insert("", "end", values=(
                        "", "", "", cta_disp, debe_str, haber_str
                    ))
            # Línea divisoria en blanco
            self.journal_tree.insert("", "end", values=("", "", "", "", "", ""))
            
        # 2. Redibujar Esquemas de Mayor (Cuentas T)
        self.render_cuentas_t(data)
        self.reset_date()
        
    def render_cuentas_t(self, data):
        """Borra y redibuja gráficamente las Cuentas T usando elementos estructurados de Tkinter."""
        # Limpiar panel
        for widget in self.scroll_content.winfo_children():
            widget.destroy()
            
        # Agrupar las cuentas activas (aquellas con al menos un movimiento o saldo)
        activas = []
        catalogo = data.get("catalogo", config.CATALOGO_CUENTAS)
        for code in catalogo.keys():
            t_data = models.obtener_cuenta_t(data, code)
            if t_data["cargos"] or t_data["abonos"] or t_data["total_debe"] > 0 or t_data["total_haber"] > 0:
                activas.append(t_data)
                
        if not activas:
            # Mostrar mensaje si está vacío
            lbl_empty = tk.Label(self.scroll_content, 
                                 text="No hay movimientos registrados en el Diario.\nCarga el 'Proyecto de Práctica' para ver las Cuentas T mayorizadas.", 
                                 font=config.FONT_BODY, 
                                 fg=config.COLOR_TEXT_MUTED, 
                                 bg=config.COLOR_BG, 
                                 pady=50)
            lbl_empty.pack(fill="both", expand=True)
            return
            
        # Configurar cuadrícula de Cuentas T (responsivo a dos columnas)
        grid_frame = tk.Frame(self.scroll_content, bg=config.COLOR_BG)
        grid_frame.pack(fill="both", expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        
        for idx, t in enumerate(activas):
            row = idx // 2
            col = idx % 2
            
            # Tarjeta de la Cuenta T
            t_card = tk.Frame(grid_frame, bg=config.COLOR_CARD, bd=1, highlightbackground=config.COLOR_GOLD, highlightthickness=1)
            t_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Nombre de la Cuenta (Cabecera Royal Blue / Texto Blanco)
            lbl_title = tk.Label(t_card, 
                                 text=f"{t['codigo']} - {t['nombre'].upper()}", 
                                 font=("Segoe UI", 9, "bold"), 
                                 fg=config.COLOR_TEXT_LIGHT, 
                                 bg=config.COLOR_SECONDARY, 
                                 pady=6)
            lbl_title.pack(fill="x")
            
            # Cuerpo de la T: Debe a la izquierda, Haber a la derecha
            columns_frame = tk.Frame(t_card, bg=config.COLOR_CARD)
            columns_frame.pack(fill="both", expand=True, pady=5)
            
            # Dividir columnas visualmente por una línea negra vertical
            debe_col = tk.Frame(columns_frame, bg=config.COLOR_CARD)
            debe_col.pack(side="left", fill="both", expand=True, padx=5)
            
            linea_div = tk.Frame(columns_frame, bg=config.COLOR_PRIMARY, width=1)
            linea_div.pack(side="left", fill="y")
            
            haber_col = tk.Frame(columns_frame, bg=config.COLOR_CARD)
            haber_col.pack(side="right", fill="both", expand=True, padx=5)
            
            # Dibujar movimientos Debe (Izquierda)
            for c in t["cargos"]:
                lbl = tk.Label(debe_col, text=f"({c['id']}) $ {c['importe']:,.2f}", font=config.FONT_MONO, fg=config.COLOR_DEBE, bg=config.COLOR_CARD, anchor="w")
                lbl.pack(fill="x")
                
            # Dibujar movimientos Haber (Derecha)
            for a in t["abonos"]:
                lbl = tk.Label(haber_col, text=f"$ {a['importe']:,.2f} ({a['id']})", font=config.FONT_MONO, fg=config.COLOR_HABER, bg=config.COLOR_CARD, anchor="e")
                lbl.pack(fill="x")
                
            # Rellenar con espacio vacío si una columna tiene menos filas para mantener simetría
            diff_lines = len(t["cargos"]) - len(t["abonos"])
            if diff_lines > 0:
                for _ in range(diff_lines):
                    tk.Label(haber_col, text=" ", bg=config.COLOR_CARD).pack()
            elif diff_lines < 0:
                for _ in range(abs(diff_lines)):
                    tk.Label(debe_col, text=" ", bg=config.COLOR_CARD).pack()
                    
            # Línea horizontal de cortes de movimientos
            h_line = tk.Frame(t_card, bg=config.COLOR_PRIMARY, height=1)
            h_line.pack(fill="x", padx=10, pady=2)
            
            # Sumas / Movimientos (Totales de movimiento)
            movs_frame = tk.Frame(t_card, bg=config.COLOR_CARD)
            movs_frame.pack(fill="x", padx=5)
            
            lbl_md = tk.Label(movs_frame, text=f"$ {t['total_debe']:,.2f}", font=("Consolas", 9, "bold"), fg=config.COLOR_TEXT_DARK, bg=config.COLOR_CARD, anchor="w")
            lbl_md.pack(side="left")
            
            lbl_ma = tk.Label(movs_frame, text=f"$ {t['total_haber']:,.2f}", font=("Consolas", 9, "bold"), fg=config.COLOR_TEXT_DARK, bg=config.COLOR_CARD, anchor="e")
            lbl_ma.pack(side="right")
            
            # Línea horizontal final de saldo (Tradicional de Cuentas T)
            h_line_saldo = tk.Frame(t_card, bg=config.COLOR_PRIMARY, height=1)
            h_line_saldo.pack(fill="x", padx=10, pady=2)
            
            # Saldo Final
            saldo_frame = tk.Frame(t_card, bg=config.COLOR_CARD)
            saldo_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            if t["saldo_deudor"] > 0:
                lbl_sd = tk.Label(saldo_frame, text=f"SD: $ {t['saldo_deudor']:,.2f}", font=("Consolas", 10, "bold"), fg=config.COLOR_SECONDARY, bg=config.COLOR_CARD, anchor="w")
                lbl_sd.pack(side="left")
            elif t["saldo_acreedor"] > 0:
                lbl_sa = tk.Label(saldo_frame, text=f"SA: $ {t['saldo_acreedor']:,.2f}", font=("Consolas", 10, "bold"), fg=config.COLOR_GOLD_DARK, bg=config.COLOR_CARD, anchor="e")
                lbl_sa.pack(side="right")
            else:
                # Saldo en cero absoluto
                lbl_zero = tk.Label(saldo_frame, text="Saldo: $ 0.00", font=("Consolas", 10, "bold"), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_CARD, anchor="center")
                lbl_zero.pack(fill="x")
