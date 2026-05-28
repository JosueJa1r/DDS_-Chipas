# Semilla Inteligente: Sistema de Apoyo a Decisiones Agricolas (DSS)
**Proyecto de 3er Semestre - Universidad Rosario Castellanos**

Este sistema es una plataforma analitica diseñada para guiar a los pequeños y medianos productores de Chiapas, Mexico, en la toma de decisiones estrategicas para la diversificacion de cultivos. El sistema automatiza el analisis agronomico de suelo, la validacion biogeografica por altitud y las proyecciones financieras para recomendar las opciones de cultivo mas viables y rentables.

---

## 1. Como Funciona el Sistema (Las 5 Fases)

El flujo del diagnostico y recomendacion de cultivos se estructura en 5 fases secuenciales:

### Fase 1: Captura de Datos
El productor ingresa dos tipos de informacion en la interfaz:
*   **Perfil del productor:** Nombre, Region (asociada a una altitud biogeografica oficial), Superficie a cultivar (en hectareas), Presupuesto de inversion y Experiencia previa.
*   **Analisis quimico de suelo:** pH, Nitrogeno (ppm) y Materia Organica (%).

### Fase 2: Diagnostico del Suelo
El sistema realiza la evaluacion de aptitud de forma individualizada para cada cultivo registrado (Cafe, Cacao, Platano y Maiz), comparando las entradas del suelo contra sus requerimientos maximos y minimos:
*   **Altitud:** Si la altitud de la region seleccionada esta fuera del rango biogeografico tolerado por el cultivo (por ejemplo, Cacao en San Cristobal de las Casas), el cultivo es descartado de inmediato (**No Apto**).
*   **Factores de Penalizacion:** Si el suelo se encuentra dentro de los rangos tolerables pero presenta deficiencias, se aplican factores multiplicadores al rendimiento base del cultivo:
    *   **pH:** 1.0 (en rango), 0.8 (ligeramente fuera ±0.3), 0.5 (fuera por mas de 0.5), 0.0 (fuera de limites críticos).
    *   **Nitrogeno:** 1.0 (en rango), 0.6 (deficit tolerable), 0.8 (exceso tolerable), 0.0 (extremo).
    *   **Materia Organica:** 1.0 (en rango), 0.7 (deficit tolerable), 0.0 (extremo).

### Fase 3: Modelos de Rendimiento y Riesgo
*   **Rendimiento Real:** Se calcula como `Rendimiento_real = Rendimiento_base * Factor_pH * Factor_N * Factor_MO`.
*   **Volatilidad (Monte Carlo):** Se utiliza la volatilidad historica registrada en la base de datos para evaluar escenarios de riesgo, determinando la probabilidad de exito inicial y la rentabilidad esperada.

### Fase 4: Analisis Financiero Avanzado
Para los cultivos considerados aptos (estado Apto o Parcial), el sistema proyecta los siguientes indicadores financieros adaptados a la superficie ingresada:
*   **Ingresos y Costo Total:** `Ingresos = Rendimiento_total * Precio_tonelada` | `Costo_total = Costo_por_hectarea * Superficie`.
*   **Utilidad Anual:** `Utilidad = Ingresos - Costos`.
*   **VPN (Valor Presente Neto):** Se calcula a 5 años con una tasa de descuento del 12% (aplicando el factor de anualidad acumulada de `3.6048`).
*   **TIR (Tasa Interna de Retorno):** Se resuelve de manera exacta mediante un algoritmo iterativo de busqueda numerica para determinar la eficiencia marginal del capital.
*   **Viabilidad Presupuestaria:** Compara el costo total estimado de establecimiento contra el presupuesto del productor.

### Fase 5: Recomendaciones y Reporte Tecnico
*   Se despliega una tabla comparativa clasificada por el VPN descendente.
*   Se genera una grafica interactiva de barras (Chart.js) que contrasta el VPN de los cultivos analizados.
*   Se formulan recomendaciones estrategicas automatizadas que sugieren la opcion financiera optima o explican las causas de descarte.
*   Se exporta un reporte formal en PDF formateado mediante ReportLab Platypus.

---

## 2. Herramientas y Tecnologias Utilizadas

La aplicacion esta desarrollada bajo una arquitectura web ligera y modular:

