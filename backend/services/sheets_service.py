"""
Servicio de conexión con Google Sheets.

Las nuevas asistencias se guardan así:

Entrada:
    crea una fila nueva.

Salida:
    busca la entrada pendiente del mismo empleado y fecha
    y completa la misma fila.

Las asistencias antiguas no se modifican ni se reorganizan.
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
        if self._client is not None:
            return

        credentials_json = Config.GOOGLE_CREDENTIALS_JSON.strip()

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
                    "Error leyendo GOOGLE_CREDENTIALS_JSON: "
                    f"{str(e)}"
                )

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

        self._client = gspread.authorize(creds)

        self._spreadsheet = self._client.open(
            Config.GOOGLE_SHEET_NAME
        )

        print(
            "Google Sheets conectado correctamente: "
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
    # UTILIDADES DE HORA
    # ============================================================

    @staticmethod
    def _hora_corta(valor: str) -> str:
        """
        Convierte una hora ISO como:

        2026-08-27T07:05:23.123

        en:

        07:05:23
        """

        valor = str(valor or "").strip()

        if not valor:
            return ""

        if "T" in valor:
            valor = valor.split("T", 1)[1]

        if "." in valor:
            valor = valor.split(".", 1)[0]

        if "Z" in valor:
            valor = valor.replace("Z", "")

        if "+" in valor:
            valor = valor.split("+", 1)[0]

        return valor[:8]

    # ============================================================
    # DUPLICADOS
    # ============================================================

    def id_ya_existe(self, id_registro: str) -> bool:
        """
        La hoja actual no tiene columna de ID.

        Se mantiene False para conservar compatibilidad
        con el sistema actual.
        """

        return False

    # ============================================================
    # BUSCAR ENTRADA PENDIENTE
    # ============================================================

    def buscar_entrada_pendiente(
        self,
        codigo: str,
        fecha: str,
    ) -> Optional[int]:
        """
        Busca una fila que tenga:

        mismo código
        misma fecha
        entrada existente
        salida vacía

        Devuelve el número de fila de Google Sheets.
        """

        hoja = self._hoja_asistencias()

        filas = hoja.get_all_values()

        if len(filas) <= 1:
            return None

        codigo = str(codigo).strip().upper()
        fecha = str(fecha).strip()

        # Saltamos la fila 1 porque contiene encabezados.
        for numero_fila, fila in enumerate(
            filas[1:],
            start=2,
        ):
            if len(fila) < 6:
                continue

            codigo_fila = str(
                fila[0]
            ).strip().upper()

            fecha_fila = str(
                fila[3]
            ).strip()

            entrada_fila = str(
                fila[4]
            ).strip()

            salida_fila = str(
                fila[5]
            ).strip()

            if (
                codigo_fila == codigo
                and fecha_fila == fecha
                and entrada_fila
                and not salida_fila
            ):
                return numero_fila

        return None

    # ============================================================
    # AGREGAR ASISTENCIA
    # ============================================================

    def agregar_asistencia(
        self,
        registro: dict,
    ) -> None:
        """
        Decide automáticamente si es entrada o salida.
        """

        entrada = str(
            registro.get("entrada", "")
        ).strip()

        salida = str(
            registro.get("salida", "")
        ).strip()

        if entrada and not salida:
            self._agregar_entrada(registro)
            return

        if salida and not entrada:
            self._agregar_salida(registro)
            return

        raise Exception(
            "El registro debe contener una entrada "
            "o una salida."
        )

    # ============================================================
    # ENTRADA
    # ============================================================

    def _agregar_entrada(
        self,
        registro: dict,
    ) -> None:
        """
        Crea una fila nueva.

        Columnas:

        A Código
        B Nombre Completo
        C CARGO
        D Fecha
        E Entrada
        F Salida
        G Minutos tarde
        H Horas trabajadas
        I Horas extras
        """

        hoja = self._hoja_asistencias()

        hora = self._hora_corta(
            registro.get("entrada", "")
        )

        fila = [
            registro.get("codigo", ""),
            registro.get("nombre_completo", ""),
            registro.get("cargo", ""),
            registro.get("fecha", ""),
            hora,
            "",
            registro.get("minutos_tarde", 0),
            "",
            "",
        ]

        hoja.append_row(
            fila,
            value_input_option="USER_ENTERED",
        )

        print(
            "ENTRADA GUARDADA EN SHEETS: "
            f"{registro.get('codigo')} "
            f"{registro.get('fecha')} "
            f"{hora}"
        )

    # ============================================================
    # SALIDA
    # ============================================================

    def _agregar_salida(
        self,
        registro: dict,
    ) -> None:
        """
        Completa la fila donde ya existe la entrada.
        """

        hoja = self._hoja_asistencias()

        codigo = str(
            registro.get("codigo", "")
        ).strip().upper()

        fecha = str(
            registro.get("fecha", "")
        ).strip()

        fila_numero = self.buscar_entrada_pendiente(
            codigo,
            fecha,
        )

        if fila_numero is None:
            raise Exception(
                "No se encontró una entrada pendiente "
                f"para {codigo} en {fecha}."
            )

        hora_salida = self._hora_corta(
            registro.get("salida", "")
        )

        horas_trabajadas = registro.get(
            "horas_trabajadas",
            "",
        )

        horas_extras = registro.get(
            "horas_extras",
            "",
        )

        # F = Salida
        hoja.update_cell(
            fila_numero,
            6,
            hora_salida,
        )

        # H = Horas trabajadas
        hoja.update_cell(
            fila_numero,
            8,
            horas_trabajadas,
        )

        # I = Horas extras
        hoja.update_cell(
            fila_numero,
            9,
            horas_extras,
        )

        print(
            "SALIDA COMPLETADA EN SHEETS: "
            f"{codigo} "
            f"{fecha} "
            f"{hora_salida} "
            f"fila={fila_numero}"
        )

    # ============================================================
    # EMPLEADOS
    # ============================================================

    def listar_empleados(self) -> list:
        hoja = self._hoja_empleados()

        filas = hoja.get_all_records()

        empleados = []

        for f in filas:
            codigo = str(
                f.get(
                    "Código",
                    f.get(
                        "Codigo",
                        "",
                    ),
                )
            ).strip()

            empleados.append({
                "codigo": codigo,

                "nombre_completo": str(
                    f.get(
                        "Nombre Completo",
                        "",
                    )
                ).strip(),

                "cargo": str(
                    f.get(
                        "Cargo",
                        f.get(
                            "CARGO",
                            "",
                        ),
                    )
                ).strip(),

                "usuario": str(
                    f.get(
                        "Usuario",
                        "",
                    )
                ).strip(),

                "rol": str(
                    f.get(
                        "Rol",
                        "empleado",
                    )
                ).strip() or "empleado",

                "activo": str(
                    f.get(
                        "Activo",
                        "SI",
                    )
                ).strip().upper() != "NO",
            })

        return empleados

    # ============================================================
    # CREAR EMPLEADO
    # ============================================================

    def agregar_empleado(
        self,
        empleado: dict,
    ) -> None:

        hoja = self._hoja_empleados()

        hoja.append_row([
            empleado.get("codigo", ""),
            empleado.get("nombre_completo", ""),
            empleado.get("cargo", ""),
            empleado.get("usuario", ""),
            empleado.get("rol", "empleado"),
            "SI",
        ])

    # ============================================================
    # ACTUALIZAR EMPLEADO
    # ============================================================

    def actualizar_empleado(
        self,
        codigo: str,
        cambios: dict,
    ) -> bool:

        hoja = self._hoja_empleados()

        columna_codigos = hoja.col_values(1)

        if codigo not in columna_codigos:
            return False

        fila_idx = (
            columna_codigos.index(codigo) + 1
        )

        mapeo = {
            "nombre_completo": 2,
            "cargo": 3,
            "usuario": 4,
            "rol": 5,
        }

        for clave, columna in mapeo.items():

            if (
                clave in cambios
                and cambios[clave] is not None
            ):
                hoja.update_cell(
                    fila_idx,
                    columna,
                    cambios[clave],
                )

        return True

    # ============================================================
    # DESACTIVAR EMPLEADO
    # ============================================================

    def desactivar_empleado(
        self,
        codigo: str,
    ) -> bool:

        hoja = self._hoja_empleados()

        columna_codigos = hoja.col_values(1)

        if codigo not in columna_codigos:
            return False

        fila_idx = (
            columna_codigos.index(codigo) + 1
        )

        hoja.update_cell(
            fila_idx,
            6,
            "NO",
        )

        return True