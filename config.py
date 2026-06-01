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

# Botones, cabeceras y herramientas: Gris Carbón Jet & Slate
COLOR_PRIMARY = "#111111"     # Gris carbón casi negro (Gray 950) para cabeceras y textos
COLOR_SECONDARY = "#1E1E1E"   # Gris oscuro profundo (Gray 900) para botones y acciones
COLOR_HOVER = "#2D2D2D"       # Gris oscuro medio (Gray 800) para estados hover

# Detalles, alertas, bordes de selección y resaltados: Naranja Neón Ultra Brillante
COLOR_GOLD = "#FF3300"        # Naranja neón de alto impacto y luminiscencia
COLOR_ACCENT = "#FF3300"      # Color de acento para la selección y enfoque
COLOR_GOLD_DARK = "#CC2900"   # Naranja neón oscuro legible para texto
COLOR_GOLD_LIGHT = "#FFEBE6"  # Crema naranja neón suave para fondos de alerta

# Sidebar específico
COLOR_SIDEBAR = "#121212"     # Fondo gris carbón jet (casi negro) de barra lateral
COLOR_SIDEBAR_HOVER = "#242424"# Hover gris carbón oscuro en menú lateral

# Colores de apoyo contable
COLOR_DEBE = "#16A34A"        # Verde contable elegante para debe
COLOR_HABER = "#DC2626"       # Rojo contable elegante para haber
COLOR_TEXT_DARK = "#111111"   # Texto principal casi negro
COLOR_TEXT_MUTED = "#555555"  # Texto secundario gris medio
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
