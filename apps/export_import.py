# apps/export_import.py

import pandas as pd
import sqlite3
import os
from apps.data_management import add_dataset, get_data, insert_data, list_datasets

def import_data(file_path, dataset_name):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Format file tidak didukung")

    conn = sqlite3.connect('tugas_akhir.db')
    if dataset_name in list_datasets():
        df.to_sql(dataset_name, conn, if_exists='append', index=False)
    else:
        df.to_sql(dataset_name, conn, if_exists='replace', index=False)
        add_dataset(dataset_name, df.columns)
    conn.commit()
    conn.close()

def export_data(dataset_name, format, file_path):
    df = get_data(dataset_name)

    if format == 'csv':
        df.to_csv(file_path, index=False)
    elif format == 'excel':
        df.to_excel(file_path, index=False)
    elif format == 'pdf':
        df.to_html(file_path.replace('.pdf', '.html'), index=False)
    else:
        raise ValueError("Format tidak didukung")
