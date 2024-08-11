# apps/visualization.py

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

def visualize_data(dataset_name, column1, column2=None, plot_type='hist'):
    conn = sqlite3.connect('tugas_akhir.db')
    query = f"SELECT * FROM {dataset_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if column1 not in df.columns:
        return {"error": "Kolom pertama tidak ditemukan dalam tabel data."}

    plt.figure(figsize=(10, 6))

    if plot_type == 'hist':
        df[column1].hist(bins=30, edgecolor='black')
        plt.title(f'Distribusi {column1}')
        plt.xlabel(column1)
        plt.ylabel('Frekuensi')
    elif plot_type == 'scatter' and column2:
        if column2 not in df.columns:
            return {"error": "Kolom kedua tidak ditemukan dalam tabel data."}
        plt.scatter(df[column1], df[column2])
        plt.title(f'Scatter Plot {column1} vs {column2}')
        plt.xlabel(column1)
        plt.ylabel(column2)
    elif plot_type == 'line' and column2:
        if column2 not in df.columns:
            return {"error": "Kolom kedua tidak ditemukan dalam tabel data."}
        plt.plot(df[column1], df[column2])
        plt.title(f'Line Plot {column1} vs {column2}')
        plt.xlabel(column1)
        plt.ylabel(column2)
    elif plot_type == 'bar' and column2:
        if column2 not in df.columns:
            return {"error": "Kolom kedua tidak ditemukan dalam tabel data."}
        df.groupby(column1)[column2].sum().plot(kind='bar')
        plt.title(f'Bar Plot {column1} vs {column2}')
        plt.xlabel(column1)
        plt.ylabel(column2)
    else:
        return {"error": "Plot type tidak valid atau kolom kedua tidak disediakan untuk scatter/line plot."}

    plt.show()
