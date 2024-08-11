from fpdf import FPDF
import sqlite3
import pandas as pd

def generate_report():
    conn = sqlite3.connect('tugas_akhir.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM datasets")
    datasets = cursor.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Data Report", ln=True, align='C')

    for dataset in datasets:
        dataset_name = dataset[0]
        conn = sqlite3.connect('tugas_akhir.db')
        df = pd.read_sql_query(f"SELECT * FROM {dataset_name}", conn)
        conn.close()

        pdf.cell(200, 10, txt=f"Dataset: {dataset_name}", ln=True, align='L')
        for i in range(len(df)):
            pdf.cell(200, 10, txt=str(df.iloc[i].to_dict()), ln=True, align='L')

    pdf.output("data_report.pdf")
