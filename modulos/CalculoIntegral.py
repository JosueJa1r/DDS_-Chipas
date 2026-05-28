import numpy as np

def funcion_densidad_probabilidad_normal(x, mu, sigma):
    """
    Función de densidad de probabilidad para una distribución normal (campana de Gauss).
    """
    return (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-((x - mu) ** 2) / (2 * (sigma ** 2)))

def integrar_trapecio(func, a, b, n=1000, **kwargs):
    """
    Realiza la integración numérica de una función 'func' desde 'a' hasta 'b'
    utilizando la Regla del Trapecio compuesta con 'n' intervalos.
    """
    x = np.linspace(a, b, n + 1)
    y = func(x, **kwargs)
    h = (b - a) / n
    suma = 0.5 * (y[0] + y[-1]) + np.sum(y[1:-1])
    return suma * h

def calcular_probabilidad_rango_ph(ph_min, ph_max, ph_optimo, std_dev=0.5):
    """
    Calcula la probabilidad acumulada (área bajo la curva de Gauss) entre ph_min y ph_max
    para un ph_optimo específico usando integración numérica por regla de trapecios.
    Representa la asimilación óptima integrada del suelo para los requerimientos del cultivo.
    """
    # Función que representa la normal con la media y desviación estándar dadas
    func = lambda x: funcion_densidad_probabilidad_normal(x, ph_optimo, std_dev)
    
    # Calcular la integral desde ph_min hasta ph_max
    probabilidad = integrar_trapecio(func, ph_min, ph_max, n=500)
    return round(float(probabilidad), 4)
