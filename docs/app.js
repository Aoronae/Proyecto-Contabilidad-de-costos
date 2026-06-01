/* ==========================================================================
   app.js - Motor Contable de Costos e Interactividad Web
   Implementa las mismas fórmulas de valuación CPP, automatización contable
   y gráficos interactivos que la aplicación de escritorio de Python.
   ========================================================================== */

// --- 1. CATÁLOGO DE CUENTAS ESTÁNDAR ---
const CATALOGO_CUENTAS = {
    "1101": { nombre: "Bancos", tipo: "Activo", naturaleza: "Deudora" },
    "1151": { nombre: "Almacén de Materias Primas", tipo: "Activo", naturaleza: "Deudora" },
    "1152": { nombre: "Almacén de Producción en Proceso", tipo: "Activo", naturaleza: "Deudora" },
    "1153": { nombre: "Almacén de Productos Terminados", tipo: "Activo", naturaleza: "Deudora" },
    "1201": { nombre: "Maquinaria y Equipo", tipo: "Activo", naturaleza: "Deudora" },
    "1202": { nombre: "Depreciación Acumulada de Maquinaria", tipo: "Activo", naturaleza: "Acreedora" },
    "2101": { nombre: "Proveedores", tipo: "Pasivo", naturaleza: "Acreedora" },
    "2105": { nombre: "Cuentas por Pagar (MOD/Gastos)", tipo: "Pasivo", naturaleza: "Acreedora" },
    "3101": { nombre: "Capital Social", tipo: "Capital", naturaleza: "Acreedora" },
    "3105": { nombre: "Utilidad del Ejercicio", tipo: "Capital", naturaleza: "Acreedora" },
    "4101": { nombre: "Ventas", tipo: "Ingresos", naturaleza: "Acreedora" },
    "5101": { nombre: "Costo de Ventas", tipo: "Costos", naturaleza: "Deudora" },
    "5102": { nombre: "Mano de Obra Directa (MOD)", tipo: "Costos", naturaleza: "Deudora" },
    "5103": { nombre: "Cargos Indirectos (GIF)", tipo: "Costos", naturaleza: "Deudora" }
};

// --- 2. BASE DE DATOS LOCAL EN MEMORIA (ESTADO DE LA DEMO) ---
let state = {
    practiceLoaded: false,
    catalogo: {},
    saldos: {},
    diario: [],
    almacen: [],
    configCostos: {
        precioVenta: 350.0,
        costoVariableU: 120.0,
        costosFijos: 45000.0,
        produccionObjetivo: 500
    }
};

let draftMovements = []; // Borrador de movimientos del asiento actual

// Guardar estado en localStorage
function saveState() {
    localStorage.setItem("cost_erp_state", JSON.stringify(state));
}

// Cargar estado de localStorage
function loadState() {
    const saved = localStorage.getItem("cost_erp_state");
    if (!saved) return false;
    try {
        state = JSON.parse(saved);
        // Garantizar que tenga catalogo
        if (!state.catalogo) {
            state.catalogo = JSON.parse(JSON.stringify(CATALOGO_CUENTAS));
        }
        return true;
    } catch (e) {
        console.error("Error al parsear estado de localStorage:", e);
        return false;
    }
}

// --- 3. INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", () => {
    if (!loadState()) {
        resetState();
    }
    setupNavigation();
    setupEventListeners();
    setupLedgerEventListeners(); // Registrar eventos del Libro Diario
    setupModalEventListeners();  // Registrar eventos de los Modales
    updateUI();
});

// Restablecer base de datos al estado virgen en blanco
function resetState() {
    state.practiceLoaded = false;
    state.diario = [];
    state.almacen = [];
    state.catalogo = JSON.parse(JSON.stringify(CATALOGO_CUENTAS));
    state.configCostos = {
        precioVenta: 350.0,
        costoVariableU: 120.0,
        costosFijos: 45000.0,
        produccionObjetivo: 500
    };
    
    // Inicializar saldos en cero
    state.saldos = {};
    for (let code in state.catalogo) {
        state.saldos[code] = 0.0;
    }
    
    draftMovements = [];
    saveState();
}

// Navegación entre Pestañas (SPA)
function setupNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabs = document.querySelectorAll(".tab-content");
    
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetTab = item.getAttribute("data-tab");
            
            // Remover activo de botones y paneles
            navItems.forEach(i => i.classList.remove("active"));
            tabs.forEach(t => t.classList.remove("active"));
            
            // Activar actual
            item.classList.add("active");
            document.getElementById(`tab-${targetTab}`).classList.add("active");
            
            // Forzar actualización de datos en el tab actual
            updateUI();
            
            // Redibujar gráfico si navegamos a reportes
            if (targetTab === "reports") {
                setTimeout(updatePE, 100);
            }
        });
    });
}

// Enlazar Eventos del Formulario y Botones
function setupEventListeners() {
    // Cargar Caso Práctico
    document.getElementById("btn-load-practice").addEventListener("click", loadPracticeCase);
    
    // Cambiar dinámicamente inputs en almacén (Entrada / Salida)
    const whTypeSelect = document.getElementById("wh-type");
    whTypeSelect.addEventListener("change", () => {
        const costGroup = document.getElementById("group-wh-cost");
        const costInput = document.getElementById("wh-cost");
        
        if (whTypeSelect.value === "Salida") {
            costGroup.style.opacity = "0.5";
            costInput.disabled = true;
            // Prefilar con el último promedio de almacén si existe
            if (state.almacen.length > 0) {
                costInput.value = state.almacen[state.almacen.length - 1].costoPromedio.toFixed(2);
            } else {
                costInput.value = "0.00";
            }
        } else {
            costGroup.style.opacity = "1";
            costInput.disabled = false;
            costInput.value = "100.00";
        }
    });
    
    // Registrar Movimiento Manual en Almacén
    document.getElementById("btn-save-wh").addEventListener("click", saveWarehouseTransaction);
    
    // Autocompletar Ciclo Automático
    document.getElementById("btn-run-sim").addEventListener("click", runCostCycleSimulation);
    
    // Botón de Reiniciar
    document.getElementById("btn-reset").addEventListener("click", () => {
        if (confirm("¿Estás seguro de que deseas limpiar la simulación y vaciar el ERP?")) {
            resetState();
            updateUI();
            alert("Sistema restablecido correctamente.");
            // Ir al dashboard
            document.querySelector('[data-tab="init"]').click();
        }
    });
    
    // Inputs del Punto de Equilibrio (Recalcular al cambiar)
    ["pe-fc", "pe-price", "pe-vc"].forEach(id => {
        document.getElementById(id).addEventListener("input", updatePE);
    });
}

// --- 4. ACCIONES CONTABLES (LOGICA DE NEGOCIO) ---

