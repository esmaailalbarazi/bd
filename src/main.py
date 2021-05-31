## Projeto de BD
## - Jason Wrisez
## - Esmaail Albarazi


from flask import Flask, jsonify, request
from passlib.hash import sha256_crypt
import psycopg2, random


## Criação do web server
app = Flask(__name__)


## Conexão à base de dados, devolve a ligação a ser usada
def db_connection():
    db = psycopg2.connect(user = "postgres", password ="pass12345",
            host="127.0.0.1", port="5432", database="dbproj")
    return db


## Verifica a autenticação de um utilizador e devolve o id
## do utilizador correspondente
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

    #Insere o novo utilizador com encriptação da palavra-passe
    try:
       # payload["password"] = sha256_crypt.hash(payload["password"])
        values = (payload["username"], payload["password"], payload["email"])
        statement = """INSERT INTO utilizador (username, password, email)
            VALUES (%s, %s, %s);"""
        cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] Utilizador " + payload["username"] + " registado.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] A registar utilizador %s."%payload["username"])
        output = {'erro': 333}
        return jsonify(output)

    #Seleciona o id do novo utilizador, gerado pelo postgreSQL
    statement = """SELECT idutilizador FROM utilizador
        WHERE username = %s;"""
    cur.execute(statement, (payload["username"],))
    row = cur.fetchone()
    if not row:
        print("[Erro] Utilizador registado mas impossível de encontrar.")
        output = {'erro': 111}
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

    #Seleciona o utilizador
    statement = """SELECT password FROM utilizador
        WHERE username = %s;"""
    cur.execute(statement, (payload["username"],))
    row = cur.fetchone()

    #Retorna erro se o utilizador não existir ou se a palavra-passe for errada
    if not row:
        print("[Erro] Utilizador inexistente")
        if db is not None:
            db.close()
        return jsonify({'erro': "AuthError"} )
    #elif not sha256_crypt.verify(payload["password"], row[0]):     //PASSWORD ENCRIPTADA
        print("[Erro] Palavra-passe incorreta.")
        if db is not None:
            db.close()
        return jsonify({'erro': "AuthError"})

    #Gera um novo token de autenticação
    try:
        token = str(random.randrange(999999))
        #values = (sha256_crypt.hash(token), payload["username"],)
        values = (token, payload["username"],)
        statement = """UPDATE utilizador SET authtoken=%s WHERE username=%s"""
        cur.execute(statement, values)
        cur.execute("commit")
        output = {'authToken': token}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[DB] Erro a autenticar utilizador.")
        output = {'erro': 222}

    if db is not None:
        db.close()
    return jsonify(output)