### Backend (Logica de Servidor)
*   **Python 3.10+**: Lenguaje de programacion base.
*   **Flask**: Micro-framework para levantar el servidor y estructurar la API REST del diagnostico y PDF.
*   **MySQL Connector**: Conector nativo de Python para la comunicacion con la base de datos MySQL.
*   **NumPy**: Procesamiento estadistico y numerico avanzado utilizado en simulaciones de riesgo.
*   **ReportLab (Platypus)**: Motor para construir el PDF dinamico estructurado en flujos de datos (`Paragraph`, `Table`, `Spacer`) evitando desbordamientos de texto.

### Frontend (Interfaz de Usuario)
*   **HTML5 y CSS3**: Diseño web en CSS puro sin dependencias externas, implementando estetica premium con tipografia *Outfit* de Google Fonts, glassmorphism (efecto de vidrio esmerilado), degradados y diseño de tarjetas responsivo.
*   **JavaScript (ES6)**: Administracion del DOM, peticiones asincronas (`Fetch API`), formateo de monedas y graficacion.
*   **Chart.js**: Libreria dinamica para renderizar la comparacion de viabilidad financiera (VPN) de los cultivos.

### Base de Datos
*   **MySQL Server**: Base de datos relacional `bd_agricultura_chiapas` con la tabla `cultivo` modificada estructuralmente para soportar limites de nitrogeno maximo (`N_max`), materia organica (`MO_min`, `MO_max`) y limites de altitud geografica (`altitud_min`, `altitud_max`).

---

## 3. Ejemplo Practico de Evaluacion

Para validar el sistema, puedes realizar pruebas con los siguientes dos escenarios:

### Escenario A: Productor Juan Perez en Tapachula (Zona Calida / Baja)
*   **Entradas del Formulario:**
    *   Region: `Tapachula (Altitud: 120m)`
    *   Superficie: `3` hectareas
    *   Presupuesto: `$90,000` MXN
    *   pH del Suelo: `6.2`
    *   Nitrogeno: `35` ppm
    *   Materia Organica: `4.0` %
*   **Salidas del Sistema:**
    *   **Platano:** Apto (Optimo) | Utilidad Anual: $306,000 | VPN: $1,103,069 | TIR: >300% | **Recomendado**
    *   **Cacao:** Apto (Optimo) | Utilidad Anual: $87,000 | VPN: $313,618 | TIR: 111% | **Recomendado**
    *   **Maiz:** Parcial (N bajo, factor 0.6) | Utilidad Anual: $4,950 | VPN: $17,844 | TIR: 10%
    *   **Cafe:** No Apto. Motivo: Exclusión por altitud (120m esta fuera del rango de 600m-1800m).

### Escenario B: Productora Maria Lopez en Simojovel (Zona de Transicion)
*   **Entradas del Formulario:**
    *   Region: `Simojovel (Altitud: 900m)`
    *   Superficie: `2` hectareas
    *   Presupuesto: `$50,000` MXN
    *   pH del Suelo: `5.8`
    *   Nitrogeno: `22` ppm
    *   Materia Organica: `3.2` %
*   **Salidas del Sistema:**
    *   **Platano:** Parcial (N bajo, factor 0.6) | Utilidad Anual: $108,000 | VPN: $389,318 | TIR: 300% | **Recomendado (Mayor VPN)**
    *   **Cafe:** Apto (Optimo) | Utilidad Anual: $71,200 | VPN: $256,662 | TIR: 160% | **Recomendado**
    *   **Maiz:** No Apto. Motivo: Nitrogeno muy bajo (22 ppm es inferior a la tolerancia minima).
    *   **Cacao:** No Apto. Motivo: Exclusión por altitud (900m supera el limite de 800m).

---

## 4. Instalacion y Uso

### Requisitos Previos
*   Python 3.10 o superior
*   MySQL Server (con la base de datos `bd_agricultura_chiapas` cargada en el puerto 3306)

### Pasos para Ejecutar
1.  Asegurate de que las credenciales de tu base de datos MySQL esten configuradas en el metodo `get_db_connection` en [database.py](file:///c:/Users/josue/OneDrive/Escritorio/univerdad%20rosario%20castellano/3%20Semestre/Proyecto%20P%20301/modulos/database.py).
2.  Instala las librerias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Inicia el servidor Flask:
    ```bash
    python app.py
    ```
4.  Abre el navegador en http://localhost:5000 para interactuar con la interfaz del sistema.
