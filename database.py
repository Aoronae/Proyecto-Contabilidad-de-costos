# -*- coding: utf-8 -*-
"""
database.py
Módulo de persistencia local. Utiliza un archivo JSON para guardar el estado del sistema,
permitiendo que sea fácil de inspeccionar, modificar y subir a GitHub sin bloqueos de archivos.
"""

import os
import json
from config import CATALOGO_CUENTAS

DB_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def get_default_data():
    """Retorna la estructura inicial de datos vacía."""
    saldos = {code: 0.0 for code in CATALOGO_CUENTAS}
    return {
        "practice_project_loaded": False,
        "catalogo": CATALOGO_CUENTAS.copy(),
        "saldos": saldos,
        "diario": [],
        "almacen": [],
        "config_costos": {
            "precio_venta": 350.0,
            "costo_variable_u": 120.0,
            "costos_fijos": 45000.0,
            "produccion_objetivo": 500  # piezas
        }
    }

def load_db():
    """Carga los datos desde el archivo JSON local. Si no existe, inicializa con defaults."""
    if not os.path.exists(DB_FILE):
        data = get_default_data()
        save_db(data)
        return data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Asegurar que todas las cuentas estén inicializadas si se agregó alguna nueva
            catalogo = data.setdefault("catalogo", CATALOGO_CUENTAS.copy())
            saldos = data.setdefault("saldos", {})
            for code in catalogo:
                if code not in saldos:
                    saldos[code] = 0.0
            data.setdefault("diario", [])
            data.setdefault("almacen", [])
            data.setdefault("config_costos", {
                "precio_venta": 350.0,
                "costo_variable_u": 120.0,
                "costos_fijos": 45000.0,
                "produccion_objetivo": 500
            })
            return data
    except Exception as e:
        print(f"Error cargando base de datos: {e}. Restaurando valores por defecto.")
        data = get_default_data()
        save_db(data)
        return data

def save_db(data):
    """Guarda el diccionario de datos en el archivo JSON."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando base de datos: {e}")
        return False

def clear_db():
    """Limpia la base de datos por completo y restablece los valores vacíos."""
    data = get_default_data()
    save_db(data)
    return data
