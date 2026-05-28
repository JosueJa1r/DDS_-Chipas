# Semilla Inteligente: Sistema de Apoyo a Decisiones Agrícolas (DSS)
**Proyecto de 3er Semestre - Universidad Rosario Castellanos**

Semilla Inteligente es una plataforma analítica avanzada diseñada como un Sistema de Soporte de Decisiones (DSS) para guiar a los pequeños y medianos productores del estado de Chiapas, México, en la reconversión y diversificación de sus cultivos. El sistema automatiza el análisis agronómico de la salud del suelo, la viabilidad biogeográfica regional por altitud, la predicción del riesgo de plagas y la viabilidad financiera estocástica.

---

## 📋 1. Descripción del Proyecto

El sistema ofrece una experiencia digital premium e interactiva con diseño **Glassmorphism**, organizada en un Dashboard de 5 pestañas de análisis técnico:
1.  **Evaluación General:** Reporte sintético de factibilidad agronómica y financiera para los cultivos principales de la región (Café, Cacao, Plátano y Maíz).
2.  **Salud Química (pH):** Gráfica interactiva de la curva de Gauss que representa la asimilación de nutrientes según la acidez del suelo.
3.  **Relación y Correlación (Pearson):** Matriz de coeficientes de Pearson y gráfico de dispersión de parcelas sintéticas que demuestran la influencia del pH, nitrógeno y plagas sobre la merma del cultivo.
4.  **Proyección de Rendimiento (Monte Carlo):** Histograma de frecuencias estocásticas generadas tras 1,000 iteraciones para evaluar la probabilidad de éxito financiero.
5.  **Recomendaciones y Reporte PDF:** Plan de manejo agronómico personalizado y botón de descarga para reportes PDF formales generados al vuelo en el backend.

## 🧮 2. Especificaciones de los Módulos Matemáticos

La lógica científica del sistema está programada de manera modular en los siguientes archivos bajo la carpeta `modulos/`:
*   **[Contabilidad.py](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/modulos/Contabilidad.py):** Contiene los cálculos financieros como el Valor Presente Neto (VPN) y la Tasa Interna de Retorno (TIR).
*   **[Probabilidad.py](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/modulos/Probabilidad.py):** Alberga los modelos estocásticos (curva de Gauss, simulación de Monte Carlo y correlación de Pearson).
*   **[CalculoIntegral.py](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/modulos/CalculoIntegral.py):** Implementa la integración numérica (Regla del Trapecio compuesta) para calcular el área bajo la curva normal de pH.
*   **[Database.py](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/modulos/Database.py):** Gestiona la conexión y consultas SQL con MySQL.

Estas son las bases algorítmicas y estadísticas utilizadas:

### A. Campana de Gauss de la Salud Química (pH)
Para evaluar cómo afecta la acidez a la asimilación de nutrientes, se modela la salud del suelo a través de una función de densidad de probabilidad normal (distribución de Gauss):

$$y = f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{1}{2} \left(\frac{x - \mu}{\sigma}\right)^2}$$

Donde:
*   $\mu$ (Media) = `ph_optimo` del cultivo (definido en la base de datos).
*   $\sigma$ (Desviación Estándar) = `0.5` (que representa la tolerancia agrónoma estándar del pH antes del bloqueo de nutrientes).
*   $x$ = Valores de pH en el rango de $3.5$ a $8.5$.
*   El punto rojo graficado representa el pH real ingresado por el usuario, indicando visualmente si se encuentra en la zona óptima, marginal o de descarte.

### B. Coeficiente de Correlación de Pearson
Se genera un dataset sintético de 50 parcelas simuladas basadas en los valores reales de pH, nitrógeno y nivel de riesgo de plagas. A partir de estas variables, se calcula la matriz de coeficientes de correlación de Pearson para modelar la merma porcentual ($X_4$):

$$r = \frac{\sum (x - \bar{x})(y - \bar{y})}{\sqrt{\sum (x - \bar{x})^2 \sum (y - \bar{y})^2}}$$

