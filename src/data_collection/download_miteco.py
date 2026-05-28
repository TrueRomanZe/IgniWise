"""
IgniWise - Descarga de Datos de Incendios Históricos
======================================================

Descarga y procesa datos históricos de incendios forestales del MITECO / IEPNB.

Fuentes disponibles:
  1. IEPNB (recomendada): datos en formato TTL/RDF (1983-2015), ~287.000 registros
     URL: https://datos.iepnb.es/datasets/mfe50.tgz (incluye geometrías post-2005)
  2. MITECO: estadísticas en formato Excel (descarga manual)
     URL: https://www.miteco.gob.es/es/biodiversidad/estadisticas/

Período disponible: 1983-2015
Output: data/raw/incendios_miteco/incendios_completo.csv
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

# Fuente principal: IEPNB (TTL/RDF format, 1983-2015)
IEPNB_BASE_URL = "https://datos.iepnb.es"
IEPNB_DATASET_URL = "https://datos.iepnb.es/datasets/mfe50.tgz"

# Fuente alternativa: MITECO (Excel, descarga manual)
MITECO_BASE_URL = "https://www.miteco.gob.es/es/biodiversidad/estadisticas/"

# Período disponible en fuentes públicas
YEAR_START = 1983
YEAR_END = 2015
YEARS = list(range(YEAR_START, YEAR_END + 1))

# Columnas esperadas tras procesamiento
EXPECTED_COLUMNS = [
    'fecha', 'provincia', 'municipio', 'causa',
    'superficie_total', 'superficie_arbolada', 'superficie_rasa',
    'latitud', 'longitud'
]

# ============================================================================
# FUNCIONES DE PROCESAMIENTO TTL (IEPNB)
# ============================================================================

def parse_ttl_to_csv(ttl_file: Path, output_dir: Path) -> bool:
    """
    Parsea el archivo TTL/RDF de IEPNB y extrae los datos relevantes a CSV.

    El formato TTL contiene registros con:
    - IdIncendio (AAAA + código)
    - Provincia (via sfWithin)
    - Municipio (código INE)
    - Año (via wasMemberOf)
    - Superficies: arbolada, no arbolada, agrícola, forestal (hectáreas)
    - Geometría del punto de origen (solo post-2005, en Spain_geom.ttl)

    Args:
        ttl_file: Ruta al archivo Spain_nogeom.ttl o Spain_geom.ttl
        output_dir: Carpeta de salida para el CSV

    Returns:
        True si procesado correctamente
    """
    logger.info(f"Parseando TTL: {ttl_file.name}")
    logger.info("Este proceso puede tardar varios minutos por el tamaño del archivo...")

    try:
        records = []
        current_record = {}

        with open(ttl_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Detectar inicio de registro de incendio
                if 'IncendioForestal' in line and 'ColeccionIncendiosForestalesEspaña' in line:
                    if current_record:
                        records.append(current_record)
                    current_record = {}

                # Extraer IdIncendio → año implícito en los primeros 4 dígitos
                if 'IdIncendio' in line:
                    id_val = line.split('"')[1] if '"' in line else ''
                    current_record['id_incendio'] = id_val
                    if len(id_val) >= 4:
                        current_record['año'] = int(id_val[:4])

                # Extraer provincia
                if 'sfWithin' in line and 'Provincia' in line:
                    prov = line.split('Provincia/')[-1].rstrip('>,')
                    current_record['provincia'] = prov.replace('%C3%B3', 'ó').replace(
                        '%C3%A1', 'á').replace('%C3%AD', 'í')

                # Extraer superficie forestal total
                if 'tieneSuperficieForestal' in line and 'SuperficieForestal/' in line:
                    try:
                        val = float(line.split('SuperficieForestal/')[-1].rstrip('> ;.'))
                        current_record['superficie_forestal'] = val
                    except ValueError:
                        pass

                # Extraer superficie arbolada
                if 'tieneSuperficieArbolada' in line and 'SuperficieArbolada/' in line:
                    try:
                        val = float(line.split('SuperficieArbolada/')[-1].rstrip('> ;.'))
                        current_record['superficie_arbolada'] = val
                    except ValueError:
                        pass

        # Añadir último registro
        if current_record:
            records.append(current_record)

        df = pd.DataFrame(records)

        if df.empty:
            logger.warning("  ⚠ No se extrajeron registros del archivo TTL")
            return False

        # Guardar CSV
        output_csv = output_dir / 'incendios_completo.csv'
        df.to_csv(output_csv, index=False, encoding='utf-8')

        logger.info(f"  ✓ Extraídos {len(df):,} registros")
        logger.info(f"  ✓ Guardado en: {output_csv}")
        logger.info(f"  Años: {df['año'].min() if 'año' in df else 'N/A'} - "
                    f"{df['año'].max() if 'año' in df else 'N/A'}")
        return True

    except Exception as e:
        logger.error(f"  ✗ Error parseando TTL: {e}")
        return False


# ============================================================================
# FUNCIONES DE PROCESAMIENTO EXCEL (MITECO)
# ============================================================================

def process_miteco_excel(excel_file: Path, output_dir: Path) -> bool:
    """
    Procesa un archivo Excel de MITECO descargado manualmente.

    Para descargar: https://www.miteco.gob.es/es/biodiversidad/estadisticas/

    Args:
        excel_file: Ruta al archivo Excel de MITECO
        output_dir: Carpeta de salida

    Returns:
        True si procesado correctamente
    """
    logger.info(f"Procesando Excel MITECO: {excel_file.name}")

    try:
        df = pd.read_excel(excel_file, sheet_name=0)
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        output_csv = output_dir / f'incendios_{excel_file.stem}.csv'
        df.to_csv(output_csv, index=False, encoding='utf-8')

        logger.info(f"  ✓ Procesadas {len(df):,} filas → {output_csv.name}")
        return True

    except Exception as e:
        logger.error(f"  ✗ Error procesando {excel_file.name}: {e}")
        return False


def merge_all_csvs(input_dir: Path, output_file: Path) -> bool:
    """Combina todos los CSVs anuales en un dataset único."""
    logger.info("Combinando archivos CSV en dataset único...")

    all_files = sorted(input_dir.glob('incendios_*.csv'))

    if not all_files:
        logger.error("  ✗ No se encontraron archivos CSV para combinar")
        return False

    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
            dfs.append(df)
            logger.info(f"    ✓ {file.name}: {len(df):,} registros")
        except Exception as e:
            logger.error(f"    ✗ {file.name}: {e}")

    if not dfs:
        return False

    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(output_file, index=False, encoding='utf-8')

    logger.info(f"  ✓ Total combinado: {len(combined):,} registros")
    logger.info(f"  ✓ Guardado en: {output_file}")
    return True


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta el proceso de descarga y procesamiento de datos de incendios."""

    logger.info("=" * 70)
    logger.info("IgniWise - Datos de Incendios Históricos (MITECO / IEPNB)")
    logger.info(f"Período: {YEAR_START}-{YEAR_END}")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    output_dir = DATA_RAW / 'incendios_miteco'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("")
    logger.info("=" * 70)
    logger.info("FUENTES DISPONIBLES")
    logger.info("=" * 70)
    logger.info("")
    logger.info("OPCIÓN 1 (Recomendada) — IEPNB, formato TTL/RDF:")
    logger.info(f"  URL: {IEPNB_DATASET_URL}")
    logger.info("  Contiene: ~287.000 incendios (1983-2015) con geometrías")
    logger.info("  Pasos:")
    logger.info("    1. Descargar y descomprimir el .tgz")
    logger.info("    2. Colocar Spain_nogeom.ttl en data/raw/incendios_miteco/")
    logger.info("    3. Ejecutar: python -c \"from src.data_collection.download_miteco")
    logger.info("       import parse_ttl_to_csv; ...\"")
    logger.info("")
    logger.info("OPCIÓN 2 — MITECO, formato Excel (descarga manual):")
    logger.info(f"  URL: {MITECO_BASE_URL}")
    logger.info("  Pasos:")
    logger.info("    1. Descargar archivos Excel de incendios")
    logger.info(f"    2. Colocarlos en: {output_dir}/")
    logger.info("    3. Este script los procesará automáticamente")
    logger.info("=" * 70)
    logger.info("")

    # Verificar si hay archivos para procesar
    ttl_files = list(output_dir.glob('*.ttl'))
    excel_files = list(output_dir.glob('*.xlsx')) + list(output_dir.glob('*.xls'))

    if ttl_files:
        logger.info(f"✓ Encontrado archivo TTL: {ttl_files[0].name}")
        parse_ttl_to_csv(ttl_files[0], output_dir)

    elif excel_files:
        logger.info(f"✓ Encontrados {len(excel_files)} archivos Excel")
        for excel_file in excel_files:
            process_miteco_excel(excel_file, output_dir)

        output_combined = output_dir / 'incendios_completo.csv'
        merge_all_csvs(output_dir, output_combined)

    else:
        logger.warning("⚠️  No se encontraron archivos de datos.")
        logger.info("  Consulta las instrucciones de descarga arriba.")

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
