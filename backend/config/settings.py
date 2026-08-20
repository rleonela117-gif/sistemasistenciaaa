import os
from datetime import time

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración central del backend.

    Todos los valores sensibles (credenciales de Google, secret key, etc.)
    se leen de variables de entorno / archivo .env — NUNCA se escriben aquí
    directamente ni se exponen en la app Flutter / el APK.
    """

    # ---- Flask ----
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    # ---- Google Sheets ----
    GOOGLE_CREDENTIALS_FILE = os.getenv(
        "GOOGLE_CREDENTIALS_FILE", "credentials/google_credentials.json"
    )
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sistema Asistencia")
    GOOGLE_SHEET_TAB_ASISTENCIAS = os.getenv(
        "GOOGLE_SHEET_TAB_ASISTENCIAS", "asistenciaa"
    )
    GOOGLE_SHEET_TAB_EMPLEADOS = os.getenv(
        "GOOGLE_SHEET_TAB_EMPLEADOS", "empleados"
    )

    # ---- Horario oficial (igual que en la app Flutter; el admin puede
    # cambiarlos vía variables de entorno sin tocar código) ----
    HORA_ENTRADA_OFICIAL = time(int(os.getenv("HORA_ENTRADA", "7")), 0)
    HORA_SALIDA_OFICIAL = time(int(os.getenv("HORA_SALIDA", "16")), 0)
    MINUTOS_ALMUERZO = int(os.getenv("MINUTOS_ALMUERZO", "60"))

    # ---- CORS ----
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