// Recalcular saldos del Libro Diario (Mayorización Dinámica)
function recalcularSaldos() {
    // Resetear
    for (let code in state.catalogo) {
        state.saldos[code] = 0.0;
    }
    
    state.diario.forEach(asiento => {
        asiento.movimientos.forEach(mov => {
            const code = mov.cuenta;
            const debe = parseFloat(mov.debe || 0.0);
            const haber = parseFloat(mov.haber || 0.0);
            
            if (code in state.saldos) {
                const info = state.catalogo[code];
                if (info.naturaleza === "Deudora") {
                    state.saldos[code] += (debe - haber);
                } else {
                    state.saldos[code] += (haber - debe);
                }
            }
        });
    });
}

// Registrar un asiento contable validando Partida Doble
function registrarAsiento(fecha, concepto, movimientos) {
    let totalDebe = 0;
    let totalHaber = 0;
    
    movimientos.forEach(m => {
        totalDebe += parseFloat(m.debe || 0.0);
        totalHaber += parseFloat(m.haber || 0.0);
    });
    
    // Redondear a centavos
    totalDebe = Math.round(totalDebe * 100) / 100;
    totalHaber = Math.round(totalHaber * 100) / 100;
    
    if (totalDebe !== totalHaber) {
        throw new Error(`Violación de Partida Doble. Debe: $${totalDebe.toFixed(2)}, Haber: $${totalHaber.toFixed(2)}. Diferencia: $${Math.abs(totalDebe - totalHaber).toFixed(2)}`);
    }
    
    const nuevoAsiento = {
        id: state.diario.length + 1,
        fecha: fecha,
        concepto: concepto,
        movimientos: movimientos
    };
    
    state.diario.push(nuevoAsiento);
    recalcularSaldos();
    saveState();
    return nuevoAsiento;
}

// Cargar Caso Práctico Completo
function loadPracticeCase() {
    resetState();
    state.practiceLoaded = true;
    
    // 1. Asiento de Apertura
    const movsApertura = [
        { cuenta: "1101", debe: 500000.0, haber: 0.0 },      // Bancos
        { cuenta: "1151", debe: 100000.0, haber: 0.0 },      // Almacén MP (1,000 un. @ $100 c/u)
        { cuenta: "1201", debe: 300000.0, haber: 0.0 },      // Maquinaria
        { cuenta: "3101", debe: 0.0, haber: 900000.0 }       // Capital Social
    ];
    registrarAsiento("2026-05-01", "Asiento de Apertura del Ejercicio", movsApertura);
    
    // Registrar saldo inicial en la tarjeta de almacén
    state.almacen.push({
        fecha: "2026-05-01",
        concepto: "Inventario Inicial",
        tipo: "Entrada",
        cantidad: 1000,
        costoUnitario: 100.0,
        debe: 100000.0,
        haber: 0.0,
        existencia: 1000,
        saldoValores: 100000.0,
        costoPromedio: 100.0
    });
    
    // 2. Compra de MP adicional (Lote 2)
    // 500 un. a $110.00 c/u. Debe: $55,000. Promedio subirá a $103.3333
    const cantidadCompra = 500;
    const costoCompra = 110.0;
    const debeCompra = cantidadCompra * costoCompra;
    
    const prevExistencia = 1000;
    const prevSaldoValores = 100000.0;
    
    const nuevaExistencia = prevExistencia + cantidadCompra;
    const nuevoSaldo = prevSaldoValores + debeCompra;
    const nuevoPromedio = nuevoSaldo / nuevaExistencia;
    
    state.almacen.push({
        fecha: "2026-05-05",
        concepto: "Compra MP Lote 2",
        tipo: "Entrada",
        cantidad: cantidadCompra,
        costoUnitario: costoCompra,
        debe: debeCompra,
        haber: 0.0,
        existencia: nuevaExistencia,
        saldoValores: nuevoSaldo,
        costoPromedio: nuevoPromedio
    });
    
    // Asiento contable de compra
    const movsCompra = [
        { cuenta: "1151", debe: debeCompra, haber: 0.0 },
        { cuenta: "1101", debe: 0.0, haber: debeCompra }
    ];
    registrarAsiento("2026-05-05", "Compra MP Lote 2 (500 un. @ $110.00)", movsCompra);
    
    updateUI();
    alert("El ejercicio práctico ha sido cargado con éxito.\nSe inicializaron los saldos de apertura y cuentas contables.");
}

// Registrar Movimiento Manual en Tarjeta de Almacén
function saveWarehouseTransaction() {
    const date = document.getElementById("wh-date").value;
    const type = document.getElementById("wh-type").value;
    const concept = document.getElementById("wh-concept").value.trim();
    const qtyInput = document.getElementById("wh-qty").value;
    const costInput = document.getElementById("wh-cost").value;
    
    if (!concept || !qtyInput) {
        alert("Debes llenar todos los campos obligatorios.");
        return;
    }
    
    const qty = parseInt(qtyInput);
    if (qty <= 0) {
        alert("La cantidad debe ser mayor a cero.");
        return;
    }
    
    let prevExistencia = 0;
    let prevSaldo = 0.0;
    let lastCpp = 0.0;
    
    if (state.almacen.length > 0) {
        const lastItem = state.almacen[state.almacen.length - 1];
        prevExistencia = lastItem.existencia;
        prevSaldo = lastItem.saldoValores;
        lastCpp = lastItem.costoPromedio;
    }
    
    if (type === "Entrada") {
        const cost = parseFloat(costInput);
        if (cost <= 0) {
            alert("El costo debe ser mayor a cero.");
            return;
        }
        
        const debe = qty * cost;
        const nuevaExistencia = prevExistencia + qty;
        const nuevoSaldo = prevSaldo + debe;
        const cpp = nuevoSaldo / nuevaExistencia;
        
        state.almacen.push({
            fecha: date,
            concepto: concept,
            tipo: "Entrada",
            cantidad: qty,
            costoUnitario: cost,
            debe: debe,
            haber: 0.0,
            existencia: nuevaExistencia,
            saldoValores: nuevoSaldo,
            costoPromedio: cpp
        });
        
        // Asiento
        registrarAsiento(date, `Compra MP: ${concept} (${qty} un.)`, [
            { cuenta: "1151", debe: debe, haber: 0.0 },
            { cuenta: "1101", debe: 0.0, haber: debe }
        ]);
        
    } else {
        // Salida
        if (qty > prevExistencia) {
            alert(`Existencia insuficiente en almacén. Disponible: ${prevExistencia} unidades.`);
            return;
        }
        
        const haber = qty * lastCpp;
        const nuevaExistencia = prevExistencia - qty;
        const nuevoSaldo = nuevaExistencia === 0 ? 0.0 : prevSaldo - haber;
        const cpp = nuevaExistencia === 0 ? 0.0 : lastCpp;
        
        state.almacen.push({
            fecha: date,
            concepto: concept,
            tipo: "Salida",
            cantidad: qty,
            costoUnitario: lastCpp,
            debe: 0.0,
            haber: haber,
            existencia: nuevaExistencia,
            saldoValores: nuevoSaldo,
            costoPromedio: cpp
        });
        
        // Asiento
        registrarAsiento(date, `Consumo MP: ${concept} (${qty} un.)`, [
            { cuenta: "1152", debe: haber, haber: 0.0 },
            { cuenta: "1151", debe: 0.0, haber: haber }
        ]);
    }
    
    // Limpiar campos
    document.getElementById("wh-concept").value = "";
    document.getElementById("wh-qty").value = "";
    
    updateUI();
    alert("Movimiento de almacén registrado con éxito.");
}

