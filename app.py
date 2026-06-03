from flask import Flask, render_template, request, jsonify, send_file
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from modulos.suelo import Suelo
from modulos.Contabilidad import calcular_vpn, calcular_tir
from modulos.Probabilidad import generar_curva_gauss, simulacion_monte_carlo_rendimiento, generar_datos_correlacion
from modulos.Database import (
    obtener_todos_los_datos_cultivos, obtener_todos_los_cultivos, obtener_altitud_region_db,
    obtener_todas_las_regiones, obtener_plagas_por_cultivo_y_region, get_fallback_data
)

# Configuración inicial de la aplicación Flask
app = Flask(__name__)

def obtener_altitud_region(region_name):
    return obtener_altitud_region_db(region_name)

# Ruta principal: Carga la interfaz de usuario (Dashboard)
@app.route('/')
def index():
    return render_template('index.html')

# API: Retorna la lista de cultivos disponibles para llenar el select del formulario (legacy support)
@app.route('/api/cultivos', methods=['GET'])
def get_cultivos():
    cultivos = obtener_todos_los_cultivos()
    return jsonify(cultivos)

# API: Retorna la lista de regiones disponibles para llenar el select del formulario
@app.route('/api/regiones', methods=['GET'])
def get_regiones():
    regiones = obtener_todas_las_regiones()
    return jsonify(regiones)

