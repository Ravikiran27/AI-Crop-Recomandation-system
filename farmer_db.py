import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect('data/farmers.db', check_same_thread=False)
    return conn

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        password TEXT NOT NULL,
        location TEXT,
        crops_grown TEXT,
        notes TEXT
    )''')
    conn.commit()
    conn.close()

init_db()
