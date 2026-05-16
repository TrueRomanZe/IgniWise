"""
IgniWise - Feature Engineering v2
Procesa datos de incendios y meteorología para crear dataset de Machine Learning

CAMBIOS v2 respecto a v1:
- add_topographic_features: usa pendiente y orientacion REALES de provincias_geo.geojson
  (extraídas de Copernicus DEM GLO-30 via opentopodata API)
- add_vegetation_features: usa ndvi y tipo_bosque REALES de provincias_geo.geojson
  (NDVI de Sentinel-2 via Google Earth Engine; tipo_bosque de CORINE Land Cover 2018)
- Se elimina toda generación aleatoria de features estáticas provinciales

Input:
  - data/raw/incendios_miteco/incendios_completo.csv
  - data/processed/provincias_geo.geojson  ← ahora incluye pendiente, orientacion, ndvi, tipo_bosque

Output:
  - data/processed/training_data.csv
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from datetime import datetime
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

# Factores de corrección estacional del NDVI para España mediterránea
# Basado en: Huete et al. (2002), Remote Sensing of Environment;
#            García-Haro et al. (2005), Remote Sensing of Environment
# El valor de GEE es la mediana anual; este factor lo ajusta por mes
NDVI_SEASONAL_FACTOR = {
    1: 0.85,   # Enero   - invierno, vegetación mínima
    2: 0.87,   # Febrero - inicio recuperación
    3: 0.95,   # Marzo   - primavera temprana
    4: 1.10,   # Abril   - pico primaveral mediterráneo
    5: 1.15,   # Mayo    - máximo primaveral
    6: 1.05,   # Junio   - inicio estrés hídrico
    7: 0.92,   # Julio   - sequía estival
    8: 0.88,   # Agosto  - mínimo veraniego
    9: 0.90,   # Septiembre - inicio recuperación otoñal
    10: 0.93,  # Octubre - recuperación otoñal
    11: 0.88,  # Noviembre - descenso invernal
    12: 0.85   # Diciembre - invierno
}

# Valores por defecto (usados si la provincia no tiene datos en el geojson)
DEFAULT_ELEVACION  = 660.0   # Elevación media España (m)
DEFAULT_PENDIENTE  = 8.0     # Pendiente media España (grados)
DEFAULT_ORIENTACION = 180.0  # Sur (orientación más común en España)
DEFAULT_NDVI       = 0.55    # NDVI típico España (primavera/otoño)
DEFAULT_TIPO_BOSQUE = 1      # Encinar (más común en España)


# ============================================================================
# FUNCIONES DE CARGA
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
    """
    Carga geometrías provinciales con features reales.

    A partir de v2, provincias_geo.geojson contiene también:
    - pendiente:   pendiente media provincial (grados), Copernicus DEM GLO-30
    - orientacion: orientación predominante (grados), Copernicus DEM GLO-30
    - ndvi:        NDVI anual mediano, Sentinel-2 via Google Earth Engine
    - tipo_bosque: clase de cobertura forestal dominante, CORINE Land Cover 2018
    """
    logger.info("Cargando datos geográficos provinciales (v2 con features reales)...")

    geo_file = DATA_PROCESSED / 'provincias_geo.geojson'
    if not geo_file.exists():
        raise FileNotFoundError(f"No se encontró: {geo_file}")

    gdf = gpd.read_file(geo_file)
    logger.info(f"  ✓ Cargadas {len(gdf)} provincias")

    # Verificar que las columnas reales existen
    real_cols = ['pendiente', 'orientacion', 'ndvi', 'tipo_bosque']
    missing = [c for c in real_cols if c not in gdf.columns]
    if missing:
        logger.warning(
            f"  ⚠ Columnas no encontradas en geojson: {missing}\n"
            "  Asegúrate de haber ejecutado el Colab 'colab_real_features.ipynb'\n"
            "  y de haber subido el archivo resultante a data/processed/"
        )
    else:
        logger.info("  ✓ Features reales confirmadas: pendiente, orientacion, ndvi, tipo_bosque")

    return gdf


# ============================================================================
# FUNCIONES DE FEATURE ENGINEERING
# ============================================================================

def generate_synthetic_weather(fire_df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera datos meteorológicos sintéticos para desarrollo.
    EN PRODUCCIÓN: estos datos vendrían de OpenWeatherMap/AEMET históricos.
    """
    logger.info("Generando datos meteorológicos (sintéticos para desarrollo)...")

    np.random.seed(42)
    n = len(fire_df)
    month = fire_df['fecha'].dt.month

    temp_base = {
        1: 8, 2: 10, 3: 14, 4: 16, 5: 20, 6: 25,
        7: 29, 8: 28, 9: 24, 10: 18, 11: 12, 12: 9
    }
    fire_df['temperatura'] = month.map(temp_base) + np.random.normal(0, 5, n)
    fire_df['humedad'] = 100 - fire_df['temperatura'] * 1.5 + np.random.normal(0, 15, n)
    fire_df['humedad'] = fire_df['humedad'].clip(10, 95)
    fire_df['viento_velocidad'] = np.random.exponential(15, n) + month * 0.5
    fire_df['viento_velocidad'] = fire_df['viento_velocidad'].clip(0, 80)
    fire_df['viento_direccion'] = np.random.uniform(0, 360, n)
    precip_prob = (12 - month) / 12
    fire_df['precip_24h'] = np.where(
        np.random.random(n) < precip_prob,
        np.random.exponential(5, n), 0
    )
    fire_df['dias_sin_lluvia'] = np.random.exponential(7, n).astype(int).clip(0, 60)
    fire_df['precip_7d'] = np.random.exponential(10, n)
    fire_df['precip_30d'] = np.random.exponential(30, n)
    fire_df['temp_max_3d'] = fire_df['temperatura'] + np.random.uniform(2, 8, n)

    logger.info("  ✓ Variables meteorológicas generadas")
    return fire_df


