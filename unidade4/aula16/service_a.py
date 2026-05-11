from flask import Flask, jsonify
import requests

app = Flask(__name__)

# TOKEN hardcoded (inseguro - proposital)
INTERNAL_TOKEN = "segredo-interno"

# ----------------------------------
# CHAMADA INSEGURA
# ----------------------------------
@app.route("/inseguro")
def inseguro():

    # Não envia token
    response = requests.get("http://localhost:5001/dados-internos")

    return jsonify({
        "status": "sem segurança",
        "resposta": response.json()
    })


# ----------------------------------
# CHAMADA SEGURA (COM TOKEN)
# ----------------------------------
@app.route("/seguro")
def seguro():

    response = requests.get(
        "http://localhost:5001/dados-internos",
        headers={"X-Internal-Token": INTERNAL_TOKEN}
    )

    return jsonify({
        "status": "com validação",
        "resposta": response.json()
    })


if __name__ == "__main__":
    app.run(port=5000)