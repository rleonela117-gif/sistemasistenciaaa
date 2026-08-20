"""
Sistema Asistencia — Backend Flask.

Ejecutar con:
    python app.py

Ver README.md (raíz del proyecto) para la guía completa de instalación,
configuración de Google Sheets y despliegue.
"""
import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

import database as db
from config.settings import Config
from routes.attendance_routes import attendance_bp
from routes.auth_routes import auth_bp
from routes.employee_routes import employee_bp


def crear_admin_por_defecto():
    """Crea un usuario administrador inicial SOLO si la base está vacía,
    para que el primer login (que requiere Internet) tenga con qué entrar.
    Cambia esta contraseña apenas inicies sesión por primera vez.
    """
    if db.get_all():
        return

    usuario = os.getenv("ADMIN_USUARIO", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin1234")
    db.create(
        codigo="ADMIN001",
        nombre_completo="Administrador del Sistema",
        cargo="Administración",
        usuario=usuario,
        password_hash=generate_password_hash(password),
        rol="admin",
    )
    print(
        f"[Sistema Asistencia] Usuario administrador creado -> "
        f"usuario: '{usuario}' / contraseña: '{password}' "
        f"(cámbiala después de tu primer inicio de sesión)."
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    db.init_db()
    crear_admin_por_defecto()

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
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
