# -*- coding: utf-8 -*-
"""
models.py
Módulo de Lógica de Negocio. Implementa las reglas contables, método de costo promedio ponderado,
partida doble, mayorización dinámica de Cuentas T y el ciclo automático de costos.
"""

from config import CATALOGO_CUENTAS
import database

def recalcular_saldos(data):
    """
    Recalcula los saldos de todas las cuentas a partir del Libro Diario para
    garantizar que la información esté 100% sincronizada.
    """
    saldos = {code: 0.0 for code in CATALOGO_CUENTAS}
    
    for asiento in data["diario"]:
        for mov in asiento["movimientos"]:
            cta = mov["cuenta"]
            debe = float(mov.get("debe", 0.0))
            haber = float(mov.get("haber", 0.0))
            
            if cta in saldos:
                info = CATALOGO_CUENTAS[cta]
                if info["naturaleza"] == "Deudora":
                    saldos[cta] += (debe - haber)
                else:
                    saldos[cta] += (haber - debe)
                    
    data["saldos"] = saldos
    return data

def registrar_asiento(data, fecha, concepto, movimientos):
    """
    Registra un asiento en el Libro Diario realizando validación estricta de partida doble.
    """
    total_debe = round(sum(float(m.get("debe", 0.0)) for m in movimientos), 2)
    total_haber = round(sum(float(m.get("haber", 0.0)) for m in movimientos), 2)
    
    if total_debe != total_haber:
        raise ValueError(f"Violación de Partida Doble: El total del Debe (${total_debe}) debe ser igual al total del Haber (${total_haber}). Diferencia: ${round(abs(total_debe - total_haber), 2)}")
    
    # Crear asiento
    nuevo_asiento = {
        "id": len(data["diario"]) + 1,
        "fecha": fecha,
        "concepto": concepto,
        "movimientos": movimientos
    }
    
    data["diario"].append(nuevo_asiento)
    data = recalcular_saldos(data)
    database.save_db(data)
    return nuevo_asiento

def registrar_entrada_almacen(data, fecha, concepto, cantidad, costo_unitario):
    """
    Registra una entrada de materia prima en la Tarjeta de Almacén usando Costo Promedio Ponderado.
    """
    cantidad = int(cantidad)
    costo_unitario = round(float(costo_unitario), 2)
    debe = round(cantidad * costo_unitario, 2)
    
    # Obtener el saldo y existencias anteriores
    prev_existencia = 0
    prev_saldo = 0.0
    
    if data["almacen"]:
        prev_existencia = data["almacen"][-1]["existencia"]
        prev_saldo = data["almacen"][-1]["saldo_valores"]
        
    nueva_existencia = prev_existencia + cantidad
    nuevo_saldo = round(prev_saldo + debe, 2)
    nuevo_promedio = round(nuevo_saldo / nueva_existencia, 4) if nueva_existencia > 0 else 0.0
    
    registro = {
        "fecha": fecha,
        "concepto": concepto,
        "tipo": "Entrada",
        "cantidad": cantidad,
        "costo_unitario": costo_unitario,
        "debe": debe,
        "haber": 0.0,
        "existencia": nueva_existencia,
        "saldo_valores": nuevo_saldo,
        "costo_promedio": nuevo_promedio
    }
    
    data["almacen"].append(registro)
    
    # Generar asiento contable automático de compra
    # Cargo a Almacén de Materias Primas (1151)
    # Abono a Proveedores (2101) o Bancos (1101) - usamos Bancos para simplificar
    movs = [
        {"cuenta": "1151", "debe": debe, "haber": 0.0},
        {"cuenta": "1101", "debe": 0.0, "haber": debe}
    ]
    registrar_asiento(data, fecha, f"Compra MP: {concepto} ({cantidad} un.)", movs)
    return registro

