# Especificaciones de Modelos Matemáticos y Financieros
**Fundamentación Algorítmica del DSS**

Este documento detalla las fórmulas matemáticas, algoritmos de simulación y lógica de negocio implementada en los módulos del sistema.

---

## 1. Modelo de Probabilidad de Éxito Agronómico
**Ubicación:** `modulos/matematicas.py` -> `calcular_probabilidad_exito`

Este modelo estima la viabilidad de un cultivo basándose en la desviación del pH actual respecto al pH óptimo del cultivo.

### Fórmula:
$$P_{exito} = \max(0, 100 - (|pH_{suelo} - pH_{optimo}| \times 20))$$

*   **Funcionalidad**: Proporciona un porcentaje de confianza inicial. Una desviación de 1.0 punto en el pH penaliza la probabilidad en un 20%. Si la diferencia es de 5.0 puntos o más, la probabilidad es 0%.

---

## 2. Simulación de Monte Carlo (Riesgo y Rentabilidad)
**Ubicación:** `modulos/matematicas.py` -> `simulacion_monte_carlo`

Utiliza el método de Monte Carlo para proyectar la rentabilidad ante la incertidumbre climática y de mercado.

### Algoritmo:
1.  **Entrada**: Inversión inicial ($I$), Ingresos esperados ($R$), Volatilidad ($V$).
2.  **Iteración**: Se ejecutan $N=1000$ escenarios.
3.  **Variación Aleatoria**: 
    $$R_{simulado} = R \times (1 + \text{Normal}(0, V))$$
    *Donde $\text{Normal}(0, V)$ es una distribución normal con media 0 y desviación estándar $V$.*
4.  **Cálculo de Ganancia**: $G_i = R_{simulado} - I$

### Resultados:
*   **Rentabilidad Promedio**: $\frac{1}{N} \sum G_i$
*   **VaR (Value at Risk) al 95%**: Se calcula el percentil 5 de la lista de resultados para determinar el peor escenario esperado con un 95% de confianza.

---

## 3. Lógica de Aptitud Nutricional (Lógica Booleana)
**Ubicación:** `modulos/suelo.py` -> `evaluar_aptitud`

Evalúa si los macronutrientes (N, P, K) cumplen con los requerimientos mínimos de la base de datos.

### Condición Óptima:
$$\text{Apto} \iff (N \ge req_N) \land (P \ge req_P) \land (K \ge req_K) \land (pH_{min} \le pH \le pH_{max})$$

*   **Funcionalidad**: Clasifica el suelo en tres niveles (Óptimo, Moderado o No Apto) para guiar la estrategia de fertilización.

---

## 4. Modelos Financieros
**Ubicación:** `modulos/finanzas.py`

### A. Retorno de Inversión (ROI)
$$ROI = \left( \frac{\text{Ingresos} - \text{Inversión}}{\text{Inversión}} \right) \times 100$$
*   **Funcionalidad**: Mide la eficiencia del capital invertido.

### B. Punto de Equilibrio (Q)
$$Q = \frac{\text{Costos Totales}}{P_{venta} - C_{variable}}$$
*   **Funcionalidad**: Determina la cantidad mínima de kilogramos que se deben cosechar y vender para cubrir todos los costos iniciales sin tener pérdidas.

---

## 5. Costo Dinámico de Enmienda de Suelo
**Ubicación:** `modulos/suelo.py` -> `estimar_costo_correccion`

Calcula el costo de corrección de pH de forma no lineal basado en la distancia al rango óptimo.

### Fórmula:
$$\text{Costo} = 1000 + (\Delta pH \times 2000)$$
*Donde $\Delta pH$ es la diferencia absoluta entre el pH actual y el límite más cercano del rango aceptable ($ph_{min}$ o $ph_{max}$).*

*   **Funcionalidad**: Estima la inversión necesaria en cal o azufre para acondicionar el terreno, integrándose directamente en el presupuesto de la Fase 4.
