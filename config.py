# -*- coding: utf-8 -*-
"""
config.py
Configuración general, constantes visuales y de negocio para el ERP de Contabilidad de Costos.
Establece la paleta de colores institucional requerida.
"""

# PALETA DE COLORES (Requisitos visuales del usuario)
# Fondo y Paneles: Blanco o gris muy claro
COLOR_BG = "#F4F6F9"          # Gris claro con sutil matiz azul/hielo, limpio y elegante
COLOR_CARD = "#FFFFFF"        # Blanco puro para tarjetas y paneles elevados
COLOR_BORDER = "#D5DBDB"      # Bordes sutiles en tono gris azulado pálido

# Botones, cabeceras y herramientas: Azul Índigo & Steel Blue
COLOR_PRIMARY = "#0D253F"     # Azul Índigo profundo, corporativo e intelectual
COLOR_SECONDARY = "#1F4E79"   # Azul acero (Steel Blue) para botones y acciones
COLOR_HOVER = "#2471A3"       # Azul cobalto brillante para hover

# Detalles, alertas, bordes de selección y resaltados: Dorado Champaña
COLOR_GOLD = "#C5A059"        # Dorado Champaña sofisticado y formal
COLOR_ACCENT = "#C5A059"      # Color de acento para la selección y enfoque
COLOR_GOLD_DARK = "#9A731C"   # Dorado oscuro legible para texto
COLOR_GOLD_LIGHT = "#FDF6E6"  # Crema champaña suave para fondos de alerta

# Sidebar específico
COLOR_SIDEBAR = "#0D253F"     # Fondo Azul Índigo profundo de barra lateral
COLOR_SIDEBAR_HOVER = "#1F4E79"# Hover azul acero en menú lateral

# Colores de apoyo contable
COLOR_DEBE = "#0E6251"        # Verde esmeralda profundo para debe
COLOR_HABER = "#78281F"       # Rojo terracota profundo para haber
COLOR_TEXT_DARK = "#1F2D3D"   # Texto principal en tono pizarra azulado oscuro
COLOR_TEXT_MUTED = "#5D6D7E"  # Texto secundario en tono gris acero
COLOR_TEXT_LIGHT = "#FFFFFF"  # Texto claro para botones/cabeceras

# TIPOGRAFÍAS
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10, "normal")
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 10, "normal")

# CATÁLOGO DE CUENTAS ESTÁNDAR
CATALOGO_CUENTAS = {
    # Activo
    "1101": {"nombre": "Bancos", "tipo": "Activo", "naturaleza": "Deudora"},
    "1151": {"nombre": "Almacén de Materias Primas", "tipo": "Activo", "naturaleza": "Deudora"},
    "1152": {"nombre": "Almacén de Producción en Proceso", "tipo": "Activo", "naturaleza": "Deudora"},
    "1153": {"nombre": "Almacén de Productos Terminados", "tipo": "Activo", "naturaleza": "Deudora"},
    "1201": {"nombre": "Maquinaria y Equipo", "tipo": "Activo", "naturaleza": "Deudora"},
    "1202": {"nombre": "Depreciación Acumulada de Maquinaria", "tipo": "Activo", "naturaleza": "Acreedora"},
    
    # Pasivo
    "2101": {"nombre": "Proveedores", "tipo": "Pasivo", "naturaleza": "Acreedora"},
    "2105": {"nombre": "Cuentas por Pagar (MOD/Gastos)", "tipo": "Pasivo", "naturaleza": "Acreedora"},
    
    # Capital
    "3101": {"nombre": "Capital Social", "tipo": "Capital", "naturaleza": "Acreedora"},
    "3105": {"nombre": "Utilidad del Ejercicio", "tipo": "Capital", "naturaleza": "Acreedora"},
    
    # Cuentas de Resultados / Costos
    "4101": {"nombre": "Ventas", "tipo": "Ingresos", "naturaleza": "Acreedora"},
    "5101": {"nombre": "Costo de Ventas", "tipo": "Costos", "naturaleza": "Deudora"},
    "5102": {"nombre": "Mano de Obra Directa (MOD)", "tipo": "Costos", "naturaleza": "Deudora"},
    "5103": {"nombre": "Cargos Indirectos (GIF)", "tipo": "Costos", "naturaleza": "Deudora"},
}
