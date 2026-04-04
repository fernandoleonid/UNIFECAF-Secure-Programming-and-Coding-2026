# ==============================================================================
# AVISO IMPORTANTE: ESTE CÓDIGO CONTÉM VULNERABILIDADES INTENCIONAIS
# Destina-se exclusivamente para fins educacionais e de treinamento em segurança.
# NÃO utilize este código em ambientes de produção.
# ==============================================================================

from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Inicializa o banco de dados em memória para teste
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (1, 'admin')")
    conn.commit()
    conn.close()

# ==============================================================================
# VULNERABILIDADE 1: SQL Injection
# OWASP Top 10: A03:2021 – Injection
# CWE: CWE-89 - SQL Injection
# Bandit: B608 (Hardcoded SQL Expressions)
# ==============================================================================
@app.route('/sql', methods=['GET', 'POST'])
def sql_injection():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Query vulnerável: concatenação direta de input do usuário
    query = f"SELECT * FROM users WHERE id = {user_id}"  # [BANDIT: B608]
    
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    
    return f"<h1>Resultado da Query</h1><p>{result}</p>"

# ==============================================================================
# VULNERABILIDADE 2: Cross-Site Scripting (XSS)
# OWASP Top 10: A03:2021 – Injection
# CWE: CWE-79 - Improper Neutralization of Input During Web Page Generation
# Bandit: B701 (Jinja2 templates without autoescape)
# ==============================================================================
@app.route('/xss', methods=['GET', 'POST'])
def xss_injection():
    name = request.args.get('name', 'Visitante')
    
    # Renderização vulnerável: input do usuário direto no template sem escape
    template = f"<h1>Olá, {name}</h1>"  # [BANDIT: B701 / XSS Risk]
    
    return render_template_string(template)

# ==============================================================================
# VULNERABILIDADE 3: Command Injection
# OWASP Top 10: A03:2021 – Injection
# CWE: CWE-78 - OS Command Injection
# Bandit: B605 (Start a process with a shell), B609 (Linux Commands Will Shell Injection)
# ==============================================================================
@app.route('/cmd', methods=['GET', 'POST'])
def command_injection():
    ip = request.args.get('ip', '127.0.0.1')
    
    # Execução de comando do sistema com input do usuário
    # Vulnerável a injeção de comandos adicionais (ex: 127.0.0.1; cat /etc/passwd)
    os.system(f"ping -c 4 {ip}")  # [BANDIT: B605, B609]
    
    return f"<h1>Ping executado para: {ip}</h1>"

# ==============================================================================
# VULNERABILIDADE 4: Security Misconfiguration (Debug Ativo)
# OWASP Top 10: A05:2021 - Security Misconfiguration
# Bandit: B201 (Flask app with debug=True)
# ==============================================================================
if __name__ == '__main__':
    init_db()
    # Rodar com debug=True em produção expõe o debugger e permite execução de código
    app.run(host='0.0.0.0', port=5000, debug=True)  # [BANDIT: B201]