// Simulador Completo del Ciclo de Costos Automático
function runCostCycleSimulation() {
    if (state.almacen.length === 0) {
        alert("El auxiliar de almacén está vacío. Cargue el ejercicio primero.");
        return;
    }
    
    const qty = parseInt(document.getElementById("sim-qty").value);
    const price = parseFloat(document.getElementById("sim-price").value);
    const modU = parseFloat(document.getElementById("sim-mod").value);
    const gifU = parseFloat(document.getElementById("sim-gif").value);
    
    if (qty <= 0 || price <= 0 || modU <= 0 || gifU <= 0) {
        alert("Todos los parámetros del ciclo deben ser mayores a cero.");
        return;
    }
    
    const fechaProceso = "2026-05-30";
    
    try {
        // 1. Salida de MPD a Producción en Proceso
        // Estimamos consumo de 1.5 unidades de MP por unidad final
        const qtyConsumoMP = Math.floor(qty * 1.5);
        const lastItem = state.almacen[state.almacen.length - 1];
        const prevExistencia = lastItem.existencia;
        const prevSaldo = lastItem.saldoValores;
        const lastCpp = lastItem.costoPromedio;
        
        if (qtyConsumoMP > prevExistencia) {
            alert(`Materia prima insuficiente en almacén para producir ${qty} unidades. Se requieren ${qtyConsumoMP} un., pero solo cuentas con ${prevExistencia}. Registra una compra primero.`);
            return;
        }
        
        const haberMP = qtyConsumoMP * lastCpp;
        const nuevaExistencia = prevExistencia - qtyConsumoMP;
        const nuevoSaldo = nuevaExistencia === 0 ? 0.0 : prevSaldo - haberMP;
        const cpp = nuevaExistencia === 0 ? 0.0 : lastCpp;
        
        state.almacen.push({
            fecha: fechaProceso,
            concepto: `Consumo simulación Orden #${101}`,
            tipo: "Salida",
            cantidad: qtyConsumoMP,
            costoUnitario: lastCpp,
            debe: 0.0,
            haber: haberMP,
            existencia: nuevaExistencia,
            saldoValores: nuevoSaldo,
            costoPromedio: cpp
        });
        
        // Asiento automático 1: Consumo MPD
        registrarAsiento(fechaProceso, `Consumo MPD simulación Orden #${101}`, [
            { cuenta: "1152", debe: haberMP, haber: 0.0 },
            { cuenta: "1151", debe: 0.0, haber: haberMP }
        ]);
        
        // 2. Aplicación de Mano de Obra Directa (MOD)
        const totalMOD = qty * modU;
        // Asiento automático 2: Nómina MOD
        registrarAsiento(fechaProceso, `Aplicación MOD: ${qty} un. a $${modU.toFixed(2)} c/u`, [
            { cuenta: "1152", debe: totalMOD, haber: 0.0 },
            { cuenta: "2105", debe: 0.0, haber: totalMOD }
        ]);
        
        // 3. Aplicación de Cargos Indirectos (GIF)
        const totalGIF = qty * gifU;
        // Asiento automático 3: Aplicación GIF (depreciación y servicios por pagar)
        registrarAsiento(fechaProceso, `Aplicación GIF: ${qty} un. a $${gifU.toFixed(2)} c/u`, [
            { cuenta: "1152", debe: totalGIF, haber: 0.0 },
            { cuenta: "2105", debe: 0.0, haber: totalGIF }
        ]);
        
        // 4. Traspaso a Producto Terminado
        const costoTotalProduccion = haberMP + totalMOD + totalGIF;
        const costoUnitarioCalculado = costoTotalProduccion / qty;
        
        // Asiento automático 4: Producción Procesada a Producto Terminado
        registrarAsiento(fechaProceso, `Traspaso PT: ${qty} un. terminadas a $${costoUnitarioCalculado.toFixed(2)} c/u`, [
            { cuenta: "1153", debe: costoTotalProduccion, haber: 0.0 },
            { cuenta: "1152", debe: 0.0, haber: costoTotalProduccion }
        ]);
        
        // 5. Ventas del Periodo (Simulamos venta del 80% del lote)
        const qtyVenta = Math.floor(qty * 0.8);
        const importeVenta = qtyVenta * price;
        const costoVenta = qtyVenta * costoUnitarioCalculado;
        
        // Asiento automático 5A: Registro de Ingreso de Ventas
        registrarAsiento(fechaProceso, `Venta periodo: ${qtyVenta} un. a $${price.toFixed(2)} c/u`, [
            { cuenta: "1101", debe: importeVenta, haber: 0.0 },
            { cuenta: "4101", debe: 0.0, haber: importeVenta }
        ]);
        
        // Asiento automático 5B: Costo de Ventas
        registrarAsiento(fechaProceso, `Registro Costo de Ventas: ${qtyVenta} un.`, [
            { cuenta: "5101", debe: costoVenta, haber: 0.0 },
            { cuenta: "1153", debe: 0.0, haber: costoVenta }
        ]);
        
        // Guardar configuración del análisis de equilibrio
        state.configCostos = {
            precioVenta: price,
            costoVariableU: parseFloat((costoUnitarioCalculado).toFixed(2)),
            costosFijos: 45000.0,
            produccionObjetivo: qty
        };
        
        // Sincronizar inputs de Punto de Equilibrio
        document.getElementById("pe-price").value = price.toFixed(2);
        document.getElementById("pe-vc").value = costoUnitarioCalculado.toFixed(2);
        
        updateUI();
        
        alert(`Cierre de costos procesado con éxito para ${qty} unidades.\n\nSe registraron los asientos de diario automáticos de traspasos y consumos y se determinó el Costo Unitario de Producción ($${costoUnitarioCalculado.toFixed(2)}).\n\nRedirigiendo a reportes...`);
        
        // Ir a pestaña de reportes de inmediato
        document.querySelector('[data-tab="reports"]').click();
        
    } catch (e) {
        alert("Error en proceso: " + e.message);
    }
}

// --- 5. RENDERIZACIÓN DE INTERFAZ GRÁFICA (UI) ---

function updateUI() {
    updateCatalogUI();
    updateWarehouseUI();
    updateReportsUI();
    updatePEDisplay();
    updateJournalAccountsSelect(); // Sincronizar cuentas en selector del diario
    renderJournalHistory();        // Pintar diario general
    renderCuentasT();              // Pintar esquemas de mayor
}

