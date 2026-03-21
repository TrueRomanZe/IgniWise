"""
IgniWise - Cálculo del Fire Weather Index (FWI)
Implementación del Sistema Canadiense de Índices de Peligro de Incendio

Referencia: Van Wagner, C.E. 1987. Development and structure of the 
Canadian Forest Fire Weather Index System. Forestry Technical Report 35.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# CONSTANTES DEL SISTEMA FWI
# ============================================================================

# Valores iniciales para primavera (1 de abril)
INITIAL_FFMC = 85.0
INITIAL_DMC = 6.0
INITIAL_DC = 15.0

# Factores de ajuste por latitud (España: ~36-43°N)
DAY_LENGTH_FACTORS = {
    # Mes: Factor de ajuste para DC
    1: 6.5, 2: 7.5, 3: 9.0, 4: 12.8, 5: 13.9, 6: 13.9,
    7: 12.4, 8: 10.9, 9: 9.4, 10: 8.0, 11: 7.0, 12: 6.0
}

# ============================================================================
# FUNCIONES DE CÁLCULO FWI
# ============================================================================

def calculate_ffmc(temp: float, rh: float, wind: float, rain: float, ffmc_prev: float) -> float:
    """
    Fine Fuel Moisture Code (FFMC)
    Humedad de combustibles finos (hojarasca, agujas, pasto fino)
    
    Args:
        temp: Temperatura (°C)
        rh: Humedad relativa (%)
        wind: Velocidad viento (km/h)
        rain: Precipitación 24h (mm)
        ffmc_prev: FFMC del día anterior
        
    Returns:
        FFMC actualizado (0-101)
    """
    # Contenido de humedad previo
    mo = 147.2 * (101.0 - ffmc_prev) / (59.5 + ffmc_prev)
    
    # Efecto de la lluvia
    if rain > 0.5:
        rf = rain - 0.5
        
        if mo <= 150.0:
            mr = mo + 42.5 * rf * np.exp(-100.0 / (251.0 - mo)) * (1.0 - np.exp(-6.93 / rf))
        else:
            mr = mo + 42.5 * rf * np.exp(-100.0 / (251.0 - mo)) * (1.0 - np.exp(-6.93 / rf)) + \
                 0.0015 * (mo - 150.0) ** 2 * np.sqrt(rf)
        
        if mr > 250.0:
            mr = 250.0
        mo = mr
    
    # Equilibrio de humedad
    ed = 0.942 * (rh ** 0.679) + 11.0 * np.exp((rh - 100.0) / 10.0) + \
         0.18 * (21.1 - temp) * (1.0 - np.exp(-0.115 * rh))
    
    # Secado del combustible
    if mo > ed:
        ko = 0.424 * (1.0 - ((100.0 - rh) / 100.0) ** 1.7) + \
             0.0694 * np.sqrt(wind) * (1.0 - ((100.0 - rh) / 100.0) ** 8)
        kd = ko * 0.581 * np.exp(0.0365 * temp)
        m = ed + (mo - ed) * 10.0 ** (-kd)
    else:
        ew = 0.618 * (rh ** 0.753) + 10.0 * np.exp((rh - 100.0) / 10.0) + \
             0.18 * (21.1 - temp) * (1.0 - np.exp(-0.115 * rh))
        
        if mo < ew:
            kl = 0.424 * (1.0 - (rh / 100.0) ** 1.7) + \
                 0.0694 * np.sqrt(wind) * (1.0 - (rh / 100.0) ** 8)
            kw = kl * 0.581 * np.exp(0.0365 * temp)
            m = ew - (ew - mo) * 10.0 ** (-kw)
        else:
            m = mo
    
    # FFMC final
    ffmc = 59.5 * (250.0 - m) / (147.2 + m)
    
    return min(101.0, max(0.0, ffmc))


def calculate_dmc(temp: float, rh: float, rain: float, dmc_prev: float, month: int) -> float:
    """
    Duff Moisture Code (DMC)
    Humedad de combustibles de profundidad media (materia orgánica semi-descompuesta)
    
    Args:
        temp: Temperatura (°C)
        rh: Humedad relativa (%)
        rain: Precipitación 24h (mm)
        dmc_prev: DMC del día anterior
        month: Mes del año (1-12)
        
    Returns:
        DMC actualizado (0-500+)
    """
    # Efecto de la lluvia
    if rain > 1.5:
        re = 0.92 * rain - 1.27
        mo = 20.0 + np.exp(5.6348 - dmc_prev / 43.43)
        
        if dmc_prev <= 33.0:
            b = 100.0 / (0.5 + 0.3 * dmc_prev)
        elif dmc_prev <= 65.0:
            b = 14.0 - 1.3 * np.log(dmc_prev)
        else:
            b = 6.2 * np.log(dmc_prev) - 17.2
        
        mr = mo + 1000.0 * re / (48.77 + b * re)
        pr = 244.72 - 43.43 * np.log(mr - 20.0)
        
        if pr < 0.0:
            pr = 0.0
        dmc_prev = pr
    
    # Secado del combustible
    if temp > -1.1:
        d = DAY_LENGTH_FACTORS.get(month, 9.0)
        k = 1.894 * (temp + 1.1) * (100.0 - rh) * d * 1e-4
        dmc = dmc_prev + k
    else:
        dmc = dmc_prev
    
    return max(0.0, dmc)


def calculate_dc(temp: float, rain: float, dc_prev: float, month: int) -> float:
    """
    Drought Code (DC)
    Índice de sequía / humedad de combustibles profundos (troncos, raíces)
    
    Args:
        temp: Temperatura (°C)
        rain: Precipitación 24h (mm)
        dc_prev: DC del día anterior
        month: Mes del año (1-12)
        
    Returns:
        DC actualizado (0-1000+)
    """
    # Efecto de la lluvia
    if rain > 2.8:
        rd = 0.83 * rain - 1.27
        qo = 800.0 * np.exp(-dc_prev / 400.0)
        qr = qo + 3.937 * rd
        dr = 400.0 * np.log(800.0 / qr)
        
        if dr < 0.0:
            dr = 0.0
        dc_prev = dr
    
    # Secado del combustible
    if temp > -2.8:
        lf = DAY_LENGTH_FACTORS.get(month, 9.0)
        v = 0.36 * (temp + 2.8) + lf
        dc = dc_prev + v / 2.0
    else:
        dc = dc_prev
    
    return max(0.0, dc)


def calculate_isi(wind: float, ffmc: float) -> float:
    """
    Initial Spread Index (ISI)
    Índice de propagación inicial del fuego
    
    Args:
        wind: Velocidad viento (km/h)
        ffmc: Fine Fuel Moisture Code
        
    Returns:
        ISI (0-50+)
    """
    # Contenido de humedad
    m = 147.2 * (101.0 - ffmc) / (59.5 + ffmc)
    
    # Factor de humedad del combustible
    ff = 91.9 * np.exp(-0.1386 * m) * (1.0 + m ** 5.31 / 49300000.0)
    
    # Factor del viento
    fw = np.exp(0.05039 * wind)
    
    # ISI
    isi = 0.208 * fw * ff
    
    return max(0.0, isi)


def calculate_bui(dmc: float, dc: float) -> float:
    """
    Build-Up Index (BUI)
    Índice de acumulación de combustible seco disponible
    
    Args:
        dmc: Duff Moisture Code
        dc: Drought Code
        
    Returns:
        BUI (0-200+)
    """
    if dmc <= 0.4 * dc:
        bui = 0.8 * dmc * dc / (dmc + 0.4 * dc)
    else:
        bui = dmc - (1.0 - 0.8 * dc / (dmc + 0.4 * dc)) * \
              (0.92 + (0.0114 * dmc) ** 1.7)
    
    return max(0.0, bui)


def calculate_fwi(isi: float, bui: float) -> float:
    """
    Fire Weather Index (FWI)
    Índice general de peligro de incendio
    
    Args:
        isi: Initial Spread Index
        bui: Build-Up Index
        
    Returns:
        FWI (0-100+)
    """
    if bui <= 80.0:
        fd = 0.626 * bui ** 0.809 + 2.0
    else:
        fd = 1000.0 / (25.0 + 108.64 * np.exp(-0.023 * bui))
    
    b = 0.1 * isi * fd
    
    if b <= 1.0:
        fwi = b
    else:
        fwi = np.exp(2.72 * (0.434 * np.log(b)) ** 0.647)
    
    return max(0.0, fwi)


def calculate_fwi_components(temp: float, rh: float, wind: float, rain: float,
                             ffmc_prev: float = INITIAL_FFMC,
                             dmc_prev: float = INITIAL_DMC,
                             dc_prev: float = INITIAL_DC,
                             month: int = 6) -> Dict[str, float]:
    """
    Calcula todos los componentes del FWI para un día
    
    Args:
        temp: Temperatura (°C)
        rh: Humedad relativa (%)
        wind: Velocidad viento (km/h)
        rain: Precipitación 24h (mm)
        ffmc_prev: FFMC del día anterior
        dmc_prev: DMC del día anterior
        dc_prev: DC del día anterior
        month: Mes del año (1-12)
        
    Returns:
        Diccionario con todos los índices FWI
    """
    # Códigos de humedad
    ffmc = calculate_ffmc(temp, rh, wind, rain, ffmc_prev)
    dmc = calculate_dmc(temp, rh, rain, dmc_prev, month)
    dc = calculate_dc(temp, rain, dc_prev, month)
    
    # Índices de comportamiento
    isi = calculate_isi(wind, ffmc)
    bui = calculate_bui(dmc, dc)
    fwi = calculate_fwi(isi, bui)
    
    return {
        'ffmc': round(ffmc, 2),
        'dmc': round(dmc, 2),
        'dc': round(dc, 2),
        'isi': round(isi, 2),
        'bui': round(bui, 2),
        'fwi': round(fwi, 2)
    }


def calculate_fwi_series(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula FWI para una serie temporal de datos meteorológicos
    
    Args:
        weather_df: DataFrame con columnas:
            - temp: temperatura (°C)
            - rh: humedad relativa (%)
            - wind: viento (km/h)
            - rain: precipitación (mm)
            - month: mes (1-12)
            
    Returns:
        DataFrame original con columnas FWI añadidas
    """
    logger.info(f"Calculando FWI para {len(weather_df)} registros...")
    
    # Inicializar valores
    ffmc_prev = INITIAL_FFMC
    dmc_prev = INITIAL_DMC
    dc_prev = INITIAL_DC
    
    results = []
    
    for idx, row in weather_df.iterrows():
        # Calcular FWI del día
        fwi_components = calculate_fwi_components(
            temp=row['temp'],
            rh=row['rh'],
            wind=row['wind'],
            rain=row['rain'],
            ffmc_prev=ffmc_prev,
            dmc_prev=dmc_prev,
            dc_prev=dc_prev,
            month=row['month']
        )
        
        # Guardar para próximo día
        ffmc_prev = fwi_components['ffmc']
        dmc_prev = fwi_components['dmc']
        dc_prev = fwi_components['dc']
        
        results.append(fwi_components)
    
    # Añadir al DataFrame
    fwi_df = pd.DataFrame(results)
    result_df = pd.concat([weather_df.reset_index(drop=True), fwi_df], axis=1)
    
    logger.info("  ✓ Cálculo FWI completado")
    
    return result_df


