"""
IgniWise - Descarga de Datos Geográficos
Descarga límites provinciales y datos topográficos del IGN España

Duración: 10-15 minutos
Output: data/processed/provincias_geo.geojson
"""

import requests
import geopandas as gpd
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import DATA_RAW, DATA_PROCESSED, PROVINCIAS_ESPANA
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'download_geodata')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URL de datos abiertos IGN/CNIG
IGN_PROVINCIAS_URL = "https://www.ign.es/web/resources/delegaciones/delegacionesProvincias.geojson"

# URL alternativa (Centro de Descargas CNIG)
CNIG_DOWNLOAD_URL = "https://centrodedescargas.cnig.es/CentroDescargas/index.jsp"

# Coordenadas de centroides provinciales (backup si no se puede descargar)
PROVINCIAS_CENTROIDES = {
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Barcelona": {"lat": 41.3851, "lon": 2.1734},
    "Valencia": {"lat": 39.4699, "lon": -0.3763},
    "Sevilla": {"lat": 37.3891, "lon": -5.9845},
    "Zaragoza": {"lat": 41.6488, "lon": -0.8891},
    "Málaga": {"lat": 36.7213, "lon": -4.4214},
    "Murcia": {"lat": 37.9922, "lon": -1.1307},
    "Las Palmas": {"lat": 28.1236, "lon": -15.4366},
    "Vizcaya": {"lat": 43.2630, "lon": -2.9350},
    "Alicante": {"lat": 38.3452, "lon": -0.4810},
    "Cádiz": {"lat": 36.5270, "lon": -6.2885},
    "A Coruña": {"lat": 43.3623, "lon": -8.4115},
    "Asturias": {"lat": 43.3614, "lon": -5.8593},
    "Granada": {"lat": 37.1773, "lon": -3.5986},
    "Córdoba": {"lat": 37.8882, "lon": -4.7794},
    "Valladolid": {"lat": 41.6528, "lon": -4.7245},
    "Toledo": {"lat": 39.8628, "lon": -4.0273},
    "Jaén": {"lat": 37.7796, "lon": -3.7849},
    "Cantabria": {"lat": 43.1828, "lon": -3.9878},
    "Castellón": {"lat": 39.9864, "lon": -0.0513},
    "Almería": {"lat": 36.8410, "lon": -2.4676},
    "Pontevedra": {"lat": 42.4321, "lon": -8.6444},
    "Huelva": {"lat": 37.2614, "lon": -6.9447},
    "León": {"lat": 42.5987, "lon": -5.5671},
    "Lleida": {"lat": 41.6175, "lon": 0.6200},
    "Girona": {"lat": 41.9794, "lon": 2.8214},
    "Tarragona": {"lat": 41.1189, "lon": 1.2445},
    "Álava": {"lat": 42.8467, "lon": -2.6716},
    "Gipuzkoa": {"lat": 43.2203, "lon": -2.3242},
    "La Rioja": {"lat": 42.2871, "lon": -2.5396},
    "Navarra": {"lat": 42.6954, "lon": -1.6761},
    "Lugo": {"lat": 43.0097, "lon": -7.5567},
    "Ourense": {"lat": 42.3367, "lon": -7.8640},
    "Badajoz": {"lat": 38.8794, "lon": -6.9706},
    "Cáceres": {"lat": 39.4753, "lon": -6.3724},
    "Salamanca": {"lat": 40.9701, "lon": -5.6635},
    "Ávila": {"lat": 40.6570, "lon": -4.6981},
    "Segovia": {"lat": 40.9429, "lon": -4.1088},
    "Palencia": {"lat": 42.0096, "lon": -4.5288},
    "Burgos": {"lat": 42.3439, "lon": -3.6970},
    "Soria": {"lat": 41.7665, "lon": -2.4790},
    "Zamora": {"lat": 41.5035, "lon": -5.7447},
    "Guadalajara": {"lat": 40.6319, "lon": -3.1679},
    "Cuenca": {"lat": 40.0704, "lon": -2.1374},
    "Albacete": {"lat": 38.9943, "lon": -1.8585},
    "Ciudad Real": {"lat": 38.9848, "lon": -3.9273},
    "Huesca": {"lat": 42.1401, "lon": -0.4080},
    "Teruel": {"lat": 40.3456, "lon": -1.1065}
}

# ============================================================================
# FUNCIONES
# ============================================================================

def download_provincias_geojson() -> gpd.GeoDataFrame:
    """
    Intenta descargar límites provinciales de IGN
    
    Returns:
        GeoDataFrame con geometrías provinciales o None si falla
    """
    logger.info("Intentando descargar límites provinciales de IGN...")
    
    try:
        # Intentar descarga directa
        response = requests.get(IGN_PROVINCIAS_URL, timeout=30)
        response.raise_for_status()
        
        # Parsear GeoJSON
        geojson_data = response.json()
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        
        logger.info(f"  ✓ Descargadas {len(gdf)} provincias desde IGN")
        return gdf
        
    except Exception as e:
        logger.warning(f"  ⚠ No se pudo descargar de IGN: {e}")
        logger.info("  Usando datos de respaldo...")
        return None


