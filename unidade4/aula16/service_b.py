from flask import Flask, request, jsonify

app = Flask(__name__)

# TOKEN SIMPLES (hardcoded - propositalmente inseguro)
INTERNAL_TOKEN = "segredo-interno"

@app.route("/dados-internos")
def dados_internos():

    token = request.headers.get("X-Internal-Token")

    # Validação simples
    if token != INTERNAL_TOKEN:
        return jsonify({"erro": "Acesso negado"}), 403

    return jsonify({
        "dados": "Informação sensível do serviço interno"
    })


if __name__ == "__main__":
    app.run(port=5001)