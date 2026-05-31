# -*- coding: utf-8 -*-
"""
config.py
Configuración general, constantes visuales y de negocio para el ERP de Contabilidad de Costos.
Establece la paleta de colores institucional requerida.
"""

# PALETA DE COLORES (Requisitos visuales del usuario)
# Fondo y Paneles: Blanco o gris muy claro
COLOR_BG = "#F8FAFC"          # Gris ultra claro (Slate 50)
COLOR_CARD = "#FFFFFF"        # Blanco puro para tarjetas y paneles elevados
COLOR_BORDER = "#E2E8F0"      # Gris claro para bordes sutiles

# Botones, cabeceras y herramientas: Azul Marino / Royal Blue
COLOR_PRIMARY = "#0F172A"     # Azul marino profundo (Slate 900) para cabeceras y títulos
COLOR_SECONDARY = "#1E3A8A"   # Azul Royal (Blue 800) para botones y acciones principales
COLOR_HOVER = "#2563EB"       # Azul brillante (Blue 600) para estados hover

# Detalles, alertas, bordes de selección y resaltados: Dorado (Gold/Amber)
COLOR_GOLD = "#D4AF37"        # Dorado Metálico
COLOR_GOLD_DARK = "#B45309"   # Ámbar oscuro para texto legible
COLOR_GOLD_LIGHT = "#FEF3C7"  # Amarillo/Dorado claro para fondos de alerta

# Colores de apoyo contable
COLOR_DEBE = "#15803D"        # Verde para cargos/debe
COLOR_HABER = "#B91C1C"       # Rojo para abonos/haber
COLOR_TEXT_DARK = "#0F172A"   # Texto principal
COLOR_TEXT_MUTED = "#64748B"  # Texto secundario
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
