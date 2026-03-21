"""
IgniWise - Generación de Predicciones
Genera predicciones de ventanas de quema para todas las provincias de España

Este script:
1. Obtiene datos meteorológicos actuales (OpenWeatherMap)
2. Calcula features (FWI, etc.)
3. Predice ventana de quema para cada provincia
4. Genera JSON con resultados para la web

Se ejecuta automáticamente cada 6 horas vía GitHub Actions
"""

import pandas as pd
import numpy as np
import joblib
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import (
    MODELS_DIR, DATA_PREDICTIONS, DATA_PROCESSED,
    OPENWEATHER_API_KEY, PROVINCIAS_ESPANA,
    COLOR_SEGURA, COLOR_MARGINAL, COLOR_PELIGROSA
)
from src.utils.logger import setup_logger
from src.data_processing.calculate_fwi import calculate_fwi_components

logger = setup_logger(__name__, 'predict')

# ============================================================================
# FUNCIONES DE OBTENCIÓN DE DATOS
# ============================================================================

def load_model():
    """Carga modelo Random Forest entrenado"""
    logger.info("Cargando modelo entrenado...")
    
    model_file = MODELS_DIR / 'random_forest_v1.pkl'
    
    if not model_file.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado: {model_file}\n"
            "Ejecuta primero: python src/modeling/train_model.py"
        )
    
    model = joblib.load(model_file)
    logger.info(f"  ✓ Modelo cargado: {model_file.name}")
    
    return model


def load_provincial_data() -> dict:
    """
    Carga datos geográficos de provincias
    
    Returns:
        Diccionario {provincia: {lat, lon, elevacion}}
    """
    logger.info("Cargando datos provinciales...")
    
    geo_file = DATA_PROCESSED / 'provincias_geo.geojson'
    
    if not geo_file.exists():
        logger.warning(f"  ⚠ Geodata no encontrada, usando coordenadas por defecto")
        return {}
    
    import geopandas as gpd
    gdf = gpd.read_file(geo_file)
    
    # Crear diccionario provincia -> datos
    provincial_data = {}
    for idx, row in gdf.iterrows():
        provincial_data[row['nombre']] = {
            'lat': row['centroide_lat'],
            'lon': row['centroide_lon'],
            'elevacion': row.get('elevacion', 500)
        }
    
    logger.info(f"  ✓ Cargados datos de {len(provincial_data)} provincias")
    
    return provincial_data


