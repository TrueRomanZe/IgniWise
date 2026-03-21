/**
 * IgniWise - JavaScript Application
 * Maneja el mapa interactivo y la visualización de predicciones
 */

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================

let map;
let predictionsData = null;
let provinceLayers = {};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 IgniWise iniciado');
    
    // Inicializar mapa
    initMap();
    
    // Cargar predicciones
    loadPredictions();
});

// ============================================================================
// FUNCIONES DE MAPA
// ============================================================================

/**
 * Inicializa el mapa de Leaflet centrado en España
 */
function initMap() {
    // Crear mapa centrado en España
    map = L.map('map').setView([40.4168, -3.7038], 6);
    
    // Añadir capa base OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    console.log('✓ Mapa inicializado');
}

/**
 * Carga datos de predicciones desde JSON
 */
async function loadPredictions() {
    try {
        console.log('Cargando predicciones...');
        
        // Cargar JSON de predicciones
        const response = await fetch('../data/predictions/current_windows.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        predictionsData = await response.json();
        
        console.log(`✓ Cargadas ${predictionsData.metadata.total_provincias} provincias`);
        
        // Actualizar timestamp
        document.getElementById('last-update').textContent = 
            `Última actualización: ${predictionsData.metadata.fecha_actualizacion}`;
        
        // Dibujar provincias en el mapa
        drawProvinces();
        
    } catch (error) {
        console.error('Error cargando predicciones:', error);
        
        // Mostrar error al usuario
        document.getElementById('last-update').innerHTML = 
            '<span style="color: #ef4444;">⚠️ Error cargando predicciones. Intenta recargar la página.</span>';
    }
}

/**
 * Dibuja marcadores de provincias en el mapa
 */
function drawProvinces() {
    if (!predictionsData || !predictionsData.provincias) {
        console.error('No hay datos de provincias');
        return;
    }
    
    predictionsData.provincias.forEach(provincia => {
        // Crear marcador circular
        const marker = L.circleMarker(
            [provincia.coordenadas.lat, provincia.coordenadas.lon],
            {
                radius: 8,
                fillColor: provincia.prediccion.color,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }
        );
        
        // Añadir popup
        marker.bindPopup(createPopupContent(provincia));
        
        // Evento click para mostrar detalles en panel
        marker.on('click', function() {
            showProvinceDetails(provincia);
        });
        
        // Efecto hover
        marker.on('mouseover', function() {
            this.setStyle({
                radius: 12,
                fillOpacity: 1
            });
        });
        
        marker.on('mouseout', function() {
            this.setStyle({
                radius: 8,
                fillOpacity: 0.8
            });
        });
        
        // Añadir al mapa
        marker.addTo(map);
        
        // Guardar referencia
        provinceLayers[provincia.provincia] = marker;
    });
    
    console.log(`✓ Dibujadas ${Object.keys(provinceLayers).length} provincias`);
}

// ============================================================================
// FUNCIONES DE UI
// ============================================================================

/**
 * Crea contenido HTML para popup de provincia
 */
function createPopupContent(provincia) {
    return `
        <div class="popup-content">
            <div class="popup-title">${provincia.provincia}</div>
            <div class="popup-status" style="background-color: ${provincia.prediccion.color};">
                ${provincia.prediccion.ventana}
            </div>
            <div class="popup-info">
                <p><strong>🌡️ Temperatura:</strong> ${provincia.clima.temperatura}°C</p>
                <p><strong>💧 Humedad:</strong> ${provincia.clima.humedad}%</p>
                <p><strong>💨 Viento:</strong> ${provincia.clima.viento} km/h</p>
                <p><strong>🔥 FWI:</strong> ${provincia.indices.fwi}</p>
                <p><strong>📊 Confianza:</strong> ${provincia.prediccion.confianza}%</p>
            </div>
        </div>
    `;
}

/**
 * Muestra detalles completos de provincia en panel lateral
 */
function showProvinceDetails(provincia) {
    const detailPanel = document.getElementById('province-detail');
    
    detailPanel.className = 'province-detail active';
    detailPanel.innerHTML = `
        <h3>${provincia.provincia}</h3>
        
        <div class="prediction-badge" style="background-color: ${provincia.prediccion.color};">
            ${provincia.prediccion.ventana}
        </div>
        
        <div class="detail-section">
            <h4>Condiciones Meteorológicas</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <strong>🌡️</strong> ${provincia.clima.temperatura}°C
                </div>
                <div class="detail-item">
                    <strong>💧</strong> ${provincia.clima.humedad}%
                </div>
                <div class="detail-item">
                    <strong>💨</strong> ${provincia.clima.viento} km/h
                </div>
                <div class="detail-item">
                    <strong>☁️</strong> ${provincia.clima.descripcion}
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Índices de Peligro</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <strong>FWI:</strong> ${provincia.indices.fwi}
                </div>
                <div class="detail-item">
                    <strong>FFMC:</strong> ${provincia.indices.ffmc}
                </div>
                <div class="detail-item">
                    <strong>DMC:</strong> ${provincia.indices.dmc}
                </div>
                <div class="detail-item">
                    <strong>Confianza:</strong> ${provincia.prediccion.confianza}%
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Recomendación</h4>
            <div class="recommendation">
                ${provincia.recomendacion}
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Probabilidades</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <strong>Segura:</strong> ${provincia.prediccion.probabilidades.SEGURA}%
                </div>
                <div class="detail-item">
                    <strong>Marginal:</strong> ${provincia.prediccion.probabilidades.MARGINAL}%
                </div>
                <div class="detail-item">
                    <strong>Peligrosa:</strong> ${provincia.prediccion.probabilidades.PELIGROSA}%
                </div>
            </div>
        </div>
    `;
    
    // Hacer scroll al panel en móviles
    if (window.innerWidth < 1024) {
        detailPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Refresca las predicciones (para actualización manual)
 */
function refreshPredictions() {
    console.log('Refrescando predicciones...');
    
    // Limpiar marcadores existentes
    Object.values(provinceLayers).forEach(layer => {
        map.removeLayer(layer);
    });
    provinceLayers = {};
    
    // Recargar
    loadPredictions();
}

// Exponer función para debugging en consola
window.refreshPredictions = refreshPredictions;

console.log('✓ IgniWise app cargada. Usa refreshPredictions() para actualizar.');
