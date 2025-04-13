from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

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
                return redirect(url_for('view_ong'))  # Redireciona para a visão da ONG
            elif tipo_usuario == 'Adotante':
                return redirect(url_for('view_adotante'))  # Redireciona para a visão do Adotante
        else:
            return 'Email ou senha inválidos!'

    return render_template('login.html')

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
    # Criação da tabela 'usuarios' caso não exista
    conn = get_db_connection()
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
    conn.commit()
    conn.close()

    app.run(debug=True)