# ============================================================================
# INTERPRETACIÓN DE FWI
# ============================================================================

def interpret_fwi(fwi: float) -> Dict[str, str]:
    """
    Interpreta el valor de FWI en términos de peligro
    
    Args:
        fwi: Valor del Fire Weather Index
        
    Returns:
        Diccionario con nivel de peligro y recomendación
    """
    if fwi < 5.0:
        return {
            'nivel': 'Muy Bajo',
            'color': '#10b981',  # Verde
            'peligro': 'bajo',
            'recomendacion': 'Condiciones ideales para quemas prescritas'
        }
    elif fwi < 10.0:
        return {
            'nivel': 'Bajo',
            'color': '#84cc16',  # Verde lima
            'peligro': 'bajo',
            'recomendacion': 'Condiciones favorables para quemas con precauciones básicas'
        }
    elif fwi < 15.0:
        return {
            'nivel': 'Moderado',
            'color': '#f59e0b',  # Amarillo
            'peligro': 'moderado',
            'recomendacion': 'Quemas solo con personal experimentado y vigilancia constante'
        }
    elif fwi < 25.0:
        return {
            'nivel': 'Alto',
            'color': '#f97316',  # Naranja
            'peligro': 'alto',
            'recomendacion': 'Evitar quemas. Riesgo significativo de descontrol'
        }
    elif fwi < 35.0:
        return {
            'nivel': 'Muy Alto',
            'color': '#ef4444',  # Rojo
            'peligro': 'muy_alto',
            'recomendacion': 'No realizar quemas. Condiciones peligrosas'
        }
    else:
        return {
            'nivel': 'Extremo',
            'color': '#991b1b',  # Rojo oscuro
            'peligro': 'extremo',
            'recomendacion': 'Prohibido quemar. Riesgo de incendio catastrófico'
        }


if __name__ == "__main__":
    # Test de ejemplo
    print("=" * 70)
    print("Test de cálculo FWI")
    print("=" * 70)
    
    # Condiciones de ejemplo
    test_conditions = {
        'temp': 28.0,       # 28°C (caluroso)
        'rh': 30.0,         # 30% humedad (seco)
        'wind': 25.0,       # 25 km/h (viento moderado-fuerte)
        'rain': 0.0         # Sin lluvia
    }
    
    # Calcular FWI
    fwi_result = calculate_fwi_components(**test_conditions)
    interpretation = interpret_fwi(fwi_result['fwi'])
    
    print("\nCondiciones:")
    print(f"  Temperatura: {test_conditions['temp']}°C")
    print(f"  Humedad: {test_conditions['rh']}%")
    print(f"  Viento: {test_conditions['wind']} km/h")
    print(f"  Lluvia: {test_conditions['rain']} mm")
    
    print("\nÍndices FWI:")
    for key, value in fwi_result.items():
        print(f"  {key.upper()}: {value}")
    
    print(f"\nInterpretación:")
    print(f"  Nivel de peligro: {interpretation['nivel']}")
    print(f"  Recomendación: {interpretation['recomendacion']}")
