from backend.services.sheets_service import SheetsService


class AttendanceService:
    def __init__(self):
        self.sheets_service = SheetsService.instance()

    def sincronizar_lote(self, registros):
        sincronizados = []
        errores = []

        # Obtener la hoja una sola vez
        try:
            hoja = self.sheets_service._hoja_asistencias()
        except Exception as e:
            return {
                "sincronizados": [],
                "errores": [
                    {
                        "error": f"No se pudo conectar con Google Sheets: {str(e)}"
                    }
                ]
            }

        # Leer registros existentes una sola vez
        try:
            filas_existentes = hoja.get_all_records()
        except Exception as e:
            return {
                "sincronizados": [],
                "errores": [
                    {
                        "error": f"No se pudieron leer los registros existentes: {str(e)}"
                    }
                ]
            }

        # Guardar los UUID existentes para evitar duplicados
        ids_existentes = set()

        for fila in filas_existentes:
            uuid_existente = (
                fila.get("id_registro")
                or fila.get("ID Registro")
                or fila.get("UUID")
                or ""
            )

            if uuid_existente:
                ids_existentes.add(str(uuid_existente).strip())

        # Procesar cada registro
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    errores.append({
                        "registro": registro,
                        "error": "El registro debe ser un objeto válido"
                    })
                    continue

                id_registro = str(registro.get("id_registro", "")).strip()
                codigo = str(registro.get("codigo", "")).strip().upper()
                fecha = str(registro.get("fecha", "")).strip()
                tipo = str(registro.get("tipo", "")).strip().lower()
                hora = str(registro.get("hora", "")).strip()

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

                if tipo not in ["entrada", "salida"]:
                    errores.append({
                        "registro": registro,
                        "error": "El tipo debe ser 'entrada' o 'salida'"
                    })
                    continue

                if not hora:
                    errores.append({
                        "registro": registro,
                        "error": "Falta hora"
                    })
                    continue

                # Evitar duplicados
                if id_registro in ids_existentes:
                    sincronizados.append(id_registro)
                    continue

                # Guardar en Google Sheets
                nueva_fila = [
                    id_registro,
                    codigo,
                    fecha,
                    tipo,
                    hora
                ]

                hoja.append_row(
                    nueva_fila,
                    value_input_option="USER_ENTERED"
                )

                # Agregar al conjunto para evitar duplicados
                # dentro del mismo lote
                ids_existentes.add(id_registro)
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