def registrar_salida_almacen(data, fecha, concepto, cantidad):
    """
    Registra una salida de materia prima valorada al último Costo Promedio Ponderado.
    """
    cantidad = int(cantidad)
    
    prev_existencia = 0
    prev_saldo = 0.0
    costo_promedio = 0.0
    
    if data["almacen"]:
        prev_existencia = data["almacen"][-1]["existencia"]
        prev_saldo = data["almacen"][-1]["saldo_valores"]
        costo_promedio = data["almacen"][-1]["costo_promedio"]
        
    if cantidad > prev_existencia:
        raise ValueError(f"Existencia insuficiente en almacén. Solicitado: {cantidad}, Disponible: {prev_existencia}")
        
    haber = round(cantidad * costo_promedio, 2)
    nueva_existencia = prev_existencia - cantidad
    nuevo_saldo = round(prev_saldo - haber, 2)
    
    # Si la existencia llega a cero, el saldo de valores debe ser cero exacto
    if nueva_existencia == 0:
        haber = prev_saldo
        nuevo_saldo = 0.0
        nuevo_promedio = 0.0
    else:
        nuevo_promedio = costo_promedio
        
    registro = {
        "fecha": fecha,
        "concepto": concepto,
        "tipo": "Salida",
        "cantidad": cantidad,
        "costo_unitario": costo_promedio,
        "debe": 0.0,
        "haber": haber,
        "existencia": nueva_existencia,
        "saldo_valores": nuevo_saldo,
        "costo_promedio": nuevo_promedio
    }
    
    data["almacen"].append(registro)
    
    # Generar asiento contable automático de consumo en producción
    # Cargo a Almacén de Producción en Proceso (1152)
    # Abono a Almacén de Materias Primas (1151)
    movs = [
        {"cuenta": "1152", "debe": haber, "haber": 0.0},
        {"cuenta": "1151", "debe": 0.0, "haber": haber}
    ]
    registrar_asiento(data, fecha, f"Consumo MP: {concepto} ({cantidad} un.)", movs)
    return registro

def obtener_cuenta_t(data, account_code):
    """
    Obtiene los movimientos auxiliares de una cuenta específica para dibujarla en la Cuenta T.
    """
    cargos = []
    abonos = []
    
    for asiento in data["diario"]:
        for mov in asiento["movimientos"]:
            if mov["cuenta"] == account_code:
                info = {"fecha": asiento["fecha"], "concepto": asiento["concepto"], "id": asiento["id"]}
                if mov["debe"] > 0:
                    info["importe"] = mov["debe"]
                    cargos.append(info)
                if mov["haber"] > 0:
                    info["importe"] = mov["haber"]
                    abonos.append(info)
                    
    total_debe = round(sum(c["importe"] for c in cargos), 2)
    total_haber = round(sum(a["importe"] for a in abonos), 2)
    
    nature = CATALOGO_CUENTAS[account_code]["naturaleza"]
    saldo_deudor = 0.0
    saldo_acreedor = 0.0
    
    if nature == "Deudora":
        diff = total_debe - total_haber
        if diff >= 0:
            saldo_deudor = round(diff, 2)
        else:
            saldo_acreedor = round(abs(diff), 2)
    else:
        diff = total_haber - total_debe
        if diff >= 0:
            saldo_acreedor = round(diff, 2)
        else:
            saldo_deudor = round(abs(diff), 2)
            
    return {
        "codigo": account_code,
        "nombre": CATALOGO_CUENTAS[account_code]["nombre"],
        "cargos": cargos,
        "abonos": abonos,
        "total_debe": total_debe,
        "total_haber": total_haber,
        "saldo_deudor": saldo_deudor,
        "saldo_acreedor": saldo_acreedor
    }

def cargar_proyecto_practica(data):
    """
    Llena el sistema con un caso práctico simulado completo de contabilidad de costos.
    Garantiza que todos los datos estén lógicamente alineados y consistentes.
    """
    # 1. Resetear base de datos
    data = database.get_default_data()
    data["practice_project_loaded"] = True
    
    # 2. Asiento de Apertura
    asiento_apertura = [
        {"cuenta": "1101", "debe": 500000.0, "haber": 0.0},      # Bancos
        {"cuenta": "1151", "debe": 100000.0, "haber": 0.0},      # Almacén MP (1,000 unidades a $100 c/u)
        {"cuenta": "1201", "debe": 300000.0, "haber": 0.0},      # Maquinaria
        {"cuenta": "3101", "debe": 0.0, "haber": 900000.0}       # Capital Social
    ]
    registrar_asiento(data, "2026-05-01", "Asiento de Apertura del Ejercicio", asiento_apertura)
    
    # Registrar inventario inicial en la tarjeta de almacén de MP
    data["almacen"].append({
        "fecha": "2026-05-01",
        "concepto": "Inventario Inicial",
        "tipo": "Entrada",
        "cantidad": 1000,
        "costo_unitario": 100.0,
        "debe": 100000.0,
        "haber": 0.0,
        "existencia": 1000,
        "saldo_valores": 100000.0,
        "costo_promedio": 100.0
    })
    
    # 3. Compra adicional de materia prima en el mes
    # Entran 500 unidades a $110. El promedio ponderado cambiará.
    registrar_entrada_almacen(data, "2026-05-05", "Compra MP Lote 2", 500, 110.0)
    
    # Guardar base de datos
    database.save_db(data)
    return data

