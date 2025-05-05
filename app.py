from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from flask import session


app = Flask(__name__)

# Conexão com o banco
def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo_usuario = request.form['tipo_usuario']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        criado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Campos opcionais
        documento_verificacao = request.form.get('documento_verificacao')
        status_verificacao = 'Pendente' if tipo_usuario == 'ONG' else None
        possui_ou_ja_teve_pets = request.form.get('possui_ou_ja_teve_pets')

        conn = get_db_connection()
        cur = conn.cursor()

        # Verifica se já existe
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if cur.fetchone():
            return 'Email já cadastrado!'

        cur.execute(''' 
            INSERT INTO usuarios 
            (nome, email, senha, tipo_usuario, telefone, endereco, documento_verificacao, status_verificacao, possui_ou_ja_teve_pets, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, email, senha, tipo_usuario, telefone, endereco, documento_verificacao, status_verificacao, possui_ou_ja_teve_pets, criado_em))

        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()

        if user:
            tipo_usuario = user['tipo_usuario']
            
            # Redireciona de acordo com o tipo de usuário
            if tipo_usuario == 'ONG':
                return redirect(url_for('cadastro_pet'))  # Redireciona para a visão da ONG
            elif tipo_usuario == 'Adotante':
                return redirect(url_for('view_adotante'))  # Redireciona para a visão do Adotante
        else:
            return 'Email ou senha inválidos!'

    return render_template('login.html')

# Nova rota para cadastro de pets (apenas para ONGs)
@app.route('/cadastro_pet', methods=['GET', 'POST'])
def cadastro_pet():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        idade = request.form['idade']
        porte = request.form['porte']
        genero = request.form['genero']
        descricao = request.form['descricao']
        status_saude = request.form['status_saude']
        id_usuario = request.form['id_usuario']  # ID da ONG que está cadastrando
        foto_url = request.form.get('foto_url', '')
        vacinado = request.form.get('vacinado', 'Não')
        castrado = request.form.get('castrado', 'Não')
        necessidades_especiais = request.form.get('necessidades_especiais', '')
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_adocao = 'Disponível'

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO pets 
            (nome, especie, raca, idade, porte, genero, descricao, status_saude, 
            id_usuario, foto_url, vacinado, castrado, necessidades_especiais, 
            data_cadastro, status_adocao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, especie, raca, idade, porte, genero, descricao, status_saude, 
              id_usuario, foto_url, vacinado, castrado, necessidades_especiais, 
              data_cadastro, status_adocao))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_ong'))
        
    return render_template('cadastro_pet.html')

# Rota para listar pets disponíveis para adoção
@app.route('/listar_pets')
def listar_pets():
    conn = get_db_connection()
    pets = conn.execute('SELECT * FROM pets WHERE status_adocao = "Disponível"').fetchall()
    conn.close()
    
    return render_template('listar_pets.html', pets=pets)

@app.route('/view_ong')
def view_ong():
    return render_template('viewONG.html')

@app.route('/view_adotante')
def view_adotante():
    return render_template('viewAdotante.html')

@app.route('/pagina_inicial')
def pagina_inicial():
    return render_template('pagina_inicial.html')

if __name__ == '__main__':
    # Criação das tabelas caso não existam
    conn = get_db_connection()
    
    # Tabela de usuários
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            documento_verificacao TEXT,
            status_verificacao TEXT,
            possui_ou_ja_teve_pets TEXT,
            criado_em TEXT
        )
    ''')
    
    # Tabela de pets
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            idade TEXT,
            porte TEXT NOT NULL,
            genero TEXT NOT NULL,
            descricao TEXT,
            status_saude TEXT,
            id_usuario INTEGER NOT NULL,
            foto_url TEXT,
            vacinado TEXT,
            castrado TEXT,
            necessidades_especiais TEXT,
            data_cadastro TEXT NOT NULL,
            status_adocao TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

    app.run(debug=True)