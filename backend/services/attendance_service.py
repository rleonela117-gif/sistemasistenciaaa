from backend.services.sheets_service import SheetsService
from backend.config.settings import Config


class AttendanceService:
    def __init__(self):
        self.sheets_service = SheetsService.instance()

    def sincronizar_lote(self, registros):
        sincronizados = []
        errores = []

        for registro in registros:
            try:
                id_registro = registro.get("id_registro")
                codigo = registro.get("codigo")
                fecha = registro.get("fecha")
                tipo = registro.get("tipo")
                hora = registro.get("hora")

                # Validar campos obligatorios
                if not id_registro:
                    errores.append({
                        "registro": registro,
                        "error": "Falta id_registro"
                    })
                    continue

                if not codigo:
                    errores.append({
                        "registro": registro,
                        "error": "Falta codigo"
                    })
                    continue

                if not fecha:
                    errores.append({
                        "registro": registro,
                        "error": "Falta fecha"
                    })
                    continue

                if not tipo:
                    errores.append({
                        "registro": registro,
                        "error": "Falta tipo"
                    })
                    continue

                if not hora:
                    errores.append({
                        "registro": registro,
                        "error": "Falta hora"
                    })
                    continue

                # Normalizar datos
                codigo = str(codigo).strip().upper()
                tipo = str(tipo).strip().lower()

                # Validar tipo
                if tipo not in ["entrada", "salida"]:
                    errores.append({
                        "registro": registro,
                        "error": "El tipo debe ser 'entrada' o 'salida'"
                    })
                    continue

                # Obtener hoja de asistencias
                hoja = self.sheets_service._hoja_asistencias()

                # Leer registros existentes para evitar duplicados
                filas_existentes = hoja.get_all_records()

                # Buscar si ya existe el UUID
                duplicado = False

                for fila in filas_existentes:
                    uuid_existente = (
                        fila.get("id_registro")
                        or fila.get("ID Registro")
                        or fila.get("UUID")
                        or ""
                    )

                    if str(uuid_existente).strip() == str(id_registro).strip():
                        duplicado = True
                        break

                # Si ya existe, no volverlo a guardar
                if duplicado:
                    sincronizados.append(id_registro)
                    continue

                # Crear fila para Google Sheets
                nueva_fila = [
                    id_registro,
                    codigo,
                    fecha,
                    tipo,
                    hora
                ]

                # Guardar en Google Sheets
                hoja.append_row(
                    nueva_fila,
                    value_input_option="USER_ENTERED"
                )

                sincronizados.append(id_registro)

            except Exception as e:
                errores.append({
                    "registro": registro,
                    "error": str(e)
                })

        return {
            "sincronizados": sincronizados,
            "errores": errores
        }