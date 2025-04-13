from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('banco.db')  # Conecta ao banco banco.db
    conn.row_factory = sqlite3.Row  # Isso faz a consulta retornar como dicionário
    return conn

# Página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Pegar os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']

        # Conectar ao banco de dados e cadastrar o usuário
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verifica se o email já existe
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = cur.fetchone()
        
        if user:
            return 'Email já cadastrado!'  # Evitar cadastrar usuários com o mesmo email
        
        # Inserir os dados no banco
        cur.execute("INSERT INTO usuarios (nome, email, senha, tipo_usuario) VALUES (?, ?, ?, ?)",
                    (nome, email, senha, tipo_usuario))
        conn.commit()  # Salva as mudanças no banco de dados
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        # Redireciona para a página de login
        return redirect(url_for('login'))

    return render_template('cadastro.html')  # Exibe o formulário de cadastro


# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', 
                            (email, senha)).fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('pagina_inicial'))  # Usuário encontrado, vai para página inicial
        else:
            return 'Email ou senha inválidos!'  # Caso o login falhe

    return render_template('login.html')

# Página inicial após login
@app.route('/pagina_inicial')
def pagina_inicial():
    return render_template('pagina_inicial.html')

if __name__ == '__main__':
    # Criar a tabela de usuários, caso ela não exista
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL,
                        senha TEXT NOT NULL,
                        tipo_usuario TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    
    app.run(debug=True)
