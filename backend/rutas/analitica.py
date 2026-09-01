from flask import Blueprint, request, jsonify
from modelos.db import get_db

bp = Blueprint("analitica", __name__)


@bp.get("/api/analitica/estadisticas")
def estadisticas():
    """Distribución por categoría y tendencia mensual."""
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT c.nombre, COALESCE(SUM(m.monto),0) FROM ingresos_gastos m "
        "JOIN categorias c ON c.id=m.id_categoria "
        "WHERE m.id_usuario=%s AND m.tipo='gasto' GROUP BY c.nombre ORDER BY 2 DESC",
        (id_usuario,),
    )
    por_categoria = [{"categoria": r[0], "total": float(r[1])} for r in cur.fetchall()]
    cur.execute(
        "SELECT to_char(fecha,'YYYY-MM') mes, "
        "COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto END),0) ingresos, "
        "COALESCE(SUM(CASE WHEN tipo='gasto' THEN monto END),0) gastos "
        "FROM ingresos_gastos WHERE id_usuario=%s "
        "GROUP BY mes ORDER BY mes",
        (id_usuario,),
    )
    tendencia = [
        {"mes": r[0], "ingresos": float(r[1]), "gastos": float(r[2])} for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify({"por_categoria": por_categoria, "tendencia": tendencia})


@bp.get("/api/analitica/prediccion")
def prediccion():
    from analitica.modulo import predecir_gasto
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    return jsonify(predecir_gasto(int(id_usuario)))


@bp.get("/api/analitica/anomalias")
def anomalias():
    from analitica.modulo import detectar_anomalias
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400
    return jsonify(detectar_anomalias(int(id_usuario)))
