from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ----------------------------------
# RATE LIMITER
# ----------------------------------
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]
)

# ----------------------------------
# ENDPOINT PÚBLICO
# ----------------------------------
@app.route("/")
def home():
    return jsonify({"msg": "API Online"})


# ----------------------------------
# ENDPOINT DEBUG (INSEGURO)
# ----------------------------------
# @app.route("/debug")
# def debug():
#     return jsonify({
#         "debug": True,
#         "version": "1.0.0",
#         "server": "dev-local"
#     })


# ----------------------------------
# LOGIN PROTEGIDO
# ----------------------------------
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.json

    user = data.get("user")
    password = data.get("password")

    if user == "admin" and password == "123456":
        return jsonify({"msg": "Login OK"})

    return jsonify({"erro": "Usuário ou senha inválidos"}), 401


# ----------------------------------
# API PÚBLICA COM LIMITADOR
# ----------------------------------
@app.route("/api/publica")
@limiter.limit("10 per minute")
def publica():
    return jsonify({"msg": "Dados públicos"})


# ----------------------------------
# HEALTH CHECK
# ----------------------------------
# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"})


# ----------------------------------
# MAIN
# ----------------------------------
if __name__ == "__main__":
    app.run(debug=True)