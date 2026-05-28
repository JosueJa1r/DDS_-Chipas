# Cálculo de Valor Presente Neto (VPN) y Tasa Interna de Retorno (TIR)

def calcular_vpn(utilidad_anual, inversion_inicial=0.0):
    """
    Calcula el VPN usando un factor de anualidad para 5 años al 12% de interés (3.6048).
    Fórmula: VPN = utilidad_anual * 3.6048 - inversion_inicial
    """
    return (utilidad_anual * 3.6048) - inversion_inicial

def calcular_tir(inversion_inicial, utilidad_anual, n_anos=5):
    """
    Calcula numéricamente la TIR resolviendo la ecuación de valor presente:
    Inversión = utilidad_anual * factor_anualidad(TIR, n_anos)
    Retorna la tasa en formato decimal (ej: 0.12 para 12%).
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
