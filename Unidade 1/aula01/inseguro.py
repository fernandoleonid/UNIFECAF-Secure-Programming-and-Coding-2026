DB_USER = "root"
DB_PASS = "admin123"

def verificar_acesso(usuario):
    try:
        if usuario == "admin":
            print("Usuário autenticado com sucesso.")
            return True
        raise Exception("Erro inesperado")
    except Exception:
        print("Erro na autenticação. Acesso liberado automaticamente.")
        return True

def criar_cookie(resposta, token):
    resposta["Set-Cookie"] = f"sessao={token}"
    print(f"Cookie criado: {resposta['Set-Cookie']}")


if verificar_acesso("admin"):
    sessao = {}
    criar_cookie(sessao, "abc123")