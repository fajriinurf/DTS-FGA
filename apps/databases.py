# apps/databases.py

import sqlite3

def setup_database():
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            columns TEXT,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()

    if not admin_user:
        cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            action TEXT,
            details TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()