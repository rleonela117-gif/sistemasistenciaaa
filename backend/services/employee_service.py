from werkzeug.security import generate_password_hash

from backend import database as db
from backend.services.sheets_service import SheetsService

class EmployeeService:
    def __init__(self):
        self.sheets_service = None

    @staticmethod
    def _sin_password(empleado):
        if not empleado:
            return None

        return {
            "codigo": empleado.get("codigo", ""),
            "nombre_completo": empleado.get("nombre_completo", ""),
            "cargo": empleado.get("cargo", ""),
            "usuario": empleado.get("usuario", ""),
            "rol": empleado.get("rol", "empleado"),
            "activo": bool(empleado.get("activo", True))
        }

    def listar(self):
        empleados = db.get_all()

        return [
            self._sin_password(empleado)
            for empleado in empleados
            if empleado.get("activo", 1)
        ]

    def listar_empleados(self):
        return self.listar()

    def obtener(self, codigo):
        codigo = str(codigo).strip().upper()

        empleado = db.get_by_codigo(codigo)

        return self._sin_password(empleado)

    def obtener_empleado_por_usuario(self, usuario):
        usuario = str(usuario).strip()

        empleado = db.get_by_usuario(usuario)

        return self._sin_password(empleado)

    def crear(
        self,
        codigo,
        nombre_completo,
        cargo,
        usuario,
        password,
        rol="empleado"
    ):
        codigo = str(codigo).strip().upper()
        nombre_completo = str(nombre_completo).strip()
        cargo = str(cargo).strip()
        usuario = str(usuario).strip()
        rol = str(rol).strip().lower()

        if not codigo:
            raise ValueError("El código es obligatorio.")

        if not nombre_completo:
            raise ValueError("El nombre completo es obligatorio.")

        if not cargo:
            raise ValueError("El cargo es obligatorio.")

        if not usuario:
            raise ValueError("El usuario es obligatorio.")

        if not password:
            raise ValueError("La contraseña es obligatoria.")

        if db.get_by_codigo(codigo):
            raise ValueError(
                "Ya existe un empleado con ese código."
            )

        if db.get_by_usuario(usuario):
            raise ValueError(
                "Ya existe un empleado con ese usuario."
            )

        password_hash = generate_password_hash(password)

        db.create(
            codigo=codigo,
            nombre_completo=nombre_completo,
            cargo=cargo,
            usuario=usuario,
            password_hash=password_hash,
            rol=rol
        )

        empleado = db.get_by_codigo(codigo)

        return self._sin_password(empleado)

    def actualizar(self, codigo, **datos):
        codigo = str(codigo).strip().upper()

        empleado = db.get_by_codigo(codigo)

        if not empleado:
            raise ValueError("Empleado no encontrado.")

        campos_permitidos = [
            "nombre_completo",
            "cargo",
            "usuario",
            "rol",
            "activo"
        ]

        campos_actualizar = {}

        for campo in campos_permitidos:
            if campo in datos and datos[campo] is not None:
                valor = datos[campo]

                if campo == "activo":
                    valor = 1 if bool(valor) else 0
                else:
                    valor = str(valor).strip()

                campos_actualizar[campo] = valor

        if "password" in datos and datos["password"]:
            campos_actualizar["password_hash"] = (
                generate_password_hash(
                    str(datos["password"])
                )
            )

        if "usuario" in campos_actualizar:
            usuario_existente = db.get_by_usuario(
                campos_actualizar["usuario"]
            )

            if (
                usuario_existente
                and usuario_existente["codigo"] != codigo
            ):
                raise ValueError(
                    "Ya existe otro empleado con ese usuario."
                )

        if campos_actualizar:
            db.update(codigo, **campos_actualizar)

        empleado_actualizado = db.get_by_codigo(codigo)

        return self._sin_password(empleado_actualizado)

    def desactivar(self, codigo):
        codigo = str(codigo).strip().upper()

        empleado = db.get_by_codigo(codigo)

        if not empleado:
            raise ValueError("Empleado no encontrado.")

        db.set_activo(codigo, False)

        empleado_actualizado = db.get_by_codigo(codigo)

        return self._sin_password(empleado_actualizado)