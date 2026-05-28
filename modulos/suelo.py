class Suelo:
    """Clase para manejar las características del terreno y su diagnóstico agronómico."""
    
    def __init__(self, ph, nitrogeno, materia_organica, color='marrón', textura='franco', densidad=1.2):
        self.ph = float(ph)
        self.nitrogeno = float(nitrogeno)
        self.materia_organica = float(materia_organica)
        self.color = color
        self.textura = textura
        self.densidad = densidad

    def evaluar_aptitud_cultivo(self, datos_cultivo, altitud_region):
        """
        Analiza si el suelo y la región son aptos para un cultivo específico.
        Retorna un diccionario con el estado de aptitud y factores de penalización.
        """
        nombre = datos_cultivo['nombre']
        ph_min = datos_cultivo['ph_min']
        ph_max = datos_cultivo['ph_max']
        ph_optimo = datos_cultivo['ph_optimo']
        N_min = datos_cultivo['N_min']
        N_max = datos_cultivo['N_max']
        MO_min = datos_cultivo['MO_min']
        MO_max = datos_cultivo['MO_max']
        alt_min = datos_cultivo['altitud_min']
        alt_max = datos_cultivo['altitud_max']
        rendimiento_base = datos_cultivo['rendimiento_base']

        # 1. Validar Altitud de la región
        if altitud_region < alt_min or altitud_region > alt_max:
            return {
                'apto': False,
                'estado': 'No Apto',
                'detalles': 'altitud fuera de rango para el cultivo',
                'factor_ph': 0.0,
                'factor_n': 0.0,
                'factor_mo': 0.0,
                'rendimiento_real': 0.0
            }

        # 2. Calcular Factor de pH
        # Rango óptimo es el rango general [ph_min, ph_max]
        if ph_min <= self.ph <= ph_max:
            factor_ph = 1.0
        elif (ph_min - 0.3) <= self.ph < ph_min or ph_max < self.ph <= (ph_max + 0.3):
            factor_ph = 0.8
        elif (ph_min - 0.5) <= self.ph < (ph_min - 0.3) or (ph_max + 0.3) < self.ph <= (ph_max + 0.5):
            factor_ph = 0.5
        else:
            factor_ph = 0.0

        # 3. Calcular Factor de Nitrógeno (N)
        if N_min <= self.nitrogeno <= N_max:
            factor_n = 1.0
        elif self.nitrogeno < N_min:
            # Tolerable hasta el 70% del mínimo
            if self.nitrogeno >= N_min * 0.7:
                factor_n = 0.6
            else:
                factor_n = 0.0
        else: # Exceso de Nitrógeno
            # Tolerable hasta el 130% del máximo
            if self.nitrogeno <= N_max * 1.3:
                factor_n = 0.8
            else:
                factor_n = 0.0

        # 4. Calcular Factor de Materia Orgánica (MO)
        if MO_min <= self.materia_organica <= MO_max:
            factor_mo = 1.0
        elif self.materia_organica < MO_min:
            # Tolerable hasta el 95% del mínimo
            if self.materia_organica >= MO_min * 0.95:
                factor_mo = 0.7
            else:
                factor_mo = 0.0
        else:
            # El exceso de Materia Orgánica usualmente no perjudica el rendimiento
            factor_mo = 1.0

        # Calcular Rendimiento Real
        rendimiento_real = rendimiento_base * factor_ph * factor_n * factor_mo

        # Determinar Estado
        if factor_ph == 0.0 or factor_n == 0.0 or factor_mo == 0.0:
            apto = False
            estado = 'No Apto'
            
            # Detalle del motivo principal
            motivos = []
            if factor_ph == 0.0:
                motivos.append("pH fuera de limites")
            if factor_n == 0.0:
                motivos.append("N bajo")
            if factor_mo == 0.0:
                motivos.append("MO baja")
            detalles = ", ".join(motivos)
        elif factor_ph < 1.0 or factor_n < 1.0 or factor_mo < 1.0:
            apto = True
            estado = 'Parcial'
            
            # Advertencias
            motivos = []
            if factor_ph < 1.0:
                motivos.append("pH suboptimo")
            if factor_n < 1.0:
                motivos.append("N bajo")
            if factor_mo < 1.0:
                motivos.append("MO baja")
            detalles = "Parcialmente apto (" + ", ".join(motivos) + ")"
        else:
            apto = True
            estado = 'Apto'
            detalles = 'Suelo en condiciones optimas'

        return {
            'apto': apto,
            'estado': estado,
            'detalles': detalles,
            'factor_ph': factor_ph,
            'factor_n': factor_n,
            'factor_mo': factor_mo,
            'rendimiento_real': round(rendimiento_real, 3)
        }


