from flask import Flask, jsonify
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


# ── Manejadores globales de error: siempre devuelven JSON ──────────────────────
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Solicitud inválida", "detalle": str(e)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "No autorizado"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Acceso denegado"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método no permitido"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Captura cualquier excepción no manejada y devuelve JSON."""
    import traceback
    print(traceback.format_exc())
    return jsonify({"error": "Error inesperado", "detalle": str(e)}), 500
# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

