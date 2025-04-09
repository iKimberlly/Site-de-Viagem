from flask import Flask, url_for, render_template, request, redirect, session, flash, jsonify
import base64
from conexao import get_db_connection
from functools import wraps
import os


if os.environ.get('VIRTUAL_ENV') is None:
    print("Virtual environment is not active. Activating...")
    os.system('venv/Scripts/activate')  


app = Flask(__name__, static_folder='static')

app.secret_key = 'chavepararodar'


@app.route("/")
def home():
    conn = get_db_connection()
    conn.close()
    return render_template('HomePage/index.html')


@app.route("/turismo")
def turismo():
    conn = get_db_connection()
    passagem = conn.execute('SELECT nome, descricao, preco, img FROM passagem').fetchall()
    conn.close()
    return render_template('HomePage/turismo.html', passagem=passagem)

@app.route("/cadastro")
def cadastro():
    return render_template('HomePage/cadastro.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function


@app.route("/login")
def login():
    return render_template('HomePage/login.html')


@app.route("/sair")
@login_required
def usuario_logout():
    session.clear()
    flash('Logout bem-sucedido!', 'success')
    return redirect(url_for('home'))


@app.route("/usuario")
@login_required
def usuario_logado():
    conn = get_db_connection()
    passagem = conn.execute('SELECT nome, descricao, pass_id FROM passagem').fetchall()
    conn.close()
    return render_template('HomePage/usuario.html', passagem=passagem)

@app.route("/HomePage/cadastrar_cliente", methods=['POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        email = request.form.get('email')
        celular = request.form.get('celular')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO cliente (nome, senha, email, celular) VALUES(?, ?, ?, ?)', 
                    (nome, senha, email, celular))
        conn.commit()
        conn.close()
        return redirect(url_for('usuario_logado'))
    return render_template('HomePage/cadastro.html')


@app.route("/validate_login", methods=["POST", "GET"])
def validate_login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cliente WHERE email = ? and senha = ?", (email, senha))
    cliente = cursor.fetchone()
    conn.close()

    if cliente:
        session['senha'] = cliente['senha']
        session['email'] = cliente['email']
        flash('Login bem-sucedido!', 'success')
        return redirect(url_for('usuario_logado'))
    else:
        flash('Login falhou. Verifique suas credenciais.', 'danger')
        return redirect(url_for('login'))


@app.route("/carrinho")
def carrinho():
    return render_template('HomePage/carrinho.html')

@app.route('/finalizar_carrinho', methods=['POST'])
def finalizar():
    cart = request.json
    print(cart)
    return jsonify({'message': 'Compra realizada com sucesso!'})

@app.route("/admin")
def admin():
    conn = get_db_connection()
    passagem = conn.execute('SELECT count(id) FROM passagem').fetchone()[0]
    conn.close()
    return render_template('admin/index.html', passagem=passagem)

@app.route("/admin/listar_passagem")
def listar_passagem():
    conn = get_db_connection()
    passagem = conn.execute('SELECT * FROM passagem').fetchall()
    conn.close()
    return render_template('admin/listar_passagem.html', passagem=passagem)

@app.route("/admin/listar")
def listar():
    conn = get_db_connection()
    passagem = conn.execute('SELECT * FROM passagem').fetchall()
    conn.close()
    return render_template('admin/listar.html', passagem=passagem)


# Inicio das rotas CADASTRAR PASSAGEM
@app.route("/admin/cadastrar_passagem", methods=['GET', 'POST'])
def cadastrar_passagem():
    if request.method == 'POST':
        nome_passagem = request.form.get('nome_passagem')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        quantidade = request.form.get('quantidade')
        imagem = request.files.get('imagem')

        if imagem:
            imagem_base64 = base64.b64encode(imagem.read()).decode("utf-8")

        if nome_passagem:
            conn = get_db_connection()
            conn.execute('INSERT INTO passagem (nome, descricao, preco, quantidade, img) VALUES (?, ?, ?, ?, ?)', 
                        (nome_passagem, descricao, preco, quantidade, imagem_base64))
            conn.commit()
            conn.close()
            return redirect(url_for('listar_passagem'))
    return render_template('admin/cadastrar_passagem.html')

@app.route("/admin/excluir_passagem/<int:id>", methods=['GET', 'POST'])
def excluir_passagem(id):
    conn = get_db_connection()
    passagem = conn.execute('SELECT * FROM passagem WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        conn.execute('DELETE FROM passagem WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_passagem'))
    
    conn.close()
    return render_template('admin/excluir_passagem.html', passagem=passagem)


@app.route("/admin/editar_passagem/<int:id>", methods=['GET', 'POST'])
def editar_passagem(id):
    conn = get_db_connection()
    passagem = conn.execute('SELECT * FROM passagem WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome_passagem = request.form.get('nome_passagem')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        quantidade = request.form.get('quantidade')
        imagem = request.files.get('imagem')

        if imagem:
            imagem_base64 = base64.b64encode(imagem.read()).decode("utf-8")
            conn.execute('UPDATE passagem SET nome=?, descricao=?, preco=?, quantidade=?, img=? WHERE id=?', 
                        (nome_passagem, descricao, preco, quantidade, imagem_base64, id))
        else:
            conn.execute('UPDATE passagem SET nome=?, descricao=?, preco=?, quantidade=? WHERE id=?', 
                        (nome_passagem, descricao, preco, quantidade, id))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_passagem'))
    conn.close()
    return render_template('admin/editar_passagem.html', passagem=passagem)

if __name__ == "__main__":
    app.run(debug=True)