def calculate_fwi_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula índices FWI para cada registro"""
    logger.info("Calculando índices FWI...")
    fwi_results = []
    for idx, row in df.iterrows():
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
    fwi_df = pd.DataFrame(fwi_results)
    df = pd.concat([df.reset_index(drop=True), fwi_df], axis=1)
    logger.info("  ✓ Índices FWI calculados")
    return df


def add_topographic_features(df: pd.DataFrame, geo_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Añade features topográficas reales por provincia.

    v2: pendiente y orientacion provienen de Copernicus DEM GLO-30
    (extraídas en colab_real_features.ipynb via opentopodata API).
    Ya no se generan aleatoriamente.
    """
    logger.info("Añadiendo features topográficas REALES (Copernicus DEM GLO-30)...")

    elevation_map  = dict(zip(geo_df['nombre'], geo_df['elevacion']))
    pendiente_map  = dict(zip(geo_df['nombre'], geo_df.get('pendiente',  pd.Series())))
    orientacion_map = dict(zip(geo_df['nombre'], geo_df.get('orientacion', pd.Series())))

    df['elevacion']   = df['provincia'].map(elevation_map).fillna(DEFAULT_ELEVACION)
    df['pendiente']   = df['provincia'].map(pendiente_map).fillna(DEFAULT_PENDIENTE)
    df['orientacion'] = df['provincia'].map(orientacion_map).fillna(DEFAULT_ORIENTACION)

    logger.info("  ✓ Elevación, pendiente y orientación asignadas desde geojson")
    logger.info(f"    Pendiente media: {df['pendiente'].mean():.1f}°  "
                f"(rango: {df['pendiente'].min():.1f}° – {df['pendiente'].max():.1f}°)")
    return df


