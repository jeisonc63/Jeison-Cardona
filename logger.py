"""
logger.py – Sistema de registro de eventos y errores (Software FJ)

Implementa un logger simple que escribe en archivo y en consola,
sin depender de base de datos ni frameworks externos.
"""

import os
from datetime import datetime


class Logger:
    """
    Registra eventos del sistema en un archivo de logs.

    Niveles soportados: INFO, WARNING, ERROR, CRITICAL
    Cada entrada incluye timestamp, nivel y mensaje.
    """

    NIVELES = {"INFO": "ℹ", "WARNING": "⚠", "ERROR": "✖", "CRITICAL": "🔴"}

    def __init__(self, ruta_archivo: str):
        self.ruta = ruta_archivo
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            # Verificar escritura
            with open(self.ruta, "a", encoding="utf-8") as f:
                f.write(
                    f"{'─'*60}\n"
                    f"  Sesión iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"{'─'*60}\n"
                )
        except OSError as e:
            print(f"[Logger] Advertencia: no se pudo abrir archivo de log → {e}")
            self.ruta = None

    def _escribir(self, nivel: str, mensaje: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        icono = self.NIVELES.get(nivel, "•")
        linea = f"[{timestamp}] [{nivel:<8}] {icono} {mensaje}\n"

        if self.ruta:
            try:
                with open(self.ruta, "a", encoding="utf-8") as f:
                    f.write(linea)
            except OSError:
                pass  # Fallo silencioso en escritura de log

    def info(self, mensaje: str):
        self._escribir("INFO", mensaje)

    def warning(self, mensaje: str):
        self._escribir("WARNING", mensaje)

    def error(self, mensaje: str):
        self._escribir("ERROR", mensaje)

    def critical(self, mensaje: str):
        self._escribir("CRITICAL", mensaje)
        print(f"[CRITICAL] {mensaje}")