def autocompletar_ciclo_costos(data, prod_objetivo, precio_venta, costo_mod_u, costo_gif_u):
    """
    Algoritmo del Ciclo de Costos Automático.
    Lleva a cabo las transferencias de producción y ventas del período basándose
    en la materia prima disponible, aplicando promedios ponderados en tiempo real.
    """
    # Validar que tengamos materias primas iniciales
    if not data["almacen"]:
        raise ValueError("El almacén de materias primas está vacío. Cargue el proyecto de práctica o registre una entrada de almacén.")
        
    fecha_proceso = "2026-05-30"
    
    # 1. Consumo de MPD a Producción en Proceso
    # Para producir 'prod_objetivo', estimamos que se consume un insumo equivalente
    # Por ejemplo, para 500 unidades finales, consumimos 750 unidades de materia prima.
    cant_consumo_mp = int(prod_objetivo * 1.5)
    existencia_disponible = data["almacen"][-1]["existencia"]
    
    if cant_consumo_mp > existencia_disponible:
        # Ajustamos el consumo al máximo disponible menos un margen para no dejar en ceros absolutos si es posible
        cant_consumo_mp = existencia_disponible - 50 if existencia_disponible > 50 else existencia_disponible
        if cant_consumo_mp <= 0:
            raise ValueError(f"Existencia de materia prima críticamente baja ({existencia_disponible} un.). Imposible simular producción.")
            
    # Registrar la salida en la tarjeta de almacén (esto genera automáticamente el Asiento en Diario)
    # Cargo a Almacén de PP (1152), Abono a Almacén de MP (1151)
    salida_almacen = registrar_salida_almacen(data, fecha_proceso, f"Consumo para OP #{101}", cant_consumo_mp)
    costo_total_mpd = salida_almacen["haber"]
    
    # 2. Registro y Aplicación de Mano de Obra Directa (MOD)
    # Cargo a Producción en Proceso (1152) con Abono a Cuentas por Pagar (2105)
    costo_total_mod = round(prod_objetivo * costo_mod_u, 2)
    movs_mod = [
        {"cuenta": "1152", "debe": costo_total_mod, "haber": 0.0},
        {"cuenta": "2105", "debe": 0.0, "haber": costo_total_mod}
    ]
    registrar_asiento(data, fecha_proceso, f"Aplicación de MOD para {prod_objetivo} un. a ${costo_mod_u} c/u", movs_mod)
    
    # 3. Registro y Aplicación de Cargos Indirectos (GIF)
    # Cargo a Producción en Proceso (1152) con Abono a Depreciación Acumulada (1202) y Cuentas por Pagar (2105)
    costo_total_gif = round(prod_objetivo * costo_gif_u, 2)
    # Simulamos depreciación de maquinaria $3,000 y el resto en servicios públicos por pagar
    depr_m = min(3000.0, costo_total_gif)
    servicios_p = round(costo_total_gif - depr_m, 2)
    
    movs_gif = [
        {"cuenta": "1152", "debe": costo_total_gif, "haber": 0.0},
        {"cuenta": "1202", "debe": 0.0, "haber": depr_m},
        {"cuenta": "2105", "debe": 0.0, "haber": servicios_p}
    ]
    registrar_asiento(data, fecha_proceso, f"Aplicación de GIF (Depr. y Servicios) a la producción", movs_gif)
    
    # 4. Traspaso a Almacén de Productos Terminados (PT)
    # Costo Total de Producción = MPD + MOD + GIF
    costo_total_produccion = round(costo_total_mpd + costo_total_mod + costo_total_gif, 2)
    costo_unitario_calculado = round(costo_total_produccion / prod_objetivo, 4)
    
    # Cargo a Almacén de PT (1153) con Abono a Almacén de PP (1152)
    movs_pt = [
        {"cuenta": "1153", "debe": costo_total_produccion, "haber": 0.0},
        {"cuenta": "1152", "debe": 0.0, "haber": costo_total_produccion}
    ]
    registrar_asiento(data, fecha_proceso, f"Traspaso de Producción Terminada ({prod_objetivo} un. a ${round(costo_unitario_calculado, 2)} c/u)", movs_pt)
    
    # 5. Registro de Ventas y su Costo de Ventas
    # Supongamos que vendemos el 80% de lo producido
    unidades_vendidas = int(prod_objetivo * 0.8)
    importe_ventas = round(unidades_vendidas * precio_venta, 2)
    costo_de_ventas = round(unidades_vendidas * costo_unitario_calculado, 2)
    
    # Asiento A: Registro del ingreso por Ventas
    # Cargo a Bancos (1101) con Abono a Ventas (4101)
    movs_v = [
        {"cuenta": "1101", "debe": importe_ventas, "haber": 0.0},
        {"cuenta": "4101", "debe": 0.0, "haber": importe_ventas}
    ]
    registrar_asiento(data, fecha_proceso, f"Venta de {unidades_vendidas} unidades a ${precio_venta} c/u", movs_v)
    
    # Asiento B: Registro del Costo de lo Vendido
    # Cargo a Costo de Ventas (5101) con Abono a Almacén de PT (1153)
    movs_cv = [
        {"cuenta": "5101", "debe": costo_de_ventas, "haber": 0.0},
        {"cuenta": "1153", "debe": 0.0, "haber": costo_de_ventas}
    ]
    registrar_asiento(data, fecha_proceso, f"Registro del Costo de Ventas de {unidades_vendidas} un.", movs_cv)
    
    # Guardar configuración de costos utilizada en el cálculo
    data["config_costos"] = {
        "precio_venta": precio_venta,
        "costo_variable_u": round(costo_mod_u + costo_gif_u + (costo_total_mpd / prod_objetivo), 2),
        "costos_fijos": 45000.0,  # Valor de costos fijos de administración/ventas
        "produccion_objetivo": prod_objetivo
    }
    
    database.save_db(data)
    return data

