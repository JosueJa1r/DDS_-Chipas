import numpy as np



# Cálculo de Valor Presente Neto (VPN) a 5 años y 12% de interés
def calcular_vpn(utilidad_anual, inversion_inicial=0.0):
    """
    Calcula el VPN usando un factor de anualidad para 5 años al 12% (3.6048).
    Fórmula: VPN = utilidad_anual * 3.6048
    """
    return utilidad_anual * 3.6048

# Cálculo exacto de la Tasa Interna de Retorno (TIR)
def calcular_tir(inversion_inicial, utilidad_anual, n_anos=5):
    """
    Calcula numéricamente la TIR resolviendo la ecuación de valor presente:
    Inversión = utilidad_anual * factor_anualidad(TIR, n_anos)
    """
    if inversion_inicial <= 0 or utilidad_anual <= 0:
        return 0.18  # Valor predeterminado de respaldo
    if utilidad_anual * n_anos <= inversion_inicial:
        return 0.0

    low = -0.99
    high = 10.0
    for _ in range(100):
        mid = (low + high) / 2
        # Calcular factor de descuento para mid
        factor = sum(1.0 / ((1 + mid) ** t) for t in range(1, n_anos + 1))
        npv = -inversion_inicial + (utilidad_anual * factor)
        
        if abs(npv) < 1e-4:
            return mid
        if npv > 0:
            low = mid
        else:
            high = mid
    return low

# --- Funciones para Fase 5 y Reporte Técnico ---

def generar_curva_gauss(ph_optimo, std_dev=0.5):
    """
    Genera puntos x, y para graficar la distribución normal de la salud del suelo respecto al pH.
    y = f(x) con media = ph_optimo y desviación estándar = std_dev.
    Rango de pH: 3.5 a 8.5 en intervalos de 0.1.
    """
    x_vals = np.arange(3.5, 8.6, 0.1)
    y_vals = (1.0 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-((x_vals - ph_optimo) ** 2) / (2 * (std_dev ** 2)))
    
    # Retornar como lista de diccionarios para Chart.js
    puntos = [{"x": round(float(x), 2), "y": round(float(y), 4)} for x, y in zip(x_vals, y_vals)]
    return puntos

def simulacion_monte_carlo_rendimiento(rendimiento_real, costo_total_ha, precio_venta_ton, volatilidad=0.15, num_escenarios=1000):
    """
    Ejecuta una simulación estocástica para el rendimiento esperado del cultivo.
    Calcula el Punto de Equilibrio (Rendimiento mínimo requerido para cubrir costos).
    Agrupa los resultados para un histograma.
    """
    # Si el rendimiento real es 0, no hay simulación
    if rendimiento_real <= 0 or precio_venta_ton <= 0:
        return {
            "rendimiento_real": 0.0,
            "rendimiento_equilibrio": 0.0,
            "probabilidad_exito": 0.0,
            "histograma": []
        }

    # Rendimiento de equilibrio (costo / precio)
    rendimiento_equilibrio = costo_total_ha / precio_venta_ton
    
    # Simular rendimientos
    np.random.seed(42)  # Semilla fija para reproducibilidad
    variaciones = np.random.normal(0, volatilidad, num_escenarios)
    rendimientos_simulados = rendimiento_real * (1 + variaciones)
    # No puede haber rendimiento negativo
    rendimientos_simulados = np.clip(rendimientos_simulados, 0, None)
    
    # Probabilidad de superar el punto de equilibrio
    exitos = np.sum(rendimientos_simulados >= rendimiento_equilibrio)
    probabilidad_exito = (exitos / num_escenarios) * 100.0
    
    # Crear histograma (15 bins)
    counts, bin_edges = np.histogram(rendimientos_simulados, bins=15)
    histograma = []
    for i in range(len(counts)):
        bin_center = (bin_edges[i] + bin_edges[i+1]) / 2.0
        histograma.append({
            "bin_center": round(float(bin_center), 2),
            "frecuencia": int(counts[i])
        })
        
    return {
        "rendimiento_real": round(float(rendimiento_real), 2),
        "rendimiento_equilibrio": round(float(rendimiento_equilibrio), 2),
        "probabilidad_exito": round(float(probabilidad_exito), 1),
        "histograma": histograma,
        "rendimientos_crudos": [float(r) for r in rendimientos_simulados] # Útil para graficar en Python backend
    }

