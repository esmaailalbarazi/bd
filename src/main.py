## Projeto de BD
## - Jason Wrisez
## - Esmaail Albarazi

from flask import Flask, jsonify, request
from passlib.hash import sha256_crypt
import psycopg2, random

## Criação do web server
app = Flask(__name__)

## Conexão à base de dados e devolve a ligação
def db_connection():
    db = psycopg2.connect(user = "postgres", password ="postgres",
            host="127.0.0.1", port="5432", database="dbproj")
    return db

## Verifica a autenticação de um utilizador e devolve o seu id
def check_authtoken(token):
    db = db_connection()
    cur = db.cursor()

    #Procura o authtoken
    statement = """SELECT idutilizador FROM utilizador
        WHERE authtoken = %s;"""
    cur.execute(statement, (token,))

    row = cur.fetchone()
    return row[0]

## / e /dbproj/ - Mostra apenas uma mensagem
@app.route('/')
@app.route('/dbproj/')
def hello():
    return "Bem-vindo ao sistema de leilões online!"

## POST /dbproj/user/ - Regista um utilizador novo
@app.route("/dbproj/user", methods=["POST"])
def user_register():
    payload = request.get_json()
    db = db_connection()
    cur = db.cursor()
    output = {}

    try:
        #Inserir o novo utilizador
        payload["password"] = sha256_crypt.hash(payload["password"])
        values = (payload["username"], payload["password"], payload["email"])
        statement = """INSERT INTO utilizador (username, password, email)
            VALUES (%s, %s, %s);"""
        cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] Utilizador " + payload["username"] + " inserido.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("[Erro] A inserir utilizador " + payload["username"] + ".")
        output = {'erro': 500} #A DEFINIR
        return jsonify(output)

    #Devolve o id do novo utilizador
    statement = """SELECT idutilizador FROM utilizador
        WHERE username = %s;"""
    cur.execute(statement, (payload["username"],))
    row = cur.fetchone()
    if not row:
        print("[Erro] Utilizador inserido mas impossível de encontrar.")
        output = {'erro': 500} #A DEFINIR
    else:
        output = {'userId': row[0]}

    if db is not None:
        db.close()
    return jsonify(output)

## PUT /dbproj/user/ - Login de um utilizador existente
@app.route("/dbproj/user", methods=["PUT"])
def user_login():
    payload = request.get_json()
    db = db_connection()
    cur = db.cursor()
    output = {}

    #Procura o utilizador
    statement = """SELECT password FROM utilizador
        WHERE username = %s;"""
    cur.execute(statement, (payload["username"],))
    row = cur.fetchone()

    #Se o utilizador existe ou a palavra-passe está errada
    if not row:
        print("[DB] Utilizador inexistente")
        return jsonify({'erro': "AuthError"} ) #A DEFINIR
    elif not sha256_crypt.verify(payload["password"], row[0]):
        print("[DB] Palavra-passe incorreta.")
        return jsonify({'erro': "AuthError"}) #A DEFINIR

    #Gera um novo authtoken
    try:
        token = str(random.randrange(999999))
        #values = (sha256_crypt.hash(token), payload["username"],)
        values = (token, payload["username"],)
        statement = """UPDATE utilizador SET authtoken=%s WHERE username=%s"""
        cur.execute(statement, values)
        cur.execute("commit")
        output = {'authToken': token}
    except (Exception, psycopg2.DatabaseError) as error:
        print("[DB] Erro a autenticar utilizador.")
        output = {'erro': 500} #A DEFINIR
    finally:
        if db is not None:
            db.close()

    return jsonify(output)

## POST /dbproj/leilao - Criação de leilão
@app.route("/dbproj/leilao", methods=["POST"])
def new_leilao():
    payload = request.get_json()
    db = db_connection()
    cur = db.cursor()

    #Se o utilizador não estiver autenticado
    userId = check_authtoken(payload["authToken"])
    if userId is None:
        print("[DB] O utilizador não está autenticado.")
        if db is not None:
            db.close()
        return jsonify({'erro': 500}) #A DEFINIR

    #Verifica se o artigo existe
    values = (payload["artigoId"],)
    statement = "SELECT 1 FROM artigo WHERE idartigo=%s"
    cur.execute(statement, values)
    row = cur.fetchone()
    if not row:
        print("[DB] O artigo não existe.")
        if db is not None:
            db.close()
        return jsonify({'erro': 500}) #A DEFINIR

    #Verifica se o utilizador já é vendedor
    values = (payload["artigoId"],)
    statement = """SELECT 1 FROM vendedor
    utilizador_idutilizador=%s"""
    cur.execute(statement, values)
    row =cur.fetchone()

    if not row:
        #Insere o utilizador na tabela vendedor
        try:
            values = (userId,)
            statement= "INSERT INTO vendedor(utilizador_idutilizador) VALUES (%s)"
            cur.execute(statement, values)
            cur.execute("commit")
            print("[DB] Novo vendedor %sregistado com sucesso."
                %payload["titulo"])
        except (Exception, psycopg2.DatabaseError) as error:
            print("[Erro] Impossível definir utilizador %s como vendedor."
                %payload["titulo"])
            output = {'erro': 500} #A DEFINIR

    #Cria o registo na tabela leilao
    try:
        values = (payload["titulo"], payload["descricao"],
            payload["dataLimite"], payload["precoMinimo"],
            payload["precoMinimo"], row[0], payload["artigoId"],)
        statement = """INSERT INTO leilao (titulo, descricao,
            datalimite, precominimo, precoatual,
            vendedor_utilizador_idutilizador, artigo_idartigo)
            VALUES (%s, %s, %s, %s, %s, %s);"""
        cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] Leilão %s criado com sucesso.", payload["titulo"])

    except (Exception, psycopg2.DatabaseError) as error:
        print("[Erro] A inserir leilão %s." %payload["titulo"])
        output = {'erro': 500} #A DEFINIR
        if db is not None:
            db.close()
        return jsonify(output)

    #Devolve o id do novo leilão
    statement = """SELECT idleilao FROM leilao
        WHERE titulo = %s;"""
    cur.execute(statement, (payload["titulo"],))
    row = cur.fetchone()
    if not row:
        print("[Erro] Leilão inserido mas impossível de encontrar.")
        output = {'erro': 500} #A DEFINIR
    else:
        output = {'leilaoId': row[0]}

    if db is not None:
        db.close()
    return jsonify(output)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080", debug=True, threaded=True)
