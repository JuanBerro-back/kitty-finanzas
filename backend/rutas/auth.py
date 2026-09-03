import json
import re
import urllib.parse
import urllib.request

from flask import Blueprint, request, jsonify

from modelos.db import get_db
from modelos.auth import hash_password, check_password, make_token, login_required
from rutas.categorias import crear_categorias_defecto

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_CLIENT_ID = "61510338551-29nagua32pgrm0j3ckjo6b3d550jkcgl.apps.googleusercontent.com"
GOOGLE_VALID_ISSUERS = {"https://accounts.google.com", "accounts.google.com"}


def _usuario_pub(fila):
    return {
        "id": fila[0],
        "nombre": fila[1],
        "email": fila[2],
        "avatar": fila[5] if len(fila) > 5 else None,
    }


def _verificar_google_token(id_token):
    """Verifica la firma y claims del id_token contra los servidores de Google."""
    if not id_token or not isinstance(id_token, str):
        return {"valid": False, "reason": "Falta el id_token de Google"}
    try:
        query = urllib.parse.urlencode({"id_token": id_token})
        req = urllib.request.Request(f"{GOOGLE_TOKENINFO_URL}?{query}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {"valid": False, "reason": "No se pudo verificar el token con Google"}
    if info.get("aud") != GOOGLE_CLIENT_ID:
        return {"valid": False, "reason": "El token no fue emitido para esta aplicación"}
    if info.get("iss") not in GOOGLE_VALID_ISSUERS:
        return {"valid": False, "reason": "Emisor del token inválido"}
    if str(info.get("email_verified")) not in ("True", "true"):
        return {"valid": False, "reason": "El correo de Google no está verificado"}
    email = (info.get("email") or "").strip().lower()
    if not EMAIL_RE.match(email):
        return {"valid": False, "reason": "Email de Google inválido"}
    return {"valid": True, "info": info}


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
        "INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
        (nombre, email, hash_password(password)),
    )
    uid = cur.fetchone()[0]
    crear_categorias_defecto(conn, cur, uid)
    conn.commit()
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


@bp.post("/api/auth/google")
def login_google():
    data = request.get_json()
    id_token = (data.get("id_token") or "").strip()

    verificacion = _verificar_google_token(id_token)
    if not verificacion["valid"]:
        return jsonify({"error": verificacion["reason"]}), 401

    info = verificacion["info"]
    google_id = str(info.get("sub") or "")
    email = (info.get("email") or "").strip().lower()
    nombre = (info.get("name") or "").strip() or email.split("@")[0]
    avatar = (info.get("picture") or "").strip()

    conn = get_db()
    cur = conn.cursor()

    # 1. Buscar por email
    cur.execute(
        "SELECT id, nombre, email, password_hash, google_id, avatar "
        "FROM usuarios WHERE email = %s",
        (email,),
    )
    fila = cur.fetchone()

    if fila:
        # Ya existe por email: si aún no tiene google_id, lo vinculamos.
        if not fila[4]:
            cur.execute(
                "UPDATE usuarios SET google_id = %s, avatar = %s WHERE id = %s",
                (google_id, avatar or None, fila[0]),
            )
            conn.commit()
        return jsonify({"token": make_token(fila[0]), "usuario": _usuario_pub(fila)}), 200

    # 2. Buscar por google_id (por si el email de Google cambió)
    cur.execute(
        "SELECT id, nombre, email, password_hash, google_id, avatar "
        "FROM usuarios WHERE google_id = %s",
        (google_id,),
    )
    fila = cur.fetchone()
    if fila:
        return jsonify({"token": make_token(fila[0]), "usuario": _usuario_pub(fila)}), 200

    # 3. Nuevo usuario con Google (sin contraseña)
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, email, google_id, avatar) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (nombre, email, google_id, avatar or None),
        )
        uid = cur.fetchone()[0]
        crear_categorias_defecto(conn, cur, uid)
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "No se pudo crear la cuenta con Google"}), 409

    cur.close()
    conn.close()
    return jsonify({"token": make_token(uid), "usuario": {"id": uid, "nombre": nombre, "email": email, "avatar": avatar or None}}), 201
