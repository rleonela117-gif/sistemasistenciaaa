import os
from datetime import time

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración central del backend."""

    # ------------------------------------------------------------
    # FLASK
    # ------------------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "cambia-esta-clave-en-produccion",
    )

    DEBUG = os.getenv(
        "FLASK_DEBUG",
        "false",
    ).lower() == "true"

    HOST = os.getenv(
        "HOST",
        "0.0.0.0",
    )

    # Render proporciona automáticamente PORT
    PORT = int(
        os.getenv(
            "PORT",
            "5000",
        )
    )

    # ------------------------------------------------------------
    # GOOGLE SHEETS
    # ------------------------------------------------------------

    # Para Render:
    # Aquí va el JSON COMPLETO de la cuenta de servicio
    # guardado como variable de entorno GOOGLE_CREDENTIALS_JSON
    GOOGLE_CREDENTIALS_JSON = os.getenv(
        "GOOGLE_CREDENTIALS_JSON",
        "",
    )

    # Para usar localmente en tu computadora
    GOOGLE_CREDENTIALS_FILE = os.getenv(
        "GOOGLE_CREDENTIALS_FILE",
        "credentials/google_credentials.json",
    )

    GOOGLE_SHEET_NAME = os.getenv(
        "GOOGLE_SHEET_NAME",
        "Sistema Asistencia",
    )

    GOOGLE_SHEET_TAB_ASISTENCIAS = os.getenv(
        "GOOGLE_SHEET_TAB_ASISTENCIAS",
        "asistenciaa",
    )

    GOOGLE_SHEET_TAB_EMPLEADOS = os.getenv(
        "GOOGLE_SHEET_TAB_EMPLEADOS",
        "empleados",
    )

    # ------------------------------------------------------------
    # HORARIO
    # ------------------------------------------------------------

    HORA_ENTRADA_OFICIAL = time(
        int(os.getenv("HORA_ENTRADA", "7")),
        0,
    )

    HORA_SALIDA_OFICIAL = time(
        int(os.getenv("HORA_SALIDA", "16")),
        0,
    )

    MINUTOS_ALMUERZO = int(
        os.getenv(
            "MINUTOS_ALMUERZO",
            "60",
        )
    )

    # ------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "*",
    )