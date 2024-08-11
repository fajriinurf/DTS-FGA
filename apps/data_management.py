import sqlite3
import pandas as pd

def insert_data(dataset_name, data):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    data.to_sql(dataset_name, conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

def update_data(dataset_name, data_id, data):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
    values = list(data.values())
    values.append(data_id)
    cursor.execute(f'UPDATE {dataset_name} SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()

def delete_data(dataset_name, data_id):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {dataset_name} WHERE id = ?', (data_id,))
    conn.commit()
    conn.close()

def get_data(dataset_name):
    conn = sqlite3.connect('tugas_akhir.db')
    df = pd.read_sql_query(f"SELECT * FROM {dataset_name}", conn)
    conn.close()
    return df

def list_datasets():
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM datasets')
    datasets = cursor.fetchall()
    conn.close()
    return [dataset[0] for dataset in datasets]

def add_dataset(name, columns):
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO datasets (name, columns) VALUES (?, ?)', (name, ','.join(columns)))
    conn.commit()
    conn.close()