// Actualizar el selector de cuentas del Libro Diario
function updateJournalAccountsSelect() {
    const select = document.getElementById("journal-account");
    if (!select) return;
    select.innerHTML = "";
    
    const sortedCodes = Object.keys(state.catalogo).sort();
    sortedCodes.forEach(code => {
        const option = document.createElement("option");
        option.value = code;
        option.innerText = `${code} - ${state.catalogo[code].nombre}`;
        select.appendChild(option);
    });
}

// Pintar Catálogo de Cuentas
function updateCatalogUI() {
    const tbody = document.querySelector("#table-catalog tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    
    // Cuentas ordenadas por código
    const sortedCodes = Object.keys(state.catalogo).sort();
    
    sortedCodes.forEach(code => {
        const info = state.catalogo[code];
        const saldo = state.saldos[code] || 0.0;
        const saldoStr = saldo > 0 ? `$ ${saldo.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "$ 0.00";
        
        const row = document.createElement("tr");
        row.style.cursor = "pointer";
        row.setAttribute("data-code", code);
        row.innerHTML = `
            <td><strong>${code}</strong></td>
            <td>${info.nombre}</td>
            <td><span class="flow-tag bg-blue" style="font-size:0.7rem; background-color:#334155;">${info.tipo}</span></td>
            <td>${info.naturaleza}</td>
            <td class="text-right"><strong>${saldoStr}</strong></td>
        `;
        // Enlazar doble clic para ajustar saldo
        row.addEventListener("dblclick", () => {
            openAdjustSaldo(code, info.nombre);
        });
        // Enlazar click simple para resaltar
        row.addEventListener("click", () => {
            tbody.querySelectorAll("tr").forEach(r => {
                r.classList.remove("selected_catalog");
                r.style.backgroundColor = "";
            });
            row.classList.add("selected_catalog");
            row.style.backgroundColor = "var(--color-gold-light)";
        });
        tbody.appendChild(row);
    });
}

// Pintar Tarjeta de Almacén y KPIs
function updateWarehouseUI() {
    const tbody = document.querySelector("#table-warehouse tbody");
    tbody.innerHTML = "";
    
    state.almacen.forEach(item => {
        const cantStr = item.tipo === "Entrada" ? `+${item.cantidad}` : `-${item.cantidad}`;
        const debeStr = item.debe > 0 ? `$ ${item.debe.toLocaleString("es-MX", { minimumFractionDigits: 2 })}` : "-";
        const haberStr = item.haber > 0 ? `$ ${item.haber.toLocaleString("es-MX", { minimumFractionDigits: 2 })}` : "-";
        const costoStr = `$ ${item.costoUnitario.toLocaleString("es-MX", { minimumFractionDigits: 2 })}`;
        const saldoStr = `$ ${item.saldoValores.toLocaleString("es-MX", { minimumFractionDigits: 2 })}`;
        const promStr = `$ ${item.costoPromedio.toLocaleString("es-MX", { minimumFractionDigits: 4, maximumFractionDigits: 4 })}`;
        
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.fecha}</td>
            <td>${item.concepto}</td>
            <td><span class="flow-tag ${item.tipo === "Entrada" ? "bg-blue" : "bg-gold"}">${item.tipo}</span></td>
            <td><strong>${cantStr}</strong></td>
            <td class="text-right">${costoStr}</td>
            <td class="text-right debe-val">${debeStr}</td>
            <td class="text-right haber-val">${haberStr}</td>
            <td><strong>${item.existencia}</strong></td>
            <td class="text-right" style="color:var(--color-primary); font-weight:600;">${saldoStr}</td>
            <td class="text-right txt-gold">${promStr}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Actualizar KPIs
    if (state.almacen.length > 0) {
        const last = state.almacen[state.almacen.length - 1];
        document.getElementById("kpi-qty").innerText = `${last.existencia.toLocaleString()} unidades`;
        document.getElementById("kpi-cpp").innerText = `$ ${last.costoPromedio.toLocaleString("es-MX", { minimumFractionDigits: 4, maximumFractionDigits: 4 })}`;
        document.getElementById("kpi-total-val").innerText = `$ ${last.saldoValores.toLocaleString("es-MX", { minimumFractionDigits: 2 })}`;
    } else {
        document.getElementById("kpi-qty").innerText = "0 unidades";
        document.getElementById("kpi-cpp").innerText = "$ 0.0000";
        document.getElementById("kpi-total-val").innerText = "$ 0.00";
    }
    
    // Setear fecha al día de hoy
    document.getElementById("wh-date").value = new Date().toISOString().split("T")[0];
}

// Pintar el Estado de Costos Formal
function updateReportsUI() {
    const container = document.getElementById("report-items");
    container.innerHTML = "";
    
    // Obtener valores dinámicos
    const invIniMP = state.practiceLoaded ? 100000.00 : 0.0;
    
    let comprasMP = 0.0;
    let first = true;
    state.almacen.forEach(item => {
        if (item.concepto === "Inventario Inicial" && first) {
            first = false;
            return;
        }
        if (item.tipo === "Entrada") {
            comprasMP += item.debe;
        }
    });
    
    const mpDisponible = invIniMP + comprasMP;
    const invFinMP = state.almacen.length > 0 ? state.almacen[state.almacen.length - 1].saldoValores : 0.0;
    const mpUtilizada = mpDisponible - invFinMP;
    
    let modAplicada = 0.0;
    let gifAplicado = 0.0;
    state.diario.forEach(a => {
        if (a.concepto.includes("Aplicación MOD")) {
            a.movimientos.forEach(m => {
                if (m.cuenta === "1152") modAplicada += m.debe;
            });
        } else if (a.concepto.includes("Aplicación GIF")) {
            a.movimientos.forEach(m => {
                if (m.cuenta === "1152") gifAplicado += m.debe;
            });
        }
    });
    
    const costoProcesada = mpUtilizada + modAplicada + gifAplicado;
    const invIniPP = 0.0;
    
    // Calcular inventario final PP (lo que quedó en saldo de 1152)
    const invFinPP = state.saldos["1152"] || 0.0;
    const costoTerminada = costoProcesada + invIniPP - invFinPP;
    
    const invIniPT = 0.0;
    const invFinPT = state.saldos["1153"] || 0.0;
    const costoVendido = state.saldos["5101"] || 0.0;
    
    const prodObj = state.configCostos.produccionObjetivo || 500;
    const costoUnitario = prodObj > 0 ? costoTerminada / prodObj : 0.0;
    
    const reportSchema = [
        { label: "Inventario Inicial de Materias Primas", val: invIniMP, indent: 0 },
        { label: "(+) Compras de Materias Primas", val: comprasMP, indent: 0, sign: "+" },
        { label: "(=) Materias Primas Disponibles", val: mpDisponible, indent: 1, bold: true },
        { label: "(-) Inventario Final de Materias Primas", val: invFinMP, indent: 0, sign: "-" },
        { label: "(=) Materia Prima Directa Utilizada", val: mpUtilizada, indent: 1, bold: true },
        { label: "(+) Mano de Obra Directa Aplicada", val: modAplicada, indent: 0, sign: "+" },
        { label: "(+) Cargos Indirectos (GIF) Aplicados", val: gifAplicado, indent: 0, sign: "+" },
        { label: "(=) Costo de la Producción Procesada", val: costoProcesada, indent: 1, bold: true },
        { label: "(+) Inventario Inicial de Producción en Proceso", val: invIniPP, indent: 0, sign: "+" },
        { label: "(-) Inventario Final de Producción en Proceso", val: invFinPP, indent: 0, sign: "-" },
        { label: "(=) Costo de la Producción Terminada", val: costoTerminada, indent: 2, bold: true },
        { label: "(+) Inventario Inicial de Productos Terminados", val: invIniPT, indent: 0, sign: "+" },
        { label: "(-) Inventario Final de Productos Terminados", val: invFinPT, indent: 0, sign: "-" },
        { label: "(=) COSTO DE PRODUCCIÓN DE LO VENDIDO", val: costoVendido, indent: 2, bold: true, final: true }
    ];
    
    reportSchema.forEach(row => {
        const div = document.createElement("div");
        div.className = `report-row indent-${row.indent} ${row.bold ? "bold" : ""} ${row.final ? "final" : ""}`;
        
        const signStr = row.sign ? `${row.sign} ` : "";
        const valStr = `$ ${row.val.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        
        div.innerHTML = `
            <span>${row.label}</span>
            <span>${signStr}${valStr}</span>
        `;
        container.appendChild(div);
    });
    
    // Actualizar costo unitario
    document.getElementById("report-unit-cost").innerText = `Costo Unitario de Producción: $ ${costoUnitario.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} c/u (Lote de ${prodObj} un.)`;
}

// Pintar variables del Punto de Equilibrio y disparar Gráfico Canvas
function updatePEDisplay() {
    const fc = parseFloat(document.getElementById("pe-fc").value || 45000);
    const price = parseFloat(document.getElementById("pe-price").value || 350);
    const vc = parseFloat(document.getElementById("pe-vc").value || 215);
    
    if (price <= vc) {
        document.getElementById("txt-pe-units").innerText = "Pto. Equilibrio: Margen Negativo";
        document.getElementById("txt-pe-sales").innerText = "Ventas Requeridas: Pérdida Infinita";
        return;
    }
    
    const margin = price - vc;
    const peUnits = fc / margin;
    const peSales = peUnits * price;
    
    document.getElementById("txt-pe-units").innerText = `Pto. Equilibrio: ${peUnits.toLocaleString("es-MX", { maximumFractionDigits: 1 })} unidades`;
    document.getElementById("txt-pe-sales").innerText = `Ventas Requeridas: $ ${peSales.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    
    drawPEChart(fc, price, vc, peUnits);
}

// Wrapper para actualización interactiva al teclear variables del PE
function updatePE() {
    updatePEDisplay();
}

// --- 6. DIBUJADO DE LA GRÁFICA DEL PUNTO DE EQUILIBRIO EN CANVAS ---
function drawPEChart(fc, price, vc, peUnits) {
    const canvas = document.getElementById("chartCanvas");
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;
    
    // Limpiar Canvas
    ctx.clearRect(0, 0, w, h);
    
    // Márgenes
    const mxLeft = 55;
    const mxRight = 25;
    const myTop = 20;
    const myBottom = 40;
    
    const gw = w - mxLeft - mxRight;
    const gh = h - myTop - myBottom;
    
    // Rango del Eje X (desde 0 a PE * 1.8)
    const maxUnits = peUnits > 0 ? Math.ceil(peUnits * 1.8) : 1000;
    
    // Rango del Eje Y (Ventas al maxUnits)
    const maxSales = maxUnits * price;
    
    // Función de conversión a coordenadas Canvas en píxeles
    function toPx(units, val) {
        const pxX = mxLeft + (units / maxUnits) * gw;
        const pxY = (myTop + gh) - (val / maxSales) * gh;
        return { x: pxX, y: pxY };
    }
    
    // 1. Dibujar Rejilla y Ejes sutiles
    ctx.strokeStyle = "#F1F5F9";
    ctx.lineWidth = 1;
    
    // Líneas horizontales (Rejilla Eje Y)
    for (let i = 0; i <= 4; i++) {
        const val = (maxSales / 4) * i;
        const pos = toPx(0, val);
        
        ctx.beginPath();
        ctx.moveTo(mxLeft, pos.y);
        ctx.lineTo(mxLeft + gw, pos.y);
        ctx.stroke();
        
        // Etiquetas Eje Y
        ctx.fillStyle = "#64748B";
        ctx.font = "10px Inter";
        ctx.textAlign = "right";
        ctx.fillText(`$${(val/1000).toFixed(0)}k`, mxLeft - 8, pos.y + 3);
    }
    
    // Líneas verticales (Rejilla Eje X)
    for (let i = 0; i <= 4; i++) {
        const units = (maxUnits / 4) * i;
        const pos = toPx(units, 0);
        
        ctx.beginPath();
        ctx.moveTo(pos.x, myTop);
        ctx.lineTo(pos.x, myTop + gh);
        ctx.stroke();
        
        // Etiquetas Eje X
        ctx.fillStyle = "#64748B";
        ctx.font = "10px Inter";
        ctx.textAlign = "center";
        ctx.fillText(Math.round(units).toLocaleString(), pos.x, myTop + gh + 15);
    }
    
    // Dibujar Ejes Principales
    ctx.strokeStyle = "#CBD5E1";
    ctx.lineWidth = 1.5;
    
    ctx.beginPath();
    ctx.moveTo(mxLeft, myTop);
    ctx.lineTo(mxLeft, myTop + gh);
    ctx.lineTo(mxLeft + gw, myTop + gh);
    ctx.stroke();
    
    // 2. Trazar Líneas Financieras
    
    // A. Costos Fijos (Línea punteada gris)
    const p1CF = toPx(0, fc);
    const p2CF = toPx(maxUnits, fc);
    
    ctx.strokeStyle = "#94A3B8";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(p1CF.x, p1CF.y);
    ctx.lineTo(p2CF.x, p2CF.y);
    ctx.stroke();
    ctx.setLineDash([]); // Reset
    
    ctx.fillStyle = "#64748B";
    ctx.font = "bold 9px Inter";
    ctx.textAlign = "right";
    ctx.fillText("Costos Fijos", p2CF.x - 5, p2CF.y - 6);
    
    // B. Ventas / Ingreso Total (Línea Verde Esmeralda)
    const p1V = toPx(0, 0);
    const p2V = toPx(maxUnits, maxUnits * price);
    
    ctx.strokeStyle = "#0B3C30";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(p1V.x, p1V.y);
    ctx.lineTo(p2V.x, p2V.y);
    ctx.stroke();
    
    ctx.fillStyle = "#0B3C30";
    ctx.font = "bold 9px Inter";
    ctx.textAlign = "right";
    ctx.fillText("Ventas", p2V.x - 5, p2V.y - 8);
    
    // C. Costo Total (Costos Fijos + Cantidad * CVU) (Línea Roja)
    const p1CT = toPx(0, fc);
    const p2CT = toPx(maxUnits, fc + (maxUnits * vc));
    
    ctx.strokeStyle = "#EF4444";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(p1CT.x, p1CT.y);
    ctx.lineTo(p2CT.x, p2CT.y);
    ctx.stroke();
    
    ctx.fillStyle = "#B91C1C";
    ctx.font = "bold 9px Inter";
    ctx.textAlign = "right";
    ctx.fillText("Costo Total", p2CT.x - 5, p2CT.y + 12);
    
    // 3. Marcar el Punto de Equilibrio (Intersección)
    if (peUnits > 0 && peUnits < maxUnits) {
        const pePos = toPx(peUnits, peUnits * price);
        
        // Líneas de alineación punteadas en Dorado Arena
        ctx.strokeStyle = "#B58C3D";
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);
        
        ctx.beginPath();
        ctx.moveTo(pePos.x, pePos.y);
        ctx.lineTo(pePos.x, myTop + gh); // Hacia eje X
        ctx.moveTo(pePos.x, pePos.y);
        ctx.lineTo(mxLeft, pePos.y); // Hacia eje Y
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Dibujar círculo dorado de PE
        ctx.fillStyle = "#B58C3D";
        ctx.strokeStyle = "#0B3C30";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(pePos.x, pePos.y, 6, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();
        
        // Globo informativo
        ctx.fillStyle = "#7E5E1C";
        ctx.font = "bold 10px Inter";
        ctx.textAlign = "left";
        ctx.fillText(`PE (${Math.round(peUnits)} un.)`, pePos.x + 10, pePos.y - 4);
    }
}

/* ==========================================================================
   MÓDULOS DE LIBRO DIARIO, CUENTAS T Y MODALES (PARIDAD CON PYTHON)
   ========================================================================== */

// --- EVENTOS DEL LIBRO DIARIO ---
function setupLedgerEventListeners() {
    // Inicializar inputs del Diario con la fecha de hoy
    const jDate = document.getElementById("journal-date");
    if (jDate) {
        jDate.value = new Date().toISOString().split("T")[0];
    }
    
    // Agregar movimiento al borrador
    const btnAdd = document.getElementById("btn-add-movement");
    if (btnAdd) {
        btnAdd.addEventListener("click", addMovementToDraft);
    }
    
    // Eliminar fila del borrador
    const btnDelRow = document.getElementById("btn-del-draft-row");
    if (btnDelRow) {
        btnDelRow.addEventListener("click", () => {
            const table = document.getElementById("table-draft");
            const selectedRow = table.querySelector("tbody tr.selected");
            if (!selectedRow) {
                alert("Por favor, selecciona una fila del borrador contable para eliminar.");
                return;
            }
            const idx = parseInt(selectedRow.getAttribute("data-index"));
            draftMovements.splice(idx, 1);
            updateDraftUI();
        });
    }
    
    // Guardar Asiento Diario completo
    const btnSaveJournal = document.getElementById("btn-save-journal");
    if (btnSaveJournal) {
        btnSaveJournal.addEventListener("click", submitAsientoContable);
    }
}

// Agregar movimiento individual al borrador en memoria
function addMovementToDraft() {
    const acctSelect = document.getElementById("journal-account");
    const code = acctSelect.value;
    const debe = parseFloat(document.getElementById("journal-debe").value) || 0.0;
    const haber = parseFloat(document.getElementById("journal-haber").value) || 0.0;
    
    if (debe < 0 || haber < 0) {
        alert("Los importes deben ser mayores o iguales a cero.");
        return;
    }
    if (debe === 0 && haber === 0) {
        alert("Ingresa un importe mayor a cero en el Debe o en el Haber.");
        return;
    }
    if (debe > 0 && haber > 0) {
        alert("Un mismo renglón no puede tener valores en el Debe y en el Haber simultáneamente. Registre dos filas por separado.");
        return;
    }
    
    draftMovements.push({ cuenta: code, debe: debe, haber: haber });
    
    // Resetear campos de importes
    document.getElementById("journal-debe").value = "0.00";
    document.getElementById("journal-haber").value = "0.00";
    
    updateDraftUI();
}

// Pintar UI del borrador
function updateDraftUI() {
    const tbody = document.querySelector("#table-draft tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    
    let totalDebe = 0.0;
    let totalHaber = 0.0;
    
    draftMovements.forEach((mov, idx) => {
        const ctaName = state.catalogo[mov.cuenta].nombre;
        const ctaDisplay = `${mov.cuenta} - ${ctaName}`;
        
        const debeDisp = mov.debe > 0 ? `$ ${mov.debe.toFixed(2)}` : "-";
        const haberDisp = mov.haber > 0 ? `$ ${mov.haber.toFixed(2)}` : "-";
        
        const row = document.createElement("tr");
        row.setAttribute("data-index", idx);
        row.innerHTML = `
            <td>${ctaDisplay}</td>
            <td class="text-right debe-val">${debeDisp}</td>
            <td class="text-right haber-val">${haberDisp}</td>
        `;
        row.addEventListener("click", () => {
            tbody.querySelectorAll("tr").forEach(r => r.classList.remove("selected"));
            row.classList.add("selected");
            tbody.querySelectorAll("tr").forEach(r => r.style.backgroundColor = "");
            row.style.backgroundColor = "var(--color-gold-light)";
        });
        tbody.appendChild(row);
        
        totalDebe += mov.debe;
        totalHaber += mov.haber;
    });
    
    totalDebe = Math.round(totalDebe * 100) / 100;
    totalHaber = Math.round(totalHaber * 100) / 100;
    
    document.getElementById("draft-sum-debe").innerText = `Total Debe: $${totalDebe.toFixed(2)}`;
    document.getElementById("draft-sum-haber").innerText = `Total Haber: $${totalHaber.toFixed(2)}`;
    
    const statusPill = document.getElementById("draft-balance-status");
    if (totalDebe === totalHaber && draftMovements.length > 0) {
        statusPill.innerText = "Cuadrado";
        statusPill.style.backgroundColor = "var(--color-debe)";
        statusPill.style.color = "#FFFFFF";
    } else {
        statusPill.innerText = "Descuadrado";
        statusPill.style.backgroundColor = "var(--color-gold-light)";
        statusPill.style.color = "var(--color-gold-dark)";
    }
}

// Guardar Asiento Diario en el Historial Contable
function submitAsientoContable() {
    const fecha = document.getElementById("journal-date").value;
    const concepto = document.getElementById("journal-concept").value.trim();
    
    if (!fecha || !concepto) {
        alert("Por favor, especifica la Fecha y el Concepto o Glosa del asiento.");
        return;
    }
    if (draftMovements.length === 0) {
        alert("El borrador del asiento está vacío. Agrega cargos y abonos primero.");
        return;
    }
    
    try {
        registrarAsiento(fecha, concepto, draftMovements);
        alert(`¡Asiento contable '${concepto}' registrado y mayorizado exitosamente!`);
        
        // Limpiar
        draftMovements = [];
        document.getElementById("journal-concept").value = "";
        updateDraftUI();
        updateUI();
    } catch (e) {
        alert(e.message);
    }
}

// --- EVENTOS DE LOS MODALES CONTABLES ---
function setupModalEventListeners() {
    // Abrir Modal Agregar Cuenta
    const btnOpenAdd = document.getElementById("btn-add-account");
    const modalAdd = document.getElementById("modal-add-account");
    if (btnOpenAdd && modalAdd) {
        btnOpenAdd.addEventListener("click", () => {
            document.getElementById("m-add-code").value = "";
            document.getElementById("m-add-name").value = "";
            modalAdd.classList.add("active");
        });
    }
    
    // Cerrar Modal Agregar Cuenta
    const btnCancelAdd = document.getElementById("btn-cancel-add-account");
    if (btnCancelAdd && modalAdd) {
        btnCancelAdd.addEventListener("click", () => {
            modalAdd.classList.remove("active");
        });
    }
    
    // Guardar Nueva Cuenta Contable
    const btnSaveAdd = document.getElementById("btn-save-add-account");
    if (btnSaveAdd && modalAdd) {
        btnSaveAdd.addEventListener("click", () => {
            const code = document.getElementById("m-add-code").value.trim();
            const name = document.getElementById("m-add-name").value.trim();
            const tType = document.getElementById("m-add-type").value;
            const nature = document.getElementById("m-add-nature").value;
            
            if (!code || !name) {
                alert("Todos los campos del formulario son requeridos.");
                return;
            }
            if (!/^\d+$/.test(code)) {
                alert("El código de cuenta debe ser numérico.");
                return;
            }
            if (code in state.catalogo) {
                alert(`El código '${code}' ya está registrado en el catálogo.`);
                return;
            }
            
            state.catalogo[code] = { nombre: name, tipo: tType, naturaleza: nature };
            state.saldos[code] = 0.0;
            saveState();
            modalAdd.classList.remove("active");
            updateUI();
            alert(`Cuenta contable '${code} - ${name}' agregada con éxito al catálogo.`);
        });
    }
    
    // Abrir Modal Ajustar Saldo (Desde Botón de Catálogo)
    const btnOpenAdjust = document.getElementById("btn-adjust-saldo");
    if (btnOpenAdjust) {
        btnOpenAdjust.addEventListener("click", () => {
            const table = document.getElementById("table-catalog");
            const selectedRow = table.querySelector("tbody tr.selected_catalog");
            if (!selectedRow) {
                alert("Por favor, selecciona una cuenta contable del catálogo haciendo un clic en ella y luego presiona este botón, o bien haz doble clic directamente.");
                return;
            }
            const code = selectedRow.getAttribute("data-code");
            const name = state.catalogo[code].nombre;
            openAdjustSaldo(code, name);
        });
    }
    
    // Cerrar Modal Ajustar Saldo
    const modalAdjust = document.getElementById("modal-adjust-saldo");
    const btnCancelAdjust = document.getElementById("btn-cancel-adjust-saldo");
    if (btnCancelAdjust && modalAdjust) {
        btnCancelAdjust.addEventListener("click", () => {
            modalAdjust.classList.remove("active");
        });
    }
    
    // Guardar Ajuste de Saldo
    const btnSaveAdjust = document.getElementById("btn-save-adjust-saldo");
    if (btnSaveAdjust && modalAdjust) {
        btnSaveAdjust.addEventListener("click", () => {
            const code = document.getElementById("m-adj-code").value;
            const val = parseFloat(document.getElementById("m-adj-val").value);
            
            if (isNaN(val) || val < 0) {
                alert("El saldo inicial debe ser un número válido mayor o igual a cero.");
                return;
            }
            
            state.saldos[code] = Math.round(val * 100) / 100;
            saveState();
            modalAdjust.classList.remove("active");
            updateUI();
            alert(`Saldo inicial de '${code}' actualizado a $${val.toFixed(2)}.`);
        });
    }
}

// Abrir modal de saldo inicial
function openAdjustSaldo(code, name) {
    const modalAdjust = document.getElementById("modal-adjust-saldo");
    if (modalAdjust) {
        document.getElementById("m-adj-title").innerText = `Ajustar Saldo Inicial\n${code} - ${name.toUpperCase()}`;
        document.getElementById("m-adj-code").value = code;
        document.getElementById("m-adj-val").value = (state.saldos[code] || 0.0).toFixed(2);
        modalAdjust.classList.add("active");
    }
}

// --- RENDERIZACIÓN DE DIARIO Y CUENTAS T EN LA WEB ---

// Pintar el Historial del Diario General Completo
function renderJournalHistory() {
    const tbody = document.querySelector("#table-journal tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    
    state.diario.forEach(asiento => {
        let firstRow = true;
        asiento.movimientos.forEach(m => {
            const ctaName = state.catalogo[m.cuenta] ? state.catalogo[m.cuenta].nombre : "Cuenta Desconocida";
            const ctaDisp = `&nbsp;&nbsp;&nbsp;&nbsp;${m.cuenta} - ${ctaName}`;
            
            const debeStr = m.debe > 0 ? `$ ${m.debe.toLocaleString("es-MX", { minimumFractionDigits: 2 })}` : "";
            const haberStr = m.haber > 0 ? `$ ${m.haber.toLocaleString("es-MX", { minimumFractionDigits: 2 })}` : "";
            
            const row = document.createElement("tr");
            if (firstRow) {
                row.innerHTML = `
                    <td><strong>${asiento.id}</strong></td>
                    <td>${asiento.fecha}</td>
                    <td><strong>${asiento.concepto}</strong></td>
                    <td>${ctaDisp}</td>
                    <td class="text-right debe-val">${debeStr}</td>
                    <td class="text-right haber-val">${haberStr}</td>
                `;
                firstRow = false;
            } else {
                row.innerHTML = `
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>${ctaDisp}</td>
                    <td class="text-right debe-val">${debeStr}</td>
                    <td class="text-right haber-val">${haberStr}</td>
                `;
            }
            tbody.appendChild(row);
        });
        
        // Línea divisoria en blanco
        const spaceRow = document.createElement("tr");
        spaceRow.innerHTML = `<td colspan="6" style="height:8px; border-bottom:none; background-color:#F8FAFC;"></td>`;
        tbody.appendChild(spaceRow);
    });
}

// Obtener datos mayorizados de una cuenta contable específica
function obtenerCuentaTData(code) {
    const cargos = [];
    const abonos = [];
    
    state.diario.forEach(asiento => {
        asiento.movimientos.forEach(m => {
            if (m.cuenta === code) {
                const info = { fecha: asiento.fecha, concepto: asiento.concepto, id: asiento.id };
                if (m.debe > 0) {
                    info.importe = m.debe;
                    cargos.push(info);
                }
                if (m.haber > 0) {
                    info.importe = m.haber;
                    abonos.push(info);
                }
            }
        });
    });
    
    let totalDebe = cargos.reduce((acc, c) => acc + c.importe, 0);
    let totalHaber = abonos.reduce((acc, a) => acc + a.importe, 0);
    
    totalDebe = Math.round(totalDebe * 100) / 100;
    totalHaber = Math.round(totalHaber * 100) / 100;
    
    const nature = state.catalogo[code].naturaleza;
    let saldoDeudor = 0.0;
    let saldoAcreedor = 0.0;
    
    if (nature === "Deudora") {
        const diff = totalDebe - totalHaber;
        if (diff >= 0) {
            saldoDeudor = Math.round(diff * 100) / 100;
        } else {
            saldoAcreedor = Math.round(Math.abs(diff) * 100) / 100;
        }
    } else {
        const diff = totalHaber - totalDebe;
        if (diff >= 0) {
            saldoAcreedor = Math.round(diff * 100) / 100;
        } else {
            saldoDeudor = Math.round(Math.abs(diff) * 100) / 100;
        }
    }
    
    return {
        codigo: code,
        nombre: state.catalogo[code].nombre,
        cargos: cargos,
        abonos: abonos,
        totalDebe: totalDebe,
        totalHaber: totalHaber,
        saldoDeudor: saldoDeudor,
        saldoAcreedor: saldoAcreedor
    };
}

// Pintar Cuentas T dinámicamente con HTML y CSS
function renderCuentasT() {
    const grid = document.getElementById("cuentas-t-grid");
    if (!grid) return;
    grid.innerHTML = "";
    
    // Filtrar cuentas contables con movimientos o saldos
    const activeAccounts = [];
    for (let code in state.catalogo) {
        const t = obtenerCuentaTData(code);
        if (t.cargos.length > 0 || t.abonos.length > 0 || t.totalDebe > 0 || t.totalHaber > 0) {
            activeAccounts.push(t);
        }
    }
    
    if (activeAccounts.length === 0) {
        grid.innerHTML = `
            <div style="text-align:center; padding:50px; font-weight:500; color:var(--color-text-muted);">
                No hay movimientos registrados en el Diario.<br>Carga el 'Caso Práctico' o crea un Asiento para ver el Libro Mayor.
            </div>
        `;
        return;
    }
    
    activeAccounts.forEach(t => {
        const box = document.createElement("div");
        box.className = "cuenta-t-box";
        
        // Cabecera de la Cuenta T
        const header = document.createElement("div");
        header.className = "cuenta-t-header";
        header.innerText = `${t.codigo} - ${t.nombre}`;
        box.appendChild(header);
        
        // Cuerpo: columnas Debe y Haber
        const body = document.createElement("div");
        body.className = "cuenta-t-body";
        
        const debeCol = document.createElement("div");
        debeCol.className = "cuenta-t-col cuenta-t-debe";
        
        const lineDiv = document.createElement("div");
        lineDiv.className = "cuenta-t-line-div";
        
        const haberCol = document.createElement("div");
        haberCol.className = "cuenta-t-col cuenta-t-haber";
        
        // Rellenar cargos (Debe)
        t.cargos.forEach(c => {
            const row = document.createElement("div");
            row.className = "cuenta-t-mov debe-val-t";
            row.innerHTML = `(${c.id}) $ ${c.importe.toLocaleString("es-MX", { minimumFractionDigits: 2 })}`;
            debeCol.appendChild(row);
        });
        
        // Rellenar abonos (Haber)
        t.abonos.forEach(a => {
            const row = document.createElement("div");
            row.className = "cuenta-t-mov haber-val-t";
            row.innerHTML = `$ ${a.importe.toLocaleString("es-MX", { minimumFractionDigits: 2 })} (${a.id})`;
            haberCol.appendChild(row);
        });
        
        // Rellenar vacíos para balancear filas visualmente
        const maxRows = Math.max(t.cargos.length, t.abonos.length);
        const cargoDiff = maxRows - t.cargos.length;
        const abonoDiff = maxRows - t.abonos.length;
        
        for (let i = 0; i < cargoDiff; i++) {
            const empty = document.createElement("div");
            empty.className = "cuenta-t-mov";
            empty.innerHTML = "&nbsp;";
            debeCol.appendChild(empty);
        }
        for (let i = 0; i < abonoDiff; i++) {
            const empty = document.createElement("div");
            empty.className = "cuenta-t-mov";
            empty.innerHTML = "&nbsp;";
            haberCol.appendChild(empty);
        }
        
        body.appendChild(debeCol);
        body.appendChild(lineDiv);
        body.appendChild(haberCol);
        box.appendChild(body);
        
        // Línea horizontal de corte
        const hLine = document.createElement("div");
        hLine.className = "cuenta-t-h-line";
        box.appendChild(hLine);
        
        // Sumas de movimientos
        const sumas = document.createElement("div");
        sumas.className = "cuenta-t-sumas";
        sumas.innerHTML = `
            <span>$ ${t.totalDebe.toLocaleString("es-MX", { minimumFractionDigits: 2 })}</span>
            <span>$ ${t.totalHaber.toLocaleString("es-MX", { minimumFractionDigits: 2 })}</span>
        `;
        box.appendChild(sumas);
        
        // Línea final de saldo
        const hLineSaldo = document.createElement("div");
        hLineSaldo.className = "cuenta-t-h-line";
        box.appendChild(hLineSaldo);
        
        // Saldo final
        const saldoRow = document.createElement("div");
        saldoRow.className = "cuenta-t-saldo-row";
        if (t.saldoDeudor > 0) {
            saldoRow.innerHTML = `<span style="color:var(--color-secondary); font-weight:800;">SD: $ ${t.saldoDeudor.toLocaleString("es-MX", { minimumFractionDigits: 2 })}</span>`;
        } else if (t.saldoAcreedor > 0) {
            saldoRow.innerHTML = `<span style="width:100%; text-align:right; color:var(--color-gold-dark); font-weight:800;">SA: $ ${t.saldoAcreedor.toLocaleString("es-MX", { minimumFractionDigits: 2 })}</span>`;
        } else {
            saldoRow.innerHTML = `<span style="width:100%; text-align:center; color:var(--color-text-muted); font-weight:700;">Saldo: $0.00</span>`;
        }
        box.appendChild(saldoRow);
        
        grid.appendChild(box);
    });
}
