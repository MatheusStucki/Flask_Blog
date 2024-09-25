import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.exceptions import abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

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
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']

    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                 (title, content))
    conn.commit()
    conn.close()

    flash('Post added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/update_quantity/<int:post_id>/<int:quantity>', methods=['POST'])
def update_quantity(post_id, quantity):
    conn = get_db_connection()
    conn.execute('UPDATE posts SET quantity = ? WHERE id = ?', (quantity, post_id))
    conn.commit()
    conn.close()
    return '', 204  # No content response

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)
