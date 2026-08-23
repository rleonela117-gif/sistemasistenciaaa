from flask import Blueprint, jsonify, request

from backend.services.employee_service import EmployeeService


employee_bp = Blueprint("employees", __name__)

employee_service = EmployeeService()


@employee_bp.route("/empleados", methods=["GET"])
def listar_empleados():
    return jsonify({
        "empleados": employee_service.listar()
    }), 200


@employee_bp.route("/empleados/<codigo>", methods=["GET"])
def obtener_empleado(codigo):
    empleado = employee_service.obtener(codigo.upper())

    if not empleado:
        return jsonify({
            "error": "Empleado no encontrado."
        }), 404

    return jsonify({
        "empleado": empleado
    }), 200


@employee_bp.route("/empleados", methods=["POST"])
def crear_empleado():
    data = request.get_json(silent=True) or {}

    requeridos = [
        "codigo",
        "nombre_completo",
        "cargo",
        "usuario",
        "password"
    ]

    faltantes = [
        campo for campo in requeridos
        if not data.get(campo)
    ]

    if faltantes:
        return jsonify({
            "error": f"Faltan campos obligatorios: {', '.join(faltantes)}"
        }), 400

    try:
        empleado = employee_service.crear(
            codigo=data["codigo"].strip().upper(),
            nombre_completo=data["nombre_completo"].strip(),
            cargo=data["cargo"].strip(),
            usuario=data["usuario"].strip(),
            password=data["password"],
            rol=data.get("rol", "empleado")
        )

        return jsonify({
            "empleado": empleado
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 409

    except Exception as e:
        return jsonify({
            "error": f"Error al crear el empleado: {str(e)}"
        }), 500


@employee_bp.route("/empleados/<codigo>", methods=["PUT"])
def actualizar_empleado(codigo):
    data = request.get_json(silent=True) or {}

    try:
        empleado = employee_service.actualizar(
            codigo.upper(),
            **data
        )

        return jsonify({
            "empleado": empleado
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "error": f"Error al actualizar el empleado: {str(e)}"
        }), 500


@employee_bp.route("/empleados/<codigo>", methods=["DELETE"])
def desactivar_empleado(codigo):
    try:
        empleado = employee_service.desactivar(codigo.upper())

        return jsonify({
            "empleado": empleado,
            "mensaje": "Empleado desactivado correctamente."
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "error": f"Error al desactivar el empleado: {str(e)}"
        }), 500