def get_current_weather(lat: float, lon: float, provincia: str) -> dict:
    """
    Obtiene datos meteorológicos actuales de OpenWeatherMap
    
    Args:
        lat: Latitud
        lon: Longitud
        provincia: Nombre de la provincia (para logging)
        
    Returns:
        Diccionario con datos meteorológicos o None si falla
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'es'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraer datos relevantes
        weather = {
            'temperatura': data['main']['temp'],
            'humedad': data['main']['humidity'],
            'viento_velocidad': data['wind']['speed'] * 3.6,  # m/s -> km/h
            'viento_direccion': data['wind'].get('deg', 0),
            'descripcion': data['weather'][0]['description'],
            'icono': data['weather'][0]['icon']
        }
        
        return weather
        
    except Exception as e:
        logger.warning(f"  ⚠ Error obteniendo clima para {provincia}: {e}")
        return None


def calculate_dias_sin_lluvia(provincia: str) -> int:
    """
    Calcula días consecutivos sin lluvia
    
    En producción: Consultar histórico de AEMET
    Aquí: Estimación simplificada
    
    Args:
        provincia: Nombre de provincia
        
    Returns:
        Número de días sin lluvia (estimado)
    """
    # TODO: En producción, consultar AEMET API
    # Para desarrollo, usar valor aleatorio realista
    return np.random.randint(0, 15)


# ============================================================================
# FUNCIONES DE PREDICCIÓN
# ============================================================================

def prepare_features(weather: dict, provincia_data: dict, provincia: str) -> pd.DataFrame:
    """
    Prepara features para predicción siguiendo estructura del modelo
    
    Args:
        weather: Datos meteorológicos actuales
        provincia_data: Datos geográficos de la provincia
        provincia: Nombre de provincia
        
    Returns:
        DataFrame con una fila de features
    """
    # Calcular FWI con datos actuales
    fwi_components = calculate_fwi_components(
        temp=weather['temperatura'],
        rh=weather['humedad'],
        wind=weather['viento_velocidad'],
        rain=0,  # Simplificado - en producción vendría de histórico
        month=datetime.now().month
    )
    
    # Días sin lluvia
    dias_sin_lluvia = calculate_dias_sin_lluvia(provincia)
    
    # Preparar todas las features en el orden correcto
    features = {
        # Meteorológicas inmediatas
        'temperatura': weather['temperatura'],
        'humedad': weather['humedad'],
        'viento_velocidad': weather['viento_velocidad'],
        'viento_direccion': weather['viento_direccion'],
        'precip_24h': 0,  # Simplificado
        
        # Meteorológicas acumuladas
        'dias_sin_lluvia': dias_sin_lluvia,
        'precip_7d': 0,  # Simplificado
        'precip_30d': 0,  # Simplificado
        'temp_max_3d': weather['temperatura'] + np.random.uniform(2, 5),
        
        # Índices FWI
        'fwi': fwi_components['fwi'],
        'ffmc': fwi_components['ffmc'],
        'dmc': fwi_components['dmc'],
        'dc': fwi_components['dc'],
        
        # Topográficas
        'elevacion': provincia_data.get('elevacion', 500),
        'pendiente': np.random.uniform(5, 20),  # Simplificado
        'orientacion': np.random.choice([0, 90, 180, 270]),
        
        # Vegetación
        'ndvi': 0.6,  # Simplificado
        'tipo_bosque': np.random.choice([0, 1, 2]),
        
        # Temporales
        'mes': datetime.now().month,
        'dia_año': datetime.now().timetuple().tm_yday
    }
    
    return pd.DataFrame([features])


def predict_for_province(model, provincia: str, provincia_data: dict) -> dict:
    """
    Genera predicción para una provincia
    
    Args:
        model: Modelo ML entrenado
        provincia: Nombre de provincia
        provincia_data: Datos geográficos
        
    Returns:
        Diccionario con predicción completa
    """
    logger.info(f"  Procesando: {provincia}")
    
    # Obtener coordenadas
    if provincia not in provincia_data:
        logger.warning(f"    ⚠ Provincia sin geodata, saltando...")
        return None
    
    coords = provincia_data[provincia]
    
    # Obtener clima actual
    weather = get_current_weather(coords['lat'], coords['lon'], provincia)
    
    if not weather:
        return None
    
    # Preparar features
    X = prepare_features(weather, coords, provincia)
    
    # Predecir
    prediction = model.predict(X)[0]
    probas = model.predict_proba(X)[0]
    
    # Mapeo de predicción a categoría
    categorias = {
        0: {'nombre': 'SEGURA', 'color': COLOR_SEGURA},
        1: {'nombre': 'MARGINAL', 'color': COLOR_MARGINAL},
        2: {'nombre': 'PELIGROSA', 'color': COLOR_PELIGROSA}
    }
    
    categoria = categorias[prediction]
    
    # Preparar resultado
    result = {
        'provincia': provincia,
        'timestamp': datetime.now().isoformat(),
        'coordenadas': {
            'lat': coords['lat'],
            'lon': coords['lon']
        },
        'clima': {
            'temperatura': round(weather['temperatura'], 1),
            'humedad': weather['humedad'],
            'viento': round(weather['viento_velocidad'], 1),
            'descripcion': weather['descripcion'],
            'icono': weather['icono']
        },
        'indices': {
            'fwi': round(X['fwi'].values[0], 2),
            'ffmc': round(X['ffmc'].values[0], 2),
            'dmc': round(X['dmc'].values[0], 2)
        },
        'prediccion': {
            'ventana': categoria['nombre'],
            'color': categoria['color'],
            'confianza': round(probas[prediction] * 100, 1),
            'probabilidades': {
                'SEGURA': round(probas[0] * 100, 1),
                'MARGINAL': round(probas[1] * 100, 1),
                'PELIGROSA': round(probas[2] * 100, 1)
            }
        },
        'recomendacion': generate_recommendation(categoria['nombre'], weather, X)
    }
    
    logger.info(f"    ✓ {categoria['nombre']} (confianza: {result['prediccion']['confianza']}%)")
    
    return result


def generate_recommendation(ventana: str, weather: dict, features: pd.DataFrame) -> str:
    """
    Genera recomendación textual basada en predicción
    
    Args:
        ventana: SEGURA, MARGINAL, PELIGROSA
        weather: Datos meteorológicos
        features: Features calculadas
        
    Returns:
        Texto con recomendación
    """
    if ventana == 'SEGURA':
        return "Condiciones favorables para quemas prescritas. Proceder con protocolos estándar."
    
    elif ventana == 'MARGINAL':
        warnings = []
        
        if weather['temperatura'] > 28:
            warnings.append("temperatura elevada")
        if weather['humedad'] < 35:
            warnings.append("baja humedad")
        if weather['viento_velocidad'] > 25:
            warnings.append("viento fuerte")
        if features['fwi'].values[0] > 15:
            warnings.append("FWI alto")
        
        if warnings:
            return f"Precaución: {', '.join(warnings)}. Solo personal experimentado con vigilancia constante."
        else:
            return "Condiciones aceptables. Tomar precauciones estándar."
    
    else:  # PELIGROSA
        reasons = []
        
        if weather['temperatura'] > 32:
            reasons.append("temperatura extrema")
        if weather['humedad'] < 25:
            reasons.append("humedad muy baja")
        if weather['viento_velocidad'] > 40:
            reasons.append("viento muy fuerte")
        if features['fwi'].values[0] > 30:
            reasons.append("FWI muy alto")
        
        if reasons:
            return f"No realizar quemas. Razones: {', '.join(reasons)}. Riesgo de descontrol."
        else:
            return "Condiciones desfavorables. No realizar quemas prescritas."


# ============================================================================
# FUNCIONES DE GUARDADO
# ============================================================================

def save_predictions(predictions: list):
    """
    Guarda predicciones en JSON para la web
    
    Args:
        predictions: Lista de predicciones provinciales
    """
    logger.info("Guardando predicciones...")
    
    # Crear carpeta si no existe
    DATA_PREDICTIONS.mkdir(parents=True, exist_ok=True)
    
    # Preparar datos finales
    output = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'total_provincias': len(predictions),
            'version': '1.0'
        },
        'provincias': predictions
    }
    
    # Guardar
    output_file = DATA_PREDICTIONS / 'current_windows.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"  ✓ Predicciones guardadas: {output_file}")
    logger.info(f"    Provincias procesadas: {len(predictions)}")
    
    # Estadísticas
    ventanas = [p['prediccion']['ventana'] for p in predictions]
    logger.info(f"  Resumen:")
    logger.info(f"    SEGURA:     {ventanas.count('SEGURA'):3d}")
    logger.info(f"    MARGINAL:   {ventanas.count('MARGINAL'):3d}")
    logger.info(f"    PELIGROSA:  {ventanas.count('PELIGROSA'):3d}")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Pipeline completo de generación de predicciones"""
    
    logger.info("=" * 70)
    logger.info("IgniWise - Generación de Predicciones")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Cargar modelo
    model = load_model()
    
    # 2. Cargar datos provinciales
    provincial_data = load_provincial_data()
    
    # 3. Generar predicciones para cada provincia
    predictions = []
    
    # Usar solo provincias con geodata
    provincias_to_process = [p for p in PROVINCIAS_ESPANA if p in provincial_data]
    
    logger.info(f"Generando predicciones para {len(provincias_to_process)} provincias...")
    
    for provincia in provincias_to_process:
        result = predict_for_province(model, provincia, provincial_data)
        
        if result:
            predictions.append(result)
    
    # 4. Guardar predicciones
    if predictions:
        save_predictions(predictions)
    else:
        logger.error("  ✗ No se generaron predicciones")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("✓ PREDICCIONES GENERADAS EXITOSAMENTE")
    logger.info("=" * 70)
    logger.info(f"Total predicciones: {len(predictions)}")
    logger.info(f"Archivo: data/predictions/current_windows.json")
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
