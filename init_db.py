import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute('UPDATE posts SET title=?, image_url=?, quantity=? WHERE id=?', 
            ('title', 'image_url', 'quantity', 'post_id'))

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

connection.commit()
connection.close()