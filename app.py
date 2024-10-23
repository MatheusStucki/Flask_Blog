import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

# Defina o caminho da pasta para salvar as imagens
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

load_dotenv()  # This loads the .env file

# Now you can access environment variables as usual
secret_key = os.getenv('SECRET_KEY')

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
    posts = conn.execute('SELECT * FROM posts WHERE is_deleted = FALSE').fetchall()
    recent_changes = conn.execute('SELECT * FROM recent_changes ORDER BY timestamp DESC LIMIT 20').fetchall()
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    conn.close()
    return render_template('index.html', posts=posts, recent_changes=recent_changes, settings=settings)

@app.route('/add', methods=['POST']) 
def add_post():
    conn = get_db_connection()
    
    # Find the lowest available ID or the highest ID + 1 if no gaps
    next_id = conn.execute('''
        SELECT MIN(t1.id + 1) AS next_id
        FROM posts t1
        LEFT JOIN posts t2 ON t1.id + 1 = t2.id
        WHERE t2.id IS NULL
    ''').fetchone()['next_id']

    # If no gaps, use max(id) + 1
    if not next_id:
        next_id = conn.execute('SELECT IFNULL(MAX(id), 0) + 1 FROM posts').fetchone()[0]
    
    # Create the new post (data should come from request)
    title = request.form['title']

    conn.execute('INSERT INTO posts (id, title) VALUES (?, ?)',
                 (next_id, title))
    conn.commit()
    conn.close()

    log_change(f"Produto {title} foi adicionado")

    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_post():
    post_id = request.form['post_id']

    conn = get_db_connection()

    # Soft delete: set is_deleted to TRUE instead of actually deleting the row
    conn.execute('UPDATE posts SET is_deleted = TRUE WHERE id = ?', (post_id,))
    
    conn.commit()
    conn.close()

    log_change(f"Produto Deletado com sucesso")
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/update_quantity/<int:post_id>/<int:quantity>', methods=['POST'])
def update_quantity(post_id, quantity):
    conn = get_db_connection()
    
    # Fetch the post and its current max_quantity
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if not post:
        conn.close()
        return "Post not found", 404  # Return 404 if the post doesn't exist

    # Get the current max_quantity from the post
    max_quantity = post['max_quantity']

    # Update max_quantity if the new quantity is greater than the current max
    if quantity > max_quantity:
        max_quantity = quantity

    # Update the quantity and possibly the max_quantity in the database
    conn.execute('UPDATE posts SET quantity = ?, max_quantity = ? WHERE id = ?',
                 (quantity, max_quantity, post_id))
    conn.commit()

    # Log the change
    log_change(f"Produto'{post['title']}' quantia em estoque: {quantity}")

    conn.close()

    # Return the updated max_quantity to the client
    return {'max_quantity': max_quantity}, 200  # Return JSON with max_quantity


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
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Save the file
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)  # Create the directory if it doesn't exist

        # Complete path to save the file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Store relative path in the database
        relative_path = f'uploads/{filename}'
        conn = get_db_connection()
        conn.execute('UPDATE posts SET image_url = ? WHERE id = ?', (relative_path, post_id))
        conn.commit()
        conn.close()

        # Return the new image URL in JSON format
        return jsonify({'image_url': url_for('static', filename=relative_path)}), 200
    else:
        return jsonify({'error': 'File not allowed'}), 400

@app.route('/update_site_name', methods=['POST'])
def update_site_name():
    data = request.get_json()
    site_name = data.get('site_name')

    conn = get_db_connection()
    conn.execute('UPDATE settings SET site_name = ? WHERE id = 1', (site_name,)) 
    conn.commit()
    conn.close()

    return 'Site name updated successfully', 200


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

        # Save the path in the database
        conn = get_db_connection()
        relative_path = f'uploads/{filename}'
        conn.execute('UPDATE settings SET pfp_path = ? WHERE id = 1', ((relative_path,)))  
        conn.commit()
        conn.close()

        return jsonify({'image_url': url_for('static', filename=relative_path)}), 200
    else:
        return jsonify({'error': 'File not allowed'}), 400


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        print(e)