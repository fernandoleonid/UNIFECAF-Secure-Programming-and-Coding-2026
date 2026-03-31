# sistema_relatorios.py
# CÓDIGO INTENCIONALMENTE INSEGURO - Fins didáticos
# Aula 1.4 - Shift Left Security: Segurança desde o Design

from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

# ----------------------------------------------------------------
# DECISÃO DE DESIGN INSEGURA 1: Superfície de ataque desnecessária
# O sistema expõe endpoints administrativos na mesma API pública,
# sem qualquer separação de contexto ou restrição de acesso.
# Identificável na fase de design, antes do código existir.
# ----------------------------------------------------------------

@app.route('/relatorios', methods=['GET'])
def listar_relatorios():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    # DECISÃO DE DESIGN INSEGURA 2: Information Disclosure (STRIDE)
    # O endpoint retorna todos os campos da tabela, incluindo dados
    # sensíveis que não são necessários para o consumidor da API.
    # Uma modelagem de ameaças teria identificado esse risco antes
    # da implementação.
    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)


@app.route('/relatorios/admin', methods=['GET'])
def admin_relatorios():
    # DECISÃO DE DESIGN INSEGURA 3: Ausência de controle de acesso (STRIDE - Elevation of Privilege)
    # O endpoint administrativo não exige autenticação nem autorização.
    # Qualquer cliente que conheça a rota tem acesso total.
    # Essa decisão deveria ter sido bloqueada na fase de design,
    # onde papéis e permissões precisam ser definidos explicitamente.
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relatorios")
    dados = cursor.fetchall()
    conn.close()
    return jsonify({"admin": True, "dados": dados})


@app.route('/relatorios/deletar', methods=['GET'])
def deletar_relatorio():
    # DECISÃO DE DESIGN INSEGURA 4: Superfície de ataque desnecessária + Fail Open
    # Uma operação destrutiva exposta via GET, sem autenticação,
    # sem confirmação e sem restrição de acesso.
    # O sistema falha de forma aberta: na ausência de controle,
    # a operação é permitida por padrão.
    id_relatorio = request.args.get('id')
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM relatorios WHERE id = {id_relatorio}")
    conn.commit()
    conn.close()
    return jsonify({"status": "deletado"})


@app.route('/sistema/info', methods=['GET'])
def info_sistema():
    # DECISÃO DE DESIGN INSEGURA 5: Information Disclosure (STRIDE)
    # Endpoint que expõe informações internas do sistema operacional
    # e do ambiente. Não tem função para o consumidor da API.
    # É superfície de ataque criada por ausência de modelagem de ameaças.
    return jsonify({
        "sistema": os.uname().sysname,
        "versao": os.uname().release,
        "host": os.uname().nodename,
        "diretorio": os.getcwd(),
        "usuario": os.getlogin()
    })


if __name__ == '__main__':
    # DECISÃO DE DESIGN INSEGURA 6: Superfície de ataque desnecessária
    # O servidor sobe exposto em todas as interfaces de rede (0.0.0.0)
    # com debug ativo, o que expõe o Werkzeug debugger publicamente.
    # Essa configuração deveria ter sido definida como restrita por padrão
    # desde o design, não deixada para o desenvolvedor decidir na implementação.
    app.run(host='0.0.0.0', port=5000, debug=True)