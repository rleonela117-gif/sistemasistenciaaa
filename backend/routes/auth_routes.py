from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

import database as db
from services.employee_service import EmployeeService

auth_bp = Blueprint("auth", __name__)
employee_service = EmployeeService()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""

    if not usuario or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios."}), 400

    empleado = db.get_by_usuario(usuario) or db.get_by_codigo(usuario)

    if not empleado:
        return jsonify({"error": "Usuario o contraseña incorrectos."}), 401

    if not check_password_hash(empleado["password_hash"], password):
        return jsonify({"error": "Usuario o contraseña incorrectos."}), 401

    if not empleado["activo"]:
        return jsonify({"error": "Este usuario está desactivado."}), 403

    return jsonify({"empleado": EmployeeService._sin_password(empleado)}), 200