def obtener_estado_costos(data):
    """
    Calcula los renglones contables para armar el Estado de Costos de Producción y de lo Vendido.
    """
    # Necesitamos calcular los movimientos específicos
    # Inventario Inicial de Materia Prima: saldo inicial de la tarjeta
    inv_ini_mp = 100000.0 if data.get("practice_project_loaded") else 0.0
    
    # Suma de compras de MP (Entradas en tarjeta de almacén después de la inicial)
    compras_mp = 0.0
    first = True
    for item in data["almacen"]:
        if item["concepto"] == "Inventario Inicial" and first:
            inv_ini_mp = item["debe"]
            first = False
            continue
        if item["tipo"] == "Entrada":
            compras_mp += item["debe"]
            
    mp_disponible = inv_ini_mp + compras_mp
    
    # Inventario Final de MP: saldo final en valores de la tarjeta
    inv_fin_mp = data["almacen"][-1]["saldo_valores"] if data["almacen"] else 0.0
    mp_utilizada = mp_disponible - inv_fin_mp
    
    # MOD aplicada
    mod_aplicada = 0.0
    # GIF aplicado
    gif_aplicado = 0.0
    
    for asiento in data["diario"]:
        if "Aplicación de MOD" in asiento["concepto"]:
            for m in asiento["movimientos"]:
                if m["cuenta"] == "1152": # Cargo a Producción en Proceso
                    mod_aplicada += m["debe"]
        elif "Aplicación de GIF" in asiento["concepto"]:
            for m in asiento["movimientos"]:
                if m["cuenta"] == "1152": # Cargo a Producción en Proceso
                    gif_aplicado += m["debe"]
                    
    costo_produccion_procesada = mp_utilizada + mod_aplicada + gif_aplicado
    
    # Almacén de Producción en Proceso (supongamos inventarios iniciales/finales de PP en cero)
    inv_ini_pp = 0.0
    inv_fin_pp = 0.0
    
    # Si hay cargos que no se traspasaron aún
    pp_t = obtener_cuenta_t(data, "1152")
    inv_fin_pp = pp_t["saldo_deudor"]
    
    costo_produccion_terminada = costo_produccion_procesada + inv_ini_pp - inv_fin_pp
    
    # Almacén de Productos Terminados
    inv_ini_pt = 0.0
    pt_t = obtener_cuenta_t(data, "1153")
    inv_fin_pt = pt_t["saldo_deudor"]
    
    costo_de_lo_vendido = pt_t["total_haber"] # Lo que salió de PT hacia Costo de Ventas
    
    # Cantidad producida
    prod_objetivo = data["config_costos"].get("produccion_objetivo", 500)
    costo_unitario = costo_produccion_terminada / prod_objetivo if prod_objetivo > 0 else 0.0
    
    return {
        "inv_ini_mp": round(inv_ini_mp, 2),
        "compras_mp": round(compras_mp, 2),
        "mp_disponible": round(mp_disponible, 2),
        "inv_fin_mp": round(inv_fin_mp, 2),
        "mp_utilizada": round(mp_utilizada, 2),
        "mod_aplicada": round(mod_aplicada, 2),
        "gif_aplicado": round(gif_aplicado, 2),
        "costo_produccion_procesada": round(costo_produccion_procesada, 2),
        "inv_ini_pp": round(inv_ini_pp, 2),
        "inv_fin_pp": round(inv_fin_pp, 2),
        "costo_produccion_terminada": round(costo_produccion_terminada, 2),
        "inv_ini_pt": round(inv_ini_pt, 2),
        "inv_fin_pt": round(inv_fin_pt, 2),
        "costo_de_lo_vendido": round(costo_de_lo_vendido, 2),
        "costo_unitario": round(costo_unitario, 2)
    }
