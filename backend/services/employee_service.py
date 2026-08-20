"""
CRUD de empleados. La base local (SQLite del servidor) es la fuente de
verdad para autenticación (guarda el hash de la contraseña); Google Sheets
recibe un espejo de los datos públicos para que el administrador pueda
consultarlos/editarlos también desde ahí si lo desea.
"""
from werkzeug.security import generate_password_hash

import database as db
from services.sheets_service import SheetsService


class EmployeeService:
    def __init__(self):
        self.sheets = SheetsService.instance()

    def listar(self) -> list:
        empleados = db.get_all()
        return [self._sin_password(e) for e in empleados]

    def obtener(self, codigo: str):
        e = db.get_by_codigo(codigo)
        return self._sin_password(e) if e else None

    def crear(self, codigo, nombre_completo, cargo, usuario, password, rol="empleado"):
        if db.get_by_codigo(codigo):
            raise ValueError(f"Ya existe un empleado con el código {codigo}.")
        if db.get_by_usuario(usuario):
            raise ValueError(f"Ya existe un empleado con el usuario {usuario}.")

        password_hash = generate_password_hash(password)
        db.create(codigo, nombre_completo, cargo, usuario, password_hash, rol)

        try:
            self.sheets.agregar_empleado(
                {
                    "codigo": codigo,
                    "nombre_completo": nombre_completo,
                    "cargo": cargo,
                    "usuario": usuario,
                    "rol": rol,
                }
            )
        except Exception:
            # No bloquea la creación si Sheets falla momentáneamente;
            # el dato ya quedó guardado de forma segura en el servidor.
            pass

        return self.obtener(codigo)

    def actualizar(self, codigo, **cambios):
        if not db.get_by_codigo(codigo):
            raise ValueError(f"No existe un empleado con el código {codigo}.")

        campos_db = {}
        if "nombre_completo" in cambios and cambios["nombre_completo"]:
            campos_db["nombre_completo"] = cambios["nombre_completo"]
        if "cargo" in cambios and cambios["cargo"]:
            campos_db["cargo"] = cambios["cargo"]
        if "usuario" in cambios and cambios["usuario"]:
            campos_db["usuario"] = cambios["usuario"]
        if "rol" in cambios and cambios["rol"]:
            campos_db["rol"] = cambios["rol"]
        if "password" in cambios and cambios["password"]:
            campos_db["password_hash"] = generate_password_hash(cambios["password"])

        db.update(codigo, **campos_db)

        try:
            self.sheets.actualizar_empleado(codigo, cambios)
        except Exception:
            pass

        return self.obtener(codigo)

    def desactivar(self, codigo):
        if not db.get_by_codigo(codigo):
            raise ValueError(f"No existe un empleado con el código {codigo}.")
        db.set_activo(codigo, False)
        try:
            self.sheets.desactivar_empleado(codigo)
        except Exception:
            pass
        return self.obtener(codigo)

    @staticmethod
    def _sin_password(empleado: dict) -> dict:
        return {
            "codigo": empleado["codigo"],
            "nombre_completo": empleado["nombre_completo"],
            "cargo": empleado["cargo"],
            "usuario": empleado["usuario"],
            "rol": empleado["rol"],
            "activo": bool(empleado["activo"]),
        }
