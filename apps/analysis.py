# apps/analysis.py
import pandas as pd
import sqlite3

def data_info(dataset_name):
    conn = sqlite3.connect('tugas_akhir.db')
    df = pd.read_sql_query(f"SELECT * FROM {dataset_name}", conn)
    conn.close()
    
    info = {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).tolist(),
        "missing_values": df.isnull().sum().tolist(),
        "shape": df.shape,
        "head": df.head().to_dict(orient='records'),
    }
    
    return info

def basic_analysis(dataset_name, selected_columns):
    conn = sqlite3.connect('tugas_akhir.db')
    df = pd.read_sql_query(f"SELECT {', '.join(selected_columns)} FROM {dataset_name}", conn)
    conn.close()
    
    analysis_results = {}
    for column in selected_columns:
        if column not in df.columns:
            analysis_results[column] = 'Column not found.'
            continue

        df[column] = pd.to_numeric(df[column], errors='coerce')
        description = df[column].describe()
        if 'mean' not in description:
            analysis_results[column] = 'Column is not numeric and could not be converted to numeric.'
        else:
            analysis_results[column] = {
                'average': description['mean'],
                'median': description['50%'],
                'min': description['min'],
                'max': description['max'],
                'std': description['std']
            }

    return analysis_results

def advanced_analysis(dataset_name, selected_columns, operations):
    conn = sqlite3.connect('tugas_akhir.db')
    df = pd.read_sql_query(f"SELECT * FROM {dataset_name}", conn)
    conn.close()

    original_df = df.copy()

    if operations.get('drop_na'):
        df = df.dropna(subset=selected_columns)
    if operations.get('fill_na'):
        fill_value = operations.get('fill_value', 0)
        df[selected_columns] = df[selected_columns].fillna(fill_value)
    if operations.get('normalize'):
        df[selected_columns] = (df[selected_columns] - df[selected_columns].mean()) / df[selected_columns].std()
    if operations.get('regex_replace'):
        for col, pattern, replacement in operations.get('regex_replace', []):
            df[col] = df[col].str.replace(pattern, replacement, regex=True)
    if operations.get('replace_values'):
        for col, to_replace, replacement in operations.get('replace_values', []):
            df[col] = df[col].replace(to_replace, replacement)

    advanced_results = {
        'original': original_df.describe().to_dict(),
        'processed': df.describe().to_dict()
    }
    try:
        correlation_matrix = df[selected_columns].corr()
        advanced_results['correlation_matrix'] = correlation_matrix.to_dict()
    except Exception as e:
        advanced_results['error'] = str(e)

    return advanced_results
