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
            filas_existentes = hoja.get_all_records()
        except Exception as e:
            return {
                "sincronizados": [],
                "errores": [
                    {
                        "error": f"No se pudo conectar con Google Sheets: {str(e)}"
                    }
                ]
            }

        # Obtener los IDs que ya existen
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
                id_registro = str(id_registro).strip()
                codigo = str(codigo).strip().upper()
                fecha = str(fecha).strip()
                tipo = str(tipo).strip().lower()
                hora = str(hora).strip()

                # Validar tipo
                if tipo not in ["entrada", "salida"]:
                    errores.append({
                        "registro": registro,
                        "error": "El tipo debe ser 'entrada' o 'salida'"
                    })
                    continue

                # Evitar duplicados
                if id_registro in ids_existentes:
                    sincronizados.append(id_registro)
                    continue

                # Crear nueva fila
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

                # Agregar ID para evitar duplicados dentro del mismo lote
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