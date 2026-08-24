from backend.services.sheets_service import SheetsService


class AttendanceService:
    def __init__(self):
        self.sheets_service = SheetsService.instance()

    def sincronizar_lote(self, registros):
        sincronizados = []
        errores = []

        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    errores.append({
                        "registro": str(registro),
                        "error": "El registro debe ser un objeto válido"
                    })
                    continue

                # Datos básicos
                id_registro = str(
                    registro.get("id_registro", "")
                ).strip()

                codigo = str(
                    registro.get("codigo", "")
                ).strip().upper()

                fecha = str(
                    registro.get("fecha", "")
                ).strip()

                tipo = str(
                    registro.get("tipo", "")
                ).strip().lower()

                hora = str(
                    registro.get("hora", "")
                ).strip()

                # Validaciones
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
                        "error": "El tipo debe ser entrada o salida"
                    })
                    continue

                if not hora:
                    errores.append({
                        "registro": registro,
                        "error": "Falta hora"
                    })
                    continue

                # Evitar duplicados usando una memoria local del servidor
                # basada en los IDs que ya existen.
                if self.sheets_service.id_ya_existe(id_registro):
                    sincronizados.append(id_registro)
                    continue

                # Buscar información del empleado
                empleados = self.sheets_service.listar_empleados()

                empleado = None

                for e in empleados:
                    if str(e.get("codigo", "")).upper() == codigo:
                        empleado = e
                        break

                # Si no está en la hoja de empleados,
                # usamos valores por defecto para no bloquear
                nombre_completo = (
                    empleado.get("nombre_completo", "")
                    if empleado
                    else ""
                )

                cargo = (
                    empleado.get("cargo", "")
                    if empleado
                    else ""
                )

                # Preparar registro según sea entrada o salida
                datos = {
                    "id_registro": id_registro,
                    "codigo": codigo,
                    "nombre_completo": nombre_completo,
                    "cargo": cargo,
                    "fecha": fecha,
                    "entrada": hora if tipo == "entrada" else "",
                    "salida": hora if tipo == "salida" else "",
                    "minutos_tarde": 0,
                    "horas_extras": "",
                    "horas_trabajadas": "",
                }

                # Guardar en Google Sheets
                self.sheets_service.agregar_asistencia(datos)

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