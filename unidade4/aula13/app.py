# app.py
# Aula 13 - Segurança em APIs na prática
# Requer: pip install flask graphene flask-graphql

from flask import Flask, jsonify, request
from flask_graphql import GraphQLView
import graphene

app = Flask(__name__)

# ----------------------------
# Banco fake
# ----------------------------
usuarios = {
    1: {"id": 1, "nome": "Fernando", "email": "fernando@email.com"},
    2: {"id": 2, "nome": "Maria", "email": "maria@email.com"},
}

# ----------------------------
# AUTENTICAÇÃO SIMPLES
# Header: X-User-Id
# ----------------------------
def usuario_logado():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return None
    return int(user_id)

# ==================================================
# 1. REST INSEGURO (BOLA / IDOR)
# ==================================================
@app.route("/api/inseguro/usuarios/<int:user_id>")
def api_insegura(user_id):
    user = usuarios.get(user_id)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(user)

# ==================================================
# 2. REST SEGURO
# ==================================================
@app.route("/api/seguro/usuarios/<int:user_id>")
def api_segura(user_id):
    logado = usuario_logado()

    if not logado:
        return jsonify({"erro": "Não autenticado"}), 401

    if logado != user_id:
        return jsonify({"erro": "Acesso negado"}), 403

    return jsonify(usuarios[user_id])

# ==================================================
# 3. RATE LIMITING SIMPLES
# ==================================================
contador = {}

@app.route("/api/publica")
def publica():
    ip = request.remote_addr

    contador[ip] = contador.get(ip, 0) + 1

    if contador[ip] > 5:
        return jsonify({"erro": "Rate limit excedido"}), 429

    return jsonify({"mensagem": "API pública OK"})


# ==================================================
# 4. GRAPHQL
# ==================================================
class Usuario(graphene.ObjectType):
    id = graphene.Int()
    nome = graphene.String()
    email = graphene.String()

class Query(graphene.ObjectType):
    usuario = graphene.Field(Usuario, id=graphene.Int(required=True))

    def resolve_usuario(self, info, id):
        # Inseguro: retorna tudo
        data = usuarios.get(id)
        if data:
            return Usuario(**data)
        return None

schema = graphene.Schema(query=Query)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True
    )
)

# ==================================================
# MAIN
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)