# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura_e_longa_aqui_para_producao' # MUDE esta chave!

def obter_conexao_bd():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo_usuario = request.form['tipo_usuario']
        nome_usuario = request.form['nome_usuario']
        email_usuario = request.form['email_usuario']
        senha_usuario = request.form['senha_usuario']
        
        telefone_usuario = request.form.get('telefone_usuario')
        endereco_usuario = request.form.get('endereco_usuario')
        criado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        documento_verificacao_ong = None
        status_verificacao_ong = None
        possui_ja_teve_pets_adotante = None

        if tipo_usuario == 'ONG':
            documento_verificacao_ong = request.form.get('documento_verificacao_ong')
            status_verificacao_ong = 'Pendente'
        elif tipo_usuario == 'Adotante':
            possui_ja_teve_pets_adotante = request.form.get('possui_ja_teve_pets_adotante')

        conn = obter_conexao_bd()
        cur = conn.cursor()

        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email_usuario,))
        if cur.fetchone():
            conn.close()
            return render_template('cadastro.html', error='E-mail já cadastrado! Por favor, use outro ou faça login.')

        try:
            cur.execute('''INSERT INTO usuarios 
                (nome, email, senha, tipo_usuario, telefone, endereco,
                documento_verificacao, status_verificacao, possui_ou_ja_teve_pets, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (nome_usuario, email_usuario, senha_usuario, tipo_usuario, telefone_usuario, endereco_usuario,
                documento_verificacao_ong, status_verificacao_ong, possui_ja_teve_pets_adotante, criado_em))
            conn.commit()
            conn.close()
            return redirect(url_for('login', success='Cadastro realizado com sucesso!'))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"Erro no cadastro: {e}")
            return render_template('cadastro.html', error=f'Ocorreu um erro ao cadastrar. Tente novamente.')

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_login = request.form['email_login']
        senha_login = request.form['senha_login']

        conn = obter_conexao_bd()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email_login, senha_login)).fetchone()
        conn.close()

        if usuario:
            session['id_usuario'] = usuario['id']
            session['nome_usuario'] = usuario['nome']
            session['tipo_usuario'] = usuario['tipo_usuario']
            session['email_usuario'] = usuario['email']

            if usuario['tipo_usuario'] == 'Adotante':
                return redirect(url_for('ver_adotante'))
            elif usuario['tipo_usuario'] == 'ONG':
                return redirect(url_for('ver_ong'))
        else:
            return render_template('login.html', error='E-mail ou senha incorretos.')
    
    return render_template('login.html')

@app.route('/cadastro_pet', methods=['GET', 'POST'])
def cadastro_pet():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'ONG':
        return redirect(url_for('login'))

    if request.method == 'POST':
        id_ong = session.get('id_usuario')
        
        nome_pet = request.form['nome_pet']
        especie_pet = request.form['especie_pet']
        raca_pet = request.form.get('raca_pet', '')
        idade_pet = request.form.get('idade_pet', '')
        porte_pet = request.form['porte_pet']
        genero_pet = request.form['genero_pet']
        descricao_pet = request.form['descricao_pet']
        status_saude_pet = request.form['status_saude_pet']
        foto_url_pet = request.form.get('foto_url_pet', '')
        vacinado_pet = request.form.get('vacinado_pet', 'Não')
        castrado_pet = request.form.get('castrado_pet', 'Não')
        necessidades_especiais_pet = request.form.get('necessidades_especiais_pet', '')
        data_cadastro_pet = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_adocao_pet = 'Disponível'

        conn = obter_conexao_bd()
        try:
            conn.execute('''INSERT INTO pets 
                (nome, especie, raca, idade, porte, genero, descricao, status_saude,
                id_usuario, foto_url, vacinado, castrado, necessidades_especiais,
                data_cadastro, status_adocao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (nome_pet, especie_pet, raca_pet, idade_pet, porte_pet, genero_pet, descricao_pet, status_saude_pet,
                id_ong, foto_url_pet, vacinado_pet, castrado_pet, necessidades_especiais_pet,
                data_cadastro_pet, status_adocao_pet))
            conn.commit()
            conn.close()
            return redirect(url_for('ver_ong', success_pet='Pet cadastrado com sucesso!'))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"Erro ao cadastrar pet: {e}")
            return render_template('cadastro_pet.html', error=f'Ocorreu um erro ao cadastrar o pet. Tente novamente.')

    return render_template('cadastro_pet.html')

