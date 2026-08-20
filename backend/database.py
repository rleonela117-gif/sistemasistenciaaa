"""
Base de datos local del SERVIDOR (independiente de la SQLite que vive en
cada teléfono). Aquí se guardan los empleados y el hash de su contraseña.

Por seguridad, las contraseñas NUNCA se guardan en Google Sheets ni en
texto plano — Sheets solo recibe los datos "públicos" del empleado
(código, nombre, cargo, usuario, rol, activo).
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "sistema_asistencia_backend.db"


def init_db():
    with _conectar() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS empleados (
                codigo TEXT PRIMARY KEY,
                nombre_completo TEXT NOT NULL,
                cargo TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'empleado',
                activo INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.commit()


@contextmanager
def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_by_usuario(usuario: str):
    with _conectar() as conn:
        row = conn.execute(
            "SELECT * FROM empleados WHERE usuario = ?", (usuario,)
        ).fetchone()
        return dict(row) if row else None


def get_by_codigo(codigo: str):
    with _conectar() as conn:
        row = conn.execute(
            "SELECT * FROM empleados WHERE codigo = ?", (codigo,)
        ).fetchone()
        return dict(row) if row else None


def get_all():
    with _conectar() as conn:
        rows = conn.execute(
            "SELECT * FROM empleados ORDER BY nombre_completo ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def create(codigo, nombre_completo, cargo, usuario, password_hash, rol="empleado"):
    with _conectar() as conn:
        conn.execute(
            """INSERT INTO empleados
               (codigo, nombre_completo, cargo, usuario, password_hash, rol, activo)
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (codigo, nombre_completo, cargo, usuario, password_hash, rol),
        )
        conn.commit()


def update(codigo, **campos):
    if not campos:
        return
    columnas = ", ".join(f"{k} = ?" for k in campos.keys())
    valores = list(campos.values()) + [codigo]
    with _conectar() as conn:
        conn.execute(f"UPDATE empleados SET {columnas} WHERE codigo = ?", valores)
        conn.commit()


def set_activo(codigo, activo: bool):
    with _conectar() as conn:
        conn.execute(
            "UPDATE empleados SET activo = ? WHERE codigo = ?",
            (1 if activo else 0, codigo),
        )
        conn.commit()