def generar_datos_correlacion(ph_optimo, ph_suelo, N_min, nitrogeno_suelo, pest_risk_score, num_puntos=50):
    """
    Genera un dataset sintético para correlacionar:
    X1: pH del suelo
    X2: Nutrientes (Nitrógeno)
    X3: Plagas (Nivel de riesgo)
    X4: Merma (%)
    Donde la merma se deriva de penalizaciones por pH inadecuado, falta de Nitrógeno y presencia de plagas.
    """
    np.random.seed(42) # Semilla fija
    
    # X1: pH (normal alrededor del pH real del suelo)
    pH_vals = np.random.normal(ph_suelo, 0.4, num_puntos)
    pH_vals = np.clip(pH_vals, 0.0, 14.0)
    
    # X2: Nitrógeno (normal alrededor del Nitrógeno real del suelo)
    N_vals = np.random.normal(nitrogeno_suelo, 8.0, num_puntos)
    N_vals = np.clip(N_vals, 0.0, None)
    
    # X3: Plagas (normal alrededor del puntaje de riesgo del cultivo/región)
    # Escala de plagas: 1 (Bajo) a 4 (Muy Alto)
    P_vals = np.random.normal(pest_risk_score, 0.6, num_puntos)
    P_vals = np.clip(P_vals, 1.0, 4.0)
    
    # X4: Merma (porcentaje de pérdida, derivado de las penalizaciones de X1, X2 y X3)
    mermas = []
    for ph, n, p in zip(pH_vals, N_vals, P_vals):
        # Penalización por pH: mayor desviación del óptimo -> mayor merma
        pen_ph = 18.0 * ((ph - ph_optimo) / 1.5) ** 2
        # Penalización por Nitrógeno: si está por debajo del mínimo, aumenta la merma
        pen_n = 25.0 * max(0.0, (N_min - n) / N_min) if N_min > 0 else 0.0
        # Penalización por plagas: proporcional al nivel de plaga
        pen_p = 10.0 * (p - 1.0)
        
        # Ruido agrónomo
        ruido = np.random.normal(0, 2.5)
        
        # Merma total
        merma_total = 5.0 + pen_ph + pen_n + pen_p + ruido
        mermas.append(np.clip(merma_total, 0.0, 95.0))
        
    mermas = np.array(mermas)
    
    # Crear la lista de diccionarios de puntos
    datos_parcelas = []
    for i in range(num_puntos):
        datos_parcelas.append({
            "ph": round(float(pH_vals[i]), 2),
            "nitrogeno": round(float(N_vals[i]), 1),
            "plagas": round(float(P_vals[i]), 2),
            "merma": round(float(mermas[i]), 2)
        })
        
    # Calcular matriz de correlación de Pearson
    matriz_datos = np.array([pH_vals, N_vals, P_vals, mermas])
    coef_matrix = np.corrcoef(matriz_datos)
    
    # Formatear la matriz para facilidad de lectura
    labels = ["pH (X1)", "Nutrientes (X2)", "Plagas (X3)", "Merma (X4)"]
    correlaciones = {}
    for i in range(len(labels)):
        correlaciones[labels[i]] = {}
        for j in range(len(labels)):
            # Evitar NaNs por si acaso
            val = coef_matrix[i, j]
            if np.isnan(val):
                val = 0.0
            correlaciones[labels[i]][labels[j]] = round(float(val), 4)
            
    return {
        "parcelas": datos_parcelas,
        "matriz": correlaciones
    }