# API: Procesa el diagnóstico completo (Fases 1 a 5)
@app.route('/api/diagnostico_completo', methods=['POST'])
def diagnostico_completo():
    data = request.json
    
    # Fase 1: Recolección de datos del productor y suelo
    productor_data = data.get('productor', {})
    suelo_data = data.get('suelo', {})
    superficie = float(data.get('superficie', 1.0))
    
    nombre = productor_data.get('nombre', 'Productor')
    region = productor_data.get('region', 'Simojovel')
    presupuesto = float(productor_data.get('presupuesto', 0.0))
    experiencia = productor_data.get('experiencia', 'Sin experiencia')
    
    ph = float(suelo_data.get('ph', 6.0))
    nitrogeno = float(suelo_data.get('nitrogeno', 20.0))
    materia_organica = float(suelo_data.get('materia_organica', 3.0))
    
    # Creamos el objeto Suelo con los valores del análisis químico
    suelo = Suelo(ph=ph, nitrogeno=nitrogeno, materia_organica=materia_organica)
    
    # Consultamos todos los cultivos registrados en la base de datos
    cultivos_datos = obtener_todos_los_datos_cultivos()
    altitud = obtener_altitud_region(region)
    
    resultados = []
    
    # Fases 2, 3 y 4: Diagnóstico y evaluación financiera para cada cultivo
    for crop in cultivos_datos:
        eval_res = suelo.evaluar_aptitud_cultivo(crop, altitud)
        
        # Rendimiento y producción total
        rendimiento_total = eval_res['rendimiento_real'] * superficie
        # Ingresos totales estimados
        ingreso = rendimiento_total * crop['precio']
        # Costos de inversión por hectárea * superficie
        costo_total = crop['costo'] * superficie
        # Utilidad neta anual
        utilidad_anual = ingreso - costo_total
        
        # Evaluación financiera
        vpn = calcular_vpn(utilidad_anual, costo_total)
        tir = calcular_tir(costo_total, utilidad_anual)
        
        if eval_res['apto']:
            # Determinar viabilidad presupuestaria
            if costo_total <= presupuesto:
                if vpn > 0:
                    recomendar = 'SI'
                else:
                    recomendar = 'NO (VPN negativo)'
            else:
                recomendar = 'NO (Excede presupuesto)'
                
            apto_texto = 'Si' if eval_res['estado'] == 'Apto' else 'Parcial'
        else:
            apto_texto = 'No'
            recomendar = 'NO'
            
        resultados.append({
            'cultivo': crop['nombre'],
            'apto': apto_texto,
            'detalles': eval_res['detalles'],
            'rendimiento_total': round(rendimiento_total, 2),
            'ingreso': round(ingreso, 2),
            'costo': round(costo_total, 2),
            'utilidad_anual': round(utilidad_anual, 2),
            'vpn': round(vpn, 2),
            'tir': round(tir, 4),
            'recomendar': recomendar
        })
        
    # Ordenar resultados: recomendados 'SI' primero y por VPN descendente
    resultados.sort(key=lambda x: (x['recomendar'] != 'SI', -x['vpn']))
    
    # Fase 5: Estructuración de Recomendaciones finales (sin emojis)
    recomendaciones = []
    recomendados_validos = [r for r in resultados if r['recomendar'] == 'SI']
    
    if recomendados_validos:
        mejor_opcion = recomendados_validos[0]
        recomendaciones.append(
            f"Se recomienda cultivar {mejor_opcion['cultivo']} debido a que presenta la mayor viabilidad financiera, "
            f"con un VPN estimado de ${mejor_opcion['vpn']:,.2f} a 5 anos y una TIR de {mejor_opcion['tir']*100:.1f}%."
        )
        
        # Alertas de plagas para el cultivo principal
        plagas_principal = obtener_plagas_por_cultivo_y_region(mejor_opcion['cultivo'], region)
        reg_p = plagas_principal.get('regionales', [])
        gen_p = plagas_principal.get('generales', [])
        if reg_p:
            alertas = [f"{p['nombre']} (Riesgo: {p['riesgo']})" for p in reg_p]
            recomendaciones.append(
                f"Alerta sanitaria para {mejor_opcion['cultivo']} en {region}: Se detecta presencia de {', '.join(alertas)}. "
                f"Se aconseja implementar medidas preventivas."
            )
        elif gen_p:
            alertas_gen = [p['nombre'] for p in gen_p[:2]]
            recomendaciones.append(
                f"Monitoreo para {mejor_opcion['cultivo']}: Aunque sin alertas locales en {region}, "
                f"en Chiapas hay registro historico de {', '.join(alertas_gen)}."
            )
            
        if len(recomendados_validos) > 1:
            segunda_opcion = recomendados_validos[1]
            recomendaciones.append(
                f"Como alternativa secundaria de diversificacion, puede considerar el cultivo de {segunda_opcion['cultivo']}, "
                f"con una utilidad anual proyectada de ${segunda_opcion['utilidad_anual']:,.2f}."
            )
            
            # Alertas de plagas para el cultivo secundario
            plagas_secundario = obtener_plagas_por_cultivo_y_region(segunda_opcion['cultivo'], region)
            reg_s = plagas_secundario.get('regionales', [])
            if reg_s:
                alertas_s = [f"{p['nombre']} (Riesgo: {p['riesgo']})" for p in reg_s]
                recomendaciones.append(
                    f"Alerta de riesgo para {segunda_opcion['cultivo']} en {region}: Incidencia local de {', '.join(alertas_s)}."
                )
    else:
        recomendaciones.append(
            "Ninguno de los cultivos analizados es apto o viable con las condiciones de suelo y presupuesto ingresadas. "
            "Se sugiere realizar enmiendas quimicas para corregir el pH o fertilizar el suelo para alcanzar los niveles minimos requeridos."
        )
        
    # Validar exclusión por altitud (ejemplo Cacao o Vainilla en San Cristóbal)
    for r in resultados:
        if 'altitud' in r['detalles'] and r['apto'] == 'No':
            recomendaciones.append(
                f"El cultivo de {r['cultivo']} esta totalmente descartado debido a que la altitud de la region ({altitud:.0f}m) "
                f"esta fuera del rango optimo para su desarrollo biogeografico."
            )
            
    # Determinar cultivo para el análisis avanzado
    cultivo_analisis = "Maiz"
    if recomendados_validos:
        cultivo_analisis = recomendados_validos[0]['cultivo']
    elif resultados:
        aptos = [r for r in resultados if r['apto'] in ('Si', 'Parcial')]
        if aptos:
            cultivo_analisis = aptos[0]['cultivo']
        else:
            cultivo_analisis = resultados[0]['cultivo']
            
    crop_data = next((c for c in cultivos_datos if c['nombre'].lower() == cultivo_analisis.lower()), None)
    if not crop_data:
        crop_data = get_fallback_data(cultivo_analisis)
        
    plagas_data = obtener_plagas_por_cultivo_y_region(cultivo_analisis, region)
    reg_p = plagas_data.get('regionales', [])
    
    risk_mapping = {'Bajo': 1.0, 'Media': 2.0, 'Alta': 3.0, 'Muy Alta': 4.0}
    if reg_p:
        pest_scores = [risk_mapping.get(p.get('riesgo', 'Media'), 2.0) for p in reg_p]
        pest_risk_score = sum(pest_scores) / len(pest_scores)
    else:
        gen_p = plagas_data.get('generales', [])
        if gen_p:
            pest_scores = [risk_mapping.get(p.get('riesgo', 'Media'), 1.5) for p in gen_p]
            pest_risk_score = sum(pest_scores) / len(pest_scores)
        else:
            pest_risk_score = 1.5
            
    res_crop = next((r for r in resultados if r['cultivo'].lower() == cultivo_analisis.lower()), None)
    rendimiento_real = res_crop['rendimiento_total'] / superficie if (res_crop and superficie > 0) else crop_data['rendimiento_base']
    
    ph_dist_data = generar_curva_gauss(ph_optimo=crop_data['ph_optimo'])
    correlacion_data = generar_datos_correlacion(
        ph_optimo=crop_data['ph_optimo'],
        ph_suelo=ph,
        N_min=crop_data['N_min'],
        nitrogeno_suelo=nitrogeno,
        pest_risk_score=pest_risk_score
    )
    montecarlo_data = simulacion_monte_carlo_rendimiento(
        rendimiento_real=rendimiento_real,
        costo_total_ha=crop_data['costo'],
        precio_venta_ton=crop_data['precio'],
        volatilidad=crop_data['volatilidad']
    )
    
    analisis_avanzado = {
        'cultivo': cultivo_analisis,
        'ph_optimo': crop_data['ph_optimo'],
        'ph_min': crop_data['ph_min'],
        'ph_max': crop_data['ph_max'],
        'N_min': crop_data['N_min'],
        'pest_risk_score': pest_risk_score,
        'gauss_ph': ph_dist_data,
        'correlacion': correlacion_data,
        'montecarlo': {
            'rendimiento_real': montecarlo_data['rendimiento_real'],
            'rendimiento_equilibrio': montecarlo_data['rendimiento_equilibrio'],
            'probabilidad_exito': montecarlo_data['probabilidad_exito'],
            'histograma': montecarlo_data['histograma']
        }
    }

    # Empaquetamos todo el resultado
    resultado_completo = {
        'productor': {
            'nombre': nombre,
            'region': region,
            'presupuesto': presupuesto,
            'superficie': superficie,
            'experiencia': experiencia,
            'altitud': altitud
        },
        'suelo': {
            'ph': ph,
            'nitrogeno': nitrogeno,
            'materia_organica': materia_organica
        },
        'resultados': resultados,
        'recomendaciones': recomendaciones,
        'analisis_avanzado': analisis_avanzado
    }
    
    return jsonify(resultado_completo)

