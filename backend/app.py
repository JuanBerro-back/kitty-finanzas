from flask import Flask
from flask_cors import CORS
from modelos.db import get_db
import os

app = Flask(__name__)
CORS(app)

from rutas import usuarios, categorias, movimientos, resumen, analitica, auth, chatbot

app.register_blueprint(usuarios.bp)
app.register_blueprint(categorias.bp)
app.register_blueprint(movimientos.bp)
app.register_blueprint(resumen.bp)
app.register_blueprint(analitica.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(chatbot.bp)


@app.get("/")
def health():
    return {"status": "ok", "api": "finanzas personales"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
