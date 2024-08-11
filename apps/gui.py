# apps/gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
from apps.databases import setup_database
from apps.user_management import *
from apps.data_management import *
from apps.analysis import *
from apps.visualization import *
from apps.export_import import *
from apps.machine_learning import *
from apps.reporting import *
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np

setup_database()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Analysis and Visualization System")
        self.geometry("1024x768")
        self.current_user = None
        self.dataset_var = tk.StringVar()
        self.page_size_var = tk.StringVar(value="10")
        self.page_size = int(self.page_size_var.get())
        self.current_page = 0
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = ttk.Frame(self)
        self.dashboard_frame = ttk.Frame(self)
        self.data_management_frame = ttk.Frame(self)
        self.analysis_frame = ttk.Frame(self)
        self.visualization_frame = ttk.Frame(self)
        self.user_management_frame = ttk.Frame(self)
        self.import_export_frame = ttk.Frame(self)
        self.ml_frame = ttk.Frame(self)
        self.report_frame = ttk.Frame(self)

        self.show_login_frame()

    def clear_frames(self):
        for frame in [self.login_frame, self.dashboard_frame, self.data_management_frame,
                      self.analysis_frame, self.visualization_frame, self.user_management_frame,
                      self.import_export_frame, self.ml_frame, self.report_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.pack_forget()

    def show_login_frame(self):
        self.clear_frames()
        self.login_frame.pack(fill="both", expand=True)

        ttk.Label(self.login_frame, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)

    def show_dashboard(self):
        self.clear_frames()
        self.dashboard_frame.pack(fill="both", expand=True)

        ttk.Label(self.dashboard_frame, text="Dashboard", font=("Arial", 20)).pack(pady=20)
        ttk.Button(self.dashboard_frame, text="Data Management", command=self.show_data_management_frame).pack(pady=5)
        ttk.Button(self.dashboard_frame, text="Analysis", command=self.show_analysis_frame).pack(pady=5)
        ttk.Button(self.dashboard_frame, text="Visualization", command=self.show_visualization_frame).pack(pady=5)
        ttk.Button(self.dashboard_frame, text="Machine Learning", command=self.show_ml_frame).pack(pady=5)
        ttk.Button(self.dashboard_frame, text="Generate Report", command=self.show_report_frame).pack(pady=5)
        if self.current_user == "admin":
            ttk.Button(self.dashboard_frame, text="User Management", command=self.show_user_management_frame).pack(pady=5)
        ttk.Button(self.dashboard_frame, text="Logout", command=self.logout).pack(pady=20)

    def show_import_export_windows(self):
        import_export_window = tk.Toplevel(self)
        import_export_window.title("Import/Export")
        import_export_window.geometry("400x400")

        ttk.Button(import_export_window, text="Import Data", command=self.import_data).pack(pady=10)
        ttk.Button(import_export_window, text="Export Data", command=self.export_data).pack(pady=10)
        ttk.Button(import_export_window, text="Back to Dashboard", command=import_export_window.destroy).pack(pady=10)


    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            dataset_name = os.path.basename(file_path).split('.')[0]
            import_data(file_path, dataset_name)
            messagebox.showinfo("Success", "Data imported successfully")
            self.update_dataset_menu()

    def export_data(self):
        dataset_name = self.dataset_var.get()
        if not dataset_name:
            messagebox.showerror("Error", "Pilih dataset yang ingin diekspor.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("PDF files", "*.pdf")])
        if file_path:
            format = file_path.split('.')[-1]
            export_data(dataset_name, format, file_path)
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")

    def update_dataset_menu(self):
        datasets = list_datasets()
        if self.dataset_menu:
            self.dataset_menu['menu'].delete(0, 'end')
            for dataset in datasets:
                self.dataset_menu['menu'].add_command(label=dataset, command=tk._setit(self.dataset_var, dataset))
        if not datasets:
            self.dataset_var.set('')
            if self.data_tree:
                self.data_tree.delete(*self.data_tree.get_children())

    def show_data_management_frame(self):
        self.clear_frames()
        self.data_management_frame.pack(fill="both", expand=True)

        datasets = list_datasets()
        if datasets:
            ttk.Button(self.data_management_frame, text="Export/Import Data", command=self.show_import_export_windows).pack(pady=5)
            ttk.Label(self.data_management_frame, text="Pilih Dataset:").pack(pady=5)
            ttk.Button(self.data_management_frame, text="Filter/Search Data", command=self.filter_search_data).pack(pady=5)
            self.dataset_menu = ttk.OptionMenu(self.data_management_frame, self.dataset_var, datasets[0], *datasets)
            self.dataset_menu.pack(pady=5)

            self.current_page = 0 

            self.data_tree_frame = ttk.Frame(self.data_management_frame)
            self.data_tree_frame.pack(fill="both", expand=True)

            self.data_tree_scroll = ttk.Scrollbar(self.data_tree_frame)
            self.data_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            self.data_tree = ttk.Treeview(self.data_tree_frame, yscrollcommand=self.data_tree_scroll.set)
            self.data_tree.pack(fill="both", expand=True)
            self.data_tree_scroll.config(command=self.data_tree.yview)

            self.load_data()

            pagination_frame = ttk.Frame(self.data_management_frame)
            pagination_frame.pack(fill=tk.X)

            ttk.Button(pagination_frame, text="Previous", command=self.previous_page).pack(side=tk.LEFT)
            ttk.Button(pagination_frame, text="Next", command=self.next_page).pack(side=tk.RIGHT)

            ttk.Label(pagination_frame, text="Rows per page:").pack(side=tk.LEFT, padx=5)
            page_size_options = [10, 50, 100, 500, "All"]
            page_size_menu = ttk.OptionMenu(pagination_frame, self.page_size_var, self.page_size_var.get(), *page_size_options, command=self.update_page_size)
            page_size_menu.pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(self.data_management_frame, text="Tidak ada dataset yang tersedia.").pack(pady=20)

        ttk.Button(self.data_management_frame, text="Tambah Data", command=self.add_data_window).pack(pady=5)
        ttk.Button(self.data_management_frame, text="Update Data", command=self.update_data_window).pack(pady=5)
        ttk.Button(self.data_management_frame, text="Hapus Data", command=self.delete_data_window).pack(pady=5)
        ttk.Button(self.data_management_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def load_data(self, *args):
        if not self.data_tree:
            return
        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)
            columns = list(data.columns)
            self.data_tree["columns"] = columns
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, anchor='center')

            for row in self.data_tree.get_children():
                self.data_tree.delete(row)

            start = self.current_page * self.page_size
            end = start + self.page_size
            if self.page_size_var.get() == "All":
                rows_to_display = data
            else:
                rows_to_display = data.iloc[start:end]

            for _, row in rows_to_display.iterrows():
                self.data_tree.insert("", "end", values=list(row))

    def next_page(self):
        data = get_data(self.dataset_var.get())
        if (self.current_page + 1) * self.page_size < len(data):
            self.current_page += 1
            self.load_data()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

    def update_page_size(self, value):
        if value == "All":
            self.page_size = len(get_data(self.dataset_var.get()))
        else:
            self.page_size = int(value)
        self.current_page = 0 
        self.load_data()

    def add_data_window(self):
        self.show_input_window("Tambah Data", self.insert_data)
        
    def update_data_window(self):
        selected_item = self.data_tree.selection()
        if selected_item:
            data_id = self.data_tree.item(selected_item[0])["values"][0]
            self.show_input_window("Update Data", self.update_data, data_id)
        else:
            messagebox.showerror("Error", "Pilih data yang ingin diupdate.")

    def delete_data_window(self):
        selected_item = self.data_tree.selection()
        if selected_item:
            data_id = self.data_tree.item(selected_item[0])["values"][0]
            delete_data(self.dataset_var.get(), data_id)
            self.load_data()
        else:
            messagebox.showerror("Error", "Pilih data yang ingin dihapus.")

    def show_input_window(self, title, callback, data_id=None):
        input_window = tk.Toplevel(self)
        input_window.title(title)
        input_window.geometry("300x200")

        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)
            columns = list(data.columns)

            inputs = {}
            for i, col in enumerate(columns):
                ttk.Label(input_window, text=col).grid(row=i, column=0, padx=10, pady=5)
                entry = ttk.Entry(input_window)
                entry.grid(row=i, column=1, padx=10, pady=5)
                inputs[col] = entry

            ttk.Button(input_window, text="Simpan", command=lambda: callback(inputs, data_id)).grid(row=len(columns), columnspan=2, pady=10)

    def filter_search_data(self):
        filter_window = tk.Toplevel(self)
        filter_window.title("Filter and Search Data")
        filter_window.geometry("300x200")

        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)
            columns = list(data.columns)

            ttk.Label(filter_window, text="Select Column:").grid(row=0, column=0, padx=10, pady=5)
            column_var = tk.StringVar()
            column_menu = ttk.OptionMenu(filter_window, column_var, columns[0], *columns)
            column_menu.grid(row=0, column=1, padx=10, pady=5)

            ttk.Label(filter_window, text="Enter Value:").grid(row=1, column=0, padx=10, pady=5)
            value_entry = ttk.Entry(filter_window)
            value_entry.grid(row=1, column=1, padx=10, pady=5)

            def apply_filter():
                column = column_var.get()
                value = value_entry.get()
                filtered_data = data[data[column].astype(str).str.contains(value, case=False, na=False)]
                self.show_filtered_data(filtered_data)
                filter_window.destroy()

            ttk.Button(filter_window, text="Apply", command=apply_filter).grid(row=2, columnspan=2, pady=10)

    def show_filtered_data(self, data):
        if not hasattr(self, 'data_tree') or self.data_tree.winfo_exists() == 0:
            self.create_data_tree()

        self.data_tree.delete(*self.data_tree.get_children())

        columns = list(data.columns)
        self.data_tree["columns"] = columns
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, anchor='center')

        for _, row in data.iterrows():
            self.data_tree.insert("", "end", values=list(row))

    def create_data_tree(self):
        if hasattr(self, 'data_tree_frame'):
            self.data_tree_frame.destroy()

        self.data_tree_frame = ttk.Frame(self)
        self.data_tree_frame.pack(fill="both", expand=True)

        self.data_tree_scroll = ttk.Scrollbar(self.data_tree_frame)
        self.data_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.data_tree = ttk.Treeview(self.data_tree_frame, yscrollcommand=self.data_tree_scroll.set)
        self.data_tree.pack(fill="both", expand=True)
        self.data_tree_scroll.config(command=self.data_tree.yview)

        
    def insert_data(self, inputs, data_id=None):
        data = {col: entry.get() for col, entry in inputs.items()}
        insert_data(self.dataset_var.get(), pd.DataFrame([data]))
        self.load_data()

    def update_data(self, inputs, data_id):
        data = {col: entry.get() for col, entry in inputs.items()}
        update_data(self.dataset_var.get(), data_id, data)
        self.load_data()

    def show_analysis_frame(self):
        self.clear_frames()
        self.analysis_frame.pack(fill="both", expand=True)

        datasets = list_datasets()
        if datasets:
            ttk.Label(self.analysis_frame, text="Pilih Dataset:").pack(pady=5)
            self.dataset_menu = ttk.OptionMenu(self.analysis_frame, self.dataset_var, datasets[0], *datasets)
            self.dataset_menu.pack(pady=5)

            ttk.Button(self.analysis_frame, text="Informasi Dataset", command=self.show_data_info).pack(pady=5)
            ttk.Button(self.analysis_frame, text="Analisis Dasar", command=self.basic_analysis_window).pack(pady=5)
            ttk.Button(self.analysis_frame, text="Analisis Lanjutan", command=self.advanced_analysis_window).pack(pady=5)
        else:
            ttk.Label(self.analysis_frame, text="Tidak ada dataset yang tersedia.").pack(pady=20)

        ttk.Button(self.analysis_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def show_data_info(self):
        dataset_name = self.dataset_var.get()
        if dataset_name:
            info = data_info(dataset_name)
            info_window = tk.Toplevel(self)
            info_window.title("Informasi Dataset")
            info_window.geometry("600x400")

            text = tk.Text(info_window)
            text.pack(fill="both", expand=True)

            text.insert("end", f"Columns: {info['columns']}\n")
            text.insert("end", f"Data Types: {info['dtypes']}\n")
            text.insert("end", f"Missing Values: {info['missing_values']}\n")
            text.insert("end", f"Shape: {info['shape']}\n")
            text.insert("end", "Head:\n")
            for row in info['head']:
                text.insert("end", f"{row}\n")

    def basic_analysis_window(self):
        self.show_analysis_window("Analisis Dasar", basic_analysis)

    def advanced_analysis_window(self):
        self.show_advanced_analysis_window()

    def show_analysis_window(self, title, analysis_function):
        analysis_window = tk.Toplevel(self)
        analysis_window.title(title)
        analysis_window.geometry("400x300")

        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)

            ttk.Label(analysis_window, text="Pilih Kolom:").pack(pady=5)
            columns = list(data.columns)
            self.columns_var = tk.StringVar(value=columns)
            self.columns_listbox = tk.Listbox(analysis_window, listvariable=self.columns_var, selectmode="multiple")
            self.columns_listbox.pack(pady=5)

            ttk.Button(analysis_window, text="Analisis", command=lambda: self.perform_analysis(analysis_function, dataset_name)).pack(pady=10)

            self.analysis_result = tk.StringVar()
            ttk.Label(analysis_window, textvariable=self.analysis_result).pack(pady=10)

    def perform_analysis(self, analysis_function, dataset_name):
        selected_columns = [self.columns_listbox.get(i) for i in self.columns_listbox.curselection()]
        result = analysis_function(dataset_name, selected_columns)
        self.analysis_result.set(str(result))

    def show_advanced_analysis_window(self):
        advanced_window = tk.Toplevel(self)
        advanced_window.title("Analisis Lanjutan")
        advanced_window.geometry("400x400")

        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)

            ttk.Label(advanced_window, text="Pilih Kolom:").pack(pady=5)
            columns = list(data.columns)
            self.columns_var = tk.StringVar(value=columns)
            self.columns_listbox = tk.Listbox(advanced_window, listvariable=self.columns_var, selectmode="multiple")
            self.columns_listbox.pack(pady=5)

            self.operations = {
                "drop_na": tk.BooleanVar(),
                "fill_na": tk.BooleanVar(),
                "normalize": tk.BooleanVar(),
                "regex_replace": [],
                "replace_values": []
            }

            ttk.Checkbutton(advanced_window, text="Hapus NaN", variable=self.operations["drop_na"]).pack(pady=5)
            ttk.Checkbutton(advanced_window, text="Isi NaN dengan 0", variable=self.operations["fill_na"]).pack(pady=5)
            ttk.Checkbutton(advanced_window, text="Normalisasi Data", variable=self.operations["normalize"]).pack(pady=5)

            ttk.Button(advanced_window, text="Tambah Regex Replace", command=self.add_regex_replace_window).pack(pady=5)
            ttk.Button(advanced_window, text="Tambah Replace Value", command=self.add_replace_value_window).pack(pady=5)

            ttk.Button(advanced_window, text="Analisis Lanjutan", command=lambda: self.perform_advanced_analysis(dataset_name)).pack(pady=10)

            self.analysis_result = tk.StringVar()
            ttk.Label(advanced_window, textvariable=self.analysis_result).pack(pady=10)

    def add_regex_replace_window(self):
        regex_window = tk.Toplevel(self)
        regex_window.title("Tambah Regex Replace")
        regex_window.geometry("300x200")

        dataset_name = self.dataset_var.get()
        data = get_data(dataset_name)
        columns = list(data.columns)

        ttk.Label(regex_window, text="Kolom:").grid(row=0, column=0, padx=10, pady=5)
        column_var = tk.StringVar()
        column_menu = ttk.OptionMenu(regex_window, column_var, columns[0], *columns)
        column_menu.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(regex_window, text="Pola:").grid(row=1, column=0, padx=10, pady=5)
        pattern_entry = ttk.Entry(regex_window)
        pattern_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(regex_window, text="Pengganti:").grid(row=2, column=0, padx=10, pady=5)
        replacement_entry = ttk.Entry(regex_window)
        replacement_entry.grid(row=2, column=1, padx=10, pady=5)

        def add_regex():
            self.operations["regex_replace"].append((column_var.get(), pattern_entry.get(), replacement_entry.get()))
            regex_window.destroy()

        ttk.Button(regex_window, text="Tambah", command=add_regex).grid(row=3, columnspan=2, pady=10)

    def add_replace_value_window(self):
        replace_window = tk.Toplevel(self)
        replace_window.title("Tambah Replace Value")
        replace_window.geometry("300x200")

        dataset_name = self.dataset_var.get()
        data = get_data(dataset_name)
        columns = list(data.columns)

        ttk.Label(replace_window, text="Kolom:").grid(row=0, column=0, padx=10, pady=5)
        column_var = tk.StringVar()
        column_menu = ttk.OptionMenu(replace_window, column_var, columns[0], *columns)
        column_menu.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(replace_window, text="Nilai yang Diganti:").grid(row=1, column=0, padx=10, pady=5)
        to_replace_entry = ttk.Entry(replace_window)
        to_replace_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(replace_window, text="Pengganti:").grid(row=2, column=0, padx=10, pady=5)
        replacement_entry = ttk.Entry(replace_window)
        replacement_entry.grid(row=2, column=1, padx=10, pady=5)

        def add_replace():
            self.operations["replace_values"].append((column_var.get(), to_replace_entry.get(), replacement_entry.get()))
            replace_window.destroy()

        ttk.Button(replace_window, text="Tambah", command=add_replace).grid(row=3, columnspan=2, pady=10)


    def perform_advanced_analysis(self, dataset_name):
        selected_columns = [self.columns_listbox.get(i) for i in self.columns_listbox.curselection()]
        result = advanced_analysis(dataset_name, selected_columns, self.operations)
        self.analysis_result.set(str(result))

    def show_visualization_frame(self):
        self.clear_frames()
        self.visualization_frame.pack(fill="both", expand=True)

        datasets = list_datasets()
        if datasets:
            ttk.Label(self.visualization_frame, text="Pilih Dataset:").pack(pady=5)
            self.dataset_menu = ttk.OptionMenu(self.visualization_frame, self.dataset_var, datasets[0], *datasets)
            self.dataset_menu.pack(pady=5)

            ttk.Button(self.visualization_frame, text="Visualisasi Data", command=self.visualization_window).pack(pady=5)
        else:
            ttk.Label(self.visualization_frame, text="Tidak ada dataset yang tersedia.").pack(pady=20)

        ttk.Button(self.visualization_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def visualization_window(self):
        visualization_window = tk.Toplevel(self)
        visualization_window.title("Visualisasi Data")
        visualization_window.geometry("400x300")

        dataset_name = self.dataset_var.get()
        if dataset_name:
            data = get_data(dataset_name)

            ttk.Label(visualization_window, text="Pilih Kolom 1:").pack(pady=5)
            columns = list(data.columns)
            self.column1_var = tk.StringVar(value=columns)
            self.column1_menu = ttk.OptionMenu(visualization_window, self.column1_var, columns[0], *columns)
            self.column1_menu.pack(pady=5)

            ttk.Label(visualization_window, text="Pilih Kolom 2 (opsional):").pack(pady=5)
            self.column2_var = tk.StringVar(value=columns)
            self.column2_menu = ttk.OptionMenu(visualization_window, self.column2_var, '', *columns)
            self.column2_menu.pack(pady=5)

            ttk.Label(visualization_window, text="Tipe Plot:").pack(pady=5)
            self.plot_type_var = tk.StringVar(value='hist')
            self.plot_type_menu = ttk.OptionMenu(visualization_window, self.plot_type_var, 'hist', 'scatter', 'line', 'bar')
            self.plot_type_menu.pack(pady=5)

            ttk.Button(visualization_window, text="Visualisasi", command=self.perform_visualization).pack(pady=10)

    def perform_visualization(self):
        column1 = self.column1_var.get()
        column2 = self.column2_var.get() if self.column2_var.get() else None
        plot_type = self.plot_type_var.get()
        dataset_name = self.dataset_var.get()

        visualize_data(dataset_name, column1, column2, plot_type)

    def show_import_export_frame(self):
        self.clear_frames()
        self.import_export_frame.pack(fill="both", expand=True)

        ttk.Button(self.import_export_frame, text="Import Data", command=self.import_data).pack(pady=5)
        ttk.Button(self.import_export_frame, text="Export Data", command=self.export_data).pack(pady=5)
        ttk.Button(self.import_export_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            dataset_name = os.path.basename(file_path).split('.')[0]
            import_data(file_path, dataset_name)
            messagebox.showinfo("Success", "Data imported successfully")
            self.update_dataset_menu()

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("PDF files", "*.pdf")])
        if file_path:
            format = file_path.split('.')[-1]
            dataset_name = self.dataset_var.get()
            export_data(dataset_name, format, file_path)
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")

    def update_dataset_menu(self):
        datasets = list_datasets()
        if self.dataset_menu:
            self.dataset_menu['menu'].delete(0, 'end')
            for dataset in datasets:
                self.dataset_menu['menu'].add_command(label=dataset, command=tk._setit(self.dataset_var, dataset))
        if not datasets:
            self.dataset_var.set('')
            if self.data_tree:
                self.data_tree.delete(*self.data_tree.get_children())

    def show_user_management_frame(self):
        self.clear_frames()
        self.user_management_frame.pack(fill="both", expand=True)

        users = get_users()
        columns = ("id", "username", "role")
        self.user_tree = ttk.Treeview(self.user_management_frame, columns=columns, show="headings")
        for col in columns:
            self.user_tree.heading(col, text=col)
        for user in users:
            self.user_tree.insert("", "end", values=user)
        self.user_tree.pack(fill="both", expand=True)

        ttk.Button(self.user_management_frame, text="Tambah Pengguna", command=self.add_user_window).pack(pady=5)
        ttk.Button(self.user_management_frame, text="Update Pengguna", command=self.update_user_window).pack(pady=5)
        ttk.Button(self.user_management_frame, text="Hapus Pengguna", command=self.delete_user_window).pack(pady=5)
        ttk.Button(self.user_management_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def add_user_window(self):
        self.show_user_input_window("Tambah Pengguna", self.insert_user)

    def update_user_window(self):
        selected_item = self.user_tree.selection()[0]
        user_id = self.user_tree.item(selected_item)["values"][0]
        self.show_user_input_window("Update Pengguna", self.update_user, user_id)

    def delete_user_window(self):
        selected_item = self.user_tree.selection()[0]
        user_id = self.user_tree.item(selected_item)["values"][0]
        delete_user(user_id)
        self.show_user_management_frame()

    def show_user_input_window(self, title, callback, user_id=None):
        user_window = tk.Toplevel(self)
        user_window.title(title)
        user_window.geometry("300x200")

        ttk.Label(user_window, text="Username").grid(row=0, column=0, padx=10, pady=5)
        username_entry = ttk.Entry(user_window)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(user_window, text="Password").grid(row=1, column=0, padx=10, pady=5)
        password_entry = ttk.Entry(user_window, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(user_window, text="Role").grid(row=2, column=0, padx=10, pady=5)
        role_var = tk.StringVar(value="user")
        role_menu = ttk.OptionMenu(user_window, role_var, "user", "admin")
        role_menu.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(user_window, text="Simpan", command=lambda: callback(username_entry.get(), password_entry.get(), role_var.get(), user_id)).grid(row=3, columnspan=2, pady=10)

    def insert_user(self, username, password, role, user_id=None):
        add_user(username, password, role)
        self.show_user_management_frame()

    def update_user(self, username, password, role, user_id):
        update_user(user_id, username, password, role)
        self.show_user_management_frame()

    def show_ml_frame(self):
        self.clear_frames()
        self.ml_frame.pack(fill="both", expand=True)

        datasets = list_datasets()
        if datasets:
            ttk.Label(self.ml_frame, text="Pilih Dataset:").pack(pady=5)
            self.dataset_menu = ttk.OptionMenu(self.ml_frame, self.dataset_var, datasets[0], *datasets)
            self.dataset_menu.pack(pady=5)

            ttk.Label(self.ml_frame, text="Pilih Target Kolom:").pack(pady=5)
            self.target_var = tk.StringVar()
            self.target_menu = ttk.OptionMenu(self.ml_frame, self.target_var, '')
            self.target_menu.pack(pady=5)

            self.update_target_menu()

            self.dataset_var.trace_add('write', lambda *args: self.update_target_menu())

            ttk.Button(self.ml_frame, text="View Cleaned Data", command=self.view_cleaned_data).pack(pady=5)
            ttk.Button(self.ml_frame, text="Train Model", command=self.train_model).pack(pady=5)
            ttk.Button(self.ml_frame, text="View Predictions", command=self.view_predictions).pack(pady=5)
            ttk.Button(self.ml_frame, text="Visualize Predictions", command=self.visualize_predictions).pack(pady=5)

        else:
            ttk.Label(self.ml_frame, text="Tidak ada dataset yang tersedia.").pack(pady=20)

        ttk.Button(self.ml_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def update_target_menu(self):
        if hasattr(self, 'target_menu'):
            dataset_name = self.dataset_var.get()
            if dataset_name:
                data = get_data(dataset_name)
                columns = list(data.columns)
                menu = self.target_menu['menu']
                menu.delete(0, 'end')
                for col in columns:
                        menu.add_command(label=col, command=lambda value=col: self.target_var.set(value))

    def show_data_in_new_window(self, data, title="Data"):
        new_window = tk.Toplevel(self)
        new_window.title(title)
        new_window.geometry("600x400")

        data_tree_scroll = ttk.Scrollbar(new_window)
        data_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        data_tree = ttk.Treeview(new_window, yscrollcommand=data_tree_scroll.set)
        data_tree.pack(fill="both", expand=True)
        data_tree_scroll.config(command=data_tree.yview)

        columns = list(data.columns)
        data_tree["columns"] = columns
        for col in columns:
            data_tree.heading(col, text=col)
            data_tree.column(col, anchor='center')

        for _, row in data.iterrows():
            data_tree.insert("", "end", values=list(row))
    def view_predictions(self):
        dataset_name = self.dataset_var.get()
        target_column = self.target_var.get()

        if not dataset_name or not target_column:
            messagebox.showerror("Error", "Pilih dataset dan kolom target untuk prediksi.")
            return

        data = get_data(dataset_name)
        X_clean, y_clean = auto_clean_data(data, target_column)

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

        if np.issubdtype(y_clean.dtype, np.number):
            model = LinearRegression()
        else:
            model = LogisticRegression()

        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})

        self.show_data_in_new_window(predictions_df, title="Predictions")
    
    def visualize_predictions(self):
        dataset_name = self.dataset_var.get()
        target_column = self.target_var.get()
        
        if not dataset_name or not target_column:
            messagebox.showerror("Error", "Pilih dataset dan kolom target untuk visualisasi.")
            return
        
        data = get_data(dataset_name)
        X_clean, y_clean = auto_clean_data(data, target_column)
        
        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
        
        if np.issubdtype(y_clean.dtype, np.number):
            model = LinearRegression()
        else:
            model = LogisticRegression()
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(y_test)), y_test, label="Actual")
        plt.plot(range(len(predictions)), predictions, label="Predicted", linestyle='--')
        plt.legend()
        plt.title("Actual vs Predicted")
        plt.show()
        
    def view_cleaned_data(self):
        dataset_name = self.dataset_var.get()
        target_column = self.target_var.get()

        if not dataset_name or not target_column:
            messagebox.showerror("Error", "Pilih dataset dan kolom target.")
            return

        data = get_data(dataset_name)
        X_clean, y_clean = auto_clean_data(data, target_column)
        cleaned_data = pd.DataFrame(X_clean.toarray()) if hasattr(X_clean, 'toarray') else pd.DataFrame(X_clean)
        cleaned_data[target_column] = y_clean.values

        self.show_data_in_new_window(cleaned_data, title="Cleaned Data")

    def train_model(self):
        dataset_name = self.dataset_var.get()
        target_column = self.target_var.get()

        if not dataset_name or not target_column:
            messagebox.showerror("Error", "Pilih dataset dan kolom target untuk training.")
            return

        data = get_data(dataset_name)

        X_clean, y_clean = auto_clean_data(data, target_column)

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

        if np.issubdtype(y_clean.dtype, np.number):
            model = LinearRegression()
            metric = mean_squared_error
            metric_name = "Mean Squared Error"
        else:
            model = LogisticRegression()
            metric = accuracy_score
            metric_name = "Accuracy"

        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        score = metric(y_test, predictions)

        self.model = model
        self.predictions = predictions
        self.y_test = y_test

        messagebox.showinfo("Model Training Result", f"Model trained successfully with {metric_name}: {score:.2f}")

    def show_report_frame(self):
        self.clear_frames()
        self.report_frame.pack(fill="both", expand=True)

        ttk.Button(self.report_frame, text="Generate Report", command=self.generate_report).pack(pady=5)
        ttk.Button(self.report_frame, text="Back to Dashboard", command=self.show_dashboard).pack(pady=10)

    def generate_report(self):
        generate_report()
        messagebox.showinfo("Success", "Report generated successfully")

    def clear_frames(self):
        for frame in [self.login_frame, self.dashboard_frame, self.data_management_frame, 
                      self.analysis_frame, self.visualization_frame, self.user_management_frame,
                      self.import_export_frame, self.ml_frame, self.report_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.pack_forget()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = login_user(username, password)
        if user:
            self.current_user = user[2] 
            messagebox.showinfo("Success", "Login successful!")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def logout(self):
        self.current_user = None
        self.show_login_frame()

def run_app():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    run_app()