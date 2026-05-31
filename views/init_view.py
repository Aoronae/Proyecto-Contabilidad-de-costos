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
                                   text="Configure los saldos iniciales de las cuentas o cargue el ejercicio práctico contable", 
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
            "Cargue los saldos de apertura y cuentas contables predeterminadas del caso práctico."
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
                                  text="Cargar Proyecto de Práctica", 
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
        
        # Barra de botones del catálogo (Estilo Vantti POS: Dorado)
        btn_bar = tk.Frame(catalog_frame, bg=config.COLOR_BG)
        btn_bar.pack(fill="x", pady=(0, 8))
        
        add_cta_btn = tk.Button(btn_bar,
                                text="✚  Agregar Cuenta Contable",
                                font=config.FONT_BODY_BOLD,
                                fg=config.COLOR_PRIMARY,
                                bg=config.COLOR_GOLD,
                                activebackground="#F59E0B",
                                activeforeground=config.COLOR_PRIMARY,
                                bd=0,
                                padx=15,
                                pady=7,
                                command=self.open_add_account_dialog)
        add_cta_btn.pack(side="left", padx=(0, 10))
        
        adjust_saldo_btn = tk.Button(btn_bar,
                                     text="✎  Ajustar Saldo Inicial",
                                     font=config.FONT_BODY_BOLD,
                                     fg=config.COLOR_PRIMARY,
                                     bg=config.COLOR_GOLD,
                                     activebackground="#F59E0B",
                                     activeforeground=config.COLOR_PRIMARY,
                                     bd=0,
                                     padx=15,
                                     pady=7,
                                     command=self.open_adjust_saldo_dialog)
        adjust_saldo_btn.pack(side="left")
        
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
        
        # Enlazar doble clic para ajustar saldo
        self.tree.bind("<Double-1>", lambda e: self.open_adjust_saldo_dialog())
        
    def load_practice(self):
        """Dispara la carga de datos simulados en la base de datos."""
        try:
            data = database.load_db()
            data = models.cargar_proyecto_practica(data)
            self.main_window.refresh_all_views()
            messagebox.showinfo("Éxito", "El ejercicio práctico ha sido cargado correctamente.\nSe inicializaron los saldos de apertura y cuentas contables.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al inicializar el ejercicio: {e}")
            
    def open_add_account_dialog(self):
        """Abre un diálogo flotante para ingresar una nueva cuenta contable."""
        dialog = tk.Toplevel(self)
        dialog.title("Nueva Cuenta Contable")
        dialog.geometry("380x280")
        dialog.configure(bg=config.COLOR_BG)
        dialog.transient(self.main_window)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centrar diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Título
        tk.Label(dialog, text="AGREGAR CUENTA CONTABLE", font=("Segoe UI", 11, "bold"), fg=config.COLOR_PRIMARY, bg=config.COLOR_BG, pady=10).pack()
        
        # Campos
        form = tk.Frame(dialog, bg=config.COLOR_BG, padx=20)
        form.pack(fill="both", expand=True)
        
        # Código
        tk.Label(form, text="Código de Cuenta:", font=config.FONT_BODY_BOLD, bg=config.COLOR_BG).grid(row=0, column=0, sticky="w", pady=5)
        entry_code = ttk.Entry(form, width=15, font=config.FONT_BODY)
        entry_code.grid(row=0, column=1, sticky="w", pady=5)
        
        # Nombre
        tk.Label(form, text="Nombre de Cuenta:", font=config.FONT_BODY_BOLD, bg=config.COLOR_BG).grid(row=1, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(form, width=22, font=config.FONT_BODY)
        entry_name.grid(row=1, column=1, sticky="w", pady=5)
        
        # Tipo
        tk.Label(form, text="Tipo de Cuenta:", font=config.FONT_BODY_BOLD, bg=config.COLOR_BG).grid(row=2, column=0, sticky="w", pady=5)
        combo_type = ttk.Combobox(form, values=["Activo", "Pasivo", "Capital", "Ingresos", "Costos", "Gastos"], state="readonly", width=18, font=config.FONT_BODY)
        combo_type.grid(row=2, column=1, sticky="w", pady=5)
        combo_type.current(0)
        
        # Naturaleza
        tk.Label(form, text="Naturaleza:", font=config.FONT_BODY_BOLD, bg=config.COLOR_BG).grid(row=3, column=0, sticky="w", pady=5)
        combo_nature = ttk.Combobox(form, values=["Deudora", "Acreedora"], state="readonly", width=18, font=config.FONT_BODY)
        combo_nature.grid(row=3, column=1, sticky="w", pady=5)
        combo_nature.current(0)
        
        # Guardar
        def save():
            code = entry_code.get().strip()
            name = entry_name.get().strip()
            t_type = combo_type.get()
            nature = combo_nature.get()
            
            if not code or not name:
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=dialog)
                return
                
            if not code.isdigit():
                messagebox.showerror("Error", "El código de cuenta debe ser numérico.", parent=dialog)
                return
                
            data = database.load_db()
            catalogo = data.get("catalogo", config.CATALOGO_CUENTAS)
            
            if code in catalogo:
                messagebox.showerror("Error", f"El código '{code}' ya está registrado en el catálogo.", parent=dialog)
                return
                
            # Agregar a base de datos
            catalogo[code] = {"nombre": name, "tipo": t_type, "naturaleza": nature}
            data["catalogo"] = catalogo
            data["saldos"][code] = 0.0
            
            database.save_db(data)
            self.main_window.refresh_all_views()
            messagebox.showinfo("Éxito", f"Cuenta '{code} - {name}' agregada con éxito al catálogo.", parent=dialog)
            dialog.destroy()
            
        tk.Button(dialog, 
                  text="Guardar Cuenta", 
                  font=config.FONT_BODY_BOLD, 
                  fg=config.COLOR_PRIMARY, 
                  bg=config.COLOR_GOLD, 
                  activebackground="#F59E0B",
                  activeforeground=config.COLOR_PRIMARY,
                  bd=0, 
                  padx=15, 
                  pady=8, 
                  command=save).pack(pady=15)
                  
    def open_adjust_saldo_dialog(self):
        """Abre un diálogo flotante para ajustar el saldo inicial de la cuenta seleccionada."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione una cuenta contable del catálogo para ajustar su saldo.")
            return
            
        item_vals = self.tree.item(selected[0], "values")
        code = item_vals[0]
        name = item_vals[1]
        
        dialog = tk.Toplevel(self)
        dialog.title("Ajustar Saldo Inicial")
        dialog.geometry("350x200")
        dialog.configure(bg=config.COLOR_BG)
        dialog.transient(self.main_window)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centrar diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Título
        tk.Label(dialog, text=f"AJUSTAR SALDO INICIAL\n{code} - {name.upper()}", font=("Segoe UI", 10, "bold"), fg=config.COLOR_PRIMARY, bg=config.COLOR_BG, pady=10).pack()
        
        # Form
        form = tk.Frame(dialog, bg=config.COLOR_BG, padx=20)
        form.pack(fill="both", expand=True)
        
        tk.Label(form, text="Nuevo Saldo Inicial ($):", font=config.FONT_BODY_BOLD, bg=config.COLOR_BG).pack(anchor="w", pady=2)
        
        data = database.load_db()
        curr_val = data["saldos"].get(code, 0.0)
        
        entry_saldo = ttk.Entry(form, width=20, font=config.FONT_BODY)
        entry_saldo.pack(anchor="w", pady=5)
        entry_saldo.insert(0, f"{curr_val:.2f}")
        
        def save():
            val_str = entry_saldo.get().strip()
            try:
                val = round(float(val_str), 2)
                if val < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "El saldo debe ser un número válido mayor o igual a cero.", parent=dialog)
                return
                
            data["saldos"][code] = val
            database.save_db(data)
            self.main_window.refresh_all_views()
            messagebox.showinfo("Éxito", f"Saldo inicial de '{code} - {name}' actualizado a $ {val:,.2f}.", parent=dialog)
            dialog.destroy()
            
        tk.Button(dialog, 
                  text="Actualizar Saldo", 
                  font=config.FONT_BODY_BOLD, 
                  fg=config.COLOR_PRIMARY, 
                  bg=config.COLOR_GOLD, 
                  activebackground="#F59E0B",
                  activeforeground=config.COLOR_PRIMARY,
                  bd=0, 
                  padx=15, 
                  pady=8, 
                  command=save).pack(pady=15)
            
    def update_data(self):
        """Refresca la tabla del catálogo con los saldos vigentes desde el catálogo dinámico."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = database.load_db()
        catalogo = data.get("catalogo", config.CATALOGO_CUENTAS)
        saldos = data.get("saldos", {})
        
        # Ordenar cuentas por código
        for code in sorted(catalogo.keys()):
            info = catalogo[code]
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
            self.load_btn.configure(text="Proyecto de Práctica Cargado", bg=config.COLOR_PRIMARY, state="disabled")
        else:
            self.load_btn.configure(text="Cargar Proyecto de Práctica", bg=config.COLOR_GOLD, state="normal")
