# ========================== CRIANDO API´s PARA POSTAGENS E PARA AUTORES (USUÁRIOS) ==========================

# Consultando APIs usando Postman: https://www.postman.com/
# Fazer uma request, passar a URL da API e escolher qual Verbo Http deseja utilizar

# Instalando o flask
# pip install flask

# Desintalar e instalar a biblioteca/módulo jwt no Terminal
# pip uninstall jwt
# pip install pyjwt

# Importando as bibliotecas
from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import json
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

# Definindo o método token_obrigatorio com o parâmetro f
# Obs.1: podemos aplicar este decorator a qualquer rota que precise ser segura (precise de autenticação)
# Obs.2: o parâmetro autor deverá ser o 1º parâmtro a ser passado onde o @token_obrigatorio foi aplicado
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificando se o Token foi enviado com a Requisição
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'Mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um Token, validar acesso  consultando Banco de Dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except Exception as error:
            print(error)
            return jsonify({'Mensagem': 'Token Inválido!'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


# Criando a rota para Login
@app.route('/login')
# Definindo o método login
def login():
    # Usando request.authorization para extrair as informações que foram passadas para a API (usuário e senha) e atribuindo a uma variável
    auth = request.authorization
    # Verificando se a autenticação foi realizada corretamente]
    if not auth or not auth.username or not auth.password:
        # Retorna para o usuário uma solicitação de login
        # Passando 3 parâmetros:
        # 1) Mensagem Login Inválido
        # 2) Status Code (401 - Usuário não autorizado para acessar o Endpoint)
        # 3) Um dicionário específico para garantir que seja solicitado um usuário e senha
        return make_response('Login Inválido!', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    # Se houver a autenticação, verificar se o usuário e senha existem no Banco de Dados
    usuario = Autor.query.filter_by(nome=auth.username).first()
    # Verificando se existe usuário
    if not usuario:
        # Retorna para o usuário uma solicitação de login
        return make_response('Login Inválido!', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    # Verificando se a senha está correta ou não
    if auth.password == usuario.senha:
        # Usando o jwt para criar um token que será expirado em 30 minutos e atribuindo a uma variável
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        # Retornando o token criado para o usuário
        return jsonify({'token':token})
    # Caso o usuário digite a senha incorreta
    return make_response('Senha Inválida!', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    
        


# ================================= CRIANDO UMA API PARA POSTAGENS =================================

# ------------------------ VERBO GET - OBTENDO TODOS OS RECURSOS ------------------------
# Obter todas as postagens
@app.route('/postagens')
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def obter_postagens(autor):
    # Extraindo todas as postagens do BD e atribuindo a uma variável
    postagens = Postagem.query.all()
    # Criando uma Lista vazia
    lista_de_postagens = []
    # Percorrendo cada postagem na variável postagens
    for postagem in postagens:
        # Criando um Dicionário vazio
        postagem_atual = {}
        # Atualizando as propriedades / informações que se deseja retornar para a postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        # Adicionando a postagem à Lista de Postagens
        lista_de_postagens.append(postagem_atual)
    # Retornando uma Lista de Dicionários com todos as postagens solicitadas pelo usuário
    return jsonify({'Postagens': lista_de_postagens})

      
# ------------------------ VERBO GET com Id - OBTENDO UM RECURSO COM ID ------------------------
# Obter postagens por Id
@app.route('/postagens/<int:id_postagem>', methods=['GET'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def obter_postagem_por_indice(autor, id_postagem):
    # Fazendo um filtro para obter o id_postagem passado na função para 1º registro do BD e atribuindo a uma variável
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    # Criando um Dicionário vazio
    postagem_atual = {}
    try:
        # Atualizando as propriedades / informações que se deseja retornar para a postagem
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    # Atualizando as propriedades / informações que se deseja retornar para a postagem
    postagem_atual['id_autor'] = postagem.id_autor
    # Retornando um Dicionário com a postagem solicitada pelo usuário
    return jsonify({'Postagens': postagem_atual})
 

# ------------------------ VERBO POST - INCLUINDO UM RECURSO ------------------------
# Criar novas postagens
@app.route('/postagens', methods=['POST'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def novo_postagem(autor):
    # Obtendo informações do BD e atribuindo a uma variável
    nova_postagem = request.get_json()
    # Instanciando a Classe Postagem passando os nomes das propriedades usando os índices para obter os valores das propriedades e atribuindo a uma variável
    postagem = Postagem(titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])
    # Adicionando a postagem ao Banco de Dados
    db.session.add(postagem)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que a postagem foi criado e o Status Code (200 - Sucesso)
    return jsonify({'Mensagem': 'Postagem criada com sucesso!'}, 200)


# ------------------------ VERBO PUT - ALTERANDO UM RECURSO ------------------------
# Alterar postagens
@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def alterar_postagem(autor, id_postagem):
    # Obtendo informações do BD e atribuindo a uma variável
    postagem_alterar = request.get_json()
    # Fazendo um filtro para obter o id_postagem passado na função para 1º registro do BD e atribuindo a uma variável
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    # Verificando se não existe uma postagem
    if not postagem:
        # Se True, retornando uma mensagem para o usuário
        return jsonify({'Mensagem': 'Esta postagem não foi encontrada'})
    # Tratando o erro para o caso da informação a ser alterada não ser encontrada
    try:
        # Se True, alterando o Titulo
        postagem.titulo = postagem_alterar['titulo']
    except:
        # Continua a execução
        pass
    # Adicionando a postagem ao Banco de Dados
    db.session.add(postagem)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que a postagem foi alterada e o Status Code (200 - Sucesso)
    return jsonify({'Mensagem': 'Sua postagem foi atualizada com sucesso!'}, 200)



# ------------------------ VERBO DELETE - EXCLUINDO UM RECURSO ------------------------
# Excluir postagens
@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def excluir_postagem(autor, id_postagem):
    # Fazendo um filtro para obter o id_postagem passado na função para 1º registro do BD e atribuindo a uma variável
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    # Verificando se não existe uma postagem
    if not postagem:
        # Se True, retornando uma mensagem para o usuário
        return jsonify({'Mensagem': 'Esta postagem não foi encontrada'})
    # Excluindo o registro do Banco de Dados
    db.session.delete(postagem)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que a postagem foi excluída e o Status Code (200 - Sucesso)
    return jsonify({'Mensagem': 'Sua postagem foi excluída com sucesso!'}, 200)

   
# Rodando o servidor Flask
# app.run(port=5000, host='localhost', debug=True)

# ====================================================================================================================






# ================================= CRIANDO UMA API PARA AUTORES =================================

# ------------------------ VERBO GET - OBTENDO TODOS OS RECURSOS ------------------------
# Obter todos os autores
@app.route('/autores')
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def obter_autores(autor):
    # Extraindo todos os autores do BD e atribuindo a uma variável
    autores = Autor.query.all()
    # Criando uma Lista vazia
    lista_de_autores = []
    # Percorrendo cada autor na variável autores
    for autor in autores:
        # Criando um Dicionário vazio
        autor_atual = {}
        # Atualizando as propriedades / informações que se deseja retornar para o usuário
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        # Adicionando o autor à Lista de Autores
        lista_de_autores.append(autor_atual)
    # Retornando uma Lista de Dicionários com todos os autores solicitada pelo usuário
    return jsonify({'Usuários': lista_de_autores})

      
# ------------------------ VERBO GET com Id - OBTENDO UM RECURSO COM ID ------------------------
# Obter autores por Id
@app.route('/autores/<int:id_autor>', methods=['GET'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def obter_autor_por_id(autor, id_autor):
    # Fazendo um filtro para obter o id_autor passado na função para 1º registro do BD e atribuindo a uma variável
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    # Verificando se não existe um autor
    if not autor:
        # Se True, retornando uma mensagem para o usuário
        return jsonify(f'Usuário não encontrado')
    # Se False, criando um Dicionário vazio
    autor_atual = {}
    # Atualizando as propriedades / informações que se deseja retornar para o usuário
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    # Retornando no formato de um Dicionário
    return jsonify({'Usuário': autor_atual})
  

# ------------------------ VERBO POST - INCLUINDO UM RECURSO ------------------------
# Criar novos autores
@app.route('/autores', methods=['POST'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def novo_autor(autor):
    # Obtendo informações do BD e atribuindo a uma variável
    novo_autor = request.get_json()
    # Instanciando a Classe Autor passando os nomes das propriedades usando os índices para obter os valores das propriedades e atribuindo a uma variável
    autor = Autor(nome=novo_autor['nome'], email=novo_autor['email'], senha=novo_autor['senha'])
    # Adicionando o autor ao Banco de Dados
    db.session.add(autor)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que o autor foi criado e o Status Code (200 - Criado com Sucesso)
    return jsonify({'Mensagem': 'Usuário foi criado com sucesso!'}, 200)


# ------------------------ VERBO PUT - ALTERANDO UM RECURSO ------------------------
# Alterar autores
@app.route('/autores/<int:id_autor>', methods=['PUT'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def alterar_autor(autor, id_autor):
    # Obtendo informações do BD e atribuindo a uma variável
    usuario_alterar = request.get_json()
    # Fazendo um filtro para obter o id_autor passado na função para 1º registro do BD e atribuindo a uma variável
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    # Verificando se não existe um autor
    if not autor:
        # Se True, retornando uma mensagem para o usuário
        return jsonify({'Mensagem': 'Este usuário não foi encontrado'})
    # Tratando o erro para o caso da informação a ser alterada não ser encontrada
    try:
        # Se True, alterando o Nome
        autor.nome = usuario_alterar['nome']
    except:
        # Continua a execução
        pass
    # Tratando o erro para o caso da informação a ser alterada não ser encontrada    
    try:
        # Se True, alterando o E-mail
        autor.email = usuario_alterar['email']
    except:
        # Continua a execução
        pass
    # Tratando o erro para o caso da informação a ser alterada não ser encontrada
    try:
        # Se True, alterando a Senha
        autor.senha = usuario_alterar['senha']
    except:
        # Continua a execução
        pass
    # Adicionando o autor ao Banco de Dados
    db.session.add(autor)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que o autor foi criado e o Status Code (200 - Criado com Sucesso)
    return jsonify({'Mensagem': 'Usuário foi atualizado com sucesso!'}, 200)



# ------------------------ VERBO DELETE - EXCLUINDO UM RECURSO ------------------------
# Excluir autores
@app.route('/autores/<int:id_autor>', methods=['DELETE'])
# Aplicando este decorator para uma rota que precise ser segura (precise de autenticação)
@token_obrigatorio
# Criando uma função
def excluir_autor(autor, id_autor):
    # Fazendo um filtro para obter o id_autor passado na função para 1º registro do BD e atribuindo a uma variável
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    # Verificando se não existe um autor
    if not autor:
        # Se True, retornando uma mensagem para o usuário
        return jsonify({'Mensagem': 'Este usuário não foi encontrado'})
    # Excluindo o registro do Banco de Dados
    db.session.delete(autor)
    # Salvando o Banco de Dados
    db.session.commit()
    # Retornando uma mensagem que o autor foi criado e o Status Code (200 - Criado com Sucesso)
    return jsonify({'Mensagem': 'Usuário foi excluído com sucesso!'}, 200)

   
# Rodando o servidor Flask
app.run(port=5000, host='localhost', debug=True)



