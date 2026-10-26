import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    dog_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
    )''')
    conn.commit()
    cur.close()
    conn.close()

def insert_order(client_name,dog_name,date,time):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO orders (client_name,dog_name,date,time)
    VALUES (?,?,?,?)''',(client_name,dog_name,date,time))
    conn.commit()
    cur.close()
    conn.close()

def delete_order(client_name,dog_name):
    conn = sqlite3.connect('data.db')

def get_orders():
    conn = sqlite3.connect('data.db')