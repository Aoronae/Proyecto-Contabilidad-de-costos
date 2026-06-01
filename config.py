# -*- coding: utf-8 -*-
"""
config.py
Configuración general, constantes visuales y de negocio para el ERP de Contabilidad de Costos.
Establece la paleta de colores institucional requerida.
"""

# PALETA DE COLORES (Requisitos visuales del usuario)
# Fondo y Paneles: Blanco o gris muy claro
COLOR_BG = "#FAFAFA"          # Blanco general muy suave, limpio y elegante
COLOR_CARD = "#FFFFFF"        # Blanco puro para tarjetas y paneles elevados
COLOR_BORDER = "#E5E7EB"      # Gris claro para bordes sutiles

# Botones, cabeceras y herramientas: Gris Oscuro Carbón & Slate
COLOR_PRIMARY = "#111827"     # Gris carbón muy oscuro (Gray 900) para cabeceras y texto principal
COLOR_SECONDARY = "#1F2937"   # Gris carbón profundo (Gray 800) para botones y acciones
COLOR_HOVER = "#374151"       # Gris carbón medio (Gray 700) para estados hover

# Detalles, alertas, bordes de selección y resaltados: Naranja Ultra Vibrante y Vivo
COLOR_GOLD = "#FF5E00"        # Naranja vivo de alto impacto y alta conversión
COLOR_ACCENT = "#FF5E00"      # Color de acento para la selección y enfoque
COLOR_GOLD_DARK = "#D34A00"   # Naranja oscuro legible para texto
COLOR_GOLD_LIGHT = "#FFF0E6"  # Crema naranja suave (Orange 50) para fondos de alerta

# Sidebar específico
COLOR_SIDEBAR = "#1F2937"     # Fondo gris oscuro carbón de barra lateral
COLOR_SIDEBAR_HOVER = "#374151"# Hover gris medio carbón en menú lateral

# Colores de apoyo contable
COLOR_DEBE = "#16A34A"        # Verde contable elegante para debe
COLOR_HABER = "#DC2626"       # Rojo contable elegante para haber
COLOR_TEXT_DARK = "#111827"   # Texto principal carbón oscuro
COLOR_TEXT_MUTED = "#4B5563"  # Texto secundario gris medio
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
