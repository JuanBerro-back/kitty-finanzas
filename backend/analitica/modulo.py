import pandas as pd
from modelos.db import get_db


def _gastos_df(id_usuario):
    conn = get_db()
    df = pd.read_sql(
        "SELECT m.fecha, m.monto, c.nombre AS categoria FROM ingresos_gastos m "
        "JOIN categorias c ON c.id=m.id_categoria "
        "WHERE m.id_usuario=%s AND m.tipo='gasto' ORDER BY fecha",
        conn,
        params=(id_usuario,),
    )
    conn.close()
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    return df


def predecir_gasto(id_usuario):
    from sklearn.linear_model import LinearRegression
    import numpy as np

    df = _gastos_df(id_usuario)
    if df.empty or df["mes"].nunique() < 3:
        return {
            "id_usuario": id_usuario,
            "prediccion_proximo_mes": None,
            "metodo": "regresion_lineal",
            "confianza": "baja",
            "detalle_por_categoria": {},
            "mensaje": "Se necesitan al menos 3 meses de gastos para predecir.",
        }
    mensual = df.groupby("mes")["monto"].sum().sort_index()
    meses = [int(m.split("-")[1]) for m in mensual.index]
    X = np.array(meses).reshape(-1, 1)
    y = mensual.values.astype(float)
    modelo = LinearRegression().fit(X, y)
    siguiente = (int(mensual.index[-1].split("-")[1]) % 12) + 1
    pred = float(modelo.predict([[siguiente]])[0])
    if pred < 0:
        pred = 0.0

    detalle = df.groupby("categoria")["monto"].mean().sort_values(ascending=False)
    confianza = "media" if df["mes"].nunique() >= 6 else "baja"
    return {
        "id_usuario": id_usuario,
        "prediccion_proximo_mes": round(pred, 2),
        "metodo": "regresion_lineal",
        "confianza": confianza,
        "mes_proximo": siguiente,
        "detalle_por_categoria": {
            c: round(float(v), 2) for c, v in detalle.items()
        },
    }


def detectar_anomalias(id_usuario):
    df = _gastos_df(id_usuario)
    if df.empty:
        return []
    resultado = []
    for categoria, grupo in df.groupby("categoria"):
        media = grupo["monto"].mean()
        desv = grupo["monto"].std()
        if pd.isna(desv) or desv == 0:
            continue
        umbral = media + 2 * desv
        for _, r in grupo[grupo["monto"] > umbral].iterrows():
            resultado.append({
                "id_usuario": id_usuario,
                "categoria": categoria,
                "monto": float(r["monto"]),
                "fecha": str(r["fecha"].date()),
                "media_categoria": float(media),
                "desviacion": float(desv),
            })
    return resultado
