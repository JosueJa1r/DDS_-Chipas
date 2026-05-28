# Función para calcular la cantidad mínima de producción necesaria
def calcular_punto_equilibrio(costos_fijos, precio_venta, costo_variable_unitario):
    """
    Determina cuántos kilos debe vender el agricultor para cubrir sus costos sin ganar ni perder.
    Q = Costos / (Precio - Costo Variable)
    """
    if precio_venta <= costo_variable_unitario:
        # Si el costo es mayor al precio, nunca se llegará al punto de equilibrio
        return float('inf')
    return costos_fijos / (precio_venta - costo_variable_unitario)

# Función para medir el porcentaje de crecimiento del capital
def calcular_roi(inversion, ganancia):
    """
    Calcula el Retorno sobre Inversión expresado en porcentaje.
    Formula: ((Ganancia - Inversión) / Inversión) * 100
    """
    if inversion == 0:
        return 0.0
    return ((ganancia - inversion) / inversion) * 100.0

# Cálculo simple de ganancia final
def calcular_utilidad_neta(ingresos, costos_totales):
    """Retorna la ganancia neta después de restar todos los costos."""
    return ingresos - costos_totales

# Valida si el agricultor tiene el dinero suficiente para iniciar el proyecto
def evaluar_presupuesto(presupuesto, costo_total_enmienda, costo_semilla):
    """
    Compara el presupuesto disponible contra la inversión mínima (Semillas + Enmienda).
    Si no alcanza, sugiere alternativas más económicas.
    """
    inversion_requerida = costo_total_enmienda + costo_semilla
    if presupuesto >= inversion_requerida:
        return True, "Viable", inversion_requerida
    # Recomendación dinámica si el capital es insuficiente
    return False, "Excede presupuesto, evaluar maíz criollo o frijol negro", inversion_requerida