Donde:
*   **$X_1$ (pH):** Generado como distribución normal alrededor del pH real. La merma se incrementa cuadráticamente a mayor desviación respecto a $\mu$.
*   **$X_2$ (Nitrógeno):** Valores normales alrededor del nitrógeno real. Un nitrógeno por debajo de la tolerancia mínima aumenta linealmente la merma.
*   **$X_3$ (Plagas):** Riesgo derivado de la región y el cultivo. El nivel de merma es directamente proporcional a este factor.
*   **$X_4$ (Merma %):** Suma ponderada de las penalizaciones anteriores con ruido aleatorio agrónomo añadido para simular condiciones de campo.

### C. Simulación de Monte Carlo (Rendimiento y Riesgo)
Para evaluar la rentabilidad frente a la volatilidad de precios y el cambio climático, se ejecutan 1,000 iteraciones estocásticas basadas en el rendimiento real esperado (el cual ya incluye penalizaciones por deficiencias de suelo):

$$Rendimiento\_Simulado = Rendimiento\_Real \times (1 + \epsilon)$$
$$\epsilon \sim N(0, \sigma_{vol})$$

Donde:
*   $\sigma_{vol}$ es el coeficiente de volatilidad histórica del cultivo (ej. 20% para café, 18% para cacao).
*   Los valores de rendimiento simulados se recortan en $0$ para evitar mermas imposibles.
*   **Punto de Equilibrio (Breakeven):** Se calcula como el rendimiento mínimo por hectárea necesario para cubrir los costos:
    $$Rendimiento\_Equilibrio = \frac{Costo\_Total\_Hectarea}{Precio\_Venta\_Tonelada}$$
*   **Probabilidad de Éxito:** Es la proporción de las 1,000 simulaciones que superan el Rendimiento de Equilibrio.

### D. Valor Presente Neto (VPN) y Tasa Interna de Retorno (TIR)
*   **VPN a 5 años (Tasa de Descuento = 12%):**
    $$VPN = \left( \sum_{t=1}^{5} \frac{\text{Utilidad\_Anual\_Total}}{(1 + 0.12)^t} \right) - \text{Inversión\_Inicial}$$
    Se simplifica multiplicando la utilidad anual por el factor de anualidad acumulada para 5 años al 12% (`3.6048`).
*   **TIR (Método Numérico):**
    Resuelve mediante el método de bisección iterativo (100 pasos) la tasa de descuento $r$ tal que:
    $$VPN(r) = -Inversión\_Inicial + \sum_{t=1}^{5} \frac{Utilidad}{(1 + r)^t} = 0$$

---

## ⚙️ 3. Instrucciones de Instalación y Configuración

### Requisitos Previos
*   Python 3.10 o superior instalado en el sistema.
*   Servidor MySQL (local o en la nube como Aiven MySQL Cloud) con base de datos activa.

### Paso 1: Clonar y Crear Entorno Virtual
1.  Abre una terminal en el directorio del proyecto.
2.  Crea e inicia el entorno virtual de Python:
    ```powershell
    # En Windows (PowerShell)
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

### Paso 2: Instalar Dependencias
Instala los paquetes necesarios listados en el archivo [requirements.txt](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/requirements.txt):
```bash
pip install -r requirements.txt
```

### Paso 3: Variables de Entorno (Archivo `.env`)
Crea un archivo `.env` en la raíz del proyecto para configurar las credenciales de la base de datos (el sistema soporta nombres de clave en minúsculas y mayúsculas):
```ini
host=tu_host_mysql_o_cloud
user=tu_usuario
password=tu_contraseña
database=nombre_de_bd
port=puerto_mysql (ej. 3306)
```
> [!NOTE]
> **Modo Fallback:** Si el servidor de base de datos no está disponible o el archivo `.env` no está configurado, el sistema iniciará en **Modo Fallback**, utilizando un dataset agronómico precargado para garantizar que la aplicación web funcione al 100% durante exposiciones locales.

### Paso 4: Ejecución Local
Inicia el servidor de desarrollo Flask:
```bash
python app.py
```
Abre tu navegador en: **`http://localhost:5000`**

### Paso 5: Despliegue en Vercel
Para desplegar la aplicación en producción en Vercel:
1.  Instala Vercel CLI e inicia sesión: `npm i -g vercel` y luego `vercel login`.
2.  Despliega ejecutando: `vercel`.
3.  Configura las variables de entorno de la base de datos en la consola web de tu proyecto de Vercel.
