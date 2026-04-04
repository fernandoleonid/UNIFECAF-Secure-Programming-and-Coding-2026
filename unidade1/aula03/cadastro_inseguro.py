import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def criar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT
        )
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, senha):
    try:
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE email = '" + email + "'"
        )

        usuario = cursor.fetchone()

        if usuario:
            return f"Erro: {Exception('Usuário já cadastrado. Email: ' + email)}"

        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES ('"
            + nome + "', '" + email + "', '" + senha + "')"
        )

        conn.commit()
        logger.debug(f"Usuário cadastrado: nome={nome}, email={email}, senha={senha}")
        return "Usuário cadastrado com sucesso."

    except Exception as e:
        return f"Erro interno: {e}"

    finally:
        conn.close()

criar_banco()
print(cadastrar_usuario("Fernando", "fernando@email.com", "senha123"))
print(cadastrar_usuario("Fernando", "fernando@email.com", "senha123"))