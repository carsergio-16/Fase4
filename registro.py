"""Configuración del archivo de logs del sistema.

Los logs son el único uso de archivos permitido por el enunciado:
aquí se registran eventos relevantes y todos los errores.
"""

import logging
from pathlib import Path

# El log se guarda junto al código, en la carpeta del proyecto
RUTA_LOG = Path(__file__).resolve().parent / "software_fj.log"


def obtener_logger() -> logging.Logger:
    """Devuelve el logger único del sistema (se configura una sola vez)."""
    logger = logging.getLogger("software_fj")
    if not logger.handlers:  # evita duplicar handlers si se llama varias veces
        logger.setLevel(logging.INFO)
        manejador = logging.FileHandler(RUTA_LOG, mode="w", encoding="utf-8")
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(manejador)
    return logger


# Instancia compartida que importan los demás módulos
log = obtener_logger()
