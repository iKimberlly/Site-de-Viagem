import os
import sqlite3
from werkzeug.security import generate_password_hash

def get_db_connection():
    db_path = 'database/sqlite.db'
    if not os.path.exists('database'):
        os.makedirs('database')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    return conn
    
def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            celular TEXT,
            email TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )     
    ''')
    conn.execute(''' 
        CREATE TABLE IF NOT EXISTS passagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            pass_id INTEGER,
            img BLOB,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (pass_id) REFERENCES cliente(id)
        )
    ''')
    
    inserir(conn)
    conn.commit()

def inserir(conn):
    cliente = conn.execute('SELECT * FROM cliente').fetchall()
    if not cliente:
        conn.execute('''
            INSERT INTO cliente (nome, email, senha)
            VALUES (?, ?, ?)
        ''', ("Kim", "kim@gmail.com", generate_password_hash("1234")))

if __name__ == "__main__":
    conn = get_db_connection()
    conn.close()
