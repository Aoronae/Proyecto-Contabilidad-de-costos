# -*- coding: utf-8 -*-
"""
main.py
Punto de Entrada Principal para el ERP de Contabilidad de Costos.
Inicializa el ciclo de vida de la interfaz de usuario de Tkinter.
"""

import sys
import tkinter as tk
from tkinter import messagebox
from views.main_window import MainWindow

def main():
    """Función de arranque principal del sistema."""
    try:
        # Inicializar la ventana principal de la aplicación
        app = MainWindow()
        
        # Iniciar el bucle de eventos principal de Tkinter
        app.mainloop()
        
    except Exception as e:
        print(f"Error crítico de inicialización: {e}", file=sys.stderr)
        
        # Intentar mostrar un cuadro de diálogo con el error
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error Crítico", 
                f"No se pudo arrancar la aplicación.\n\nDetalle técnico:\n{e}"
            )
        except Exception:
            pass
            
        sys.exit(1)

if __name__ == "__main__":
    main()
