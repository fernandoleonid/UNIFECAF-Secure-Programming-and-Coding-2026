import os
import secrets

# Least Privilege: usuário com permissões restritas, credenciais via variáveis de ambiente
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

def verificar_acesso(usuario):
    # Fail Secure: em caso de erro, acesso é NEGADO
    try:
        if usuario == "admin":
            print("Usuário autenticado com sucesso.")
            return True
        print("Usuário não autorizado.")
        return False
    except Exception:
        print("Erro na autenticação. Acesso negado por segurança.")
        return False

def criar_cookie(resposta, token):
    # Secure Defaults: cookie com flags de segurança habilitadas
    resposta["Set-Cookie"] = f"sessao={token}; Secure; HttpOnly; SameSite=Strict"
    print(f"Cookie criado com flags de segurança.")


if verificar_acesso("admin"):
    sessao = {}
    # Secure Defaults: token gerado de forma criptograficamente segura
    criar_cookie(sessao, secrets.token_hex(32))
