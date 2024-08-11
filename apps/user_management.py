# apps/user_management.py

import sqlite3
import bcrypt

def login_user(username, password):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return user
    return None

def add_user(username, password, role):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def update_user(user_id, username, password, role):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?', (username, hashed_password, role, user_id))
    conn.commit()
    conn.close()

