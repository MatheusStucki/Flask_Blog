import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('database.db')

# Execute the schema.sql script to set up the database (if needed)
with open('schema.sql') as f:
    connection.executescript(f.read()) 

cur = connection.cursor()
cur.execute('INSERT INTO settings (id, site_name, pfp_path) VALUES (?, ?, ?)', (1 ,'Default Site Name', 'uploads/placeholder.png'))
# Commit the changes to the database
connection.commit()

# Close the connection
connection.close()