# API: Generación de reporte técnico en formato PDF
@app.route('/api/generar_pdf', methods=['POST'])
def generar_pdf():
    data = request.json
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos de texto personalizados sin emojis
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor('#1b5e20'),
        alignment=1,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#2e7d32'),
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.white,
        alignment=1
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        alignment=1
    )

    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=1
    )
    
    story = []
    
    # 1. TÍTULO PRINCIPAL
    story.append(Paragraph("ANALISIS TECNICO-ECONOMICO PARA LA DIVERSIFICACION DE CULTIVOS EN MEXICO", title_style))
    story.append(Paragraph("Sistema de Apoyo a Decisiones Agricolas (DSS) - Reporte Tecnico de Resultados", body_style))
    story.append(Spacer(1, 10))
    
    # 2. INTRODUCCIÓN TEÓRICA
    intro_txt = (
        "La seguridad alimentaria, la sostenibilidad agricola y la competitividad economica representan retos prioritarios, "
        "asi que resulta fundamental evaluar nuevas estrategias productivas que permitan a las y los pequeños y medianos "
        "productores incrementar su rentabilidad y responder a las demandas del mercado regional y nacional en un contexto "
        "cada vez mas globalizado. La diversificacion agricola hacia cultivos de mayor valor comercial constituye una alternativa "
        "relevante para fortalecer la economia local, especialmente en espacios periurbanos donde la presion sobre el suelo y "
        "los recursos limita la produccion tradicional. En este sentido, la aplicacion de herramientas analiticas propias de la "
        "ciencia de datos permite estructurar, interpretar y optimizar informacion economica, productiva y comercial, facilitando "
        "la toma de decisiones estrategicas fundamentadas en datos."
    )
    story.append(Paragraph(intro_txt, body_style))
    story.append(Spacer(1, 10))
    
    # 3. INFORMACIÓN DEL PRODUCTOR Y SUELO
    story.append(Paragraph("Fase 1: Datos de Entrada del Diagnostico", h2_style))
    
    prod = data.get('productor', {})
    suelo = data.get('suelo', {})
    
    info_datos = [
        [
            Paragraph(f"<b>Productor:</b> {prod.get('nombre')}", body_style),
            Paragraph(f"<b>pH del Suelo:</b> {suelo.get('ph')}", body_style)
        ],
        [
            Paragraph(f"<b>Region:</b> {prod.get('region')} (Altitud: {prod.get('altitud', 0):.0f}m)", body_style),
            Paragraph(f"<b>Nitrogeno:</b> {suelo.get('nitrogeno')} ppm", body_style)
        ],
        [
            Paragraph(f"<b>Superficie:</b> {prod.get('superficie')} ha", body_style),
            Paragraph(f"<b>Materia Organica:</b> {suelo.get('materia_organica')}%", body_style)
        ],
        [
            Paragraph(f"<b>Presupuesto:</b> ${prod.get('presupuesto'):,.2f} MXN", body_style),
            Paragraph(f"<b>Experiencia:</b> {prod.get('experiencia')}", body_style)
        ]
    ]
    
    t_info = Table(info_datos, colWidths=[260, 260])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))
    
    # 4. EXPLICACIÓN CLAVE DE LA CONEXIÓN
    story.append(Paragraph("Fase 2 y 3: La Conexion entre el Suelo y la Rentabilidad", h2_style))
    conexion_txt = (
        "El problema principal consiste en comprender y explicar como un sistema utiliza el analisis quimico del suelo "
        "para estimar variables financieras de largo plazo como el Valor Presente Neto (VPN) y la Tasa Interna de Retorno (TIR). "
        "Nuestro sistema toma los datos de entrada del productor y el analisis del suelo, y mediante reglas tecnicas basadas "
        "en los requerimientos de cada cultivo, evalua la aptitud. Si el suelo cumple con los requisitos, se calcula un factor "
        "de penalizacion y el rendimiento esperado (toneladas por hectarea). Este rendimiento real se multiplica por el precio "
        "de mercado para proyectar los ingresos brutos, de los cuales se restan los costos operativos para estimar los flujos de "
        "caja netos, calculando finalmente el VPN a 5 años (con tasa de descuento del 12%) y la TIR."
    )
    story.append(Paragraph(conexion_txt, body_style))
    story.append(Spacer(1, 10))
    
    # 5. TABLA DE RESULTADOS COMPARATIVOS
    story.append(Paragraph("Fase 4: Analisis Comparativo de Diversificacion de Cultivos", h2_style))
    
    # Headers
    headers = [
        Paragraph("Cultivo", table_header_style),
        Paragraph("Apto", table_header_style),
        Paragraph("Rend. Total", table_header_style),
        Paragraph("Ingreso", table_header_style),
        Paragraph("Costo", table_header_style),
        Paragraph("Utilidad", table_header_style),
        Paragraph("VPN (5a)", table_header_style),
        Paragraph("TIR", table_header_style),
        Paragraph("Recomendar", table_header_style)
    ]
    
    table_data = [headers]
    
    for r in data.get('resultados', []):
        fmt_curr = lambda v: f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"
        row = [
            Paragraph(f"<b>{r['cultivo']}</b>", table_cell_style),
            Paragraph(r['apto'], table_cell_style),
            Paragraph(f"{r['rendimiento_total']:.1f} ton", table_cell_style),
            Paragraph(fmt_curr(r['ingreso']), table_cell_style),
            Paragraph(fmt_curr(r['costo']), table_cell_style),
            Paragraph(fmt_curr(r['utilidad_anual']), table_cell_style),
            Paragraph(fmt_curr(r['vpn']), table_cell_style),
            Paragraph(f"{r['tir']*100:.0f}%", table_cell_style),
            Paragraph(r['recomendar'], table_cell_bold_style)
        ]
        table_data.append(row)
        
    t_results = Table(table_data, colWidths=[65, 45, 60, 60, 60, 60, 65, 45, 60])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e7d32')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(t_results)
    story.append(Spacer(1, 10))
    
    # --- Gráficos Estadísticos Avanzados en el PDF ---
    analisis_avanzado = data.get('analisis_avanzado', {})
    if analisis_avanzado:
        try:
            ph_optimo = analisis_avanzado.get('ph_optimo', 6.5)
            ph_min = analisis_avanzado.get('ph_min', 5.5)
            ph_max = analisis_avanzado.get('ph_max', 7.5)
            cultivo_analisis = analisis_avanzado.get('cultivo', 'Cultivo')
            parcelas = analisis_avanzado.get('correlacion', {}).get('parcelas', [])
            montecarlo_hist = analisis_avanzado.get('montecarlo', {}).get('histograma', [])
            rendimiento_equilibrio = analisis_avanzado.get('montecarlo', {}).get('rendimiento_equilibrio', 0.0)
            probabilidad_exito = analisis_avanzado.get('montecarlo', {}).get('probabilidad_exito', 0.0)
            
            # 1. Gráfico de Gauss para pH
            fig_gauss, ax_g = plt.subplots(figsize=(4, 2.2))
            x_g = np.linspace(3.5, 8.5, 100)
            y_g = (1.0 / (0.5 * np.sqrt(2 * np.pi))) * np.exp(-((x_g - ph_optimo) ** 2) / (2 * (0.5 ** 2)))
            ax_g.plot(x_g, y_g, color='#1b5e20', lw=2)
            
            # Colorear zonas
            ax_g.fill_between(x_g, 0, y_g, where=(x_g < 5.0), color='#ef9a9a', alpha=0.5)
            ax_g.fill_between(x_g, 0, y_g, where=((x_g >= 5.0) & (x_g <= 7.0)), color='#c8e6c9', alpha=0.5)
            ax_g.fill_between(x_g, 0, y_g, where=(x_g > 7.0), color='#ef9a9a', alpha=0.5)
            
            # Línea de pH actual
            ph_actual = float(data.get('suelo', {}).get('ph', 6.0))
            ax_g.axvline(ph_actual, color='red', linestyle='--', linewidth=1.5)
            
            ax_g.set_title(f'Salud del Suelo: pH ({cultivo_analisis})', fontsize=8, fontweight='bold', color='#1b5e20')
            ax_g.set_xlabel('pH', fontsize=7)
            ax_g.set_ylabel('Probabilidad', fontsize=7)
            ax_g.tick_params(labelsize=6)
            plt.tight_layout()
            
            buf_gauss = io.BytesIO()
            plt.savefig(buf_gauss, format='png', dpi=150)
            buf_gauss.seek(0)
            plt.close(fig_gauss)
            
            # 2. Gráfico de Matriz de Dispersión / Correlación (3x3: pH, Nitrogeno, Merma)
            ph_vals = [p['ph'] for p in parcelas]
            n_vals = [p['nitrogeno'] for p in parcelas]
            m_vals = [p['merma'] for p in parcelas]
            
            vars_data = [ph_vals, n_vals, m_vals]
            vars_names = ['pH', 'Nutrientes (N)', 'Merma (%)']
            
            fig_mat, axes = plt.subplots(3, 3, figsize=(4, 4))
            for i in range(3):
                for j in range(3):
                    ax_m = axes[i, j]
                    if i == j:
                        ax_m.hist(vars_data[i], bins=8, color='#2e7d32', alpha=0.7)
                        ax_m.annotate(vars_names[i], (0.5, 0.5), xycoords='axes fraction', 
                                     ha='center', va='center', fontweight='bold', fontsize=7, color='#000000')
                    else:
                        ax_m.scatter(vars_data[j], vars_data[i], s=2.5, color='#1565c0', alpha=0.6)
                    
                    ax_m.tick_params(labelsize=5)
                    if i < 2:
                        ax_m.set_xticklabels([])
                    if j > 0:
                        ax_m.set_yticklabels([])
            
            plt.suptitle('Matriz de Dispersión y Relaciones', fontsize=8, fontweight='bold', color='#2e7d32')
            plt.tight_layout()
            
            buf_mat = io.BytesIO()
            plt.savefig(buf_mat, format='png', dpi=150)
            buf_mat.seek(0)
            plt.close(fig_mat)
            
            # 3. Gráfico de Histograma Monte Carlo
            fig_mc, ax_mc = plt.subplots(figsize=(6, 2.5))
            bins_centers = [b['bin_center'] for b in montecarlo_hist]
            frequencies = [b['frecuencia'] for b in montecarlo_hist]
            
            if bins_centers:
                width = (bins_centers[1] - bins_centers[0]) * 0.9 if len(bins_centers) > 1 else 0.5
                ax_mc.bar(bins_centers, frequencies, width=width, color='#1565c0', edgecolor='white', alpha=0.85)
                
                # Línea de equilibrio
                ax_mc.axvline(rendimiento_equilibrio, color='red', linestyle='-', linewidth=1.5)
                ax_mc.text(rendimiento_equilibrio * 1.02, max(frequencies) * 0.7, 'Punto de Equilibrio', 
                           color='red', fontsize=7, fontweight='bold')
                
                # Texto de porcentaje
                ax_mc.text(0.95, 0.1, f'{probabilidad_exito}% escenarios > Equilibrio', 
                           transform=ax_mc.transAxes, ha='right', va='bottom',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#cccccc'),
                           fontsize=7, fontweight='bold', color='#1b5e20')
            
            ax_mc.set_title(f'Simulación Monte Carlo: Rendimiento de {cultivo_analisis}', fontsize=8, fontweight='bold', color='#1565c0')
            ax_mc.set_xlabel('Rendimiento (Ton/Ha)', fontsize=7)
            ax_mc.set_ylabel('Frecuencia', fontsize=7)
            ax_mc.tick_params(labelsize=6)
            plt.tight_layout()
            
            buf_mc = io.BytesIO()
            plt.savefig(buf_mc, format='png', dpi=150)
            buf_mc.seek(0)
            plt.close(fig_mc)
            
            # Construir imágenes de ReportLab
            img_gauss = Image(buf_gauss, width=240, height=132)
            img_mat = Image(buf_mat, width=240, height=240)
            img_mc = Image(buf_mc, width=490, height=204)
            
            # Agregar al story
            story.append(Paragraph("Fase 5: Análisis Estadístico y Matemático del Suelo y Rendimiento", h2_style))
            
            # Tabla para Gauss y Matriz lado a lado
            t_analitico = Table([[img_gauss, img_mat]], colWidths=[245, 245])
            t_analitico.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t_analitico)
            story.append(Spacer(1, 5))
            
            # Monte Carlo
            story.append(img_mc)
            story.append(Spacer(1, 10))
            
        except Exception as e:
            print("Error al generar las gráficas para el PDF:", e)
            story.append(Paragraph(f"<i>Nota: No se pudieron renderizar los gráficos estadísticos en el PDF debido a un error técnico: {str(e)}</i>", body_style))
            story.append(Spacer(1, 10))
    
    # 6. RECOMENDACIONES ESTRATÉGICAS
    story.append(Paragraph("Fase 5: Recomendaciones y Conclusiones del Sistema", h2_style))
    for rec in data.get('recomendaciones', []):
        story.append(Paragraph(f"- {rec}", body_style))
        
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Este reporte es una simulacion tecnica basada en los datos de suelo y modelos financieros proporcionados.</i>", body_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='reporte_diversificacion.pdf', mimetype='application/pdf')

# Punto de entrada de la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=5000)
