"""
Configuración centralizada de logging para la aplicación.
Proporciona loggers configurados para diferentes módulos.
"""
import logging
import sys
from pathlib import Path

# Crear directorio de logs si no existe
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Formato estándar para todos los logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Crea y configura un logger con handlers para archivo y consola.
    
    Args:
        name: Nombre del logger (generalmente __name__ del módulo)
        level: Nivel de logging (default: INFO)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formatter común
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = logging.FileHandler(
        LOG_DIR / f"{name.replace('.', '_')}.log",
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Loggers predefinidos para módulos principales
auth_logger = setup_logger("auth")
file_logger = setup_logger("file_operations")
security_logger = setup_logger("security")
database_logger = setup_logger("database")
