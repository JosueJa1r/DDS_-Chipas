import os
import mysql.connector
import dotenv

# Cargar variables de entorno del archivo .env (si existe)
dotenv.load_dotenv()

# Función para gestionar la conexión a MySQL
def get_db_connection():
    """Establece la conexión con la base de datos MySQL de Agricultura Chiapas."""
    try:
        host = os.environ.get("DB_HOST", os.environ.get("host", "localhost"))
        user = os.environ.get("DB_USER", os.environ.get("user", "root"))
        password = os.environ.get("DB_PASSWORD", os.environ.get("password", "Pentathlon1938"))
        database = os.environ.get("DB_NAME", os.environ.get("database", "bd_agricultura_chiapas"))
        port = os.environ.get("DB_PORT", os.environ.get("port", "3306"))
        
        conexion = mysql.connector.connect(
            host=host, 
            user=user,
            password=password,
            database=database, 
            port=port
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

# Función para consultar toda la información técnica de un cultivo
def obtener_datos_cultivo(nombre_cultivo):
    """
    Obtiene los parámetros de un cultivo específico de la base de datos.
    """
    conexion = get_db_connection()
    if not conexion:
        return get_fallback_data(nombre_cultivo)

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT 
                c.Nom_CULTIVO as nombre,
                f.Costo_Cultivo as costo,
                f.Precio_Venta as precio,
                p.ph as ph_optimo,
                c.Rendimiento_Esperado as rendimiento_base,
                s.req_N as N_min,
                s.N_max,
                s.MO_min,
                s.MO_max,
                s.ph_min,
                s.ph_max,
                g.altitud_min,
                g.altitud_max,
                f.volatilidad
            FROM cultivo c
            LEFT JOIN cultivo_finanzas f ON c.Id_cultivo = f.Id_cultivo
            LEFT JOIN cultivo_requisitos_suelo s ON c.Id_cultivo = s.Id_cultivo
            LEFT JOIN cultivo_requisitos_geograficos g ON c.Id_cultivo = g.Id_cultivo
            LEFT JOIN ph_optimo p ON s.Id_ph = p.Id_ph
            WHERE LOWER(c.Nom_CULTIVO) = LOWER(%s)
        """
        cursor.execute(query, (nombre_cultivo,))
        r = cursor.fetchone()
        cursor.close()
        conexion.close()

        if r:
            return {
                'nombre': r['nombre'].capitalize(),
                'costo': float(r['costo'] or 1000),
                'precio': float(r['precio'] or 10),
                'ph_optimo': float(r['ph_optimo'] or 6.5),
                'rendimiento_base': float(r['rendimiento_base'] or 1.0),
                'N_min': float(r['N_min'] or 20),
                'N_max': float(r['N_max'] or 100),
                'MO_min': float(r['MO_min'] or 2.0),
                'MO_max': float(r['MO_max'] or 5.0),
                'ph_min': float(r['ph_min'] or 5.5),
                'ph_max': float(r['ph_max'] or 7.5),
                'altitud_min': float(r['altitud_min'] or 0),
                'altitud_max': float(r['altitud_max'] or 2000),
                'volatilidad': float(r['volatilidad'] or 0.15)
            }
        else:
            return get_fallback_data(nombre_cultivo)

    except mysql.connector.Error as err:
        print(f"Error en la consulta: {err}")
        return get_fallback_data(nombre_cultivo)

# Función para obtener todos los cultivos con sus datos detallados
def obtener_todos_los_datos_cultivos():
    """
    Obtiene todos los cultivos con su información completa para la evaluación integral.
    """
    conexion = get_db_connection()
    if not conexion:
        return [get_fallback_data(name) for name in ['cafe', 'cacao', 'platano', 'maiz']]
    
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT 
                c.Nom_CULTIVO as nombre,
                f.Costo_Cultivo as costo,
                f.Precio_Venta as precio,
                p.ph as ph_optimo,
                c.Rendimiento_Esperado as rendimiento_base,
                s.req_N as N_min,
                s.N_max,
                s.MO_min,
                s.MO_max,
                s.ph_min,
                s.ph_max,
                g.altitud_min,
                g.altitud_max,
                f.volatilidad
            FROM cultivo c
            LEFT JOIN cultivo_finanzas f ON c.Id_cultivo = f.Id_cultivo
            LEFT JOIN cultivo_requisitos_suelo s ON c.Id_cultivo = s.Id_cultivo
            LEFT JOIN cultivo_requisitos_geograficos g ON c.Id_cultivo = g.Id_cultivo
            LEFT JOIN ph_optimo p ON s.Id_ph = p.Id_ph
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        ret = []
        for r in resultados:
            ret.append({
                'nombre': r['nombre'].capitalize(),
                'costo': float(r['costo'] or 1000),
                'precio': float(r['precio'] or 10),
                'ph_optimo': float(r['ph_optimo'] or 6.5),
                'rendimiento_base': float(r['rendimiento_base'] or 1.0),
                'N_min': float(r['N_min'] or 20),
                'N_max': float(r['N_max'] or 100),
                'MO_min': float(r['MO_min'] or 2.0),
                'MO_max': float(r['MO_max'] or 5.0),
                'ph_min': float(r['ph_min'] or 5.5),
                'ph_max': float(r['ph_max'] or 7.5),
                'altitud_min': float(r['altitud_min'] or 0),
                'altitud_max': float(r['altitud_max'] or 2000),
                'volatilidad': float(r['volatilidad'] or 0.15)
            })
        return ret
    except mysql.connector.Error as err:
        print(f"Error al obtener todos los cultivos: {err}")
        return [get_fallback_data(name) for name in ['cafe', 'cacao', 'platano', 'maiz']]

# Función para obtener la lista de nombres para el menú desplegable
def obtener_todos_los_cultivos():
    """Obtiene la lista de todos los nombres de cultivos disponibles en la base de datos."""
    conexion = get_db_connection()
    if not conexion:
        return ['Café', 'Cacao', 'Plátano', 'Maíz']
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT Nom_CULTIVO FROM cultivo ORDER BY Nom_CULTIVO ASC")
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return [r[0].capitalize() for r in resultados]
    except mysql.connector.Error as err:
        print(f"Error al obtener cultivos: {err}")
        return ['Café', 'Cacao', 'Plátano', 'Maíz']

# Datos de seguridad (Fallback) por si la base de datos no está disponible
def get_fallback_data(nombre_cultivo):
    """Proporciona datos de respaldo en caso de fallo en la BD o registro inexistente."""
    fallbacks = {
        'cafe': {
            'nombre': 'Café', 'costo': 22000.0, 'precio': 32000.0, 'ph_optimo': 6.0, 'rendimiento_base': 1.8,
            'N_min': 20.0, 'N_max': 40.0, 'MO_min': 2.5, 'MO_max': 4.5, 'ph_min': 5.5, 'ph_max': 6.5,
            'altitud_min': 600.0, 'altitud_max': 1800.0, 'volatilidad': 0.20
        },
        'cacao': {
            'nombre': 'Cacao', 'costo': 25000.0, 'precio': 45000.0, 'ph_optimo': 6.5, 'rendimiento_base': 1.2,
            'N_min': 25.0, 'N_max': 50.0, 'MO_min': 3.0, 'MO_max': 5.0, 'ph_min': 6.0, 'ph_max': 7.0,
            'altitud_min': 0.0, 'altitud_max': 800.0, 'volatilidad': 0.18
        },
        'platano': {
            'nombre': 'Plátano', 'costo': 18000.0, 'precio': 8000.0, 'ph_optimo': 6.2, 'rendimiento_base': 15.0,
            'N_min': 30.0, 'N_max': 60.0, 'MO_min': 2.0, 'MO_max': 4.0, 'ph_min': 5.5, 'ph_max': 7.0,
            'altitud_min': 0.0, 'altitud_max': 1000.0, 'volatilidad': 0.15
        },
        'maiz': {
            'nombre': 'Maíz', 'costo': 12000.0, 'precio': 6500.0, 'ph_optimo': 6.5, 'rendimiento_base': 3.5,
            'N_min': 40.0, 'N_max': 80.0, 'MO_min': 2.0, 'MO_max': 3.5, 'ph_min': 5.8, 'ph_max': 7.2,
            'altitud_min': 0.0, 'altitud_max': 2500.0, 'volatilidad': 0.12
        }
    }
    nombre_lower = nombre_cultivo.lower()
    
    key = 'maiz'
    if 'cafe' in nombre_lower or 'caf' in nombre_lower:
        key = 'cafe'
    elif 'cacao' in nombre_lower:
        key = 'cacao'
    elif 'platano' in nombre_lower or 'plá' in nombre_lower:
        key = 'platano'
    return fallbacks.get(key, fallbacks['maiz'])

# Función para obtener la altitud de una región desde la base de datos
def obtener_altitud_region_db(region_name):
    """
    Consulta la altitud de una región en la base de datos.
    Si la base de datos no está disponible o no se encuentra la región,
    retorna un valor por defecto basado en un diccionario fallback.
    """
    conexion = get_db_connection()
    fallbacks = {
        'simojovel': 900.0,
        'tapachula': 120.0,
        'san cristobal': 2200.0,
        'cristobal': 2200.0,
        'palenque': 60.0,
        'comitan': 1600.0,
        'tuxtla': 530.0
    }
    
    # Procesar nombre para comparación
    r_lower = region_name.lower()
    
    if not conexion:
        # Fallback local
        for key, val in fallbacks.items():
            if key in r_lower:
                return val
        return 500.0  # Altitud por defecto si no coincide nada
        
    try:
        cursor = conexion.cursor()
        # Buscaremos una coincidencia parcial (LIKE) para que sea flexible
        query = "SELECT Altitud FROM region WHERE LOWER(Nom_Region) LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{r_lower}%",))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if resultado:
            return float(resultado[0])
            
        # Si no se encuentra en la base de datos, usamos el fallback
        for key, val in fallbacks.items():
            if key in r_lower:
                return val
        return 500.0
    except mysql.connector.Error as err:
        print(f"Error al obtener altitud de la región {region_name}: {err}")
        for key, val in fallbacks.items():
            if key in r_lower:
                return val
        return 500.0

def obtener_todas_las_regiones():
    """Obtiene la lista de todas las regiones y sus altitudes registradas en la base de datos."""
    conexion = get_db_connection()
    if not conexion:
        return [
            {'nombre': 'Simojovel', 'altitud': 900.0},
            {'nombre': 'Tapachula', 'altitud': 120.0},
            {'nombre': 'San Cristobal de las Casas', 'altitud': 2200.0},
            {'nombre': 'Palenque', 'altitud': 60.0},
            {'nombre': 'Comitan', 'altitud': 1600.0},
            {'nombre': 'Tuxtla Gutierrez', 'altitud': 530.0}
        ]
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Nom_Region as nombre, Altitud as altitud FROM region ORDER BY Nom_Region ASC")
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return [{'nombre': r['nombre'], 'altitud': float(r['altitud'])} for r in resultados]
    except mysql.connector.Error as err:
        print(f"Error al obtener regiones: {err}")
        return [
            {'nombre': 'Simojovel', 'altitud': 900.0},
            {'nombre': 'Tapachula', 'altitud': 120.0},
            {'nombre': 'San Cristobal de las Casas', 'altitud': 2200.0},
            {'nombre': 'Palenque', 'altitud': 60.0},
            {'nombre': 'Comitan', 'altitud': 1600.0},
            {'nombre': 'Tuxtla Gutierrez', 'altitud': 530.0}
        ]

def obtener_plagas_por_cultivo_y_region(nombre_cultivo, nombre_region):
    """
    Retorna las plagas asociadas a un cultivo en Chiapas.
    Separa las plagas con incidencia directa en la región seleccionada
    de las plagas generales registradas para el cultivo en otros municipios del estado.
    """
    conexion = get_db_connection()
    if not conexion:
        return {'regionales': [], 'generales': []}
        
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # 1. Obtener ID de cultivo
        cursor.execute("SELECT Id_cultivo FROM cultivo WHERE LOWER(Nom_CULTIVO) = LOWER(%s)", (nombre_cultivo,))
        cultivo_row = cursor.fetchone()
        if not cultivo_row:
            return {'regionales': [], 'generales': []}
        id_cultivo = cultivo_row['Id_cultivo']
        
        # 2. Obtener ID de región
        cursor.execute("SELECT Id_region FROM region WHERE LOWER(Nom_Region) = LOWER(%s)", (nombre_region,))
        region_row = cursor.fetchone()
        id_region = region_row['Id_region'] if region_row else None
        
        # 3. Query plagas específicas de la región
        regionales = []
        if id_region:
            query_reg = """
                SELECT DISTINCT
                    p.Nom_Plaga as nombre,
                    p.Nombre_Cientifico as cientifico,
                    p.Tipo_Organismo as tipo,
                    p.Descripcion_Dano as dano,
                    i.Nivel_Riesgo as riesgo,
                    i.Municipio_Original as municipio
                FROM plaga_incidencia i
                JOIN plaga p ON i.Id_plaga = p.Id_plaga
                WHERE i.Id_cultivo = %s AND i.Id_region = %s
                ORDER BY 
                    CASE i.Nivel_Riesgo 
                        WHEN 'Muy Alta' THEN 1 
                        WHEN 'Alta' THEN 2 
                        WHEN 'Media' THEN 3 
                        WHEN 'Bajo' THEN 4 
                        ELSE 5 
                    END ASC
            """
            cursor.execute(query_reg, (id_cultivo, id_region))
            regionales = cursor.fetchall()
            
        # 4. Query plagas generales (otros municipios de Chiapas)
        query_gen = """
            SELECT DISTINCT
                p.Nom_Plaga as nombre,
                p.Nombre_Cientifico as cientifico,
                p.Tipo_Organismo as tipo,
                p.Descripcion_Dano as dano,
                i.Nivel_Riesgo as riesgo,
                i.Municipio_Original as municipio
            FROM plaga_incidencia i
            JOIN plaga p ON i.Id_plaga = p.Id_plaga
            WHERE i.Id_cultivo = %s AND (i.Id_region != %s OR i.Id_region IS NULL)
        """
        
        # Si no hay id_region, consultamos todas
        if not id_region:
            query_gen = """
                SELECT DISTINCT
                    p.Nom_Plaga as nombre,
                    p.Nombre_Cientifico as cientifico,
                    p.Tipo_Organismo as tipo,
                    p.Descripcion_Dano as dano,
                    i.Nivel_Riesgo as riesgo,
                    i.Municipio_Original as municipio
                FROM plaga_incidencia i
                JOIN plaga p ON i.Id_plaga = p.Id_plaga
                WHERE i.Id_cultivo = %s
            """
            cursor.execute(query_gen, (id_cultivo,))
        else:
            cursor.execute(query_gen, (id_cultivo, id_region))
            
        generales_all = cursor.fetchall()
        
        # Filtrar plagas que ya están en regionales
        reg_names = {r['nombre'] for r in regionales}
        generales = [g for g in generales_all if g['nombre'] not in reg_names]
        
        cursor.close()
        conexion.close()
        return {
            'regionales': regionales,
            'generales': generales
        }
    except mysql.connector.Error as err:
        print(f"Error al obtener plagas: {err}")
        return {'regionales': [], 'generales': []}