def create_provincias_from_centroides() -> gpd.GeoDataFrame:
    """
    Crea GeoDataFrame con puntos centroides de provincias
    
    Usado como respaldo si no se pueden descargar geometrías completas
    
    Returns:
        GeoDataFrame con puntos centroides
    """
    from shapely.geometry import Point
    
    logger.info("Creando geometrías desde centroides...")
    
    features = []
    
    for provincia, coords in PROVINCIAS_CENTROIDES.items():
        # Crear punto
        point = Point(coords['lon'], coords['lat'])
        
        # Crear buffer de ~25km para simular área provincial
        # (en grados, aprox 0.25°)
        polygon = point.buffer(0.25)
        
        features.append({
            'geometry': polygon,
            'NAMEUNIT': provincia,
            'properties': {
                'nombre': provincia,
                'centroide_lat': coords['lat'],
                'centroide_lon': coords['lon']
            }
        })
    
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    
    logger.info(f"  ✓ Creadas {len(gdf)} geometrías provinciales")
    return gdf


def simplify_geometries(gdf: gpd.GeoDataFrame, tolerance: float = 0.01) -> gpd.GeoDataFrame:
    """
    Simplifica geometrías para reducir tamaño de archivo
    
    Args:
        gdf: GeoDataFrame original
        tolerance: Tolerancia de simplificación (grados)
    
    Returns:
        GeoDataFrame simplificado
    """
    logger.info(f"Simplificando geometrías (tolerancia: {tolerance}°)...")
    
    # Simplificar geometrías
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    
    # Calcular centroides
    gdf['centroide_lon'] = gdf['geometry'].centroid.x
    gdf['centroide_lat'] = gdf['geometry'].centroid.y
    
    logger.info("  ✓ Geometrías simplificadas")
    
    return gdf


def normalize_province_names(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Normaliza nombres de provincias para matching con PROVINCIAS_ESPANA
    
    Args:
        gdf: GeoDataFrame con columna de nombres
        
    Returns:
        GeoDataFrame con nombres normalizados
    """
    logger.info("Normalizando nombres de provincias...")
    
    # Detectar columna de nombres (puede variar según fuente)
    name_column = None
    for col in ['NAMEUNIT', 'nombre', 'provincia', 'name']:
        if col in gdf.columns:
            name_column = col
            break
    
    if not name_column:
        logger.warning("  ⚠ No se encontró columna de nombres")
        return gdf
    
    # Crear columna normalizada
    gdf['nombre'] = gdf[name_column].str.strip()
    
    # Verificar coverage
    matched = gdf['nombre'].isin(PROVINCIAS_ESPANA)
    logger.info(f"  ✓ Matched: {matched.sum()}/{len(gdf)} provincias")
    
    if matched.sum() < len(gdf) * 0.8:  # <80% match
        logger.warning("  ⚠ Muchas provincias sin match - revisar nombres")
    
    return gdf


def add_elevation_data(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Añade elevación promedio provincial (simplificado)
    
    En producción real, esto se obtendría del MDT del IGN
    Aquí usamos estimaciones razonables
    
    Args:
        gdf: GeoDataFrame
        
    Returns:
        GeoDataFrame con columna 'elevacion'
    """
    logger.info("Añadiendo datos de elevación (estimados)...")
    
    # Elevaciones aproximadas por provincia (metros)
    elevaciones = {
        "Madrid": 650,
        "Barcelona": 100,
        "Valencia": 50,
        "Ávila": 1130,
        "Soria": 1050,
        "Teruel": 915,
        "Guadalajara": 690,
        "Cuenca": 950,
        "Granada": 738,
        "Huesca": 490,
        "León": 840,
        # ... (añadir resto, o usar promedio)
    }
    
    # Asignar elevación
    gdf['elevacion'] = gdf['nombre'].map(elevaciones).fillna(500)  # 500m por defecto
    
    logger.info("  ✓ Elevaciones añadidas")
    return gdf


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta descarga y procesamiento de datos geográficos"""
    
    logger.info("=" * 70)
    logger.info("IgniWise - Descarga de Datos Geográficos")
    logger.info("=" * 70)
    
    # Intentar descarga de IGN
    gdf = download_provincias_geojson()
    
    # Si falla, usar centroides
    if gdf is None:
        gdf = create_provincias_from_centroides()
    
    # Normalizar nombres
    gdf = normalize_province_names(gdf)
    
    # Simplificar geometrías (reduce tamaño archivo)
    gdf = simplify_geometries(gdf, tolerance=0.01)
    
    # Añadir elevación
    gdf = add_elevation_data(gdf)
    
    # Seleccionar solo columnas necesarias
    columns_to_keep = ['nombre', 'geometry', 'centroide_lat', 'centroide_lon', 'elevacion']
    gdf = gdf[columns_to_keep]
    
    # Guardar como GeoJSON
    output_file = DATA_PROCESSED / 'provincias_geo.geojson'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    gdf.to_file(output_file, driver='GeoJSON')
    
    logger.info("=" * 70)
    logger.info("✓ PROCESO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"Provincias procesadas: {len(gdf)}")
    logger.info(f"Archivo guardado: {output_file}")
    logger.info(f"Tamaño: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Mostrar preview
    logger.info("\nPreview de provincias:")
    logger.info(gdf.head()[['nombre', 'centroide_lat', 'centroide_lon', 'elevacion']])


if __name__ == "__main__":
    main()
