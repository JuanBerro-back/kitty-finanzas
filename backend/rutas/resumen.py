from flask import Blueprint, request, jsonify
from modelos.db import get_db

bp = Blueprint("resumen", __name__)


@bp.get("/api/resumen")
def resumen():
    id_usuario = request.args.get("id_usuario")
    mes = request.args.get("mes")  # formato YYYY-MM
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    conn = get_db()
    cur = conn.cursor()
    if mes:
        cur.execute(
            "SELECT tipo, COALESCE(SUM(monto),0) FROM ingresos_gastos "
            "WHERE id_usuario=%s AND DATE_FORMAT(fecha,'%%Y-%%m')=%s GROUP BY tipo",
            (id_usuario, mes),
        )
    else:
        cur.execute(
            "SELECT tipo, COALESCE(SUM(monto),0) FROM ingresos_gastos "
            "WHERE id_usuario=%s GROUP BY tipo",
            (id_usuario,),
        )
    filas = cur.fetchall()
    cur.close()
    conn.close()
    totales = {"ingresos": 0.0, "gastos": 0.0}
    for f in filas:
        totales[f[0]] = float(f[1])
    balance = totales["ingresos"] - totales["gastos"]
    porcentaje_ahorro = 0.0
    if totales["ingresos"] > 0:
        porcentaje_ahorro = balance / totales["ingresos"] * 100
    return jsonify({
        "ingresos": totales["ingresos"],
        "gastos": totales["gastos"],
        "balance": balance,
        "porcentaje_ahorro": round(porcentaje_ahorro, 2),
    })
