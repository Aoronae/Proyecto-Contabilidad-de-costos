# -*- coding: utf-8 -*-
"""
config.py
Configuración general, constantes visuales y de negocio para el ERP de Contabilidad de Costos.
Establece la paleta de colores institucional requerida.
"""

# PALETA DE COLORES (Requisitos visuales del usuario)
# Fondo y Paneles: Blanco o gris muy claro
COLOR_BG = "#F4F7F5"          # Blanco/Grisáceo Sage muy suave y elegante
COLOR_CARD = "#FFFFFF"        # Blanco puro para tarjetas y paneles elevados
COLOR_BORDER = "#D1DCD6"      # Bordes sutiles en tono verde pálido

# Botones, cabeceras y herramientas: Verde Bosque Académico
COLOR_PRIMARY = "#0B3C30"     # Verde bosque profundo, académico y formal
COLOR_SECONDARY = "#0E5A47"   # Verde esmeralda medio para botones
COLOR_HOVER = "#12755D"       # Verde esmeralda claro para hover

# Detalles, alertas, bordes de selección y resaltados: Dorado Arena
COLOR_GOLD = "#B58C3D"        # Dorado Arena Metálico premium
COLOR_ACCENT = "#B58C3D"      # Color de acento para la selección y enfoque
COLOR_GOLD_DARK = "#7E5E1C"   # Dorado oscuro legible para texto
COLOR_GOLD_LIGHT = "#FBF4E6"  # Crema suave dorado para fondos de alerta

# Sidebar específico
COLOR_SIDEBAR = "#0B3C30"     # Fondo verde bosque profundo de barra lateral
COLOR_SIDEBAR_HOVER = "#0E5A47"# Hover verde en menú lateral

# Colores de apoyo contable
COLOR_DEBE = "#047857"        # Verde esmeralda para debe
COLOR_HABER = "#B91C1C"       # Rojo contable elegante para haber
COLOR_TEXT_DARK = "#1E2E2A"   # Texto principal en tono pizarra verde oscuro
COLOR_TEXT_MUTED = "#556B65"  # Texto secundario en tono verde grisáceo
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
