import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Vulnerabilidade 1 — Senha hardcoded
DB_PASSWORD = "senha_super_secreta123"

usuarios = {
    "fernando": "senha123",
    "maria": "abc456"
}


# Vulnerabilidade 2 — Uso de assert para segurança
def verificar_admin(usuario):
    assert usuario == "fernando", "Acesso negado."
    return True


# Vulnerabilidade 3 — Stack trace exposto ao usuário
def buscar_usuario(usuario):
    try:
        return usuarios[usuario]
    except Exception as e:
        print(f"Erro interno: {e}")
        return None


# Vulnerabilidade 4 — Senha no log
def autenticar(usuario, senha):
    try:
        senha_cadastrada = buscar_usuario(usuario)
        if senha_cadastrada == senha:
            return True
        else:
            return False
    except Exception as e:
        logger.error(
            f"Falha ao autenticar. Usuário: {usuario}, "
            f"Senha: {senha}, Erro: {e}"
        )
        return False


# Vulnerabilidade 5 — Mensagens diferentes por tipo de erro
def login(usuario, senha):
    if usuario not in usuarios:
        return "Usuário não encontrado."
    if usuarios[usuario] != senha:
        return "Senha incorreta."
    return "Login realizado com sucesso."


# Vulnerabilidade 6 — Fail Open
def verificar_permissao(usuario, recurso):
    try:
        if recurso not in ["relatorio", "dashboard"]:
            raise ValueError("Recurso não mapeado.")
        return True
    except Exception as e:
        logger.warning(f"Erro na verificação: {e}")
        return True


if __name__ == "__main__":
    print(login("fernando", "senha123"))
    print(login("joao", "qualquer"))
    print(login("fernando", "errada"))
    print(verificar_permissao("fernando", "admin"))
    print(verificar_admin("fernando"))