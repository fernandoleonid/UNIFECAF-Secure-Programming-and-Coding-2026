# sistema_relatorios.py
# CÓDIGO INTENCIONALMENTE INSEGURO - Fins didáticos
# Aula 04 - Shift Left Security: Segurança desde o Design

from flask import Flask, jsonify, request
import sqlite3
import os
import platform

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS relatorios (
        id INTEGER PRIMARY KEY,
        titulo TEXT,
        conteudo TEXT
    )''')
    cursor.execute("INSERT OR IGNORE INTO relatorios (id, titulo, conteudo) VALUES (1, 'Relatório Financeiro', 'Dados sigilosos')")
    cursor.execute("INSERT OR IGNORE INTO relatorios (id, titulo, conteudo) VALUES (2, 'Relatório RH', 'Salários dos funcionários')")
    conn.commit()
    conn.close()


init_db()


@app.route('/relatorios', methods=['GET'])
def listar_relatorios():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)


@app.route('/relatorios/admin', methods=['GET'])
def admin_relatorios():

    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify({"admin": True, "dados": dados})


@app.route('/relatorios/deletar', methods=['GET'])
def deletar_relatorio():

    id_relatorio = request.args.get('id')
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM relatorios WHERE id = {id_relatorio}")
    conn.commit()
    conn.close()
    return jsonify({"status": "deletado"})


@app.route('/sistema/info', methods=['GET'])
def info_sistema():

    return jsonify({
        "sistema": platform.system(),
        "versao": platform.version(),
        "host": platform.node(),
        "diretorio": os.getcwd(),
        "usuario": os.getlogin()
    })


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)