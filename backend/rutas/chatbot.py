from flask import Blueprint, request, jsonify

from modelos.db import get_db
from modelos.auth import login_required

bp = Blueprint("chatbot", __name__)


def _datos_usuario(uid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto END),0), "
        "COALESCE(SUM(CASE WHEN tipo='gasto' THEN monto END),0) "
        "FROM ingresos_gastos WHERE id_usuario=%s",
        (uid,),
    )
    r = cur.fetchone()
    ingresos, gastos = float(r[0]), float(r[1])
    cur.execute(
        "SELECT c.nombre, COALESCE(SUM(m.monto),0) FROM ingresos_gastos m "
        "JOIN categorias c ON c.id=m.id_categoria "
        "WHERE m.id_usuario=%s AND m.tipo='gasto' GROUP BY c.nombre ORDER BY 2 DESC",
        (uid,),
    )
    top = cur.fetchall()
    cur.execute("SELECT COUNT(*), COALESCE(AVG(monto),0) FROM ingresos_gastos WHERE id_usuario=%s", (uid,))
    total_m, monto_prom = cur.fetchone()
    cur.close()
    conn.close()
    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": ingresos - gastos,
        "top_categoria": top[0][0] if top else None,
        "top_monto": float(top[0][1]) if top else 0.0,
        "total_movimientos": total_m,
        "monto_promedio": float(monto_prom),
    }


def _kitty_respuesta(d):
    msgs = []
    if d["total_movimientos"] == 0:
        msgs.append("¡Miau! Aún no tienes movimientos registrados. Empieza anotando tus ingresos y gastos para que pueda ayudarte mejor. 🐾")
        return msgs
    if d["ingresos"] > 0:
        porcentaje_ahorro = d["balance"] / d["ingresos"] * 100
        if d["balance"] < 0:
            msgs.append("¡Cuidado! Estás gastando más de lo que ingresas. Intenta recortar gastos en categorías no esenciales. 🚨")
        elif porcentaje_ahorro >= 30:
            msgs.append(f"¡Excelente! Ahorras el {porcentaje_ahorro:.0f}% de tus ingresos. Sigue así, gatito ahorrador. 🐱💪")
        elif porcentaje_ahorro > 0:
            msgs.append(f"Ahorras el {porcentaje_ahorro:.0f}% de tus ingresos. Sugerencia: trata de llegar a 20-30% destinando a ahorro una parte fija de cada ingreso. 🐾")
        else:
            msgs.append("Ingresos y gastos están muy parejos. Considera buscar formas de aumentar ingresos o reducir gastos. 🐾")
    if d["top_categoria"]:
        msgs.append(f"Tu categoría de gasto más costosa es {d['top_categoria']} con {d['top_monto']:,.0f}. Revisa si puedes optimizarla. 🎯")
    msgs.append(f"Tienes {d['total_movimientos']} movimientos con un gasto promedio de {d['monto_promedio']:,.0f} por movimiento. Registra todo para tener mejor control. ⭐")
    return msgs


