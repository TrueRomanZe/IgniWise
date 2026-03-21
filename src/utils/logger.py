"""
IgniWise - Sistema de Logging
Configuración consistente de logs para todo el proyecto
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from .config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIR


def setup_logger(name: str, log_file: str = None, level: str = None):
    """
    Configura un logger con formato consistente
    
    Args:
        name: Nombre del logger (usar __name__)
        log_file: Archivo donde guardar logs (opcional)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configurado
    
    Example:
        >>> from src.utils.logger import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Script iniciado")
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    if log_file:
        # Crear carpeta de logs si no existe
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Añadir timestamp al nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = LOGS_DIR / f"{log_file}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger por defecto para el proyecto
default_logger = setup_logger('igniwise')
