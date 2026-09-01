from flask import Blueprint, request, jsonify
from modelos.db import get_db

bp = Blueprint("usuarios", __name__)


@bp.post("/api/usuarios")
def crear_usuario():
    data = request.get_json()
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nombre) VALUES (%s)", (nombre,))
    conn.commit()
    cur.execute("SELECT id, nombre, fecha_registro FROM usuarios WHERE id = %s", (cur.lastrowid,))
    fila = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"id": fila[0], "nombre": fila[1], "fecha_registro": str(fila[2])}), 201
