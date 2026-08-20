"""
Sistema Asistencia — Backend Flask.

Ejecutar con:
    python app.py
"""

import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from backend import database as db
from backend.config.settings import Config
from backend.routes.attendance_routes import attendance_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.employee_routes import employee_bp


def crear_usuarios_por_defecto():
    """
    Crea el administrador y los 5 empleados iniciales
    si todavía no existen en la base de datos.
    """

    usuarios = [
        {
            "codigo": "ADMIN001",
            "nombre_completo": "Administrador del Sistema",
            "cargo": "Administración",
            "usuario": os.getenv("ADMIN_USUARIO", "admin"),
            "password": os.getenv("ADMIN_PASSWORD", "admin1234"),
            "rol": "admin",
        },
        {
            "codigo": "EMP001",
            "nombre_completo": "Empleado 1",
            "cargo": "Empleado",
            "usuario": "empleado1",
            "password": "empleado123",
            "rol": "empleado",
        },
        {
            "codigo": "EMP002",
            "nombre_completo": "Empleado 2",
            "cargo": "Empleado",
            "usuario": "empleado2",
            "password": "empleado123",
            "rol": "empleado",
        },
        {
            "codigo": "EMP003",
            "nombre_completo": "Empleado 3",
            "cargo": "Empleado",
            "usuario": "empleado3",
            "password": "empleado123",
            "rol": "empleado",
        },
        {
            "codigo": "EMP004",
            "nombre_completo": "Empleado 4",
            "cargo": "Empleado",
            "usuario": "empleado4",
            "password": "empleado123",
            "rol": "empleado",
        },
        {
            "codigo": "EMP005",
            "nombre_completo": "Empleado 5",
            "cargo": "Empleado",
            "usuario": "empleado5",
            "password": "empleado123",
            "rol": "empleado",
        },
    ]

    for usuario in usuarios:
        existente = db.get_by_codigo(usuario["codigo"])

        if existente:
            continue

        db.create(
            codigo=usuario["codigo"],
            nombre_completo=usuario["nombre_completo"],
            cargo=usuario["cargo"],
            usuario=usuario["usuario"],
            password_hash=generate_password_hash(usuario["password"]),
            rol=usuario["rol"],
        )

        print(
            f"[Sistema Asistencia] Usuario creado -> "
            f"{usuario['usuario']} / {usuario['password']}"
        )


def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": Config.CORS_ORIGINS
            }
        },
    )

    # Inicializar la base de datos
    db.init_db()

    # Crear administrador y 5 empleados
    crear_usuarios_por_defecto()

    # Registrar rutas
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(employee_bp, url_prefix="/api")
    app.register_blueprint(attendance_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return jsonify(
            {
                "servicio": "Sistema Asistencia API",
                "estado": "activo",
                "endpoints": [
                    "POST /api/login",
                    "GET /api/empleados",
                    "POST /api/empleados",
                    "PUT /api/empleados/<codigo>",
                    "DELETE /api/empleados/<codigo>",
                    "POST /api/asistencia",
                    "GET /api/asistencias",
                    "POST /api/sincronizar",
                    "GET /api/estado",
                ],
            }
        )

    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify({"error": "Ruta no encontrada."}), 404

    @app.errorhandler(500)
    def error_interno(e):
        return jsonify({"error": "Error interno del servidor."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )