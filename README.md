# ERP Contabilidad de Costos - Premium Edition 📊💼

Este es un sistema de contabilidad de costos e inventarios robusto, modular y altamente profesional desarrollado en **Python** utilizando la librería estándar **Tkinter** y **ttk**. Ha sido diseñado bajo principios de arquitectura limpia y modularización por componentes, ideal para entornos educativos o proyectos profesionales listos para desplegar en tu repositorio de GitHub.

La interfaz de usuario ha sido cuidadosamente estilizada siguiendo requisitos visuales institucionales: fondos limpios y elegantes (blancos y grises claros), barras, cabeceras y botones primarios en **Azul Marino / Royal Blue**, y líneas divisoras, estados resaltados y alertas clave en **Dorado Metálico**.

---

## 🚀 Características del Sistema

### 1. Inicialización y Catálogo de Cuentas (`🏢`)
- **Catálogo Integrado:** Contiene cuentas específicas del costeo industrial (MPD, PP, MOD, GIF, PT, Costo de Ventas).
- **Cargar Proyecto de Práctica:** Llena el sistema instantáneamente con un caso práctico preconfigurado (saldos iniciales en Bancos, Almacén de MP, Maquinaria y Capital Social) para facilitar pruebas académicas y presentaciones.

### 2. Tarjetas de Almacén (`📦`)
- **Costo Promedio Ponderado (CPP):** Valuación en tiempo real de entradas y salidas de materia prima.
- **Formulas Contables Dinámicas:** Actualización instantánea de existencias, saldos en valores y costo promedio por cada movimiento.
- **Asientos Automáticos:** Cada entrada (compra) o salida (consumo) genera su respectivo asiento contable sincronizado en el Libro Diario y Cuentas T.

### 3. Libro Diario y Cuentas T (`📖`)
- **Validación Estricta de Partida Doble:** Formularios inteligentes con sumatoria de cargos y abonos en tiempo real; el sistema prohíbe el registro de asientos descuadrados.
- **Mayorización Gráfica:** Esquemas de mayor (Cuentas T) interactivos dibujados con estética corporativa (Azul y Dorado), desglosando cargos, abonos, movimientos deudores/acreedores y el saldo neto.

### 4. Automatización del Ciclo de Costos (`⚡`)
- **Simulación Completa:** Permite procesar el ciclo entero con un solo clic.
- **Flujo de Costo Industrial:** Ejecuta los traspasos lógicos de materia prima a producción, aplica la nómina (MOD) y el prorrateo de servicios y depreciaciones (GIF), determina el costo unitario real al transferir a Producto Terminado, y calcula el costo de venta según las piezas vendidas.

### 5. Reportes Financieros (`📊`)
- **Estado de Costos de Producción y de lo Vendido:** Reporte contable estructurado formal con inventarios iniciales/finales de MP, PP y PT.
- **Punto de Equilibrio:** Herramienta interactiva para calcular unidades críticas y ventas de equilibrio con una **gráfica de líneas trazada dinámicamente** en un lienzo (Canvas).

---

## 📁 Estructura del Repositorio

El proyecto se distribuye en una estructura limpia de Model-View-Controller (MVC) por componentes:

```text
Proyecto-Contabilidad-de-costos/
│
├── main.py                 # Punto de entrada y arranque de la interfaz
├── config.py               # Paleta de colores institucionales y catálogo base
├── database.py             # Capa de almacenamiento y persistencia (JSON local)
├── models.py               # Lógica matemática y contable del negocio
├── README.md               # Documentación del proyecto (esta guía)
│
└── views/                  # Vistas modulares de las pestañas
    ├── __init__.py         # Inicializador de paquete de vistas
    ├── main_window.py      # Contenedor del dashboard y menú de navegación lateral
    ├── init_view.py        # Ficha 1: Catálogo contable y saldos iniciales
    ├── warehouse_view.py   # Ficha 2: Fichas de Almacén (Promedio Ponderado)
    ├── ledger_view.py      # Ficha 3: Diario General y Esquemas de Mayor
    ├── automation_view.py  # Ficha 4: Simulador de ciclos de costos
    └── reports_view.py     # Ficha 5: Estado de costos y Punto de Equilibrio interactivo
```

---

## 🛠️ Requisitos e Instalación

El sistema ha sido desarrollado utilizando exclusivamente librerías del núcleo de Python, por lo que **no tiene dependencias externas obligatorias**. Se garantiza su portabilidad total, lo que significa que tus profesores o sinodales podrán ejecutarlo al instante en cualquier computadora.

### Requisitos Previos
- Python 3.8 o superior instalado en el sistema.

### Instrucciones de Ejecución
1. Clona el repositorio en tu máquina local:
   ```bash
   git clone https://github.com/tu-usuario/Proyecto-Contabilidad-de-costos.git
   cd Proyecto-Contabilidad-de-costos
   ```
2. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```

---

## 📖 Caso Práctico Pre-cargado

Al presionar el botón **Cargar Proyecto de Práctica**, el ERP registrará:
1. **Asiento de Apertura:** Bancos ($500k), Almacén de MP ($100k - 1,000 un. a $100 c/u), Maquinaria ($300k) contra Capital Social ($900k).
2. **Compra Adicional (Lote 2):** Compra de 500 unidades a $110.00 c/u, cambiando automáticamente el Costo Promedio Ponderado de materias primas a **$103.3333**.
3. **Parámetros por Defecto para Automatizar:**
   - Producción Objetivo: 500 unidades.
   - Precio de Venta: $350.00.
   - Costo MOD Unitario: $40.00.
   - Costo GIF Unitario: $20.00.
   - Costo Variable Unitario de Producción: **$215.00** (incluye MP promedio).
   - Costos Fijos: $45,000.00.

Al correr la automatización, el Punto de Equilibrio resultante se situará en **333.3 unidades**, lo que se visualizará inmediatamente en el gráfico del reporte.

---

## ✍️ Licencia y Créditos
Desarrollado de manera profesional como proyecto de Contabilidad de Costos y Sistemas de Información ERP. Puedes subir este código libremente a tus repositorios personales y académicos de GitHub.
