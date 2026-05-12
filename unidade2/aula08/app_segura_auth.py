# ==============================================================================
# VERSÃO CORRIGIDA — Autenticação e Autorização Seguras
# ==============================================================================

import os
import functools
from datetime import timedelta

from flask import Flask, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# --- CORREÇÃO 1: secret_key forte gerada aleatoriamente (ou via variável de ambiente) ---
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# --- CORREÇÃO: Configuração segura de cookies ---
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # impede acesso via JavaScript
    SESSION_COOKIE_SAMESITE='Lax', # proteção contra CSRF
    SESSION_COOKIE_SECURE=True,    # apenas HTTPS (desabilitar em dev local se necessário)
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # expiração de sessão
)

# --- CORREÇÃO: Proteção CSRF ---
csrf = CSRFProtect(app)

# --- CORREÇÃO: Rate limiting contra brute-force ---
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# --- CORREÇÃO 2: Senhas armazenadas com hash (bcrypt via werkzeug) ---
USUARIOS = {
    '1':     {'id': '1',     'nome': 'Alice',          'role': 'user',  'senha_hash': generate_password_hash('senha123')},
    '2':     {'id': '2',     'nome': 'Bob',            'role': 'user',  'senha_hash': generate_password_hash('bob123')},
    'admin': {'id': 'admin', 'nome': 'Administrador',  'role': 'admin', 'senha_hash': generate_password_hash('Admin@Forte!2024')},
}


# ==============================================================================
# Decorador: exige autenticação
# ==============================================================================
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'erro': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return wrapper


# ==============================================================================
# Decorador: exige role de admin (verificado na base, não na sessão)
# ==============================================================================
def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        usuario_id = session.get('usuario')
        if not usuario_id:
            return jsonify({'erro': 'Autenticação necessária'}), 401
        # CORREÇÃO 3 (escalonamento vertical): role verificado na base, não no cookie
        usuario = USUARIOS.get(usuario_id)
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    return wrapper


# ==============================================================================
# CORREÇÃO 1: Login seguro — sem enumeração, com rate limit
# ==============================================================================
@app.route('/login', methods=['POST'])
@csrf.exempt          # API JSON; em produção, usar token CSRF ou autenticação por header
@limiter.limit("5 per minute")  # CORREÇÃO: limita tentativas de login
def login():
    dados = request.json
    if not dados:
        return jsonify({'erro': 'Dados inválidos'}), 400

    usuario = dados.get('usuario', '')
    senha = dados.get('senha', '')

    user = USUARIOS.get(usuario)

    # CORREÇÃO (enumeração): mensagem genérica, mesma para usuário ou senha inválidos
    if not user or not check_password_hash(user['senha_hash'], senha):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    # CORREÇÃO (session fixation): regenerar sessão no login
    session.clear()
    session['usuario'] = usuario
    session.permanent = True  # ativa o PERMANENT_SESSION_LIFETIME
    return jsonify({'mensagem': 'Login realizado com sucesso'})


# ==============================================================================
# CORREÇÃO 2 (IDOR): Usuário só acessa o próprio perfil; admin acessa qualquer
# ==============================================================================
@app.route('/api/perfil/<id_usuario>')
@login_required
def ver_perfil(id_usuario):
    usuario_logado = session['usuario']
    role_logado = USUARIOS.get(usuario_logado, {}).get('role')

    # CORREÇÃO (IDOR): apenas o próprio perfil ou admin
    if id_usuario != usuario_logado and role_logado != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    user = USUARIOS.get(id_usuario)
    if not user:
        return jsonify({'erro': 'Perfil não encontrado'}), 404

    # CORREÇÃO: nunca retornar o hash da senha
    return jsonify({
        'id': user['id'],
        'nome': user['nome'],
        'role': user['role'],
    })


# ==============================================================================
# CORREÇÃO 3 (Escalonamento Vertical): usa decorator com verificação na base
# ==============================================================================
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return jsonify({'mensagem': 'Bem-vindo ao Painel Administrativo', 'dados': 'Secretos'})


# ==============================================================================
# CORREÇÃO 4: Logout seguro — limpa a sessão inteira
# ==============================================================================
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()  # CORREÇÃO: limpa tudo, não só 'usuario'
    return jsonify({'mensagem': 'Logout realizado com sucesso'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
