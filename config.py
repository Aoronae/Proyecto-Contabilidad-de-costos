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
COLOR_BORDER = "#E2E8F0"      # Gris claro para bordes sutiles

# Botones, cabeceras y herramientas: Gris Medio Sofisticado & Slate
COLOR_PRIMARY = "#1E293B"     # Slate 800 (Gris oscuro elegante) para cabeceras y texto
COLOR_SECONDARY = "#64748B"   # Gris medio sofisticado (Slate 500) para botones y acciones
COLOR_HOVER = "#475569"       # Slate 600 para estados hover

# Detalles, alertas, bordes de selección y resaltados: Naranja Vibrante
COLOR_GOLD = "#F97316"        # Naranja vibrante de alta conversión
COLOR_ACCENT = "#F97316"      # Color de acento para la selección y enfoque
COLOR_GOLD_DARK = "#C2410C"   # Naranja oscuro legible para texto
COLOR_GOLD_LIGHT = "#FFEDD5"  # Naranja claro suave (Orange 100) para fondos de alerta

# Sidebar específico
COLOR_SIDEBAR = "#64748B"     # Fondo gris medio de barra lateral
COLOR_SIDEBAR_HOVER = "#475569"# Hover gris oscuro en menú lateral

# Colores de apoyo contable
COLOR_DEBE = "#16A34A"        # Verde contable elegante para debe
COLOR_HABER = "#DC2626"       # Rojo contable elegante para haber
COLOR_TEXT_DARK = "#0F172A"   # Texto principal Slate 900
COLOR_TEXT_MUTED = "#64748B"  # Texto secundario Slate 500
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
