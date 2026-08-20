"""
Reglas de negocio del servidor: cálculo de minutos tarde / trabajados / extra
(debe coincidir con utils/time_calculator.dart del lado Flutter) y la
prevención de registros duplicados por UUID, requisito obligatorio del
proyecto.
"""
from datetime import datetime, time

from config.settings import Config
from services.sheets_service import SheetsService


def _minutos_tarde(hora_entrada: datetime) -> int:
    oficial = hora_entrada.replace(
        hour=Config.HORA_ENTRADA_OFICIAL.hour,
        minute=Config.HORA_ENTRADA_OFICIAL.minute,
        second=0,
        microsecond=0,
    )
    diff = int((hora_entrada - oficial).total_seconds() // 60)
    return max(diff, 0)


def _minutos_extra(hora_salida: datetime) -> int:
    oficial = hora_salida.replace(
        hour=Config.HORA_SALIDA_OFICIAL.hour,
        minute=Config.HORA_SALIDA_OFICIAL.minute,
        second=0,
        microsecond=0,
    )
    diff = int((hora_salida - oficial).total_seconds() // 60)
    return max(diff, 0)


def _formato_horas(minutos: int) -> str:
    h, m = divmod(max(minutos, 0), 60)
    return f"{h}:{m:02d}"


class AttendanceService:
    """Procesa el guardado de un lote de asistencias enviado por la app,
    evitando duplicados y calculando/validando los tiempos antes de
    escribir en Google Sheets."""

    def __init__(self):
        self.sheets = SheetsService.instance()

    def sincronizar_lote(self, registros: list) -> dict:
        sincronizados = []
        errores = []

        for r in registros:
            id_registro = r.get("id_registro")
            if not id_registro:
                errores.append({"id_registro": None, "motivo": "Falta id_registro"})
                continue

            try:
                # --- Prevención de duplicados (requisito obligatorio) ---
                if self.sheets.id_ya_existe(id_registro):
                    # Ya existe: se considera sincronizado igualmente, para
                    # que el cliente lo marque como enviado y no reintente.
                    sincronizados.append(id_registro)
                    continue

                tipo = r.get("tipo")
                hora_iso = r.get("hora")
                hora_dt = datetime.fromisoformat(hora_iso) if hora_iso else datetime.now()

                fila = {
                    "codigo": r.get("codigo"),
                    "nombre_completo": r.get("nombre_completo"),
                    "cargo": r.get("cargo"),
                    "fecha": r.get("fecha"),
                    "id_registro": id_registro,
                    "estado": "OK",
                }

                if tipo == "entrada":
                    fila["entrada"] = hora_dt.strftime("%I:%M %p")
                    fila["minutos_tarde"] = r.get("minutos_tarde", _minutos_tarde(hora_dt))
                else:
                    fila["salida"] = hora_dt.strftime("%I:%M %p")
                    minutos_trab = r.get("minutos_trabajados", 0)
                    minutos_ext = r.get("minutos_extra", _minutos_extra(hora_dt))
                    fila["horas_trabajadas"] = _formato_horas(minutos_trab)
                    fila["horas_extras"] = _formato_horas(minutos_ext)

                self.sheets.agregar_asistencia(fila)
                sincronizados.append(id_registro)

            except Exception as e:  # noqa: BLE001 - se reporta al cliente
                errores.append({"id_registro": id_registro, "motivo": str(e)})

        return {"sincronizados": sincronizados, "errores": errores}
