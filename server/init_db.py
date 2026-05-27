import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, 'data.db')

def init():
    if os.path.exists(DB):
        print('DB already exists at', DB)
        return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')

    admin_user = 'admin'
    # Accept admin password from environment to avoid shipping weak defaults.
    admin_pass = os.environ.get('ADMIN_PASS', 'password')
    if admin_pass == 'password':
        print('WARNING: Using default admin password. Set ADMIN_PASS env var to a stronger password.')
    pw_hash = generate_password_hash(admin_pass)
    c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (admin_user, pw_hash))
    conn.commit()
    conn.close()
    print('Initialized DB at', DB)
    print('Created admin user: username=admin password=password')

if __name__ == '__main__':
    init()
