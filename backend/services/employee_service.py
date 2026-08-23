from werkzeug.security import generate_password_hash

from backend.services.sheets_service import SheetsService


class EmployeeService:
    def __init__(self):
        self.sheets_service = SheetsService.instance()

    def _obtener_hoja(self):
        return self.sheets_service._hoja_empleados()

    def listar(self):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            empleados = []

            for fila in filas:
                activo = fila.get("Activo", fila.get("activo", True))

                if str(activo).strip().lower() not in [
                    "false",
                    "0",
                    "no",
                    "inactivo"
                ]:
                    empleados.append(fila)

            return empleados

        except Exception as e:
            raise Exception(
                f"No se pudieron obtener los empleados: {str(e)}"
            )

    def listar_empleados(self):
        return self.listar()

    def obtener(self, codigo):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            codigo = str(codigo).strip().upper()

            for fila in filas:
                codigo_fila = str(
                    fila.get("Código")
                    or fila.get("Codigo")
                    or fila.get("codigo")
                    or ""
                ).strip().upper()

                if codigo_fila == codigo:
                    return fila

            return None

        except Exception as e:
            raise Exception(
                f"No se pudo obtener el empleado: {str(e)}"
            )

    def obtener_empleado_por_usuario(self, usuario):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            usuario = str(usuario).strip()

            for fila in filas:
                usuario_fila = str(
                    fila.get("Usuario")
                    or fila.get("usuario")
                    or ""
                ).strip()

                if usuario_fila == usuario:
                    return fila

            return None

        except Exception as e:
            raise Exception(
                f"No se pudo obtener el empleado: {str(e)}"
            )

    def crear(
        self,
        codigo,
        nombre_completo,
        cargo,
        usuario,
        password,
        rol="empleado"
    ):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            codigo = str(codigo).strip().upper()
            usuario = str(usuario).strip()

            for fila in filas:
                codigo_fila = str(
                    fila.get("Código")
                    or fila.get("Codigo")
                    or fila.get("codigo")
                    or ""
                ).strip().upper()

                usuario_fila = str(
                    fila.get("Usuario")
                    or fila.get("usuario")
                    or ""
                ).strip()

                if codigo_fila == codigo:
                    raise ValueError(
                        "Ya existe un empleado con ese código."
                    )

                if usuario_fila == usuario:
                    raise ValueError(
                        "Ya existe un empleado con ese usuario."
                    )

            password_hash = generate_password_hash(password)

            nueva_fila = [
                codigo,
                nombre_completo,
                cargo,
                usuario,
                password_hash,
                rol,
                True
            ]

            hoja.append_row(
                nueva_fila,
                value_input_option="USER_ENTERED"
            )

            return {
                "codigo": codigo,
                "nombre_completo": nombre_completo,
                "cargo": cargo,
                "usuario": usuario,
                "rol": rol,
                "activo": True
            }

        except ValueError:
            raise

        except Exception as e:
            raise Exception(
                f"No se pudo crear el empleado: {str(e)}"
            )

    def actualizar(self, codigo, **datos):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            codigo = str(codigo).strip().upper()

            encabezados = hoja.row_values(1)

            numero_fila = None
            empleado_actual = None

            for indice, fila in enumerate(filas, start=2):
                codigo_fila = str(
                    fila.get("Código")
                    or fila.get("Codigo")
                    or fila.get("codigo")
                    or ""
                ).strip().upper()

                if codigo_fila == codigo:
                    numero_fila = indice
                    empleado_actual = fila
                    break

            if numero_fila is None:
                raise ValueError("Empleado no encontrado.")

            mapa_columnas = {
                "nombre_completo": [
                    "Nombre Completo",
                    "nombre_completo"
                ],
                "cargo": [
                    "Cargo",
                    "cargo"
                ],
                "usuario": [
                    "Usuario",
                    "usuario"
                ],
                "password": [
                    "Password",
                    "password",
                    "Password Hash",
                    "password_hash"
                ],
                "rol": [
                    "Rol",
                    "rol"
                ],
                "activo": [
                    "Activo",
                    "activo"
                ]
            }

            for campo, valor in datos.items():
                if campo not in mapa_columnas:
                    continue

                if valor is None:
                    continue

                if campo == "password":
                    valor = generate_password_hash(str(valor))

                columna = None

                for nombre_columna in mapa_columnas[campo]:
                    if nombre_columna in encabezados:
                        columna = encabezados.index(nombre_columna) + 1
                        break

                if columna:
                    hoja.update_cell(
                        numero_fila,
                        columna,
                        valor
                    )

            empleado_actualizado = self.obtener(codigo)

            return empleado_actualizado

        except ValueError:
            raise

        except Exception as e:
            raise Exception(
                f"No se pudo actualizar el empleado: {str(e)}"
            )

    def desactivar(self, codigo):
        try:
            hoja = self._obtener_hoja()
            filas = hoja.get_all_records()

            codigo = str(codigo).strip().upper()

            encabezados = hoja.row_values(1)

            numero_fila = None

            for indice, fila in enumerate(filas, start=2):
                codigo_fila = str(
                    fila.get("Código")
                    or fila.get("Codigo")
                    or fila.get("codigo")
                    or ""
                ).strip().upper()

                if codigo_fila == codigo:
                    numero_fila = indice
                    break

            if numero_fila is None:
                raise ValueError("Empleado no encontrado.")

            columna_activo = None

            for nombre in ["Activo", "activo"]:
                if nombre in encabezados:
                    columna_activo = encabezados.index(nombre) + 1
                    break

            if columna_activo is None:
                raise Exception(
                    "No existe una columna 'Activo' en la hoja de empleados."
                )

            hoja.update_cell(
                numero_fila,
                columna_activo,
                False
            )

            empleado = self.obtener(codigo)

            return empleado

        except ValueError:
            raise

        except Exception as e:
            raise Exception(
                f"No se pudo desactivar el empleado: {str(e)}"
            )