from flask import Flask, request, jsonify, session
import jwt
import datetime

app = Flask(__name__)
app.secret_key = "segredo-aula"

JWT_SECRET = "jwt-super-seguro"

usuarios = {
    "fernando": "123456"
}

# -------------------------                    
# LOGIN COM SESSÃO
# -------------------------
@app.route("/login-session", methods=["POST"])
def login_session():
    data = request.json

    if usuarios.get(data["user"]) == data["password"]:
        session["user"] = data["user"]
        return jsonify({"msg": "Login com sessão OK"})

    return jsonify({"erro": "Credenciais inválidas"}), 401


@app.route("/perfil-session")
def perfil_session():
    if "user" not in session:
        return jsonify({"erro": "Não autenticado"}), 401

    return jsonify({"user": session["user"]})


# -------------------------
# LOGIN COM JWT
# -------------------------
@app.route("/login-token", methods=["POST"])
def login_token():
    data = request.json

    if usuarios.get(data["user"]) == data["password"]:

        token = jwt.encode(
            {
                "user": data["user"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            },
            JWT_SECRET,
            algorithm="HS256"
        )

        return jsonify({"token": token})

    return jsonify({"erro": "Credenciais inválidas"}), 401


@app.route("/perfil-token")
def perfil_token():
    auth = request.headers.get("Authorization")

    if not auth:
        return jsonify({"erro": "Token ausente"}), 401

    token = auth.replace("Bearer ", "")

    try:
        dados = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({"user": dados["user"]})

    except:
        return jsonify({"erro": "Token inválido ou expirado"}), 401


if __name__ == "__main__":
    app.run(debug=True)