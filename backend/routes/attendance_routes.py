from flask import Blueprint, jsonify, request

from services.attendance_service import AttendanceService
from services.sheets_service import SheetsService

attendance_bp = Blueprint("attendance", __name__)
attendance_service = AttendanceService()
sheets_service = SheetsService.instance()


@attendance_bp.route("/sincronizar", methods=["POST"])
def sincronizar():
    """Recibe un lote de asistencias pendientes desde el teléfono y las
    guarda en Google Sheets, ignorando cualquier UUID ya recibido antes
    (prevención de duplicados obligatoria)."""
    data = request.get_json(silent=True) or {}
    registros = data.get("registros", [])

    if not isinstance(registros, list):
        return jsonify({"error": "El campo 'registros' debe ser una lista."}), 400

    if not registros:
        return jsonify({"sincronizados": [], "errores": []}), 200

    resultado = attendance_service.sincronizar_lote(registros)
    return jsonify(resultado), 200


@attendance_bp.route("/asistencia", methods=["POST"])
def registrar_asistencia_individual():
    """Registro individual en tiempo real (cuando el teléfono SÍ tiene
    Internet en el momento del escaneo). Reutiliza la misma lógica que el
    endpoint de sincronización por lote, con un solo registro."""
    data = request.get_json(silent=True) or {}
    requeridos = ["id_registro", "codigo", "fecha", "tipo", "hora"]
    faltantes = [c for c in requeridos if not data.get(c)]
    if faltantes:
        return jsonify(
            {"error": f"Faltan campos obligatorios: {', '.join(faltantes)}"}
        ), 400

    resultado = attendance_service.sincronizar_lote([data])
    if data["id_registro"] in resultado["sincronizados"]:
        return jsonify({"mensaje": "Asistencia registrada correctamente."}), 201
    return jsonify({"error": "No se pudo registrar la asistencia.", "detalle": resultado["errores"]}), 500


@attendance_bp.route("/asistencias", methods=["GET"])
def listar_asistencias():
    """Consulta general (opcionalmente filtrando por código de empleado)."""
    codigo = request.args.get("codigo")
    try:
        hoja = sheets_service._hoja_asistencias()  # noqa: SLF001 (uso interno controlado)
        filas = hoja.get_all_records()
        if codigo:
            filas = [f for f in filas if str(f.get("Código", "")).upper() == codigo.upper()]
        return jsonify({"asistencias": filas}), 200
    except Exception as e:
        return jsonify({"error": f"No se pudo consultar Google Sheets: {e}"}), 502


@attendance_bp.route("/estado", methods=["GET"])
def estado():
    """Endpoint ligero de salud, usado por la app para el 'ping' de
    conectividad real con el backend."""
    return jsonify({"status": "ok", "servicio": "Sistema Asistencia API"}), 200
