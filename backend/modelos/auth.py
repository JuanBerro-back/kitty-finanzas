import os
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from flask import request, jsonify

SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
TOKEN_TTL_MIN = int(os.getenv("TOKEN_TTL_MIN", 60 * 24))


def hash_password(plain):
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(plain, hashed):
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def make_token(usuario_id):
    payload = {
        "uid": usuario_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MIN),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token = header.removeprefix("Bearer ").strip() if header else None
        payload = decode_token(token) if token else None
        if not payload:
            return jsonify({"error": "No autorizado"}), 401
        request.usuario_id = payload["uid"]
        return fn(*args, **kwargs)
    return wrapper
