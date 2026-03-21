"""
IgniWise - Utilidades
Módulo con funciones de configuración y logging
"""

from .config import *
from .logger import setup_logger

__all__ = [
    'setup_logger',
    'DATA_RAW',
    'DATA_PROCESSED',
    'DATA_PREDICTIONS',
    'MODELS_DIR'
]