@bp.post("/api/chatbot")
@login_required
def hablar():
    data = request.get_json() or {}
    texto = (data.get("mensaje") or "").lower().strip()
    d = _datos_usuario(request.usuario_id)

    def dinero(v):
        return f"{v:,.0f}"

    # Saludo
    if any(p in texto for p in ["hola", "buenas", "hey", "hi", "que tal"]):
        return jsonify({"respuestas": [
            f"¡Hola! Soy Kitty, tu asistente financiera. 🐱 Puedo contarte de tus balance, ahorro, gasto más alto, predicción o darte un consejo. ¿Qué quieres saber?"
        ]})

    # Despedida / gracias
    if any(p in texto for p in ["gracias", "chao", "adios", "bye", "nos vemos"]):
        return jsonify({"respuestas": ["¡De nada! Recuerda registrar tus movimientos para tener mejores consejos. ¡Miau, cuídate! 🐾"]})

    # Qué puedes hacer
    if any(p in texto for p in ["que puedes", "ayuda", "help", "que haces", "funciones", "comandos", "puedes hacer"]):
        return jsonify({"respuestas": [
            "Puedo ayudarte con: (1) tu balance y ahorro, (2) tu categoría más costosa, (3) ingresos y gastos, (4) la predicción del próximo mes, (5) consejos de ahorro. ¡Pregúntame por cualquiera de estos! 🐾"
        ]})

    # Balance / estado / resumen
    if any(p in texto for p in ["balance", "estado", "resumen", "como voy", "como ando", "resumi"]):
        estado = "¡Vas muy bien! 🎉" if d["balance"] >= 0 else "Estás en números rojos, revisa tus gastos. 🚨"
        return jsonify({"respuestas": [
            f"Ingresos: {dinero(d['ingresos'])} · Gastos: {dinero(d['gastos'])} · Balance: {dinero(d['balance'])}. {estado} 🐾"
        ]})

    # Ingresos
    if any(p in texto for p in ["ingreso", "cuanto gano", "cuanto entra"]):
        return jsonify({"respuestas": [
            f"Tus ingresos totales son {dinero(d['ingresos'])}. Registra cada ingreso para ver tu tendencia mes a mes. 💰"
        ]})

    # Ahorro
    if any(p in texto for p in ["ahorro", "ahorrar", "ahorra"]):
        if d["ingresos"] <= 0:
            return jsonify({"respuestas": ["Aún no registras ingresos, así que no puedo calcular tu ahorro. Comienza registrando lo que ganas. 🐾"]})
        if d["balance"] > 0:
            pct = d["balance"] / d["ingresos"] * 100
            consejo = "¡Estás por encima del 30%, excelente trabajo!" if pct >= 30 else "Aplica la regla 50/30/20 (50% necesidades, 30% deseos, 20% ahorro) para mejorarlo."
            return jsonify({"respuestas": [
                f"Actualmente ahorras un {pct:.0f}% de tus ingresos (balance {dinero(d['balance'])}). {consejo} 🐾"
            ]})
        return jsonify({"respuestas": ["Tu balance es negativo, así que no hay ahorro todavía. Pro tip: separa un 20% de cada ingreso en cuanto lo recibas. 🐾"]})

    # Gasto / categoría más costosa
    if any(p in texto for p in ["gasto", "gasto mas", "categoria", "en que gasto", "donde gasto"]):
        if not d["top_categoria"]:
            return jsonify({"respuestas": ["Aún no tienes gastos registrados para analizar. ¡Registra tus gastos! 🐾"]})
        share = f", que es el {d['top_monto'] / d['ingresos'] * 100:.0f}% de tus ingresos" if d["ingresos"] > 0 else ""
        return jsonify({"respuestas": [
            f"Tu categoría de gasto más costosa es {d['top_categoria']} con {dinero(d['top_monto'])}{share}. Intenta que ninguna categoría supere el 30% de tus ingresos. 🎯"
        ]})

    # Predicción
    if any(p in texto for p in ["predic", "proximo mes", "cuanto gastare", "futuro", "proyeccion"]):
        try:
            from analitica.modulo import predecir_gasto
            p = predecir_gasto(request.usuario_id)
            if p.get("prediccion_proximo_mes") is None:
                return jsonify({"respuestas": ["Aún no tengo suficientes datos (necesito al menos 3 meses) para predecir tu gasto del próximo mes. 🐾"]})
            return jsonify({"respuestas": [
                f"Con tu histórico, estimo que gastarás {dinero(p['prediccion_proximo_mes'])} el próximo mes (confianza: {p['confianza']}). Úsalo de referencia para presupuestar. 📈"
            ]})
        except Exception:
            return jsonify({"respuestas": ["No pude calcular la predicción en este momento. Inténtalo de nuevo. 🐾"]})

    # Anomalías
    if any(p in texto for p in ["anomali", "raro", "alerta", "sospechoso", "compra rara"]):
        try:
            from analitica.modulo import detectar_anomalias
            an = detectar_anomalias(request.usuario_id)
            if not an:
                return jsonify({"respuestas": ["No he detectado anomalías en tus gastos. ¡Tus movimientos están dentro de lo habitual! 🐾"]})
            lista = "; ".join(f"{a['fecha']} en {a['categoria']} por {dinero(a['monto'])}" for a in an[:3])
            return jsonify({"respuestas": [f"Encontré {len(an)} movimiento(s) que se salen de lo normal: {lista}. Revísalos en el panel de anomalías. 🔍"]})
        except Exception:
            return jsonify({"respuestas": ["No pude revisar anomalías en este momento. 🐾"]})

    # Consejo general
    if any(p in texto for p in ["consejo", "tip", "recomenda", "sugerencia", "como mejoro"]):
        return jsonify({"respuestas": _kitty_respuesta(d)})

    # Fallback coherente con el programa
    if d["total_movimientos"] == 0:
        return jsonify({"respuestas": [
            "No entendí bien lo que preguntaste. Como aún no tienes movimientos, anota tus ingresos y gastos para que pueda darte consejos. ¿Quieres ver ayuda? 🐾"
        ]})
    return jsonify({"respuestas": [
        "No estoy seguro de haber entendido eso. 💭 Puedo decirte tu balance, ahorro, categoría más costosa, predicción o detectar anomalías. ¿Sobre cuál preguntas?"
    ]})

