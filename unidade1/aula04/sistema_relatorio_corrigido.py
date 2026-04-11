# sistema_relatorio_corrigido.py
# CÓDIGO CORRIGIDO - Fins didáticos
# Aula 04 - Shift Left Security: Segurança desde o Design

from flask import Flask, jsonify, request
from functools import wraps
import sqlite3
import os
import platform

app = Flask(__name__)

# [CORREÇÃO 5] Secret key para sessões (em produção, usar variável de ambiente)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# Simulação simples de token de autenticação (em produção, usar JWT ou OAuth)
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'token-seguro-exemplo')


def requer_autenticacao(f):
    """[CORREÇÃO 2] Decorator para verificar autenticação via token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {ADMIN_TOKEN}":
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated


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
@requer_autenticacao  # [CORREÇÃO 2] Endpoint protegido
def listar_relatorios():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)


@app.route('/relatorios/admin', methods=['GET'])
@requer_autenticacao  # [CORREÇÃO 2] Endpoint admin protegido com autenticação
def admin_relatorios():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify({"admin": True, "dados": dados})


@app.route('/relatorios/deletar', methods=['DELETE'])  # [CORREÇÃO 3] Mudado de GET para DELETE
@requer_autenticacao  # [CORREÇÃO 2] Requer autenticação para deletar
def deletar_relatorio():
    # [CORREÇÃO 6] Validação de input
    id_relatorio = request.args.get('id')
    if not id_relatorio or not id_relatorio.isdigit():
        return jsonify({"erro": "ID inválido. Deve ser um número inteiro."}), 400

    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    # [CORREÇÃO 1] Query parametrizada para evitar SQL Injection
    cursor.execute("DELETE FROM relatorios WHERE id = ?", (id_relatorio,))
    conn.commit()
    linhas_afetadas = cursor.rowcount
    conn.close()

    if linhas_afetadas == 0:
        return jsonify({"erro": "Relatório não encontrado"}), 404

    return jsonify({"status": "deletado", "id": id_relatorio})


# [CORREÇÃO 4] Endpoint de info do sistema protegido e com dados reduzidos
@app.route('/sistema/info', methods=['GET'])
@requer_autenticacao
def info_sistema():
    return jsonify({
        "sistema": platform.system(),
        "versao_app": "1.0.0"
        # Removidos: versão do SO, hostname, diretório e usuário
    })


if __name__ == '__main__':
    # [CORREÇÃO 5] Debug desabilitado e bind apenas em localhost
    app.run(host='127.0.0.1', port=5000, debug=False)
