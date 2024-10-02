import sqlite3
import csv

def export_to_csv(db_file, csv_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Fetch all data from the posts table
    cursor.execute('SELECT * FROM settings')
    rows = cursor.fetchall()
    
    # Write to CSV
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow([i[0] for i in cursor.description])  # write headers
        # Write data
        writer.writerows(rows)
    
    
    conn.close()

# Usage
export_to_csv('database.db', 'posts.csv')
