# Copyright 2025 Roberto Canija
# License: GPL-3.0-or-later

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import datetime

# --- CONFIGURACION DE COLORES (Tema Oscuro) ---
BG_COLOR = "#1e1e1e"        # Fondo principal (Negro suave)
SIDEBAR_COLOR = "#252526"   # Barra lateral (Gris oscuro)
TABLE_BG = "#2d2d30"        # Fondo de las tablas
BLUE_COLOR = "#0078d7"      # Azul KU
GREEN_COLOR = "#4ec9b0"     # Exito
RED_COLOR = "#f48771"       # Error
TEXT_WHITE = "#ffffff"
TEXT_GREY = "#cccccc"

# --- LOGICA DEL PROGRAMA (BACKEND) ---
# Esta clase maneja todos los datos y calculos
class UniversityLogic:
    def __init__(self):
        # Dataframes vacios al inicio para evitar errores
        self.clean_data = pd.DataFrame()
        self.gpa_data = pd.DataFrame()
        self.course_stats = pd.DataFrame()
        self.logs = []

    def add_log(self, message):
        # Funcion para guardar logs con la hora exacta
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{now}] {message}"
        print(entry) # Imprimir en consola tambien por si acaso
        self.logs.append(entry)

    def load_file(self, filepath):
        self.logs = [] # Limpiar logs de la corrida anterior
        self.add_log(f"Starting process for: {filepath}")
        
        try:
            # Detectar formato (CSV o JSON)
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                self.add_log("Error: File format not supported (Only .csv or .json)")
                return False

            # --- LIMPIEZA DE COLUMNAS (Manual) ---
            # Pasamos todo a minusculas y quitamos espacios para evitar problemas
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

            # Arreglamos nombres de columnas manualmente (Requisito del compañero)
            # A veces el archivo trae 'academic_term' y a veces 'period'
            if 'academic_term' in df.columns:
                df = df.rename(columns={'academic_term': 'term'})
            elif 'period' in df.columns:
                df = df.rename(columns={'period': 'term'})
            
            if 'student_no' in df.columns:
                df = df.rename(columns={'student_no': 'student_id'})
            elif 'id' in df.columns:
                df = df.rename(columns={'id': 'student_id'})

            if 'course_code' in df.columns:
                df = df.rename(columns={'course_code': 'course_id'})

            if 'full_name' in df.columns:
                df = df.rename(columns={'full_name': 'student_name'})
            elif 'name' in df.columns:
                df = df.rename(columns={'name': 'student_name'})

            # Verificar columnas obligatorias
            required = ['student_id', 'term', 'credits', 'grade']
            missing = []
            for col in required:
                if col not in df.columns:
                    missing.append(col)
            
            if len(missing) > 0:
                self.add_log(f"CRITICAL ERROR: Missing columns {missing}")
                return False

            # --- VALIDACION FILA POR FILA ---
            good_rows = []
            
            for index, row in df.iterrows():
                try:
                    # Validar creditos (debe ser numero entre 1 y 5)
                    c = float(row['credits'])
                    if c < 1 or c > 5:
                        raise ValueError(f"Credits out of range: {c}")

                    # Validar notas (Solo A, B, C, D, F)
                    # Cualquier otra letra como 'E' se considera error
                    g = str(row['grade']).upper().strip()
                    if g not in ['A', 'B', 'C', 'D', 'F']:
                        raise ValueError(f"Invalid grade: {g}")

                    # Si pasa las pruebas, la guardamos
                    good_rows.append(row)

                except Exception as e:
                    # Si falla, la saltamos y guardamos por qué en el log
                    self.add_log(f"Skipping Row {index}: {e}")

            # Creamos el dataframe limpio con solo las filas buenas
            self.clean_data = pd.DataFrame(good_rows)

            # Escribir el log en un archivo fisico (KU_academic_run.log)
            try:
                f = open("KU_academic_run.log", "w")
                for line in self.logs:
                    f.write(line + "\n")
                f.close()
            except:
                print("Could not save log file")

            if self.clean_data.empty:
                self.add_log("Warning: No valid data found after cleaning.")
                return False

            # Si todo sale bien, calculamos los reportes
            self.calculate_gpa()
            self.calculate_stats()
            return True

        except Exception as e:
            self.add_log(f"Critical System Error: {e}")
            return False

    def calculate_gpa(self):
        # Tabla de puntos
        points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        
        data = self.clean_data.copy()
        data['points'] = data['grade'].str.upper().map(points)
        data['credits'] = data['credits'].astype(float)
        
        data['quality_points'] = data['points'] * data['credits']
        
        # Agrupar datos (usamos try para ser flexibles con columnas opcionales)
        cols_to_group = ['student_id', 'term']
        if 'student_name' in data.columns: cols_to_group.append('student_name')
        if 'major' in data.columns: cols_to_group.append('major')
        if 'campus' in data.columns: cols_to_group.append('campus')

        grouped = data.groupby(cols_to_group)
        
        results = []
        for ids, group in grouped:
            total_qp = group['quality_points'].sum()
            total_cr = group['credits'].sum()
            
            final_gpa = total_qp / total_cr if total_cr > 0 else 0.0
            
            # Crear diccionario para la fila
            row_dict = {}
            for i in range(len(cols_to_group)):
                col_name = cols_to_group[i]
                val = ids[i]
                row_dict[col_name] = val
            
            row_dict['GPA'] = round(final_gpa, 2)
            results.append(row_dict)

        self.gpa_data = pd.DataFrame(results)
        self.gpa_data.to_csv("KU_academic_master_gpa.csv", index=False)

    def calculate_stats(self):
        # Estadisticas por curso
        points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        
        cols = ['course_id']
        if 'course_name' in self.clean_data.columns: cols.append('course_name')
        if 'department' in self.clean_data.columns: cols.append('department')

        grouped = self.clean_data.groupby(cols)
        
        stats_list = []
        for ids, group in grouped:
            count = len(group)
            
            # Promedio numerico
            nums = group['grade'].str.upper().map(points)
            avg = nums.mean()
            
            # Convertir promedio a letra
            if avg >= 3.5: letter = 'A'
            elif avg >= 2.5: letter = 'B'
            elif avg >= 1.5: letter = 'C'
            elif avg >= 0.5: letter = 'D'
            else: letter = 'F'
            
            # Pass rate (D o mejor aprueba)
            passed = group[group['grade'].str.upper().isin(['A','B','C','D'])]
            pass_rate = len(passed) / count
            
            grades = sorted(group['grade'].unique())
            high = grades[0] 
            low = grades[-1]

            row_dict = {}
            if len(cols) == 1:
                row_dict[cols[0]] = ids
            else:
                for i in range(len(cols)):
                    row_dict[cols[i]] = ids[i]
            
            row_dict['enrollment_count'] = count
            row_dict['avg_grade'] = letter
            row_dict['pass_rate'] = round(pass_rate, 2)
            row_dict['highest_grade'] = high
            row_dict['lowest_grade'] = low
            
            stats_list.append(row_dict)
            
        self.course_stats = pd.DataFrame(stats_list)
        self.course_stats.to_csv("KU_academic_stats_by_course.csv", index=False)


