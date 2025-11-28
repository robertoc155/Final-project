import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time

# --- CONFIGURATION & STYLES ---
COLORS = {
    "bg_main": "#1e1e1e",
    "bg_panel": "#252526",
    "bg_input": "#333333",
    "accent": "#007acc", 
    "text_main": "#ffffff",
    "text_dim": "#cccccc",
    "success": "#4ec9b0",
    "danger": "#f48771"
}

class DataHandler:
    def __init__(self):
        self.dataset = []
        self.is_loaded = False

    def load_file(self, filepath):
        # Here your teammate will implement pandas logic
        # Example: self.df = pd.read_csv(filepath)
        print(f"Logic: Loading file {filepath}")
        self.is_loaded = True
        return True

    def get_dashboard_data(self):
        # Mock data for UI testing
        return [
            ("S001", "Alice Johnson", "CompSci", "Miami", "4.0", "Honor"),
            ("S002", "Brian Lee", "Business", "Orlando", "3.2", "Passed"),
            ("S003", "Carmen Rivera", "Math", "Online", "2.1", "Risk"),
            ("S004", "David Chen", "Biology", "Tampa", "3.9", "Honor"),
            ("S005", "Eva Green", "Psychology", "Miami", "1.5", "Failed"),
            ("S006", "Frank White", "History", "Orlando", "3.0", "Passed"),
            ("S007", "Grace Hall", "Nursing", "Tampa", "3.8", "Honor"),
        ]

    def export_report(self):
        print("Logic: Generating CSV reports...")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University Grade Processor")
        self.geometry("1100x700")
        self.configure(bg=COLORS["bg_main"])
        
        self.logic = DataHandler()
        self.setup_styles()
        
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        self.setup_landing()
        self.setup_dashboard()
        
        self.show_view("Landing")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Treeview (Table) Styling
        style.configure("Treeview", 
                        background=COLORS["bg_panel"],
                        foreground=COLORS["text_main"], 
                        fieldbackground=COLORS["bg_panel"],
                        font=("Segoe UI", 10),
                        rowheight=30, borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background=COLORS["bg_input"],
                        foreground=COLORS["text_main"],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        
        style.map("Treeview", background=[('selected', COLORS["accent"])])

    def setup_landing(self):
        frame = tk.Frame(self.container, bg=COLORS["bg_main"])
        self.frames["Landing"] = frame
        
        panel = tk.Frame(frame, bg=COLORS["bg_panel"], padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(panel, text="University Grade Processor", font=("Segoe UI", 24, "bold"), 
                 bg=COLORS["bg_panel"], fg=COLORS["text_main"]).pack(pady=(0, 5))
                 
        tk.Label(panel, text="Academic Analytics System", font=("Segoe UI", 11), 
                 bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(pady=(0, 30))
        
        self.btn_upload = tk.Button(panel, text="UPLOAD DATASET", font=("Segoe UI", 11, "bold"),
                                    bg=COLORS["accent"], fg="white", relief="flat", 
                                    padx=20, pady=10, cursor="hand2", command=self.handle_upload)
        self.btn_upload.pack()
        
        self.lbl_loading = tk.Label(panel, text="Processing...", font=("Segoe UI", 10, "italic"),
                                    bg=COLORS["bg_panel"], fg=COLORS["text_dim"])

    def setup_dashboard(self):
        frame = tk.Frame(self.container, bg=COLORS["bg_main"])
        self.frames["Dashboard"] = frame
        
        # Sidebar
        sidebar = tk.Frame(frame, bg=COLORS["bg_panel"], width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="KU ANALYTICS", font=("Segoe UI", 18, "bold"),
                 bg=COLORS["bg_panel"], fg=COLORS["accent"]).pack(anchor="w", padx=20, pady=(30, 5))
                 
        tk.Label(sidebar, text="Control Panel", font=("Segoe UI", 10),
                 bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(0, 30))
        
        # Menu Buttons
        opts = ["Dashboard", "Charts", "Settings"]
        for opt in opts:
            btn = tk.Button(sidebar, text=f"  {opt}", font=("Segoe UI", 11),
                            bg=COLORS["bg_panel"], fg=COLORS["text_main"],
                            relief="flat", anchor="w", cursor="hand2", pady=8,
                            activebackground=COLORS["bg_input"], activeforeground=COLORS["accent"])
            btn.pack(fill="x", padx=10)

        # Reset Button
        btn_reset = tk.Button(sidebar, text="Reset System", font=("Segoe UI", 10),
                              bg="#3a1c1c", fg="#ff6b6b", relief="flat", cursor="hand2",
                              command=lambda: self.show_view("Landing"))
        btn_reset.pack(side="bottom", fill="x", padx=20, pady=20)

        # Content Area
        content = tk.Frame(frame, bg=COLORS["bg_main"])
        content.pack(side="right", fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(content, bg=COLORS["bg_main"])
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(header, text="Academic Overview", font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side="left")
                 
        tk.Button(header, text="Export Reports", font=("Segoe UI", 10, "bold"),
                  bg=COLORS["bg_input"], fg=COLORS["text_main"], relief="flat",
                  padx=15, pady=5, cursor="hand2", command=self.logic.export_report).pack(side="right")

        # Table (Treeview)
        cols = ("ID", "Name", "Major", "Campus", "GPA", "Status")
        self.tree = ttk.Treeview(content, columns=cols, show="headings", selectmode="browse")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        self.tree.pack(fill="both", expand=True)

        # Tags for coloring rows
        self.tree.tag_configure("Honor", foreground=COLORS["success"])
        self.tree.tag_configure("Failed", foreground=COLORS["danger"])
        self.tree.tag_configure("Risk", foreground="#e5c07b") # Yellowish

    def show_view(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def handle_upload(self):
        path = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv;*.json")])
        if path:
            self.btn_upload.config(state="disabled", bg=COLORS["bg_input"])
            self.lbl_loading.pack(pady=(15, 0))
            
            # Threading to simulate processing without freezing UI
            threading.Thread(target=lambda: self.process_file(path)).start()

    def process_file(self, path):
        time.sleep(1.5) # Simulate Logic work
        self.logic.load_file(path)
        self.after(0, self.finish_upload)

    def finish_upload(self):
        self.lbl_loading.pack_forget()
        self.btn_upload.config(state="normal", bg=COLORS["accent"])
        self.update_table()
        self.show_view("Dashboard")

    def update_table(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert new data
        data = self.logic.get_dashboard_data()
        for row in data:
            # Last column is Status, used for coloring
            status = row[-1]
            self.tree.insert("", "end", values=row, tags=(status,))

if __name__ == "__main__":
    app = App()
    app.mainloop()