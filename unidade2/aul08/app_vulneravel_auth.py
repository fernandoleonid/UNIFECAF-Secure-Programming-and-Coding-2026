# ==============================================================================
# AVISO IMPORTANTE: ESTE CÓDIGO CONTÉM VULNERABILIDADES INTENCIONAIS
# ==============================================================================

from flask import Flask, request, session, redirect, url_for, jsonify
import functools

app = Flask(__name__)
app.secret_key = 'chave_secreta_fraca_123'

USUARIOS = {
    '1': {'id': '1', 'nome': 'Alice', 'role': 'user', 'senha': 'senha123'},
    '2': {'id': '2', 'nome': 'Bob', 'role': 'user', 'senha': 'bob123'},
    'admin': {'id': 'admin', 'nome': 'Administrador', 'role': 'admin', 'senha': 'admin'}
}

# ==============================================================================
# VULNERABILIDADE 1: Credenciais Hardcoded e Auth Fraca
# ==============================================================================
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuario = dados.get('usuario')
    senha = dados.get('senha')
    
    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        session['usuario'] = usuario
        session['role'] = USUARIOS[usuario]['role']
        return jsonify({'mensagem': 'Login realizado com sucesso'})
    
    if usuario in USUARIOS:
        return jsonify({'erro': 'Senha incorreta'}), 401
    else:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

# ==============================================================================
# VULNERABILIDADE 2: IDOR (Insecure Direct Object Reference)
# ==============================================================================
@app.route('/api/perfil/<id_usuario>')
def ver_perfil(id_usuario):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if id_usuario in USUARIOS:
        return jsonify(USUARIOS[id_usuario])
    
    return jsonify({'erro': 'Perfil não encontrado'}), 404

# ==============================================================================
# VULNERABILIDADE 3: Escalonamento Vertical (Broken Access Control)
# ==============================================================================
@app.route('/admin/dashboard')
def admin_dashboard():

    if session.get('role') == 'admin':
        return jsonify({'mensagem': 'Bem-vindo ao Painel Administrativo', 'dados': 'Secretos'})
    
    return jsonify({'erro': 'Acesso negado. Apenas administradores.'}), 403

# ==============================================================================
# VULNERABILIDADE 4: Gerenciamento de Sessão Inseguro
# ==============================================================================
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
 
    app.run(host='127.0.0.1', port=5000, debug=False)