def add_vegetation_features(df: pd.DataFrame, geo_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Añade features de vegetación reales por provincia.

    v2:
    - ndvi: mediana anual de Sentinel-2 (GEE) + factor de corrección estacional
    - tipo_bosque: clase dominante de CORINE Land Cover 2018
      Codificación: 0=pinar, 1=encinar/frondosas, 2=matorral, 3=mixto

    Fuentes:
    - NDVI: Copernicus Sentinel-2 Level-2A, 2023-2024, via Google Earth Engine
    - Cobertura: CORINE Land Cover 2018 (Copernicus / CNIG)
    """
    logger.info("Añadiendo features de vegetación REALES (Sentinel-2 + CORINE 2018)...")

    ndvi_map       = dict(zip(geo_df['nombre'], geo_df.get('ndvi',        pd.Series())))
    tipo_bosque_map = dict(zip(geo_df['nombre'], geo_df.get('tipo_bosque', pd.Series())))

    # NDVI base anual por provincia
    df['ndvi_base'] = df['provincia'].map(ndvi_map).fillna(DEFAULT_NDVI)

    # Aplicar variación estacional (Huete et al., 2002; García-Haro et al., 2005)
    df['ndvi'] = df.apply(
        lambda row: row['ndvi_base'] * NDVI_SEASONAL_FACTOR.get(row['fecha'].month, 1.0),
        axis=1
    )
    df['ndvi'] = df['ndvi'].clip(0.0, 1.0)
    df.drop(columns=['ndvi_base'], inplace=True)

    # Tipo de bosque real desde CORINE
    df['tipo_bosque'] = (
        df['provincia'].map(tipo_bosque_map).fillna(DEFAULT_TIPO_BOSQUE).astype(int)
    )

    logger.info(f"  ✓ NDVI asignado (media dataset: {df['ndvi'].mean():.3f})")
    logger.info(f"  ✓ tipo_bosque: {dict(df['tipo_bosque'].value_counts().sort_index())}")
    return df


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Añade features temporales"""
    logger.info("Añadiendo features temporales...")
    df['mes']      = df['fecha'].dt.month
    df['dia_año']  = df['fecha'].dt.dayofyear
    df['estacion'] = pd.cut(df['mes'], bins=[0, 3, 6, 9, 12], labels=[0, 1, 2, 3]).astype(int)
    df['dia_semana']    = df['fecha'].dt.dayofweek
    df['es_fin_semana'] = (df['dia_semana'] >= 5).astype(int)
    logger.info("  ✓ Features temporales añadidas")
    return df


def create_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Crea variable target: clasificación de ventana de quema"""
    logger.info("Creando variable target (ventana)...")
    segura = (
        (df['temperatura'] >= VENTANA_SEGURA_THRESHOLDS['temp_min']) &
        (df['temperatura'] <= VENTANA_SEGURA_THRESHOLDS['temp_max']) &
        (df['humedad']     >= VENTANA_SEGURA_THRESHOLDS['humedad_min']) &
        (df['viento_velocidad'] <= VENTANA_SEGURA_THRESHOLDS['viento_max']) &
        (df['dias_sin_lluvia']  <= VENTANA_SEGURA_THRESHOLDS['dias_sin_lluvia_max']) &
        (df['fwi'] <= VENTANA_SEGURA_THRESHOLDS['fwi_max'])
    )
    marginal = (
        (df['temperatura'] >= VENTANA_MARGINAL_THRESHOLDS['temp_min']) &
        (df['temperatura'] <= VENTANA_MARGINAL_THRESHOLDS['temp_max']) &
        (df['humedad']     >= VENTANA_MARGINAL_THRESHOLDS['humedad_min']) &
        (df['viento_velocidad'] <= VENTANA_MARGINAL_THRESHOLDS['viento_max']) &
        (df['dias_sin_lluvia']  <= VENTANA_MARGINAL_THRESHOLDS['dias_sin_lluvia_max']) &
        (df['fwi'] <= VENTANA_MARGINAL_THRESHOLDS['fwi_max'])
    )
    df['ventana'] = 2
    df.loc[marginal, 'ventana'] = 1
    df.loc[segura,   'ventana'] = 0
    counts = df['ventana'].value_counts().sort_index()
    logger.info("  ✓ Variable target creada:")
    logger.info(f"    SEGURA (0):     {counts.get(0,0):5d} ({counts.get(0,0)/len(df)*100:5.1f}%)")
    logger.info(f"    MARGINAL (1):   {counts.get(1,0):5d} ({counts.get(1,0)/len(df)*100:5.1f}%)")
    logger.info(f"    PELIGROSA (2):  {counts.get(2,0):5d} ({counts.get(2,0)/len(df)*100:5.1f}%)")
    return df


def select_final_features(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona las 20 features finales para el modelo"""
    logger.info("Seleccionando features finales...")
    selected_features = [
        'temperatura', 'humedad', 'viento_velocidad', 'viento_direccion', 'precip_24h',
        'dias_sin_lluvia', 'precip_7d', 'precip_30d', 'temp_max_3d',
        'fwi', 'ffmc', 'dmc', 'dc',
        'elevacion', 'pendiente', 'orientacion',
        'ndvi', 'tipo_bosque',
        'mes', 'dia_año',
        'ventana'
    ]
    missing = [f for f in selected_features if f not in df.columns]
    if missing:
        raise ValueError(f"Features faltantes: {missing}")
    df_final = df[selected_features].copy()
    logger.info(f"  ✓ Seleccionadas {len(selected_features)-1} features + target")
    return df_final


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia dataset: elimina NaN, outliers y duplicados"""
    logger.info("Limpiando dataset...")
    initial_rows = len(df)
    df = df.dropna()
    df = df[df['fwi'] <= 100]
    df = df[(df['temperatura'] >= -20) & (df['temperatura'] <= 50)]
    df = df.drop_duplicates()
    logger.info(f"  ✓ Dataset limpio: {len(df)} registros ({initial_rows - len(df)} eliminados)")
    return df


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta pipeline completo de feature engineering"""
    logger.info("=" * 70)
    logger.info("IgniWise - Feature Engineering v2 (datos reales)")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Cargar datos
    fire_df = load_fire_data()
    geo_df  = load_geodata()

    # 2. Weather features (sintéticos - en producción vendrían de AEMET/OpenWeather)
    fire_df = generate_synthetic_weather(fire_df)

    # 3. Índices FWI
    fire_df = calculate_fwi_features(fire_df)

    # 4. Topografía REAL (Copernicus DEM GLO-30)
    fire_df = add_topographic_features(fire_df, geo_df)

    # 5. Vegetación REAL (Sentinel-2 + CORINE 2018)
    fire_df = add_vegetation_features(fire_df, geo_df)

    # 6. Temporales
    fire_df = add_temporal_features(fire_df)

    # 7. Target
    fire_df = create_target_variable(fire_df)

    # 8. Selección final
    df_final = select_final_features(fire_df)

    # 9. Limpieza
    df_final = clean_dataset(df_final)

    # 10. Guardar
    output_file = DATA_PROCESSED / 'training_data.csv'
    df_final.to_csv(output_file, index=False)

    logger.info("=" * 70)
    logger.info("✓ FEATURE ENGINEERING v2 COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"Dataset final: {len(df_final)} registros, {len(df_final.columns)} columnas")
    logger.info(f"Archivo: {output_file}")
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
