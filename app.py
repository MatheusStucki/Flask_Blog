import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os

# Defina o caminho da pasta para salvar as imagens
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Necessário para mensagens flash

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_change(message):
    conn = get_db_connection()
    conn.execute('INSERT INTO recent_changes (message) VALUES (?)', (message,))
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    recent_changes = conn.execute('SELECT * FROM recent_changes ORDER BY timestamp DESC LIMIT 20').fetchall()
    user_settings = conn.execute('SELECT pfp_path FROM settings WHERE id = 1').fetchone()
    conn.close()
    return render_template('index.html', posts=posts, recent_changes=recent_changes, user_settings=user_settings)

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']

    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title) VALUES (?)', (title,))
    conn.commit()

    # Registre a adição do novo produto
    log_change(f"Product '{title}' was added")

    conn.close()
    flash('Post added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/update_quantity/<int:post_id>/<int:quantity>', methods=['POST'])
def update_quantity(post_id, quantity):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.execute('UPDATE posts SET quantity = ? WHERE id = ?', (quantity, post_id))
    conn.commit()

    # Registre a alteração na quantidade
    log_change(f"Product '{post['title']}' quantity updated to {quantity}")

    conn.close()
    return '', 204  # Resposta sem conteúdo

@app.route('/update_title/<int:post_id>', methods=['POST'])
def update_title(post_id):
    new_title = request.json['title']
    conn = get_db_connection()
    conn.execute('UPDATE posts SET title = ? WHERE id = ?', (new_title, post_id))
    conn.commit()
    conn.close()
    return '', 204  # Resposta sem conteúdo

@app.route('/upload_image/<int:post_id>', methods=['POST'])
def upload_image(post_id):
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Salve o arquivo
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)  # Crie o diretório se não existir
        # Fazer ele puxar uma copia do arquivo para o diretorio

        # Caminho completo para salvar o arquivo
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Atualize a URL da imagem no banco de dados (armazene apenas o caminho relativo)
        relative_path = f'uploads/{filename}'  # Armazene o caminho relativo
        conn = get_db_connection()
        conn.execute('UPDATE posts SET image_url = ? WHERE id = ?', (relative_path, post_id))
        conn.commit()
        conn.close()

        return 'Image uploaded successfully', 200
    else:
        return 'File not allowed', 400

@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        # Salve o caminho no banco de dados (atualize a lógica conforme necessário)
        conn = get_db_connection()
        conn.execute('UPDATE settings SET pfp_path = ?', (filename,))
        conn.commit()
        conn.close()

        # Retorne a URL da imagem para atualizar o frontend
        return 'Profile image uploaded successfully', 200
    else:
        return 'File not allowed', 400
    
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)
