"""
Capa de conexión con Google Sheets.
Funciona localmente con archivo JSON y en Render con
la variable de entorno GOOGLE_CREDENTIALS_JSON.
"""

import json
import os
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from backend.config.settings import Config


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsService:
    _instance: Optional["SheetsService"] = None

    def __init__(self):
        self._client = None
        self._spreadsheet = None

    @classmethod
    def instance(cls) -> "SheetsService":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    # ============================================================
    # CONEXIÓN
    # ============================================================

    def _conectar(self):
        """Conecta con Google Sheets."""

        if self._client is not None:
            return

        credentials_json = Config.GOOGLE_CREDENTIALS_JSON.strip()

        # --------------------------------------------------------
        # OPCIÓN 1: RENDER
        # --------------------------------------------------------
        if credentials_json:
            try:
                info = json.loads(credentials_json)

                creds = Credentials.from_service_account_info(
                    info,
                    scopes=SCOPES,
                )

                print(
                    "Google Sheets: usando GOOGLE_CREDENTIALS_JSON"
                )

            except Exception as e:
                raise Exception(
                    f"Error leyendo GOOGLE_CREDENTIALS_JSON: {str(e)}"
                )

        # --------------------------------------------------------
        # OPCIÓN 2: COMPUTADORA LOCAL
        # --------------------------------------------------------
        else:
            archivo = Config.GOOGLE_CREDENTIALS_FILE

            if not os.path.exists(archivo):
                raise FileNotFoundError(
                    "No se encontraron credenciales de Google. "
                    "Configura GOOGLE_CREDENTIALS_JSON en Render "
                    "o GOOGLE_CREDENTIALS_FILE localmente."
                )

            creds = Credentials.from_service_account_file(
                archivo,
                scopes=SCOPES,
            )

            print(
                f"Google Sheets: usando archivo {archivo}"
            )

        # --------------------------------------------------------
        # CONECTAR
        # --------------------------------------------------------

        self._client = gspread.authorize(creds)

        self._spreadsheet = self._client.open(
            Config.GOOGLE_SHEET_NAME
        )

        print(
            f"Google Sheets conectado correctamente: "
            f"{Config.GOOGLE_SHEET_NAME}"
        )

    # ============================================================
    # HOJAS
    # ============================================================

    def _hoja_asistencias(self):
        self._conectar()

        return self._spreadsheet.worksheet(
            Config.GOOGLE_SHEET_TAB_ASISTENCIAS
        )

    def _hoja_empleados(self):
        self._conectar()

        return self._spreadsheet.worksheet(
            Config.GOOGLE_SHEET_TAB_EMPLEADOS
        )

    # ============================================================
    # ASISTENCIAS
    # ============================================================

    def id_ya_existe(self, id_registro: str) -> bool:
        """
        Tu hoja actual no tiene la columna ID Registro.

        Por ahora permitimos guardar los registros.
        """
        return False

    def agregar_asistencia(self, registro: dict) -> None:
        """
        Guarda una asistencia usando exactamente las columnas
        actuales de tu hoja:
        Codigo | Nombre Completo | CARGO | Fecha | Entrada |
        Salida | Minutos tarde | Horas extras | Horas trabajadas
        """

        hoja = self._hoja_asistencias()

        fila = [
            registro.get("codigo", ""),
            registro.get("nombre_completo", ""),
            registro.get("cargo", ""),
            registro.get("fecha", ""),
            registro.get("entrada", ""),
            registro.get("salida", ""),
            registro.get("minutos_tarde", 0),
            registro.get("horas_extras", ""),
            registro.get("horas_trabajadas", ""),
        ]

        hoja.append_row(
            fila,
            value_input_option="USER_ENTERED",
        )

    # ============================================================
    # EMPLEADOS
    # ============================================================

    def listar_empleados(self) -> list:
        hoja = self._hoja_empleados()

        filas = hoja.get_all_records()

        empleados = []

        for f in filas:
            empleados.append({
                "codigo": str(
                    f.get(
                        "Código",
                        f.get("Codigo", ""),
                    )
                ).strip(),

                "nombre_completo": str(
                    f.get("Nombre Completo", "")
                ).strip(),

                "cargo": str(
                    f.get(
                        "Cargo",
                        f.get("CARGO", ""),
                    )
                ).strip(),

                "usuario": str(
                    f.get("Usuario", "")
                ).strip(),

                "rol": str(
                    f.get("Rol", "empleado")
                ).strip() or "empleado",

                "activo": str(
                    f.get("Activo", "SI")
                ).strip().upper() != "NO",
            })

        return empleados

    def agregar_empleado(self, empleado: dict) -> None:
        hoja = self._hoja_empleados()

        hoja.append_row([
            empleado.get("codigo", ""),
            empleado.get("nombre_completo", ""),
            empleado.get("cargo", ""),
            empleado.get("usuario", ""),
            empleado.get("rol", "empleado"),
            "SI",
        ])

    def actualizar_empleado(
        self,
        codigo: str,
        cambios: dict,
    ) -> bool:

        hoja = self._hoja_empleados()

        columna_codigos = hoja.col_values(1)

        if codigo not in columna_codigos:
            return False

        fila_idx = columna_codigos.index(codigo) + 1

        mapeo = {
            "nombre_completo": 2,
            "cargo": 3,
            "usuario": 4,
            "rol": 5,
        }

        for clave, columna in mapeo.items():
            if clave in cambios and cambios[clave] is not None:
                hoja.update_cell(
                    fila_idx,
                    columna,
                    cambios[clave],
                )

        return True

    def desactivar_empleado(self, codigo: str) -> bool:
        hoja = self._hoja_empleados()

        columna_codigos = hoja.col_values(1)

        if codigo not in columna_codigos:
            return False

        fila_idx = columna_codigos.index(codigo) + 1

        hoja.update_cell(
            fila_idx,
            6,
            "NO",
        )

        return True
