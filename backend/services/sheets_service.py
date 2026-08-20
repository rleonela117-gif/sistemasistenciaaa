"""
Capa de acceso a Google Sheets.

Usa gspread + credenciales de una cuenta de servicio de Google Cloud.
El archivo de credenciales NUNCA debe subirse al repositorio ni incluirse
en el APK — solo vive en el servidor (ver README para cómo generarlo).
"""
import os
from datetime import datetime
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from backend.config.settings import Config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

# Columnas EXACTAS de la hoja "asistenciaa", en este orden.
COLUMNAS_ASISTENCIA = [
    "Código",
    "Nombre Completo",
    "Cargo",
    "Fecha",
    "Entrada",
    "Salida",
    "Horas trabajadas",
    "Minutos tarde",
    "Horas extras",
    "Estado",
    "ID Registro",
    "Sincronizado",
]

# Columnas de la hoja de empleados.
COLUMNAS_EMPLEADO = [
    "Código",
    "Nombre Completo",
    "Cargo",
    "Usuario",
    "Rol",
    "Activo",
]


class SheetsService:
    _instance: Optional["SheetsService"] = None

    def __init__(self):
        self._client = None
        self._spreadsheet = None

    @classmethod
    def instance(cls) -> "SheetsService":
        if cls._instance is None:
            cls._instance = SheetsService()
        return cls._instance

    def _conectar(self):
        if self._client is not None:
            return
        if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"No se encontró el archivo de credenciales de Google en "
                f"'{Config.GOOGLE_CREDENTIALS_FILE}'. Revisa el README, "
                f"sección 'Configurar Google Sheets'."
            )
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        self._client = gspread.authorize(creds)
        self._spreadsheet = self._client.open(Config.GOOGLE_SHEET_NAME)

    def _hoja_asistencias(self):
        self._conectar()
        try:
            return self._spreadsheet.worksheet(Config.GOOGLE_SHEET_TAB_ASISTENCIAS)
        except gspread.WorksheetNotFound:
            hoja = self._spreadsheet.add_worksheet(
                title=Config.GOOGLE_SHEET_TAB_ASISTENCIAS, rows=1000, cols=20
            )
            hoja.append_row(COLUMNAS_ASISTENCIA)
            return hoja

    def _hoja_empleados(self):
        self._conectar()
        try:
            return self._spreadsheet.worksheet(Config.GOOGLE_SHEET_TAB_EMPLEADOS)
        except gspread.WorksheetNotFound:
            hoja = self._spreadsheet.add_worksheet(
                title=Config.GOOGLE_SHEET_TAB_EMPLEADOS, rows=500, cols=10
            )
            hoja.append_row(COLUMNAS_EMPLEADO)
            return hoja

    # ---------------- ASISTENCIAS ----------------

    def id_ya_existe(self, id_registro: str) -> bool:
        """Comprueba si un UUID ya fue sincronizado antes (anti-duplicados)."""
        hoja = self._hoja_asistencias()
        columna_ids = hoja.col_values(COLUMNAS_ASISTENCIA.index("ID Registro") + 1)
        return id_registro in columna_ids

    def agregar_asistencia(self, registro: dict) -> None:
        """Agrega una fila de asistencia. `registro` ya viene validado y
        con los tiempos calculados desde attendance_service.py."""
        hoja = self._hoja_asistencias()
        fila = [
            registro["codigo"],
            registro["nombre_completo"],
            registro["cargo"],
            registro["fecha"],
            registro.get("entrada", ""),
            registro.get("salida", ""),
            registro.get("horas_trabajadas", ""),
            registro.get("minutos_tarde", 0),
            registro.get("horas_extras", ""),
            registro.get("estado", "OK"),
            registro["id_registro"],
            "SÍ",
        ]
        hoja.append_row(fila)

    # ---------------- EMPLEADOS ----------------

    def listar_empleados(self) -> list:
        hoja = self._hoja_empleados()
        filas = hoja.get_all_records()
        empleados = []
        for f in filas:
            empleados.append(
                {
                    "codigo": str(f.get("Código", "")).strip(),
                    "nombre_completo": str(f.get("Nombre Completo", "")).strip(),
                    "cargo": str(f.get("Cargo", "")).strip(),
                    "usuario": str(f.get("Usuario", "")).strip(),
                    "rol": str(f.get("Rol", "empleado")).strip() or "empleado",
                    "activo": str(f.get("Activo", "SI")).strip().upper() != "NO",
                }
            )
        return empleados

    def agregar_empleado(self, empleado: dict) -> None:
        hoja = self._hoja_empleados()
        hoja.append_row(
            [
                empleado["codigo"],
                empleado["nombre_completo"],
                empleado["cargo"],
                empleado["usuario"],
                empleado.get("rol", "empleado"),
                "SI",
            ]
        )

    def actualizar_empleado(self, codigo: str, cambios: dict) -> bool:
        hoja = self._hoja_empleados()
        columna_codigos = hoja.col_values(COLUMNAS_EMPLEADO.index("Código") + 1)
        if codigo not in columna_codigos:
            return False
        fila_idx = columna_codigos.index(codigo) + 1  # 1-indexed en gspread

        mapeo = {
            "nombre_completo": "Nombre Completo",
            "cargo": "Cargo",
            "usuario": "Usuario",
            "rol": "Rol",
        }
        for clave, columna in mapeo.items():
            if clave in cambios and cambios[clave] is not None:
                col_idx = COLUMNAS_EMPLEADO.index(columna) + 1
                hoja.update_cell(fila_idx, col_idx, cambios[clave])
        return True

    def desactivar_empleado(self, codigo: str) -> bool:
        hoja = self._hoja_empleados()
        columna_codigos = hoja.col_values(COLUMNAS_EMPLEADO.index("Código") + 1)
        if codigo not in columna_codigos:
            return False
        fila_idx = columna_codigos.index(codigo) + 1
        col_idx = COLUMNAS_EMPLEADO.index("Activo") + 1
        hoja.update_cell(fila_idx, col_idx, "NO")
        return True
