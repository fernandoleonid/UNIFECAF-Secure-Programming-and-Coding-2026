import logging
import hashlib
import os

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# Correção 1 — Senhas armazenadas como hash com salt (nunca em texto plano)
def gerar_hash_senha(senha, salt=None):
    if salt is None:
        salt = os.urandom(16)
    hash_senha = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100_000)
    return salt, hash_senha


def verificar_hash_senha(senha, salt, hash_esperado):
    _, hash_calculado = gerar_hash_senha(senha, salt)
    return hash_calculado == hash_esperado


# Senhas armazenadas com hash (simulando um banco de dados)
def _criar_usuarios():
    db = {}
    for usuario, senha in [("fernando", "senha123"), ("maria", "abc456")]:
        salt, hash_senha = gerar_hash_senha(senha)
        db[usuario] = {"salt": salt, "hash": hash_senha}
    return db


usuarios = _criar_usuarios()


# Correção 2 — Substituir assert por verificação explícita com raise
# assert é removido com python -O, então nunca deve ser usado para segurança
def verificar_admin(usuario):
    if usuario != "fernando":
        raise PermissionError("Acesso negado.")
    return True


# Correção 3 — Não expor detalhes internos do erro ao usuário
# Logar o erro internamente, mas retornar mensagem genérica
def buscar_usuario(usuario):
    try:
        return usuarios[usuario]
    except KeyError:
        logger.debug("Tentativa de busca para usuário inexistente.")
        return None
    except Exception:
        logger.exception("Erro inesperado ao buscar usuário.")
        return None


# Correção 4 — Nunca registrar senhas em logs
# Registrar apenas o identificador do usuário, sem dados sensíveis
def autenticar(usuario, senha):
    try:
        dados_usuario = buscar_usuario(usuario)
        if dados_usuario is None:
            return False
        return verificar_hash_senha(senha, dados_usuario["salt"], dados_usuario["hash"])
    except Exception:
        logger.exception("Falha ao autenticar usuário.")
        return False


# Correção 5 — Mensagem genérica para evitar enumeração de usuários
# Não informar se o erro foi no usuário ou na senha
def login(usuario, senha):
    if not autenticar(usuario, senha):
        return "Credenciais inválidas."
    return "Login realizado com sucesso."


# Correção 6 — Fail Closed: em caso de erro, negar acesso (não conceder)
# O padrão seguro é negar quando algo dá errado
def verificar_permissao(usuario, recurso):
    try:
        if recurso not in ["relatorio", "dashboard"]:
            raise ValueError("Recurso não mapeado.")
        return True
    except Exception:
        logger.exception("Erro na verificação de permissão.")
        return False  # Fail Closed — nega acesso em caso de erro


if __name__ == "__main__":
    print(login("fernando", "senha123"))
    print(login("joao", "qualquer"))
    print(login("fernando", "errada"))
    print(verificar_permissao("fernando", "admin"))

    try:
        verificar_admin("fernando")
        print("Admin verificado.")
    except PermissionError as e:
        print(e)
