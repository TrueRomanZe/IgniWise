"""
IgniWise - Descarga de Datos MITECO
Descarga datos históricos de incendios forestales del Ministerio para la 
Transición Ecológica de España (MITECO)

Duración: 30-40 minutos
Output: data/raw/incendios_miteco/incendios_*.csv
"""

import requests
import pandas as pd
from pathlib import Path
import time
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import DATA_RAW
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'download_miteco')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URLs de MITECO (datos públicos)
# NOTA: Estas URLs son ejemplos. MITECO publica datos en formato Excel
# que deben ser descargados manualmente de:
# https://www.miteco.gob.es/es/biodiversidad/estadisticas/

MITECO_BASE_URL = "https://www.miteco.gob.es/es/biodiversidad/estadisticas/"

# Años disponibles
YEARS = list(range(2001, 2025))  # 2001-2024

# Columnas esperadas en archivos MITECO
EXPECTED_COLUMNS = [
    'fecha', 'provincia', 'municipio', 'causa', 
    'superficie_total', 'superficie_arbolada', 'superficie_rasa',
    'latitud', 'longitud', 'hora_inicio', 'hora_control'
]

# ============================================================================
# FUNCIONES DE DESCARGA
# ============================================================================

def download_miteco_year(year: int, output_dir: Path) -> bool:
    """
    Descarga datos de incendios de MITECO para un año específico
    
    IMPORTANTE: En la realidad, MITECO publica archivos Excel que deben
    descargarse manualmente. Este script simula el proceso y muestra
    cómo procesarlos una vez descargados.
    
    Args:
        year: Año a descargar (2001-2024)
        output_dir: Carpeta donde guardar los datos
        
    Returns:
        True si descarga exitosa, False si error
    """
    logger.info(f"Procesando datos de incendios para año {year}...")
    
    # En producción real, estos archivos se descargan manualmente de MITECO
    # y se colocan en data/raw/incendios_miteco/manual_downloads/
    
    manual_file = output_dir / 'manual_downloads' / f'incendios_{year}.xlsx'
    
    if manual_file.exists():
        logger.info(f"  ✓ Archivo encontrado: {manual_file.name}")
        try:
            # Leer Excel de MITECO
            df = pd.read_excel(manual_file, sheet_name=0)
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Guardar como CSV procesado
            output_csv = output_dir / f'incendios_{year}.csv'
            df.to_csv(output_csv, index=False, encoding='utf-8')
            
            logger.info(f"  ✓ Procesado: {len(df)} registros guardados en {output_csv.name}")
            return True
            
        except Exception as e:
            logger.error(f"  ✗ Error procesando {manual_file.name}: {e}")
            return False
    else:
        logger.warning(f"  ⚠ Archivo no encontrado: {manual_file}")
        logger.info(f"    Descargar manualmente de: {MITECO_BASE_URL}")
        return False


