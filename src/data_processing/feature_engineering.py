"""
IgniWise - Feature Engineering
Procesa datos de incendios y meteorología para crear dataset de Machine Learning

Input: 
  - data/raw/incendios_miteco/incendios_completo.csv
  - data/processed/provincias_geo.geojson
  
Output: 
  - data/processed/training_data.csv (dataset ML completo)
  
Features generadas: 20 variables
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import DATA_RAW, DATA_PROCESSED
from src.utils.logger import setup_logger
from src.data_processing.calculate_fwi import calculate_fwi_components

logger = setup_logger(__name__, 'feature_engineering')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Umbrales para clasificación de ventanas
VENTANA_SEGURA_THRESHOLDS = {
    'temp_min': 10,
    'temp_max': 28,
    'humedad_min': 40,
    'viento_max': 25,
    'dias_sin_lluvia_max': 10,
    'fwi_max': 15
}

VENTANA_MARGINAL_THRESHOLDS = {
    'temp_min': 5,
    'temp_max': 35,
    'humedad_min': 25,
    'viento_max': 40,
    'dias_sin_lluvia_max': 20,
    'fwi_max': 30
}

# ============================================================================
# FUNCIONES DE FEATURE ENGINEERING
# ============================================================================

def load_fire_data() -> pd.DataFrame:
    """Carga datos de incendios históricos de MITECO"""
    logger.info("Cargando datos de incendios históricos...")
    
    fire_file = DATA_RAW / 'incendios_miteco' / 'incendios_completo.csv'
    
    if not fire_file.exists():
        raise FileNotFoundError(
            f"No se encontró archivo de incendios: {fire_file}\n"
            "Ejecuta primero: python src/data_collection/download_miteco.py"
        )
    
    df = pd.read_csv(fire_file, parse_dates=['fecha'])
    
    logger.info(f"  ✓ Cargados {len(df)} incendios")
    logger.info(f"  Período: {df['fecha'].min()} a {df['fecha'].max()}")
    
    return df


def load_geodata() -> gpd.GeoDataFrame:
    """Carga geometrías provinciales"""
    logger.info("Cargando datos geográficos...")
    
    geo_file = DATA_PROCESSED / 'provincias_geo.geojson'
    
    if not geo_file.exists():
        raise FileNotFoundError(
            f"No se encontró archivo geográfico: {geo_file}\n"
            "Ejecuta primero: python src/data_collection/download_geodata.py"
        )
    
    gdf = gpd.read_file(geo_file)
    
    logger.info(f"  ✓ Cargadas {len(gdf)} provincias")
    
    return gdf


def generate_synthetic_weather(fire_df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera datos meteorológicos sintéticos para desarrollo
    
    EN PRODUCCIÓN: Estos datos vendrían de OpenWeatherMap/AEMET históricos
    
    Args:
        fire_df: DataFrame de incendios con fechas
        
    Returns:
        DataFrame con weather features añadidos
    """
    logger.info("Generando datos meteorológicos (sintéticos para desarrollo)...")
    
    np.random.seed(42)
    n = len(fire_df)
    
    # Temperatura (realista por mes)
    month = fire_df['fecha'].dt.month
    temp_base = {
        1: 8, 2: 10, 3: 14, 4: 16, 5: 20, 6: 25,
        7: 29, 8: 28, 9: 24, 10: 18, 11: 12, 12: 9
    }
    fire_df['temperatura'] = month.map(temp_base) + np.random.normal(0, 5, n)
    
    # Humedad (inversamente correlacionada con temperatura)
    fire_df['humedad'] = 100 - fire_df['temperatura'] * 1.5 + np.random.normal(0, 15, n)
    fire_df['humedad'] = fire_df['humedad'].clip(10, 95)
    
    # Viento (más fuerte en primavera/verano)
    fire_df['viento_velocidad'] = np.random.exponential(15, n) + month * 0.5
    fire_df['viento_velocidad'] = fire_df['viento_velocidad'].clip(0, 80)
    
    # Dirección del viento (grados)
    fire_df['viento_direccion'] = np.random.uniform(0, 360, n)
    
    # Precipitación (más en invierno)
    precip_prob = (12 - month) / 12  # Mayor en invierno
    fire_df['precip_24h'] = np.where(
        np.random.random(n) < precip_prob,
        np.random.exponential(5, n),
        0
    )
    
    # Días consecutivos sin lluvia
    fire_df['dias_sin_lluvia'] = np.random.exponential(7, n).astype(int)
    fire_df['dias_sin_lluvia'] = fire_df['dias_sin_lluvia'].clip(0, 60)
    
    # Precipitación acumulada
    fire_df['precip_7d'] = np.random.exponential(10, n)
    fire_df['precip_30d'] = np.random.exponential(30, n)
    
    # Temperatura máxima últimos 3 días
    fire_df['temp_max_3d'] = fire_df['temperatura'] + np.random.uniform(2, 8, n)
    
    logger.info(f"  ✓ Generadas variables meteorológicas")
    
    return fire_df