@app.route('/listar_pets')
def listar_pets():
    conn = obter_conexao_bd()
    
    query = 'SELECT * FROM pets WHERE status_adocao = "Disponível"'
    parametros = []

    especie_filtro = request.args.get('especie_filtro')
    porte_filtro = request.args.get('porte_filtro')
    genero_filtro = request.args.get('genero_filtro')

    if especie_filtro:
        query += ' AND especie = ?'
        parametros.append(especie_filtro)
    if porte_filtro:
        query += ' AND porte = ?'
        parametros.append(porte_filtro)
    if genero_filtro:
        query += ' AND genero = ?'
        parametros.append(genero_filtro)

    pets = conn.execute(query, parametros).fetchall()
    conn.close()
    return render_template('listar_pets.html', pets=pets)

@app.route('/pet/<int:id_pet>')
def ver_detalhes_pet(id_pet):
    conn = obter_conexao_bd()
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (id_pet,)).fetchone()
    
    solicitacao_existente = None
    if 'id_usuario' in session and session['tipo_usuario'] == 'Adotante':
        id_adotante = session['id_usuario']
        solicitacao_existente = conn.execute(
            'SELECT * FROM solicitacoes_adocao WHERE id_pet = ? AND id_adotante = ?',
            (id_pet, id_adotante)
        ).fetchone()

    conn.close()

    if not pet:
        return "Pet não encontrado ou não disponível.", 404
    
    pet_dict = dict(pet)

    return render_template('detalhes_pet.html', pet=pet_dict, solicitacao_existente=solicitacao_existente)

@app.route('/solicitar_adocao/<int:id_pet>', methods=['POST'])
def solicitar_adocao(id_pet):
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'Adotante':
        return redirect(url_for('login', error='Você precisa estar logado como Adotante para solicitar adoção.'))

    id_adotante = session['id_usuario']
    mensagem = request.form.get('mensagem', '')

    conn = obter_conexao_bd()

    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (id_pet,)).fetchone()
    if not pet or pet['status_adocao'] != 'Disponível':
        conn.close()
        return redirect(url_for('ver_detalhes_pet', id_pet=id_pet, error='Este pet não está disponível para adoção no momento.'))

    solicitacao_existente = conn.execute(
        'SELECT * FROM solicitacoes_adocao WHERE id_pet = ? AND id_adotante = ?',
        (id_pet, id_adotante)
    ).fetchone()

    if solicitacao_existente:
        conn.close()
        return redirect(url_for('ver_detalhes_pet', id_pet=id_pet, error='Você já enviou uma solicitação para este pet.'))

    try:
        data_solicitacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_solicitacao = 'Pendente'

        conn.execute('''INSERT INTO solicitacoes_adocao
            (id_pet, id_adotante, data_solicitacao, status, mensagem)
            VALUES (?, ?, ?, ?, ?)''',
            (id_pet, id_adotante, data_solicitacao, status_solicitacao, mensagem))
        
        conn.execute('UPDATE pets SET status_adocao = "Em Processo" WHERE id = ?', (id_pet,))
        
        conn.commit()
        conn.close()
        return redirect(url_for('minhas_adocoes', success='Sua solicitação de adoção foi enviada! Acompanhe o status aqui!'))

    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"Erro ao solicitar adoção: {e}")
        return redirect(url_for('ver_detalhes_pet', id_pet=id_pet, error='Ocorreu um erro ao enviar sua solicitação. Tente novamente.'))

@app.route('/ver_ong')
def ver_ong():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'ONG':
        return redirect(url_for('login'))
    return render_template('viewONG.html')