# --- INTERFAZ GRAFICA (GUI) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keiser University - Grade Processor")
        self.geometry("1100x700")
        self.configure(bg=BG_COLOR) # Fondo principal oscuro
        
        self.logic = UniversityLogic()
        
        # Configurar estilos de tablas (Para que se vean oscuras)
        self.setup_styles()

        # Layout
        self.setup_sidebar()
        self.setup_main_area()
        
        # Iniciar en dashboard
        self.show_dashboard()

    def setup_styles(self):
        # Aqui configuramos los colores de la tabla (Treeview)
        style = ttk.Style()
        style.theme_use("clam") # 'clam' permite cambiar colores facil
        
        # Cuerpo de la tabla
        style.configure("Treeview", 
                        background=TABLE_BG, 
                        foreground=TEXT_WHITE, 
                        fieldbackground=TABLE_BG, 
                        borderwidth=0)
        
        # Encabezados de la tabla
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground=TEXT_WHITE, 
                        relief="flat")
        
        # Color al seleccionar una fila
        style.map("Treeview", background=[('selected', BLUE_COLOR)])

    def setup_sidebar(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR_COLOR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        lbl = tk.Label(self.sidebar, text="KU ANALYTICS", font=("Arial", 16, "bold"), 
                       bg=SIDEBAR_COLOR, fg=BLUE_COLOR)
        lbl.pack(pady=(30, 10), padx=10, anchor="w")

        lbl2 = tk.Label(self.sidebar, text="Control Panel", font=("Arial", 10), 
                        bg=SIDEBAR_COLOR, fg=TEXT_GREY)
        lbl2.pack(pady=(0, 30), padx=10, anchor="w")

        # Botones del menu
        self.btn_dash = tk.Button(self.sidebar, text="Dashboard", bg=SIDEBAR_COLOR, fg="white", 
                                  bd=0, command=self.show_dashboard, anchor="w", padx=20)
        self.btn_dash.pack(fill="x", pady=5)

        self.btn_gpa = tk.Button(self.sidebar, text="GPA Report", bg=SIDEBAR_COLOR, fg="white", 
                                 bd=0, command=self.show_gpa, anchor="w", padx=20)
        self.btn_gpa.pack(fill="x", pady=5)

        self.btn_stats = tk.Button(self.sidebar, text="Course Stats", bg=SIDEBAR_COLOR, fg="white", 
                                   bd=0, command=self.show_stats, anchor="w", padx=20)
        self.btn_stats.pack(fill="x", pady=5)

        self.btn_charts = tk.Button(self.sidebar, text="Charts", bg=SIDEBAR_COLOR, fg="white", 
                                    bd=0, command=self.show_charts, anchor="w", padx=20)
        self.btn_charts.pack(fill="x", pady=5)

        self.btn_logs = tk.Button(self.sidebar, text="View Logs", bg=SIDEBAR_COLOR, fg="white", 
                                  bd=0, command=self.show_logs, anchor="w", padx=20)
        self.btn_logs.pack(fill="x", pady=5)

    def setup_main_area(self):
        # Frame principal (Fondo oscuro)
        self.main_frame = tk.Frame(self, bg=BG_COLOR)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    def clear_main_area(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- PANTALLAS ---

    def show_dashboard(self):
        self.clear_main_area()
        
        # Aseguramos que los labels tengan bg=BG_COLOR
        lbl = tk.Label(self.main_frame, text="Academic Data Processor", font=("Arial", 24, "bold"), 
                       bg=BG_COLOR, fg="white")
        lbl.pack(pady=(50, 10))

        lbl2 = tk.Label(self.main_frame, text="Upload your CSV or JSON file to start", 
                        font=("Arial", 12), bg=BG_COLOR, fg=TEXT_GREY)
        lbl2.pack(pady=10)

        btn = tk.Button(self.main_frame, text="UPLOAD FILE", bg=BLUE_COLOR, fg="white", 
                        font=("Arial", 12, "bold"), padx=20, pady=10, command=self.upload_file)
        btn.pack(pady=30)

        self.status_label = tk.Label(self.main_frame, text="Waiting for file...", bg=BG_COLOR, fg="yellow")
        self.status_label.pack(pady=20)

    def show_gpa(self):
        self.clear_main_area()
        lbl = tk.Label(self.main_frame, text="GPA Report", font=("Arial", 18, "bold"), 
                       bg=BG_COLOR, fg="white")
        lbl.pack(anchor="w", pady=10)

        # La tabla usara los colores oscuros configurados en setup_styles
        cols = ("student_id", "student_name", "major", "term", "GPA")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill="both", expand=True)

        if not self.logic.gpa_data.empty:
            for index, row in self.logic.gpa_data.iterrows():
                vals = list(row)
                tree.insert("", "end", values=vals)

    def show_stats(self):
        self.clear_main_area()
        lbl = tk.Label(self.main_frame, text="Course Statistics", font=("Arial", 18, "bold"), 
                       bg=BG_COLOR, fg="white")
        lbl.pack(anchor="w", pady=10)

        cols = ("course_id", "course_name", "enrollment_count", "pass_rate", "avg_grade")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill="both", expand=True)

        if not self.logic.course_stats.empty:
            for index, row in self.logic.course_stats.iterrows():
                vals = [row[c] for c in cols if c in row]
                tree.insert("", "end", values=vals)

    def show_charts(self):
        self.clear_main_area()
        lbl = tk.Label(self.main_frame, text="Charts", font=("Arial", 18, "bold"), 
                       bg=BG_COLOR, fg="white")
        lbl.pack(anchor="w", pady=10)
        
        frame_btns = tk.Frame(self.main_frame, bg=BG_COLOR)
        frame_btns.pack(fill="x")
        
        b1 = tk.Button(frame_btns, text="Top Enrollment", command=lambda: self.plot(1))
        b1.pack(side="left", padx=5)
        b2 = tk.Button(frame_btns, text="GPA Pie Chart", command=lambda: self.plot(2))
        b2.pack(side="left", padx=5)
        b3 = tk.Button(frame_btns, text="Pass Rate", command=lambda: self.plot(3))
        b3.pack(side="left", padx=5)

        self.chart_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.chart_frame.pack(fill="both", expand=True, pady=20)

    def show_logs(self):
        self.clear_main_area()
        lbl = tk.Label(self.main_frame, text="Execution Logs", font=("Arial", 18, "bold"), 
                       bg=BG_COLOR, fg="white")
        lbl.pack(anchor="w", pady=10)

        text_area = tk.Text(self.main_frame, bg="black", fg="#00ff00")
        text_area.pack(fill="both", expand=True)
        
        for line in self.logic.logs:
            text_area.insert("end", line + "\n")
        text_area.config(state="disabled")

    # --- FUNCIONES DE BOTONES ---

    def upload_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv *.json")])
        if filename:
            self.status_label.config(text="Processing... please wait")
            self.update()
            
            # Usar hilos para no congelar la app
            t = threading.Thread(target=self.run_process, args=(filename,))
            t.start()

    def run_process(self, filename):
        result = self.logic.load_file(filename)
        
        if result:
            self.status_label.config(text="Success! File processed.", fg=GREEN_COLOR)
            messagebox.showinfo("Done", "Processing Complete!\nCheck tabs for results.")
        else:
            self.status_label.config(text="Error. Check logs tab.", fg=RED_COLOR)
            messagebox.showerror("Error", "Something went wrong.\nCheck Logs.")

    def plot(self, chart_id):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if self.logic.clean_data.empty:
            return

        fig = plt.Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Colores oscuros para el grafico
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_color('white')

        try:
            if chart_id == 1:
                data = self.logic.course_stats.sort_values('enrollment_count', ascending=False).head(10)
                ax.bar(data['course_name'], data['enrollment_count'], color=BLUE_COLOR)
                ax.set_title("Top 10 Courses by Enrollment")
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

            elif chart_id == 2:
                gpas = self.logic.gpa_data['GPA']
                low = len(gpas[gpas < 3.0])
                mid = len(gpas[(gpas >= 3.0) & (gpas < 3.5)])
                high = len(gpas[(gpas >= 3.5) & (gpas < 4.0)])
                perfect = len(gpas[gpas == 4.0])
                
                counts = [low, mid, high, perfect]
                labels = ['< 3.0', '3.0 - 3.49', '3.5 - 3.99', '4.0']
                
                # 'textprops' cambia el color de los numeros a blanco
                ax.pie(counts, labels=labels, autopct='%1.1f%%', textprops={'color':"white"})
                ax.set_title("GPA Distribution")

            elif chart_id == 3:
                data = self.logic.course_stats.groupby('department')['pass_rate'].mean()
                ax.barh(data.index, data.values, color=GREEN_COLOR)
                ax.set_title("Pass Rate by Department")

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            print("Error graphing:", e)

if __name__ == "__main__":
    app = App()
    app.mainloop()
