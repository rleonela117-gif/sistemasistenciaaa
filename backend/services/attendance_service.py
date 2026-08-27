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
                        "error": (
                            "El registro debe ser un objeto válido"
                        ),
                    })
                    continue

                # ====================================================
                # DATOS
                # ====================================================

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

                # ====================================================
                # VALIDACIONES
                # ====================================================

                if not id_registro:
                    errores.append({
                        "registro": registro,
                        "error": "Falta id_registro",
                    })
                    continue

                if not codigo:
                    errores.append({
                        "registro": registro,
                        "error": "Falta codigo",
                    })
                    continue

                if not fecha:
                    errores.append({
                        "registro": registro,
                        "error": "Falta fecha",
                    })
                    continue

                if tipo not in (
                    "entrada",
                    "salida",
                ):
                    errores.append({
                        "registro": registro,
                        "error": (
                            "El tipo debe ser entrada o salida"
                        ),
                    })
                    continue

                if not hora:
                    errores.append({
                        "registro": registro,
                        "error": "Falta hora",
                    })
                    continue

                # ====================================================
                # DUPLICADOS
                # ====================================================

                if self.sheets_service.id_ya_existe(
                    id_registro
                ):
                    sincronizados.append(
                        id_registro
                    )
                    continue

                # ====================================================
                # BUSCAR EMPLEADO
                # ====================================================

                empleados = (
                    self.sheets_service.listar_empleados()
                )

                empleado = None

                for e in empleados:
                    codigo_empleado = str(
                        e.get(
                            "codigo",
                            "",
                        )
                    ).strip().upper()

                    if codigo_empleado == codigo:
                        empleado = e
                        break

                nombre_completo = (
                    empleado.get(
                        "nombre_completo",
                        "",
                    )
                    if empleado
                    else str(
                        registro.get(
                            "nombre_completo",
                            "",
                        )
                    )
                )

                cargo = (
                    empleado.get(
                        "cargo",
                        "",
                    )
                    if empleado
                    else str(
                        registro.get(
                            "cargo",
                            "",
                        )
                    )
                )

                # ====================================================
                # DATOS PARA SHEETS
                # ====================================================

                datos = {
                    "id_registro": id_registro,

                    "codigo": codigo,

                    "nombre_completo": (
                        nombre_completo
                    ),

                    "cargo": cargo,

                    "fecha": fecha,

                    "entrada": (
                        hora
                        if tipo == "entrada"
                        else ""
                    ),

                    "salida": (
                        hora
                        if tipo == "salida"
                        else ""
                    ),

                    "minutos_tarde": registro.get(
                        "minutos_tarde",
                        0,
                    ),

                    "horas_trabajadas": (
                        registro.get(
                            "minutos_trabajados",
                            0,
                        )
                    ),

                    "horas_extras": (
                        registro.get(
                            "minutos_extra",
                            0,
                        )
                    ),
                }

                # ====================================================
                # GUARDAR
                # ====================================================

                self.sheets_service.agregar_asistencia(
                    datos
                )

                sincronizados.append(
                    id_registro
                )

            except Exception as e:
                errores.append({
                    "registro": registro,
                    "error": str(e),
                })

        return {
            "sincronizados": sincronizados,
            "errores": errores,
        }