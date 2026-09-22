import logging
import os
from datetime import datetime


def obtener_logger(nombre_modulo: str = "QuantBot") -> logging.Logger:
    """
    Configura y devuelve un logger que escribe tanto en la consola como en un archivo .log.
    """
    # 1. Crear la carpeta de logs en la raíz del proyecto si no existe
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    carpeta_logs = os.path.join(directorio_script, "../../logs")
    os.makedirs(carpeta_logs, exist_ok=True)

    # 2. Nombrar el archivo con la fecha de hoy (ej. bot_2026-09-21.log)
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ruta_log = os.path.join(carpeta_logs, f"bot_{fecha_hoy}.log")

    # 3. Crear el logger
    logger = logging.getLogger(nombre_modulo)
    logger.setLevel(logging.INFO)

    # Evitar que se dupliquen las líneas si el logger se llama varias veces
    if not logger.handlers:
        # Formato exacto de cómo se verá cada línea
        formato = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

        # Archivo de texto
        file_handler = logging.FileHandler(ruta_log, encoding='utf-8')
        file_handler.setFormatter(formato)

        # Consola (Terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger