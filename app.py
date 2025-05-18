from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

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
        documento_verificacao = request.form.get('documento_verificacao')
        status_verificacao = 'Pendente' if tipo_usuario == 'ONG' else None
        possui_ou_ja_teve_pets = request.form.get('possui_ou_ja_teve_pets')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if cur.fetchone():
            return 'Email já cadastrado!'
        cur.execute('''INSERT INTO usuarios 
            (nome, email, senha, tipo_usuario, telefone, endereco, documento_verificacao, status_verificacao, possui_ou_ja_teve_pets, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (nome, email, senha, tipo_usuario, telefone, endereco, documento_verificacao, status_verificacao, possui_ou_ja_teve_pets, criado_em))
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
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_tipo'] = user['tipo_usuario']
            session['user_email'] = user['email']

            if user['tipo_usuario'] == 'Adotante':
                return redirect(url_for('view_adotante'))
            elif user['tipo_usuario'] == 'ONG':
                return redirect(url_for('cadastro_pet'))  # ou 'cadastro_pet' se preferir
            else:
                return redirect(url_for('pagina_inicial'))  # fallback seguro

    return render_template('login.html')

@app.route('/cadastro_pet', methods=['GET', 'POST'])
def cadastro_pet():
    if request.method == 'POST':
        id_usuario = session.get('user_id')
        if id_usuario is None:
            return redirect(url_for('login'))
        nome = request.form['nome']
        especie = request.form['especie']
        raca = request.form['raca']
        idade = request.form['idade']
        porte = request.form['porte']
        genero = request.form['genero']
        descricao = request.form['descricao']
        status_saude = request.form['status_saude']
        foto_url = request.form.get('foto_url', '')
        vacinado = request.form.get('vacinado', 'Não')
        castrado = request.form.get('castrado', 'Não')
        necessidades_especiais = request.form.get('necessidades_especiais', '')
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_adocao = 'Disponível'
        conn = get_db_connection()
        conn.execute('''INSERT INTO pets 
            (nome, especie, raca, idade, porte, genero, descricao, status_saude, 
            id_usuario, foto_url, vacinado, castrado, necessidades_especiais, 
            data_cadastro, status_adocao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (nome, especie, raca, idade, porte, genero, descricao, status_saude, id_usuario, foto_url, vacinado, castrado, necessidades_especiais, data_cadastro, status_adocao))
        conn.commit()
        conn.close()
        return redirect(url_for('view_ong'))
    return render_template('cadastro_pet.html')

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

@app.route('/perfil')
def perfil():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not usuario:
        return 'Usuário não encontrado', 404
    usuario = dict(usuario)
    usuario['data_cadastro'] = datetime.strptime(usuario['criado_em'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
    return render_template('perfil.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/pagina_inicial')
def pagina_inicial():
    return render_template('pagina_inicial.html')

@app.route('/editar_perfil')
def editar_perfil():
    return "<h3>Página de edição de perfil (em construção)</h3>"

if __name__ == '__main__':
    app.run(debug=True)
