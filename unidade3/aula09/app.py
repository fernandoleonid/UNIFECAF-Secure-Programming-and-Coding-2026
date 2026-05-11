# app.py - Código vulnerável
from flask import Flask, request

app = Flask(__name__)

@app.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    
    # VULNERABILIDADE: SQL Injection por concatenação
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    
    # Executar query no banco...
    return f"Query executada: {query}"

if __name__ == '__main__':
    app.run()