def calculate_fwi_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula índices FWI (Fire Weather Index) para cada registro
    
    Args:
        df: DataFrame con weather features
        
    Returns:
        DataFrame con FWI features añadidos
    """
    logger.info("Calculando índices FWI...")
    
    fwi_results = []
    
    for idx, row in df.iterrows():
        # Calcular FWI con valores previos (simplificado para batch)
        fwi = calculate_fwi_components(
            temp=row['temperatura'],
            rh=row['humedad'],
            wind=row['viento_velocidad'],
            rain=row['precip_24h'],
            month=row['fecha'].month
        )
        
        fwi_results.append(fwi)
        
        if (idx + 1) % 1000 == 0:
            logger.info(f"  Procesados {idx + 1}/{len(df)} registros...")
    
    # Añadir al DataFrame
    fwi_df = pd.DataFrame(fwi_results)
    df = pd.concat([df.reset_index(drop=True), fwi_df], axis=1)
    
    logger.info(f"  ✓ Índices FWI calculados")
    
    return df


def add_topographic_features(df: pd.DataFrame, geo_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Añade features topográficas desde geodata provincial
    
    Args:
        df: DataFrame de incendios
        geo_df: GeoDataFrame con datos provinciales
        
    Returns:
        DataFrame con topographic features añadidos
    """
    logger.info("Añadiendo features topográficas...")
    
    # Crear mapping provincia -> elevación
    elevation_map = dict(zip(geo_df['nombre'], geo_df['elevacion']))
    
    # Asignar elevación (ya deberíamos tener provincia en df)
    df['elevacion'] = df['provincia'].map(elevation_map).fillna(500)
    
    # Pendiente (simulada - en producción vendría de MDT)
    # Provincias montañosas tienen mayor pendiente
    mountain_provinces = ['Ávila', 'Soria', 'Teruel', 'Granada', 'Huesca', 'León']
    df['pendiente'] = np.where(
        df['provincia'].isin(mountain_provinces),
        np.random.uniform(15, 35, len(df)),  # Pendiente alta
        np.random.uniform(0, 15, len(df))    # Pendiente baja
    )
    
    # Orientación (N=0, E=90, S=180, W=270)
    df['orientacion'] = np.random.choice([0, 90, 180, 270], len(df))
    
    logger.info(f"  ✓ Features topográficas añadidas")
    
    return df


