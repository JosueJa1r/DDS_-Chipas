# Análisis de Costos y Escalabilidad: Semilla Inteligente (DSS)

Este informe detalla los costos asociados con la infraestructura del proyecto y evalúa la capacidad del sistema para escalar a medida que aumente el volumen de usuarios y datos.

---

## 1. Análisis de Costos (Infraestructura)

El proyecto está diseñado bajo una arquitectura web ligera y moderna, combinando un backend **Serverless** (Vercel) y una **base de datos relacional en la nube** (Aiven MySQL).

### Tabla de Costos de Infraestructura

| Servicio / Componente | Proveedor | Nivel Gratuito (Hobby/Dev) | Nivel Producción / Comercial | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Backend & Frontend Hosting** | Vercel | **$0 USD / mes**<br>- 100 GB ancho de banda.<br>- 100k ejecuciones/día. | **$20 USD / mes** (Pro)<br>- 1 TB ancho de banda.<br>- Concurrencia dedicada. | Aloja la interfaz HTML/CSS/JS y las funciones serverless de Python (API y reportes PDF). |
| **Base de Datos MySQL** | Aiven | **$0 USD / mes**<br>- Nivel gratuito básico (suficiente para pruebas). | **$15 a $30 USD / mes**<br>- Base de datos dedicada.<br>- Copias de seguridad diarias. | Almacena requerimientos de cultivos, plagas, altitudes y regiones. |
| **Motor de PDF (ReportLab)** | Integrado | **$0 USD / mes**<br>- Procesamiento en memoria. | **$0 USD / mes** | El PDF y los gráficos de `matplotlib` se procesan en el backend en milisegundos sin servicios externos. |
| **Gráficos en UI (Chart.js)** | Integrado | **$0 USD / mes**<br>- Renderizado en cliente. | **$0 USD / mes** | Los gráficos se dibujan en el navegador del usuario utilizando JavaScript, ahorrando CPU al servidor. |
| **Total Estimado** | | **$0 USD / mes** (Fase inicial/Piloto) | **$35 a $50 USD / mes** (Uso comercial continuo) | **Esquema de costos sumamente económico.** |

---

## 2. Análisis de Escalabilidad

### A. Escalabilidad del Servidor (Backend Serverless)
Al estar desplegado en **Vercel Serverless Functions**:
*   **Concurrencia Automática**: No tienes un servidor encendido 24/7 que pueda saturarse. Cada petición web activa una pequeña instancia independiente en milisegundos. Si entran 1,000 productores a la vez, Vercel levantará 1,000 microservicios de manera automática y los apagará después.
*   **Aislamiento de Carga de CPU**: La renderización de PDF y los cálculos estocásticos (Monte Carlo) consumen CPU. Al ejecutarse en serverless, la carga se distribuye en la infraestructura de Vercel, evitando que un usuario alenté la página de los demás.

### B. Escalabilidad de la Base de Datos (Lecturas y Escrituras)
*   **Arquitectura Orientada a Lecturas**: El sistema realiza consultas de lectura de datos estáticos (cultivos, plagas, regiones) en el momento del diagnóstico. No escribe información constantemente. Esto hace que una base de datos MySQL básica de 1 GB de RAM pueda soportar miles de consultas de lectura por hora sin pestañear.
*   **Optimización**: Si el volumen de usuarios crece a decenas de miles por día, se puede implementar un caché en memoria simple (como Redis o el caché de Flask) para evitar consultar a MySQL en cada diagnóstico, ya que la información agronómica de los cultivos cambia muy rara vez.

### C. Escalabilidad Funcional (Fácil Expansión de Datos)
El diseño del DSS está **orientado a datos** (data-driven):
*   **Añadir Nuevos Cultivos**: No requiere modificar ni una sola línea de código Python o JavaScript. Solo debes insertar un registro en la tabla `cultivo` y sus correspondientes parámetros en las tablas de `cultivo_requisitos_suelo`, `cultivo_requisitos_geograficos` y `cultivo_finanzas`. El sistema listará y evaluará automáticamente el nuevo cultivo.
*   **Añadir Nuevas Regiones**: Se escala de la misma forma insertando una nueva fila en la tabla `region` (con su altitud). La interfaz la mostrará de inmediato en el menú desplegable.
*   **Soporte Multi-macronutrientes**: La base de datos ya está estructurada para soportar Fósforo (P) y Potasio (K) (`req_P`, `req_K` en `cultivo_requisitos_suelo`). Ampliar el análisis químico de suelo del formulario para evaluarlos solo requiere activarlos en la lógica de evaluación agronómica.
