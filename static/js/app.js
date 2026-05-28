let ultimoDiagnostico = null;
let chartInstance = null;
let chartGauss = null;
let chartDispersion = null;
let chartMonteCarlo = null;

document.getElementById('diagnostico-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('btn-submit');
    submitBtn.textContent = 'Procesando diagnostico...';
    submitBtn.disabled = true;
    
    const formData = new FormData(e.target);
    
    const data = {
        productor: {
            nombre: formData.get('nombre'),
            region: formData.get('region'),
            presupuesto: parseFloat(formData.get('presupuesto')),
            experiencia: formData.get('experiencia')
        },
        suelo: {
            ph: parseFloat(formData.get('ph')),
            nitrogeno: parseFloat(formData.get('nitrogeno')),
            materia_organica: parseFloat(formData.get('materia_organica'))
        },
        superficie: parseFloat(formData.get('superficie'))
    };

    try {
        const response = await fetch('/api/diagnostico_completo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Error al conectar con la API de diagnostico');
        }
        
        const result = await response.json();
        ultimoDiagnostico = result;
        mostrarResultados(result);
    } catch (error) {
        console.error("Error al procesar el diagnostico:", error);
        alert("Ocurrio un error al procesar la solicitud. Verifique los datos e intente de nuevo.");
    } finally {
        submitBtn.textContent = 'Generar Diagnostico Completo';
        submitBtn.disabled = false;
    }
});

function mostrarResultados(data) {
    // Mostrar la sección de resultados
    const resultadosSeccion = document.getElementById('resultados-seccion');
    resultadosSeccion.style.display = 'block';
    
    // Desplazar suavemente hasta los resultados
    resultadosSeccion.scrollIntoView({ behavior: 'smooth' });
    
    // Rellenar la tabla
    const tbody = document.querySelector('#tabla-cultivos tbody');
    tbody.innerHTML = '';
    
    data.resultados.forEach(r => {
        const tr = document.createElement('tr');
        
        // Asignar clases de estilo según aptitud
        let aptoClass = '';
        if (r.apto === 'Si') aptoClass = 'apto-si';
        else if (r.apto === 'Parcial') aptoClass = 'apto-parcial';
        else aptoClass = 'apto-no';
        
        let recClass = r.recomendar === 'SI' ? 'rec-si' : 'rec-no';
        
        // Formatear números
        const rendimientoStr = r.rendimiento_total > 0 ? `${r.rendimiento_total.toFixed(1)} ton` : '-';
        const ingresoStr = r.ingreso > 0 ? `$${r.ingreso.toLocaleString('es-MX', { maximumFractionDigits: 0 })}` : '-';
        const costoStr = r.costo > 0 ? `$${r.costo.toLocaleString('es-MX', { maximumFractionDigits: 0 })}` : '-';
        const utilidadStr = r.utilidad_anual !== 0 ? `$${r.utilidad_anual.toLocaleString('es-MX', { maximumFractionDigits: 0 })}` : '-';
        const vpnStr = r.vpn > 0 ? `$${r.vpn.toLocaleString('es-MX', { maximumFractionDigits: 0 })}` : '-';
        const tirStr = r.tir > 0 ? `${(r.tir * 100).toFixed(0)}%` : '-';
        
        tr.innerHTML = `
            <td><strong>${r.cultivo}</strong></td>
            <td class="${aptoClass}">${r.apto} <br><small>${r.detalles}</small></td>
            <td>${rendimientoStr}</td>
            <td>${ingresoStr}</td>
            <td>${costoStr}</td>
            <td>${utilidadStr}</td>
            <td><strong>${vpnStr}</strong></td>
            <td>${tirStr}</td>
            <td class="${recClass}"><strong>${r.recomendar}</strong></td>
        `;
        tbody.appendChild(tr);
    });
    
    // Rellenar las recomendaciones
    const listaRecomendaciones = document.getElementById('lista-recomendaciones');
    listaRecomendaciones.innerHTML = '';
    data.recomendaciones.forEach(rec => {
        const p = document.createElement('p');
        p.className = 'rec-item';
        p.textContent = rec;
        listaRecomendaciones.appendChild(p);
    });
    
    // Dibujar los gráficos
    dibujarGrafico(data.resultados);
    
    // Dibujar análisis estadísticos avanzados
    if (data.analisis_avanzado) {
        document.getElementById('cultivo-analisis-titulo').textContent = data.analisis_avanzado.cultivo;
        
        dibujarGraficoGauss(data.analisis_avanzado, data.suelo.ph);
        dibujarTablaCorrelacion(data.analisis_avanzado.correlacion.matriz);
        dibujarGraficoDispersion(data.analisis_avanzado.correlacion.parcelas);
        dibujarHistogramaMonteCarlo(data.analisis_avanzado.montecarlo);
    }
}