@app.route('/ver_adotante')
def ver_adotante():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'Adotante':
        if session.get('tipo_usuario') == 'ONG':
            return redirect(url_for('ver_ong'))
        return redirect(url_for('login'))
    return render_template('viewAdotante.html')

@app.route('/perfil')
def perfil():
    id_usuario_logado = session.get('id_usuario')
    if not id_usuario_logado:
        return redirect(url_for('login'))

    conn = obter_conexao_bd()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id_usuario_logado,)).fetchone()
    conn.close()

    if not usuario:
        return 'Usuário não encontrado', 404
    
    usuario_dict = dict(usuario)
    if usuario_dict.get('criado_em'):
        try:
            usuario_dict['data_cadastro_formatada'] = datetime.strptime(usuario_dict['criado_em'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        except ValueError:
            usuario_dict['data_cadastro_formatada'] = 'Data inválida'
    
    return render_template('perfil.html', usuario=usuario_dict)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/pagina_inicial')
def pagina_inicial():
    if 'id_usuario' in session:
        if session.get('tipo_usuario') == 'Adotante':
            return redirect(url_for('ver_adotante'))
        elif session.get('tipo_usuario') == 'ONG':
            return redirect(url_for('ver_ong'))
    return redirect(url_for('login'))

@app.route('/editar_perfil')
def editar_perfil():
    return "<h3>Página de edição de perfil (em construção)</h3>"

@app.route('/minhas_adocoes')
def minhas_adocoes():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'Adotante':
        return redirect(url_for('login'))
    
    id_adotante = session.get('id_usuario')
    conn = obter_conexao_bd()
    
    # Busca solicitações do adotante, incluindo dados do pet
    adocoes = conn.execute('''
        SELECT sa.*, p.nome AS nome_pet, p.especie AS especie_pet, p.foto_url AS foto_pet
        FROM solicitacoes_adocao sa
        JOIN pets p ON sa.id_pet = p.id
        WHERE sa.id_adotante = ?
        ORDER BY sa.data_solicitacao DESC
    ''', (id_adotante,)).fetchall()
    
    conn.close()

    return render_template('minhas_adocoes.html', adocoes=adocoes)

@app.route('/meus_pets_ong')
def meus_pets_ong():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'ONG':
        return redirect(url_for('login'))
    
    id_ong = session.get('id_usuario')
    conn = obter_conexao_bd()
    pets_da_ong = conn.execute('SELECT * FROM pets WHERE id_usuario = ?', (id_ong,)).fetchall()
    conn.close()
    
    return render_template('meus_pets_ong.html', pets=pets_da_ong)

@app.route('/solicitacoes_adocao')
def solicitacoes_adocao():
    if 'id_usuario' not in session or session.get('tipo_usuario') != 'ONG':
        return redirect(url_for('login'))
    
    id_ong = session.get('id_usuario')
    conn = obter_conexao_bd()
    
    solicitacoes = conn.execute('''
        SELECT sa.*, p.nome AS nome_pet, u.nome AS nome_adotante, u.email AS email_adotante
        FROM solicitacoes_adocao sa
        JOIN pets p ON sa.id_pet = p.id
        JOIN usuarios u ON sa.id_adotante = u.id
        WHERE p.id_usuario = ?
        ORDER BY sa.data_solicitacao DESC
    ''', (id_ong,)).fetchall()
    
    conn.close()

    return render_template('solicitacoes_adocao.html', solicitacoes=solicitacoes)


if __name__ == '__main__':
    conn = obter_conexao_bd()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            documento_verificacao TEXT,
            status_verificacao TEXT,
            possui_ou_ja_teve_pets TEXT,
            criado_em TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            idade TEXT,
            porte TEXT NOT NULL,
            genero TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status_saude TEXT NOT NULL,
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS solicitacoes_adocao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pet INTEGER NOT NULL,
            id_adotante INTEGER NOT NULL,
            data_solicitacao TEXT NOT NULL,
            status TEXT NOT NULL,
            mensagem TEXT,
            FOREIGN KEY (id_pet) REFERENCES pets (id),
            FOREIGN KEY (id_adotante) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    conn.close()

    app.run(debug=True) 