from flask import Blueprint, request, jsonify
from modelos.db import get_db

bp = Blueprint("movimientos", __name__)


def _fila_a_dict(f):
    return {
        "id": f[0],
        "id_usuario": f[1],
        "id_categoria": f[2],
        "categoria": f[3],
        "tipo": f[4],
        "monto": float(f[5]),
        "fecha": str(f[6]),
        "descripcion": f[7],
    }


@bp.post("/api/movimientos")
def crear_movimiento():
    data = request.get_json()
    id_usuario = data.get("id_usuario")
    id_categoria = data.get("id_categoria")
    tipo = data.get("tipo")
    monto = data.get("monto")
    fecha = data.get("fecha")
    descripcion = (data.get("descripcion") or "").strip()
    if tipo not in ("ingreso", "gasto"):
        return jsonify({"error": "tipo debe ser 'ingreso' o 'gasto'"}), 400
    if not (id_usuario and id_categoria and monto and fecha):
        return jsonify({"error": "Campos obligatorios faltantes"}), 400
    if monto <= 0:
        return jsonify({"error": "El monto debe ser positivo"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (id_usuario, id_categoria, tipo, monto, fecha, descripcion),
    )
    conn.commit()
    _id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": _id}), 201


@bp.get("/api/movimientos")
def listar_movimientos():
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    categoria = request.args.get("categoria")
    conn = get_db()
    cur = conn.cursor()
    sql = ("SELECT m.id, m.id_usuario, m.id_categoria, c.nombre, m.tipo, m.monto, "
           "m.fecha, m.descripcion FROM ingresos_gastos m "
           "JOIN categorias c ON c.id = m.id_categoria WHERE m.id_usuario = %s")
    params = [id_usuario]
    if desde:
        sql += " AND m.fecha >= %s"
        params.append(desde)
    if hasta:
        sql += " AND m.fecha <= %s"
        params.append(hasta)
    if categoria:
        sql += " AND m.id_categoria = %s"
        params.append(categoria)
    sql += " ORDER BY m.fecha DESC"
    cur.execute(sql, params)
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([_fila_a_dict(f) for f in filas])


def _get_mov(id, cur):
    cur.execute(
        "SELECT m.id, m.id_usuario, m.id_categoria, c.nombre, m.tipo, m.monto, "
        "m.fecha, m.descripcion FROM ingresos_gastos m "
        "JOIN categorias c ON c.id = m.id_categoria WHERE m.id = %s",
        (id,),
    )
    return cur.fetchone()


@bp.put("/api/movimientos/<int:id>")
def editar_movimiento(id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    fila = _get_mov(id, cur)
    if not fila:
        cur.close()
        conn.close()
        return jsonify({"error": "Movimiento no encontrado"}), 404
    tipo = data.get("tipo", fila[4])
    monto = data.get("monto", fila[5])
    fecha = data.get("fecha", fila[6])
    id_categoria = data.get("id_categoria", fila[2])
    descripcion = (data.get("descripcion") if data.get("descripcion") is not None else fila[7]).strip()
    if tipo not in ("ingreso", "gasto"):
        return jsonify({"error": "tipo inválido"}), 400
    cur.execute(
        "UPDATE ingresos_gastos SET tipo=%s, monto=%s, fecha=%s, id_categoria=%s, descripcion=%s "
        "WHERE id=%s",
        (tipo, monto, fecha, id_categoria, descripcion, id),
    )
    conn.commit()
    fila2 = _get_mov(id, cur)
    cur.close()
    conn.close()
    return jsonify(_fila_a_dict(fila2))


@bp.delete("/api/movimientos/<int:id>")
def eliminar_movimiento(id):
    conn = get_db()
    cur = conn.cursor()
    fila = _get_mov(id, cur)
    if not fila:
        cur.close()
        conn.close()
        return jsonify({"error": "Movimiento no encontrado"}), 404
    cur.execute("DELETE FROM ingresos_gastos WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return "", 204