def generate_synthetic_data(year: int, output_dir: Path, n_records: int = 500):
    """
    Genera datos sintéticos para desarrollo/testing
    
    SOLO PARA DESARROLLO: En producción, usar datos reales de MITECO
    
    Args:
        year: Año a simular
        output_dir: Carpeta donde guardar
        n_records: Número de registros a generar
    """
    import numpy as np
    
    logger.warning(f"⚠️  GENERANDO DATOS SINTÉTICOS para {year} (SOLO DESARROLLO)")
    
    # Provincias españolas
    provincias = [
        "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza",
        "Málaga", "Murcia", "Las Palmas", "Vizcaya", "Alicante",
        "Cádiz", "A Coruña", "Asturias", "Granada", "Córdoba"
    ]
    
    # Generar datos aleatorios realistas
    np.random.seed(year)  # Reproducibilidad
    
    data = {
        'fecha': pd.date_range(f'{year}-01-01', f'{year}-12-31', periods=n_records),
        'provincia': np.random.choice(provincias, n_records),
        'municipio': [f'Municipio_{i}' for i in range(n_records)],
        'causa': np.random.choice(['Rayo', 'Negligencia', 'Intencionado', 'Desconocida'], n_records),
        'superficie_total': np.random.exponential(10, n_records),  # hectáreas
        'superficie_arbolada': np.random.exponential(5, n_records),
        'superficie_rasa': np.random.exponential(3, n_records),
        'latitud': np.random.uniform(36.0, 43.5, n_records),  # España peninsular
        'longitud': np.random.uniform(-9.0, 3.5, n_records),
        'hora_inicio': np.random.randint(0, 24, n_records),
        'hora_control': np.random.randint(1, 48, n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Guardar
    output_csv = output_dir / f'incendios_{year}_SYNTHETIC.csv'
    df.to_csv(output_csv, index=False, encoding='utf-8')
    
    logger.info(f"  ✓ Generados {len(df)} registros sintéticos en {output_csv.name}")
    return True


def merge_all_years(input_dir: Path, output_file: Path):
    """
    Combina todos los archivos CSV anuales en un dataset único
    
    Args:
        input_dir: Carpeta con CSVs anuales
        output_file: Archivo de salida combinado
    """
    logger.info("Combinando todos los años en dataset único...")
    
    all_files = sorted(input_dir.glob('incendios_*.csv'))
    
    if not all_files:
        logger.error("  ✗ No se encontraron archivos CSV para combinar")
        return False
    
    logger.info(f"  Encontrados {len(all_files)} archivos")
    
    # Leer y combinar
    dfs = []
    total_records = 0
    
    for file in all_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
            dfs.append(df)
            total_records += len(df)
            logger.info(f"    ✓ {file.name}: {len(df)} registros")
        except Exception as e:
            logger.error(f"    ✗ Error leyendo {file.name}: {e}")
    
    if not dfs:
        logger.error("  ✗ No se pudo leer ningún archivo")
        return False
    
    # Combinar
    combined = pd.concat(dfs, ignore_index=True)
    
    # Guardar
    combined.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"  ✓ Dataset combinado: {len(combined)} registros totales")
    logger.info(f"  ✓ Guardado en: {output_file}")
    
    return True


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta el proceso completo de descarga de datos MITECO"""
    
    logger.info("=" * 70)
    logger.info("IgniWise - Descarga de Datos MITECO")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear carpetas
    output_dir = DATA_RAW / 'incendios_miteco'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manual_downloads = output_dir / 'manual_downloads'
    manual_downloads.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Carpeta de salida: {output_dir}")
    
    # Mensaje importante sobre descarga manual
    logger.info("")
    logger.info("=" * 70)
    logger.info("IMPORTANTE: Descarga Manual Requerida")
    logger.info("=" * 70)
    logger.info("Los datos de MITECO deben descargarse manualmente desde:")
    logger.info("https://www.miteco.gob.es/es/biodiversidad/estadisticas/")
    logger.info("")
    logger.info("Pasos:")
    logger.info("1. Descargar archivos Excel de incendios (2001-2024)")
    logger.info(f"2. Colocarlos en: {manual_downloads}")
    logger.info("3. Nombrar como: incendios_2001.xlsx, incendios_2002.xlsx, etc.")
    logger.info("4. Ejecutar este script para procesarlos")
    logger.info("=" * 70)
    logger.info("")
    
    # Verificar si hay archivos manuales
    manual_files = list(manual_downloads.glob('*.xlsx'))
    
    if manual_files:
        logger.info(f"✓ Encontrados {len(manual_files)} archivos Excel para procesar")
        
        # Procesar cada año
        success_count = 0
        for year in YEARS:
            if download_miteco_year(year, output_dir):
                success_count += 1
            time.sleep(0.5)  # Pequeña pausa
        
        logger.info(f"Procesados exitosamente: {success_count}/{len(YEARS)} años")
        
    else:
        logger.warning("⚠️  No se encontraron archivos manuales")
        logger.info("Generando datos sintéticos para desarrollo...")
        
        # Generar datos sintéticos para cada año
        for year in YEARS:
            generate_synthetic_data(year, output_dir, n_records=500)
            time.sleep(0.1)
    
    # Combinar todos los años
    output_combined = output_dir / 'incendios_completo.csv'
    merge_all_years(output_dir, output_combined)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ PROCESO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Dataset final: {output_combined}")
    

if __name__ == "__main__":
    main()