def add_vegetation_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade features de vegetación
    
    En producción: NDVI de Sentinel-2, tipo de bosque de MAPAMA
    Aquí: Generación sintética realista
    
    Args:
        df: DataFrame de incendios
        
    Returns:
        DataFrame con vegetation features añadidos
    """
    logger.info("Añadiendo features de vegetación...")
    
    # NDVI (Normalized Difference Vegetation Index)
    # Mayor vegetación en primavera/verano
    month = df['fecha'].dt.month
    ndvi_seasonal = {
        1: 0.3, 2: 0.35, 3: 0.5, 4: 0.65, 5: 0.75, 6: 0.8,
        7: 0.7, 8: 0.6, 9: 0.5, 10: 0.45, 11: 0.35, 12: 0.3
    }
    df['ndvi'] = month.map(ndvi_seasonal) + np.random.normal(0, 0.1, len(df))
    df['ndvi'] = df['ndvi'].clip(0, 1)
    
    # Tipo de bosque (codificado)
    # 0 = pinar, 1 = encinar, 2 = matorral, 3 = mixto
    df['tipo_bosque'] = np.random.choice([0, 1, 2, 3], len(df), 
                                         p=[0.3, 0.25, 0.3, 0.15])
    
    logger.info(f"  ✓ Features de vegetación añadidas")
    
    return df


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade features temporales
    
    Args:
        df: DataFrame con columna 'fecha'
        
    Returns:
        DataFrame con temporal features añadidos
    """
    logger.info("Añadiendo features temporales...")
    
    # Mes del año (1-12)
    df['mes'] = df['fecha'].dt.month
    
    # Día del año (1-365)
    df['dia_año'] = df['fecha'].dt.dayofyear
    
    # Estación (0=invierno, 1=primavera, 2=verano, 3=otoño)
    df['estacion'] = pd.cut(
        df['mes'],
        bins=[0, 3, 6, 9, 12],
        labels=[0, 1, 2, 3]
    ).astype(int)
    
    # Día de la semana (0=lunes, 6=domingo)
    df['dia_semana'] = df['fecha'].dt.dayofweek
    
    # Es fin de semana (más incendios intencionados)
    df['es_fin_semana'] = (df['dia_semana'] >= 5).astype(int)
    
    logger.info(f"  ✓ Features temporales añadidas")
    
    return df


