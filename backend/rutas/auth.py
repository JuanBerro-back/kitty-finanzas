import re

from flask import Blueprint, request, jsonify

from modelos.db import get_db
from modelos.auth import hash_password, check_password, make_token, login_required

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _usuario_pub(fila):
    return {
        "id": fila[0],
        "nombre": fila[1],
        "email": fila[2],
    }


@bp.post("/api/auth/register")
def registrar():
    data = request.get_json()
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son obligatorios"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Ya existe una cuenta con ese email"}), 409
    cur.execute(
        "INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)",
        (nombre, email, hash_password(password)),
    )
    conn.commit()
    uid = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"token": make_token(uid), "usuario": {"id": uid, "nombre": nombre, "email": email}}), 201


@bp.post("/api/auth/login")
def login():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, email, password_hash, google_id, avatar "
        "FROM usuarios WHERE email = %s",
        (email,),
    )
    fila = cur.fetchone()
    cur.close()
    conn.close()
    if not fila or not check_password(password, fila[3]):
        return jsonify({"error": "Email o contraseña incorrectos"}), 401
    return jsonify({"token": make_token(fila[0]), "usuario": _usuario_pub(fila)})


@bp.get("/api/auth/me")
@login_required
def yo():
    uid = request.usuario_id
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, email, password_hash, google_id, avatar FROM usuarios WHERE id = %s",
        (uid,),
    )
    fila = cur.fetchone()
    cur.close()
    conn.close()
    if not fila:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(_usuario_pub(fila))
