"""
IgniWise - Configuración Central
Gestiona variables de entorno, rutas y parámetros del sistema
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ============================================================================
# RUTAS DEL PROYECTO
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_RAW = DATA_DIR / 'raw'
DATA_PROCESSED = DATA_DIR / 'processed'
DATA_PREDICTIONS = DATA_DIR / 'predictions'

MODELS_DIR = PROJECT_ROOT / 'models'
WEB_DIR = PROJECT_ROOT / 'web'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Crear carpetas si no existen
for directory in [DATA_RAW, DATA_PROCESSED, DATA_PREDICTIONS, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# API KEYS
# ============================================================================

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
AEMET_API_KEY = os.getenv('AEMET_API_KEY')

if not OPENWEATHER_API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY no encontrada. "
        "Configura tu .env con la API key de OpenWeatherMap"
    )

# ============================================================================
# ZENODO URLS (Dataset publicado)
# ============================================================================

ZENODO_DATASET_URL = os.getenv(
    'ZENODO_DATASET_URL',
    'https://zenodo.org/record/XXXXXXX/files/training_data.csv'
)

ZENODO_MODEL_URL = os.getenv(
    'ZENODO_MODEL_URL',
    'https://zenodo.org/record/XXXXXXX/files/random_forest_v1.pkl'
)

ZENODO_GEODATA_URL = os.getenv(
    'ZENODO_GEODATA_URL',
    'https://zenodo.org/record/XXXXXXX/files/provincias_geo.geojson'
)

# ============================================================================
# PARÁMETROS DEL MODELO
# ============================================================================

# Random Forest
RF_N_ESTIMATORS = int(os.getenv('RF_N_ESTIMATORS', 200))
RF_MAX_DEPTH = int(os.getenv('RF_MAX_DEPTH', 15))
RF_MIN_SAMPLES_SPLIT = 20
RF_MIN_SAMPLES_LEAF = 10
RF_MAX_FEATURES = 'sqrt'
RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))

# Training
TRAIN_TEST_SPLIT = 0.3  # 70% train, 30% test
CV_FOLDS = 5

# ============================================================================
# PARÁMETROS DE PREDICCIÓN
# ============================================================================

FORECAST_DAYS = int(os.getenv('FORECAST_DAYS', 7))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.75))

# Clasificación de ventanas
VENTANA_SEGURA_MIN_SCORE = 70
VENTANA_MARGINAL_MIN_SCORE = 40

# ============================================================================
# CONFIGURACIÓN DE AUTOMATIZACIÓN
# ============================================================================

UPDATE_FREQUENCY_HOURS = int(os.getenv('UPDATE_FREQUENCY_HOURS', 6))
RETRAIN_FREQUENCY_HOURS = int(os.getenv('RETRAIN_FREQUENCY_HOURS', 24))

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# PROVINCIAS ESPAÑOLAS (para predicciones)
# ============================================================================

PROVINCIAS_ESPANA = [
    "A Coruña", "Álava", "Albacete", "Alicante", "Almería", "Asturias",
    "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", "Cádiz",
    "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona",
    "Granada", "Guadalajara", "Gipuzkoa", "Huelva", "Huesca", "Jaén",
    "León", "Lleida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra",
    "Ourense", "Palencia", "Las Palmas", "Pontevedra", "La Rioja",
    "Salamanca", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel",
    "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza"
]

# ============================================================================
# COLORES PARA VISUALIZACIÓN
# ============================================================================

COLOR_SEGURA = '#10b981'      # Verde
COLOR_MARGINAL = '#f59e0b'    # Amarillo/Naranja
COLOR_PELIGROSA = '#ef4444'   # Rojo
COLOR_SIN_DATOS = '#9ca3af'   # Gris

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_model_path(version='v1'):
    """Obtiene la ruta del modelo según versión"""
    return MODELS_DIR / f'random_forest_{version}.pkl'

def get_predictions_path(current=True):
    """Obtiene la ruta del archivo de predicciones"""
    if current:
        return DATA_PREDICTIONS / 'current_windows.json'
    else:
        return DATA_PREDICTIONS / 'forecast_7days.json'

def get_dataset_path(processed=True):
    """Obtiene la ruta del dataset"""
    if processed:
        return DATA_PROCESSED / 'training_data.csv'
    else:
        return DATA_RAW / 'incendios_miteco' / 'incendios_completo.csv'
