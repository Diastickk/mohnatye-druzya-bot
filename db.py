import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    client_username TEXT NOT NULL,
    dog_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL
        )''')
    conn.commit()
    cur.close()
    conn.close()

def get_services():
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM services''')
        services = cur.fetchall()
        cur.close()
        return services

def delete_service(id:int)->None:
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''DELETE FROM services WHERE id = ?''', (id,))
        conn.commit()
        cur.close()

def change_service(id:int, new_name:str, new_price:int)->None:
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''UPDATE services SET name = ?, price = ? WHERE id = ?''', (new_name,new_price,id))
        conn.commit()
        cur.close()

def add_service(name:str, price:int)->None:
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''INSERT INTO services (name,price) VALUES (?,?)''', (name,price))
        conn.commit()
        cur.close()

def insert_order(client_name,client_username, dog_name,date,time):
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO orders (client_name,client_username,dog_name,date,time)
        VALUES (?,?,?,?,?)''',(client_name,client_username,dog_name,date,time))
        conn.commit()
        cur.close()

def delete_order(id:int)->None:
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''DELETE FROM orders WHERE id = ?''', (id,))
        conn.commit()
        cur.close()

def get_orders():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM orders''')
    full_answer = ''
    for row in cur.fetchall():
        full_answer += f'''Запись номер{row[0]}:
    Имя клиента: {row[1]}
    Юзернейм клиента: @{row[2]}
    Имя питомца: {row[3]}
    Дата: {row[4]}
    Вреня: {row[5]}:00

'''
    return full_answer

def get_ordered_time(day):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('SELECT time FROM orders WHERE date = ?', (day.strip().lower(),))
    ordered = [int(row[0]) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return ordered