function dibujarGrafico(resultados) {
    const ctx = document.getElementById('chart-vpn').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    // Filtrar los cultivos que tienen VPN calculado (mayor a 0)
    const cultivosFiltrados = resultados.filter(r => r.vpn > 0);
    
    if (cultivosFiltrados.length === 0) {
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
        return;
    }
    
    const labels = cultivosFiltrados.map(r => r.cultivo);
    const vpnDatos = cultivosFiltrados.map(r => r.vpn);
    
    const backgroundColors = cultivosFiltrados.map(r => 
        r.recomendar === 'SI' ? 'rgba(46, 125, 50, 0.75)' : 'rgba(198, 40, 40, 0.75)'
    );
    const borderColors = cultivosFiltrados.map(r => 
        r.recomendar === 'SI' ? 'rgba(46, 125, 50, 1)' : 'rgba(198, 40, 40, 1)'
    );
    
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valor Presente Neto (VPN a 5 años, MXN)',
                data: vpnDatos,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString('es-MX');
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toLocaleString('es-MX');
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function dibujarGraficoGauss(analisis, phActual) {
    const ctx = document.getElementById('chart-gauss-ph').getContext('2d');
    
    if (chartGauss) {
        chartGauss.destroy();
    }
    
    const phOptimo = analisis.ph_optimo;
    const gaussPoints = analisis.gauss_ph;
    
    const pointsAcida = gaussPoints.filter(p => p.x <= 5.0);
    const pointsFavorable = gaussPoints.filter(p => p.x >= 5.0 && p.x <= 7.0);
    const pointsAlcalina = gaussPoints.filter(p => p.x >= 7.0);
    
    let yActual = 0.01;
    let closestPoint = gaussPoints.reduce((prev, curr) => 
        Math.abs(curr.x - phActual) < Math.abs(prev.x - phActual) ? curr : prev
    );
    if (closestPoint) {
        yActual = closestPoint.y;
    }
    
    const vLinePoints = [
        { x: phActual, y: 0 },
        { x: phActual, y: 0.8 }
    ];
    
    chartGauss = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    type: 'line',
                    label: 'Zona Ácida (Riesgo)',
                    data: pointsAcida,
                    borderColor: 'rgba(198, 40, 40, 1)',
                    backgroundColor: 'rgba(198, 40, 40, 0.2)',
                    fill: 'origin',
                    showLine: true,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    type: 'line',
                    label: 'Zona Favorable',
                    data: pointsFavorable,
                    borderColor: 'rgba(46, 125, 50, 1)',
                    backgroundColor: 'rgba(46, 125, 50, 0.2)',
                    fill: 'origin',
                    showLine: true,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    type: 'line',
                    label: 'Zona Alcalina (Riesgo)',
                    data: pointsAlcalina,
                    borderColor: 'rgba(198, 40, 40, 1)',
                    backgroundColor: 'rgba(198, 40, 40, 0.2)',
                    fill: 'origin',
                    showLine: true,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    type: 'line',
                    label: `pH Actual del Productor (${phActual})`,
                    data: vLinePoints,
                    borderColor: '#ef6c00',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false,
                    showLine: true
                },
                {
                    type: 'scatter',
                    label: 'Suelo Evaluado',
                    data: [{ x: phActual, y: yActual }],
                    backgroundColor: '#ef6c00',
                    borderColor: '#ffffff',
                    borderWidth: 1.5,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    min: 3.5,
                    max: 8.5,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'pH del Suelo', color: '#aaa', font: { size: 10 } }
                },
                y: {
                    min: 0,
                    max: 0.9,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'Probabilidad', color: '#aaa', font: { size: 10 } }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#ccc', boxWidth: 12, font: { size: 9 } }
                }
            }
        }
    });
}