## POST /dbproj/leilao - Criação de leilão
@app.route("/dbproj/leilao", methods=["POST"])
def new_leilao():
    payload = request.get_json()
    db = db_connection()
    cur = db.cursor()

    #Retorna erro se o utilizador não estiver autenticado
    userId = check_authtoken(payload["authToken"])
    if userId is None:
        print("[DB] O utilizador não está autenticado.")
        if db is not None:
            db.close()
        return jsonify({'erro': 444})

    #Retorna erro se o artigo a por em venda não existe
    values = (payload["artigoId"],)
    statement = "SELECT 1 FROM artigo WHERE idartigo=%s"
    cur.execute(statement, values)
    row = cur.fetchone()
    if not row:
        print("[DB] O artigo não existe.")
        if db is not None:
            db.close()
        return jsonify({'erro': 111})

    #Verifica se o utilizador já é vendedor
    values = (userId,)
    statement = """SELECT utilizador_idutilizador FROM vendedor
    WHERE utilizador_idutilizador=%s"""
    cur.execute(statement, values)
    row = cur.fetchone()

    #Insere o utilizador na tabela vendedor, se não existir
    if not row:
        try:
            values = (userId,)
            statement= """INSERT INTO vendedor (utilizador_idutilizador)
            VALUES (%s)"""
            cur.execute(statement, values)
            cur.execute("commit")
            print("[DB] Novo vendedor (id: %s) registado com sucesso." % userId)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print("[Erro] Impossível definir utilizador (id: %s) como vendedor."
                % userId)
            output = {'erro': 333}

    #Cria o registo na tabela leilao
    try:
        values = (payload["titulo"], payload["descricao"],
            payload["dataLimite"], payload["precoMinimo"],
            payload["precoMinimo"], userId, payload["artigoId"],)
        statement = """INSERT INTO leilao (titulo, descricao,
            datalimite, precominimo, precoatual,
            vendedor_utilizador_idutilizador, artigo_idartigo)
            VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] Leilão %s criado com sucesso." % payload["titulo"])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] A inserir leilão %s." % payload["titulo"])
        output = {'erro': 333}
        if db is not None:
            db.close()
        return jsonify(output)

    #Seleciona o ID do novo leilão, gerado pelo postgreSQL
    statement = """SELECT idleilao FROM leilao
        WHERE titulo = %s;"""
    cur.execute(statement, (payload["titulo"],))
    row = cur.fetchone()
    if not row:
        print("[Erro] Leilão inserido mas impossível de encontrar.")
        output = {'erro': 111}
    else:
        output = {'leilaoId': row[0]}

    if db is not None:
        db.close()
    return jsonify(output)


## GET /dbproj/leiloes - Listar todos os leilões no sistema
@app.route("/dbproj/leiloes", methods=["GET"])
def list_leiloes():
    db = db_connection()
    cur = db.cursor()

    cur.execute("SELECT idleilao, descricao FROM leilao;")
    rows = cur.fetchall()
    output = []
    for row in rows:
        output.append({"leilaoId": row[0], "descricao": row[1]})

    if db is not None:
        db.close()
    return jsonify(output)


## GET /dbproj/leiloes/<keyword> - Listar leilões no sistema, pesquisando
## a keyword nos códigos dos artigos e na descrição dos leilões
@app.route("/dbproj/leiloes/<keyword>", methods=["GET"])
def search_leiloes(keyword):
    db = db_connection()
    cur = db.cursor()

    #O % serve para encontrar caracteres antes e depois da keyword
    keyword = '%' + keyword + '%'
    #Seleciona os leilões com a keyword na descrição ou nos códigos
    statement = """SELECT idleilao, descricao FROM leilao
        WHERE descricao LIKE %s OR artigo_idartigo IN (
	       SELECT artigo_idartigo FROM artigoean WHERE codigo LIKE %s
	       UNION
	       SELECT artigo_idartigo FROM artigoisbn WHERE codigo LIKE %s
        )"""
    values = (keyword, keyword, keyword,)
    cur.execute(statement, values)
    rows = cur.fetchall()
    output = []
    for row in rows:
        output.append({"leilaoId": row[0], "descricao": row[1]})

    if db is not None:
        db.close()
    return jsonify(output)


## GET /dbproj/leilao/<leilaoId> - Devolve todos os detalhes do leilão
## com o ID recebido
@app.route("/dbproj/leilao/<leilaoId>", methods=["GET"])
def get_leilao(leilaoId):
    db = db_connection()
    cur = db.cursor()

    #Devolve os dados da tabela de leilões
    values = (leilaoId,)
    statement = "SELECT * FROM leilao WHERE idleilao=%s"
    cur.execute(statement,values)
    row = cur.fetchone()
    if not row:
        print("[DB] Nenhum leilão existente com o id recebido.")
        if db is not None:
            db.close()
        return jsonify({"erro": 111})
    output = {"leilaoId": row[0], "titulo": row[1], "descricao": row[2],
        "dataLimite": row[3], "precoMinimo": row[4], "precoAtual": row[5],
        "terminou": row[6]}
    vendedorId = row[7]
    artigoId = row[8]

    #Devolve o username do vendedor
    values = (vendedorId,)
    statement = "SELECT username FROM utilizador WHERE idutilizador=%s"
    cur.execute(statement,values)
    row = cur.fetchone()
    output["vendedor"] = row[0]

    #Devolve o código do artigo a ser vendido
    values = (artigoId, artigoId, )
    statement = """SELECT codigo FROM artigoean WHERE artigo_idartigo=%s
        UNION SELECT codigo FROM artigoisbn WHERE artigo_idartigo=%s
        LIMIT 1"""
    cur.execute(statement,values)
    row = cur.fetchone()
    output["artigo"] = row[0]

    #Devolve as mensagens escritas nesse leilão (mural)
    mensagens = []
    values = (leilaoId,)
    statement = """SELECT utilizador_idutilizador, conteudo FROM mensagem
        WHERE leilao_idleilao=%s"""
    cur.execute(statement, values)
    rows = cur.fetchall()
    for row in rows:
        mensagens.append({"utilizadorId": row[0], "mensagem": row[1]})
    output["mural"] = mensagens

    #Devolve as licitações nesse leilão
    licitacoes = []
    statement = """SELECT data, comprador_utilizador_idutilizador, valor
        FROM licitacao WHERE leilao_idleilao=%s
        ORDER BY data,milisegundos DESC"""
    cur.execute(statement, values)
    rows = cur.fetchall()
    for row in rows:
        licitacoes.append({"data": row[0], "compradorId": row[1],
        "valor": row[2]})
    output["licitacoes"] = licitacoes

    if db is not None:
        db.close()
    return jsonify(output)


## GET /dbproj/atividade/<userId>"- Consultar a atividade em leilões de um
## utilizador, tanto como vendedor como comprador
@app.route("/dbproj/atividade/<userId>", methods=["GET"])
def get_atividade(userId):
    db = db_connection()
    cur = db.cursor()

    #Obtem a lista de leilões em que é o vendedor
    output = []
    values = (userId,userId,)
    statement = """SELECT idleilao, descricao FROM leilao
        WHERE vendedor_utilizador_idutilizador=%s
        UNION
        SELECT idleilao, descricao FROM leilao WHERE idleilao IN (
    	   SELECT leilao_idleilao FROM licitacao
           WHERE comprador_utilizador_idutilizador=%s
        )"""
    cur.execute(statement,values)
    rows = cur.fetchall()
    for row in rows:
        output.append({"idLeilao": row[0], "descricao": row[1]})

    if db is not None:
        db.close()
    return jsonify(output)


## POST /dbproj/licitar/<leilaoId> - Criar uma licitação num
## determinado leilão
@app.route("/dbproj/licitar/<leilaoId>", methods=["POST"])
def create_licitacao(leilaoId):

    payload = request.get_json()
    #Verifica se o utilizador está autenticado
    userId = check_authtoken(payload["authToken"])
    if not userId:
        print("[DB] O utilizador não está autenticado.")
        return jsonify({"erro": 444})

    db = db_connection()
    cur = db.cursor()

    #Verificar se o leilão existe e tirar o preço atual, bloqueando a linha
    cur.execute("begin transaction")
    statement = "SELECT precoatual FROM leilao WHERE idleilao=%s FOR UPDATE"
    values = (leilaoId,)
    cur.execute(statement, values)
    row = cur.fetchone()
    if not row:
        print("[Erro] Não existe nenhum leilão com o ID %s." %leilaoId)
        if db is not None:
            db.close()
        return jsonify({"erro": 111})
    precoAtual = row[0]

    #Verifica que a licitação é mais alta do que o preço atual
    if int(precoAtual) >= int(payload["valor"]):
        print("[Erro] O valor da licitação deve ser maior que o preço atual.")
        if db is not None:
            db.close()
        return jsonify({"erro": 111})

    #Verifica se o utilizador já é comprador
    values = (userId,)
    statement = """SELECT utilizador_idutilizador FROM comprador
    WHERE utilizador_idutilizador=%s"""
    cur.execute(statement, values)
    row = cur.fetchone()

    #Insere o utilizador na tabela vendedor, se não existir
    if not row:
        try:
            values = (userId,)
            statement = """INSERT INTO comprador (utilizador_idutilizador)
            VALUES (%s)"""
            cur.execute(statement, values)
            print("[DB] Novo comprador (id: %s) registado com sucesso." % userId)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print("[Erro] Impossível definir utilizador (id: %s) como comprador."
                % userId)
            if db is not None:
                db.close()
            return jsonify({'erro': 333})

    #Registar nova licitação e atualizar o preço atual
    try:
        statement = """INSERT INTO licitacao (valor, data,
            comprador_utilizador_idutilizador, leilao_idleilao)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"""
        values = (payload["valor"], userId, leilaoId,)
        cur.execute(statement, values)
        statement = "UPDATE leilao SET precoatual=%s WHERE idleilao=%s"
        values = (payload["valor"], leilaoId,)
        cur.execute(statement, values)
        print("[DB] Licitação registada com sucesso.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] Impossível criar licitação.")
        if db is not None:
            db.close()
        return jsonify({'erro': 333})

    #Procurar o id da nova licitação e da última para notificar
    statement = """SELECT idlicitacao, comprador_utilizador_idutilizador
        FROM licitacao ORDER BY valor DESC LIMIT 2"""
    cur.execute(statement)
    rows = cur.fetchall()
    licitacaoId = rows[0][0]
    lastUserId = rows[1][1]
    print(licitacaoId)
    print(lastUserId)
    cur.execute("commit")

    #Notificar o utilizador da última licitação
    notificacao = "O utilizador xxx ultrapassou a sua licitação de "\
        + str(precoAtual) +"€."
    statement = """INSERT INTO notificacaolicitacao (texto, data,
        licitacao_idlicitacao, utilizador_idutilizador)
        VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"""
    values = (notificacao, licitacaoId, lastUserId,)
    cur.execute(statement, values)
    cur.execute("commit")

    if db is not None:
        db.close()
    return jsonify({"licitacaoId": licitacaoId})


## PUT /dbproj/leilao/<leilaoId> - Editar um leilão existente, guardando as
## versões anteriores
@app.route("/dbproj/leilao/<leilaoId>", methods=["PUT"])
def edit_leilao(leilaoId):
    payload = request.get_json()
    db = db_connection()
    cur = db.cursor()
    #Verifica se o utilizador está autenticado
    userId = check_authtoken(payload["authToken"])
    if not userId:
        print("[DB] O utilizador não está autenticado.")
        return jsonify({"erro": 500}) #A DEFINIR

    #Verifica se o utilizador é o vendedor do leilão
    statement = """SELECT 1 FROM leilao
        WHERE vendedor_utilizador_idutilizador=%s, idleilao=%s"""
    values = (userId,leilaoId,)
    cur.execute(statement,values)
    row = cur.fetchone()
    if not row:
        print("[DB] O utilizador não é vendedor do leilão ID:%s.") %leilaoId
        return jsonify({"erro": 500}) #A DEFINIR

    #Copiar o leilão atual e termina-o
    try:
        cur.execute("begin transaction")
        values = (leilaoId,)
        statement = """INSERT into leilao (titulo, descricao, datalimite,
            precominimo, precoatual, vendedor_utilizador_idutilizador,
            artigo_idartigo, terminou)
            SELECT titulo, descricao, datalimite, precominimo, precoatual,
            vendedor_utilizador_idutilizador, artigo_idartigo, terminou
            FROM leilao WHERE idleilao = %s"""
        cur.execute(statement, values)
        statement = """UPDATE leilao SET terminou='true' WHERE idleilao = %s"""
        cur.execute(statement, values)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] A encontrar ou copiar leilão id:%s." % leilaoId)
        output = {'erro': 333}
        if db is not None:
            db.close()
        return jsonify(output)

    #Encontra o id do novo leilão
    statement = "SELECT idleilao FROM leilao ORDER BY idleilao DESC LIMIT 1"
    cur.execute(statement)
    novoLeilaoId = cur.fetchone()

    #Passa as mensagens e licitações do antigo para o novo
    try:
        values = (novoLeilaoId, leilaoId,)
        statement = """UPDATE licitacao SET leilao_idleilao=%s
            WHERE leilao_idleilao = %s"""
        cur.execute(statement, values)
        statement = """UPDATE mensagem SET leilao_idleilao=%s
            WHERE leilao_idleilao = %s"""
        cur.execute(statement, values)
        print("[DB] Foi feita uma cópia do leilão antigo.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("""[Erro] A copiar licitações e mensagens para o novo leilão
            id:%s.""" % novoLeilaoId)
        output = {'erro': 222}
        if db is not None:
            db.close()
        return jsonify(output)

    #Atualiza os dados para os recebidos
    statement = "UPDATE leilao SET "
    values = ()
    if "titulo" in payload:
        statement += "titulo = %s,"
        values += (payload["titulo"],)
    if "descricao" in payload:
        statement += "descricao = %s,"
        values += (payload["descricao"],)
    if "dataLimite" in payload:
        statement += "datalimite = %s,"
        values += (payload["dataLimite"],)
    if "precoMinimo" in payload:
        statement += "precominimo = %s,"
        values += (payload["precoMinimo"],)
    statement = statement[:-1]
    statement += " WHERE idleilao=%s"
    values += (novoLeilaoId,)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] O novo leilão foi atualizado")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("""[Erro] A copiar licitações e mensagens para o novo leilão
            id:%s.""" % novoLeilaoId)
        output = {'erro': 222}
        if db is not None:
            db.close()
        return jsonify(output)

    #Devolve o novo leilão atualizado
    statement = "SELECT idleilao, titulo, descricao  FROM leilao WHERE idleilao=%s"
    values = (novoLeilaoId,)
    cur.execute(statement, values)
    row = cur.fetchone()
    output = {"leilaoId": row[0], "titulo": row[1], "descricao": row[2]}
    return jsonify(output)


## POST /dbproj/leilao/<leilaoId>/mensagem - Cria uma mensagem associada a um
## leilão e notifica o vendedor e toda a gente que já mandou mensagens
@app.route("/dbproj/leilao/<leilaoId>/mensagem", methods=["POST"])
def create_mensagem(leilaoId):

    payload = request.get_json()
    #Verifica se o utilizador está autenticado
    userId = check_authtoken(payload["authToken"])
    if not userId:
        print("[DB] O utilizador não está autenticado.")
        return jsonify({"erro": 444})

    db = db_connection()
    cur = db.cursor()

    #Verificar se o leilão existe
    statement = """SELECT vendedor_utilizador_idutilizador FROM leilao
        WHERE idleilao=%s"""
    values = (leilaoId,)
    cur.execute(statement, values)
    row = cur.fetchone()
    if not row:
        print("[DB] Não existe nenhum leilão com o ID %s." %leilaoId)
        return jsonify({"erro": 111})
    vendedorId = (row[0],)

    #Procura quem já escreveu mensagens acerca do leilão (para notificar)
    statement = """SELECT DISTINCT utilizador_idutilizador FROM mensagem
        WHERE leilao_idleilao=%s"""
    values = (leilaoId,)
    cur.execute(statement, values)
    participantes = cur.fetchall()
    print(participantes)

    #Registar a mensagem no leilão
    try:
        statement = """INSERT INTO mensagem
            (conteudo, utilizador_idutilizador, leilao_idleilao, data)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"""
        values = (payload["mensagem"], userId, leilaoId,)
        cur.execute(statement, values)
        print("[DB] Mensagem criada com sucesso.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] A criar nova mensagem.")
        if db is not None:
            db.close()
        return jsonify({"erro": 333})

    #Retira o ID da nova mensagem (mensagemId, username, leilao)
    statement = """SELECT idmensagem FROM mensagem
        ORDER BY idmensagem DESC LIMIT 1"""
    cur.execute(statement)
    row = cur.fetchone()
    cur.execute("commit")
    mensagemId = row[0]
    statement = "SELECT username FROM utilizador WHERE idutilizador=%s"
    values = (userId,)
    cur.execute(statement, values)
    row = cur.fetchone()
    username = row[0]
    statement = "SELECT titulo, descricao FROM leilao WHERE idleilao=%s"
    values = (leilaoId,)
    cur.execute(statement, values)
    row = cur.fetchone()
    leilao = row[0] + " - " + row[1]

    #Notifica os participantes
    if vendedorId not in participantes:
        participantes.append(vendedorId)
    notificacao = "O utilizador " + username + \
        " escreveu uma mensagem no leilão " + leilao + "."
    try:
        for row in participantes:
            statement = """INSERT INTO notificacaomensagem (texto, data,
                mensagem_idmensagem, utilizador_idutilizador)
                VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"""
            values = (notificacao, mensagemId) + row
            cur.execute(statement, values)
        cur.execute("commit")
        print("[DB] Os utilizadores participantes foram notificados \
        com sucesso.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] A notificar utilizadores da nova mensagem.")

    if db is not None:
        db.close()
    return jsonify({"mensagemId": mensagemId})


## GET /dbproj/notificacoes"- Devolve as notificações pertencentes ao utilizador
## logado, recebendo o seu token
@app.route("/dbproj/notificacoes", methods=["GET"])
def list_notificacoes():

    payload = request.get_json()
    #Verifica se o utilizador está autenticado
    userId = check_authtoken(payload["authToken"])
    if not userId:
        print("[DB] O utilizador não está autenticado.")
        return jsonify({"erro": 444})

    db = db_connection()
    cur = db.cursor()

    #Procura as notificações de licitações
    statement = """SELECT * FROM notificacaolicitacao
        WHERE utilizador_idutilizador=%s ORDER BY data DESC"""
    values = (userId,)
    cur.execute(statement, values)
    rows = cur.fetchall()
    notifLic = []
    for row in rows:
        statement = """SELECT valor, data FROM licitacao
            WHERE idlicitacao=%s"""
        values = (row[2],)
        cur.execute(statement, values)
        licitacao = cur.fetchone()
        notifLic.append({"tipo": "licitacao", "info": row[0], "data": row[1],
            "conteudo":{"valor": licitacao[0], "dataLicitacao": licitacao[1]}})

    #Procura as notificações de mensagens
    statement = """SELECT * FROM notificacaomensagem
        WHERE utilizador_idutilizador=%s ORDER BY data DESC"""
    values = (userId,)
    cur.execute(statement, values)
    rows = cur.fetchall()
    notifMsg = []
    for row in rows:
        statement = """SELECT conteudo, data FROM mensagem
            WHERE idmensagem=%s"""
        values = (row[2],)
        cur.execute(statement, values)
        mensagem = cur.fetchone()
        notifMsg.append({"data": row[1], "info": row[0],
            "conteudo":{"conteudo": mensagem[0], "dataMensagem": mensagem[1]}})

    output = {"licitacoes": notifLic, "mensagens": notifMsg}
    if db is not None:
        db.close()
    return jsonify(output)


## PUT /dbproj/leilao/<leilaoId>/end"- Termina um leilão no momento,
## independentemente da hora
@app.route("/dbproj/leilao/<leilaoId>/end", methods=["PUT"])
def end_leilao(leilaoId):

    db = db_connection()
    cur = db.cursor()
    output = {}

    #Verifica se o utilizador é o vendedor do leilão
    statement = """SELECT 1 FROM leilao
        WHERE vendedor_utilizador_idutilizador=%s, idleilao=%s"""
    values = (userId,leilaoId,)
    cur.execute(statement,values)
    row = cur.fetchone()
    if not row:
        print("[DB] O utilizador não é vendedor do leilão ID:%s.") %leilaoId
        return jsonify({"erro": 500}) #A DEFINIR

    #Seleciona o bool "terminou" para atualizar, bloqueando a linha
    try:
        statement = "UPDATE leilao SET terminou='true' WHERE idleilao=%s"
        values = (leilaoId,)
        cur.execute(statement, values)
        cur.execute("commit")
        output = {"leilaoId": leilaoId}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("[Erro] Impossível terminar o leilão referido.")
        output = {"erro": 222}
    finally:
        if db is not None:
            db.close()
    return jsonify(output)


## Main
if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080", debug=True, threaded=True)
