# ==============================================================================
# VERSÃO CORRIGIDA: Todas as vulnerabilidades foram tratadas
# Baseado no arquivo app_vulneravel_injection.py
# ==============================================================================

from flask import Flask, request, render_template_string
from markupsafe import escape
import sqlite3
import os
import hashlib

app = Flask(__name__)

def hash_password(password):
    """Gera hash SHA-256 da senha (em produção, usar bcrypt ou argon2)."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # CORREÇÃO: Senhas armazenadas com hash em vez de texto plano
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', ?)", (hash_password('senha_secreta_123'),))
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'maria', ?)", (hash_password('maria@2024'),))
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (3, 'joao', ?)", (hash_password('joao_pass!'),))
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (4, 'professor', ?)", (hash_password('prof_root_99'),))
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco TEXT)")
    conn.commit()
    conn.close()

# ==============================================================================
# CORREÇÃO 1: SQL Injection → Query Parametrizada
# ==============================================================================
@app.route('/sql', methods=['GET', 'POST'])
def sql_injection():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # CORREÇÃO: Usar placeholder (?) em vez de f-string na query
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    conn.close()

    # CORREÇÃO: Escapar a saída HTML para evitar XSS refletido
    return f"<h1>Resultado da Query</h1><p>{escape(str(result))}</p>"

# ==============================================================================
# CORREÇÃO 2: SSTI/XSS → Variável passada como contexto do template
# ==============================================================================
@app.route('/xss', methods=['GET', 'POST'])
def xss_injection():
    name = request.args.get('name', 'Visitante')

    # CORREÇÃO: Passar variável como parâmetro do template (auto-escape do Jinja2)
    template = "<h1>Olá, {{ name }}</h1>"
    return render_template_string(template, name=name)

# ==============================================================================
# CORREÇÃO 3: Stored XSS → Dados escapados na saída via template Jinja2
# ==============================================================================
@app.route('/xss-stored', methods=['GET', 'POST'])
def xss_stored():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome', '')
        preco = request.form.get('preco', '')
        cursor.execute("INSERT INTO products (nome, preco) VALUES (?, ?)", (nome, preco))
        conn.commit()

    cursor.execute("SELECT nome, preco FROM products")
    produtos = cursor.fetchall()
    conn.close()

    # CORREÇÃO: Passar os dados como variável do template Jinja2
    # O Jinja2 faz auto-escape de variáveis {{ }}, prevenindo XSS
    template = '''
    <html><head><style>
    body, form{font-family:Arial;display:flex;flex-direction:column;align-items:center;padding:20px}
    input{width:100%;padding:8px;box-sizing:border-box;margin-bottom:10px}
    button{padding:10px 20px;background:#007bff;color:#fff;border:none;cursor:pointer}
    table{width:100%;border-collapse:collapse;margin-top:20px}
    th,td{border:1px solid #ddd;padding:10px;text-align:left}
    th{background:#f4f4f4}
    </style></head>
    <body>
        <h1>Cadastro de Produtos</h1>
        <form method="POST">
            <label><b>Nome do Produto:</b></label>
            <input type="text" name="nome" placeholder="Ex: Notebook Dell">
            <label><b>Preco:</b></label>
            <input type="text" name="preco" placeholder="Ex: R$ 3.500,00">
            <button type="submit">Cadastrar</button>
        </form>
        <table>
            <thead><tr><th>Produto</th><th>Preco</th></tr></thead>
            <tbody>
                {% for produto in produtos %}
                <tr><td>{{ produto[0] }}</td><td>{{ produto[1] }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    '''
    return render_template_string(template, produtos=produtos)


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000)
