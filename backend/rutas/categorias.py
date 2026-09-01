from flask import Blueprint, request, jsonify
from modelos.db import get_db

bp = Blueprint("categorias", __name__)


@bp.post("/api/categorias")
def crear_categoria():
    data = request.get_json()
    id_usuario = data.get("id_usuario")
    nombre = (data.get("nombre") or "").strip()
    if not (id_usuario and nombre):
        return jsonify({"error": "id_usuario y nombre son obligatorios"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO categorias (id_usuario, nombre) VALUES (%s, %s) RETURNING id",
        (id_usuario, nombre),
    )
    nuevo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": nuevo_id, "nombre": nombre}), 201


@bp.get("/api/categorias")
def listar_categorias():
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre FROM categorias WHERE id_usuario = %s ORDER BY nombre",
        (id_usuario,),
    )
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": r[0], "nombre": r[1]} for r in filas])