def create_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variable target: clasificación de ventana
    
    Basado en condiciones meteorológicas:
    - SEGURA (0): Condiciones ideales para quemas prescritas
    - MARGINAL (1): Condiciones aceptables con precauciones
    - PELIGROSA (2): No apto para quemas
    
    Args:
        df: DataFrame con todas las features
        
    Returns:
        DataFrame con columna 'ventana' añadida
    """
    logger.info("Creando variable target (ventana)...")
    
    # Condiciones para SEGURA
    segura = (
        (df['temperatura'] >= VENTANA_SEGURA_THRESHOLDS['temp_min']) &
        (df['temperatura'] <= VENTANA_SEGURA_THRESHOLDS['temp_max']) &
        (df['humedad'] >= VENTANA_SEGURA_THRESHOLDS['humedad_min']) &
        (df['viento_velocidad'] <= VENTANA_SEGURA_THRESHOLDS['viento_max']) &
        (df['dias_sin_lluvia'] <= VENTANA_SEGURA_THRESHOLDS['dias_sin_lluvia_max']) &
        (df['fwi'] <= VENTANA_SEGURA_THRESHOLDS['fwi_max'])
    )
    
    # Condiciones para MARGINAL
    marginal = (
        (df['temperatura'] >= VENTANA_MARGINAL_THRESHOLDS['temp_min']) &
        (df['temperatura'] <= VENTANA_MARGINAL_THRESHOLDS['temp_max']) &
        (df['humedad'] >= VENTANA_MARGINAL_THRESHOLDS['humedad_min']) &
        (df['viento_velocidad'] <= VENTANA_MARGINAL_THRESHOLDS['viento_max']) &
        (df['dias_sin_lluvia'] <= VENTANA_MARGINAL_THRESHOLDS['dias_sin_lluvia_max']) &
        (df['fwi'] <= VENTANA_MARGINAL_THRESHOLDS['fwi_max'])
    )
    
    # Asignar categoría
    df['ventana'] = 2  # PELIGROSA por defecto
    df.loc[marginal, 'ventana'] = 1  # MARGINAL
    df.loc[segura, 'ventana'] = 0    # SEGURA
    
    # Estadísticas
    counts = df['ventana'].value_counts().sort_index()
    logger.info(f"  ✓ Variable target creada:")
    logger.info(f"    SEGURA (0):     {counts.get(0, 0):5d} ({counts.get(0, 0)/len(df)*100:5.1f}%)")
    logger.info(f"    MARGINAL (1):   {counts.get(1, 0):5d} ({counts.get(1, 0)/len(df)*100:5.1f}%)")
    logger.info(f"    PELIGROSA (2):  {counts.get(2, 0):5d} ({counts.get(2, 0)/len(df)*100:5.1f}%)")
    
    return df


def select_final_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona las 20 features finales para el modelo
    
    Args:
        df: DataFrame completo
        
    Returns:
        DataFrame solo con features seleccionadas + target
    """
    logger.info("Seleccionando features finales...")
    
    # 20 features + 1 target
    selected_features = [
        # Meteorológicas inmediatas (5)
        'temperatura',
        'humedad',
        'viento_velocidad',
        'viento_direccion',
        'precip_24h',
        
        # Meteorológicas acumuladas (4)
        'dias_sin_lluvia',
        'precip_7d',
        'precip_30d',
        'temp_max_3d',
        
        # Índices de peligro (4)
        'fwi',
        'ffmc',
        'dmc',
        'dc',
        
        # Topográficas (3)
        'elevacion',
        'pendiente',
        'orientacion',
        
        # Vegetación (2)
        'ndvi',
        'tipo_bosque',
        
        # Temporales (2)
        'mes',
        'dia_año',
        
        # Target
        'ventana'
    ]
    
    # Verificar que todas existen
    missing = [f for f in selected_features if f not in df.columns]
    if missing:
        logger.error(f"  ✗ Features faltantes: {missing}")
        raise ValueError(f"Features faltantes: {missing}")
    
    df_final = df[selected_features].copy()
    
    logger.info(f"  ✓ Seleccionadas {len(selected_features)-1} features + target")
    
    return df_final


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia dataset: elimina NaN, outliers, duplicados
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        DataFrame limpio
    """
    logger.info("Limpiando dataset...")
    
    initial_rows = len(df)
    
    # Eliminar NaN
    df = df.dropna()
    logger.info(f"  Eliminados {initial_rows - len(df)} registros con NaN")
    
    # Eliminar outliers extremos en FWI (>100)
    df = df[df['fwi'] <= 100]
    
    # Eliminar temperaturas imposibles
    df = df[(df['temperatura'] >= -20) & (df['temperatura'] <= 50)]
    
    # Eliminar duplicados
    df = df.drop_duplicates()
    
    final_rows = len(df)
    logger.info(f"  ✓ Dataset limpio: {final_rows} registros ({initial_rows - final_rows} eliminados)")
    
    return df


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta pipeline completo de feature engineering"""
    
    logger.info("=" * 70)
    logger.info("IgniWise - Feature Engineering")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Cargar datos
    fire_df = load_fire_data()
    geo_df = load_geodata()
    
    # 2. Generar/cargar weather features
    fire_df = generate_synthetic_weather(fire_df)
    
    # 3. Calcular FWI
    fire_df = calculate_fwi_features(fire_df)
    
    # 4. Añadir topografía
    fire_df = add_topographic_features(fire_df, geo_df)
    
    # 5. Añadir vegetación
    fire_df = add_vegetation_features(fire_df)
    
    # 6. Añadir temporales
    fire_df = add_temporal_features(fire_df)
    
    # 7. Crear target
    fire_df = create_target_variable(fire_df)
    
    # 8. Seleccionar features finales
    df_final = select_final_features(fire_df)
    
    # 9. Limpiar
    df_final = clean_dataset(df_final)
    
    # 10. Guardar
    output_file = DATA_PROCESSED / 'training_data.csv'
    df_final.to_csv(output_file, index=False)
    
    logger.info("=" * 70)
    logger.info("✓ FEATURE ENGINEERING COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"Dataset final: {len(df_final)} registros, {len(df_final.columns)} columnas")
    logger.info(f"Archivo guardado: {output_file}")
    logger.info(f"Tamaño: {output_file.stat().st_size / (1024*1024):.1f} MB")
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
