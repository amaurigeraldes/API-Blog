# Aula 16 - Criar estrutura inicial de tabelas autor e postagem C/ SQLAlchemy

# Documentação sobre Models no SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/models/

# Instalando a biblioteca
# pip install flask-sqlalchemy

# Importando os Módulos que serão utilizados
from flask import Flask                    # Criação da API
from flask_sqlalchemy import SQLAlchemy    # Criação do Banco de Dados


# Passo a passo a ser seguido:
# 1) Criar uma API
app = Flask(__name__)

# 2) Criar uma instância de SQLAlchemy
# Gerando um acesso de autenticação único para a aplicação
app.config['SECRET_KEY'] = '@Geraldes1963*'
# Conectando a um BD Local
# Obs.1: o Banco de Dados blog.db será criado dentro da pasta instance
# Obs.2: para fazer a conexão com um BD Online pesquisar por CONNECTION STRING ORACLE ou CONNECTION STRING SQL SERVER 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' 
# Obs.3: fazendo uma conexão com um Banco de Dados POSTGRESQL do supabase.com usando a PASSWORD: nOGA8tdwSaewyu8o
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nOGA8tdwSaewyu8o@db.ymwjcdknnojerpnqkwpb.supabase.co:5432/postgres' 
# Instanciando o SQLAlchemy e atribuindo a uma variável
db = SQLAlchemy(app)
# Especificando que a variável será tipada como SQLAlchemy
db:SQLAlchemy

# 3) Definir a estrutura da tabela Postagem (sem usar o SQL)
# Criando uma classe e instanciando para ser herdada da classe db.Model (permite criar tabelas)
class Postagem(db.Model):
    # Definindo a estrutura da Tabela 
    # Obs.: uma tabela postagem deverá conter id_postagem, titulo e autor

    # Criando um nome para a Tabela
    __tablename__ = 'postagem'
    
    # Definindo as variáveis que se tornarão os campos (colunas) da tabela
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor')) # passando o nome da Tabela e o id da Tabela

# 4) Definir a estrutura da tabela Autor
# Criando uma classe e instanciando para ser herdada da classe db.Model (permite criar tabelas)
class Autor(db.Model):
    # Definindo a estrutura da Tabela 
    # Obs.: uma tabela autor deverá conter id_autor, nome, email, senha, admin, postagens

    # Criando um nome para a Tabela
    __tablename__ = 'autor'

    # Definindo as variáveis que se tornarão os campos (colunas) da tabela
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem') # passando o Nome da Classe

# -------------------- Para que a estrutura de banco de dados seja inicializada da forma correta --------------------
# 1) Criando a função para garantir que o BD não seja criado e dropado todas as vezes que rodar este código
def inicializar_banco():
    # Criando um gerenciador de contextos
    with app.app_context():
        # Executando o comando para a criação da Estrutura Inicial do Banco de Dados
        db.drop_all()
        db.create_all()
        # Criando usuários administradores e atribuindo a uma variável
        autor = Autor(nome='geraldes', email='amaurimgeraldes@gmail.com', senha='123456', admin=True)
        # Adicionando o autor ao Banco de Dados
        db.session.add(autor)
        # Salvando o Banco de Dados
        db.session.commit()

# 2) Para garantir que a função inicializar_banco() só será chamada quando quisermos
# Obs.1: a função só será chamada quando rodarmos o arquivo 9-estrutura_banco_de_dados.py diretamente
# Obs.2: caso contrário ela não será chamada e não teremos o Banco de Dados sendo apagado e reconstruído a cada momento que fizermos uso da classe db
if __name__ == '__main__':
    inicializar_banco()


'''

Nossa estrutura atual:

1) Nós já temos uma classe que representa uma postagem no nosso blog
2) Nós já temos uma classe que representa um autor no nosso blog
3) Já temos uma API para criar novas postagens
4) Nos resta agora fazer o seguinte:
    4.1) Criar uma API para criar novos autores
    4.2) Adicionar banco de dados a cada chamado do nosso apis autores e postagem
    4.3) Adicionar autenticação a nossas apis de postagem e autores

'''