function dibujarTablaCorrelacion(matriz) {
    const tbody = document.querySelector('#tabla-correlacion tbody');
    tbody.innerHTML = '';
    
    const factors = ["pH (X1)", "Nutrientes (X2)", "Plagas (X3)", "Merma (X4)"];
    
    factors.forEach(rowFactor => {
        const tr = document.createElement('tr');
        
        const thRow = document.createElement('td');
        thRow.style.fontWeight = '600';
        thRow.style.textAlign = 'left';
        thRow.style.color = '#fff';
        thRow.textContent = rowFactor;
        tr.appendChild(thRow);
        
        factors.forEach(colFactor => {
            const val = matriz[rowFactor][colFactor];
            const td = document.createElement('td');
            td.textContent = val.toFixed(2);
            td.style.fontWeight = 'bold';
            
            let alpha = Math.abs(val);
            if (val > 0.01) {
                td.style.backgroundColor = `rgba(76, 175, 80, ${alpha * 0.6})`;
                td.style.color = '#ffffff';
            } else if (val < -0.01) {
                td.style.backgroundColor = `rgba(229, 115, 115, ${alpha * 0.6})`;
                td.style.color = '#ffffff';
            } else {
                td.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                td.style.color = '#aaa';
            }
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}

function dibujarGraficoDispersion(parcelas) {
    const ctx = document.getElementById('chart-dispersion').getContext('2d');
    
    if (chartDispersion) {
        chartDispersion.destroy();
    }
    
    const scatterPoints = parcelas.map(p => ({
        x: p.plagas,
        y: p.merma
    }));
    
    chartDispersion = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Relación Plagas vs Merma',
                data: scatterPoints,
                backgroundColor: 'rgba(21, 101, 192, 0.8)',
                borderColor: '#ffffff',
                borderWidth: 0.8,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    min: 1.0,
                    max: 4.0,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'Plagas (1:Bajo a 4:Muy Alto)', color: '#aaa', font: { size: 9 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'Merma (%)', color: '#aaa', font: { size: 9 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function dibujarHistogramaMonteCarlo(montecarlo) {
    const ctx = document.getElementById('chart-montecarlo-rendimiento').getContext('2d');
    
    if (chartMonteCarlo) {
        chartMonteCarlo.destroy();
    }
    
    const histData = montecarlo.histograma;
    const rendimientoEquilibrio = montecarlo.rendimiento_equilibrio;
    const probabilidadExito = montecarlo.probabilidad_exito;
    
    document.getElementById('montecarlo-badge-exito').textContent = `${probabilidadExito}%`;
    document.getElementById('montecarlo-equilibrio-ton').textContent = rendimientoEquilibrio.toFixed(2);
    
    const badge = document.getElementById('montecarlo-badge-exito');
    badge.className = 'badge-prob';
    if (probabilidadExito >= 90) {
        badge.classList.add('prob-alta');
    } else if (probabilidadExito >= 65) {
        badge.classList.add('prob-media');
    } else {
        badge.classList.add('prob-baja');
    }
    
    const labels = histData.map(b => b.bin_center.toFixed(1));
    const frecuencias = histData.map(b => b.frecuencia);
    const maxFreq = Math.max(...frecuencias);
    
    let closestIdx = 0;
    let minDiff = Infinity;
    histData.forEach((b, idx) => {
        let diff = Math.abs(b.bin_center - rendimientoEquilibrio);
        if (diff < minDiff) {
            minDiff = diff;
            closestIdx = idx;
        }
    });
    
    const verticalLinePlugin = {
        id: 'verticalLine',
        afterDatasetsDraw(chart) {
            const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;
            const xPos = x.getPixelForValue(closestIdx);
            ctx.save();
            ctx.beginPath();
            ctx.strokeStyle = '#d32f2f';
            ctx.lineWidth = 2.5;
            ctx.setLineDash([5, 5]);
            ctx.moveTo(xPos, top);
            ctx.lineTo(xPos, bottom);
            ctx.stroke();
            
            // Etiqueta del Punto de Equilibrio
            ctx.fillStyle = '#ef9a9a';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText('Punto de Equilibrio', xPos + 6, top + 15);
            ctx.restore();
        }
    };
    
    chartMonteCarlo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Escenarios Proyectados',
                data: frecuencias,
                backgroundColor: 'rgba(21, 101, 192, 0.7)',
                borderColor: 'rgba(21, 101, 192, 1)',
                borderWidth: 1.2,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'Rendimiento Proyectado (Ton/Ha)', color: '#aaa', font: { size: 10 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'Frecuencia (Ensayos)', color: '#aaa', font: { size: 10 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        },
        plugins: [verticalLinePlugin]
    });
}

document.getElementById('btn-pdf').addEventListener('click', async () => {
    if (!ultimoDiagnostico) return;
    
    const pdfBtn = document.getElementById('btn-pdf');
    const originalText = pdfBtn.textContent;
    pdfBtn.textContent = 'Descargando reporte PDF...';
    pdfBtn.disabled = true;
    
    try {
        const response = await fetch('/api/generar_pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ultimoDiagnostico)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'reporte_diversificacion_agricola.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert("Error al generar el archivo PDF.");
        }
    } catch (error) {
        console.error("Error al descargar PDF:", error);
        alert("Ocurrio un error al intentar descargar el PDF.");
    } finally {
        pdfBtn.textContent = originalText;
        pdfBtn.disabled = false;
    }
});

// Cargar regiones dinámicamente y configurar pestañas al cargar la página
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Cargar regiones
    try {
        const response = await fetch('/api/regiones');
        if (response.ok) {
            const regiones = await response.json();
            const selectRegion = document.getElementById('region');
            if (selectRegion && regiones.length > 0) {
                selectRegion.innerHTML = '';
                regiones.forEach(r => {
                    const option = document.createElement('option');
                    option.value = r.nombre;
                    option.textContent = `${r.nombre} (Altitud: ${r.altitud}m)`;
                    selectRegion.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error("Error al cargar regiones dinámicamente:", error);
    }

    // 2. Configurar el comportamiento de las pestañas del dashboard
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Desactivar todas las pestañas y contenidos
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Activar la pestaña clicada
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            const content = document.getElementById(tabId);
            if (content) {
                content.classList.add('active');
            }
            
            // Forzar resize de los gráficos para evitar bugs visuales cuando se muestran
            setTimeout(() => {
                if (tabId === 'tab-resumen' && chartInstance) chartInstance.resize();
                if (tabId === 'tab-gauss' && chartGauss) chartGauss.resize();
                if (tabId === 'tab-correlacion' && chartDispersion) chartDispersion.resize();
                if (tabId === 'tab-montecarlo' && chartMonteCarlo) chartMonteCarlo.resize();
            }, 50);
        });
    });
});

