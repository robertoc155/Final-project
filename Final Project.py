import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QStackedWidget, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QProgressBar, 
                             QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# ============================================================================
# 🎨 UI CONFIGURATION (Your Part)
# ============================================================================
COLORS = {
    "bg_main":    "#0F172A",    # Dark Blue Background
    "sidebar":    "#1E293B",    # Sidebar Background
    "card":       "#334155",    # Card/Panel Background
    "accent":     "#38BDF8",    # Cyan Accent
    "text":       "#F8FAFC",    # Main Text
    "text_dim":   "#94A3B8",    # Dimmed Text
    "border":     "#475569"     # Borders
}

APP_STYLES = f"""
    QMainWindow {{ background-color: {COLORS['bg_main']}; }}
    QLabel {{ color: {COLORS['text']}; font-family: 'Segoe UI', sans-serif; }}
    QPushButton {{
        background-color: {COLORS['card']}; color: {COLORS['text']};
        border: none; border-radius: 8px; padding: 10px;
        font-weight: bold; font-size: 14px;
    }}
    QPushButton:hover {{ background-color: {COLORS['accent']}; color: #0F172A; }}
    QTableWidget {{
        background-color: {COLORS['sidebar']}; color: {COLORS['text']};
        gridline-color: {COLORS['border']}; border: none; border-radius: 10px;
    }}
    QHeaderView::section {{
        background-color: {COLORS['card']}; color: {COLORS['accent']};
        padding: 8px; border: none; font-weight: bold;
    }}
"""

# ============================================================================
# 🧠 LOGIC SECTION (Teammate's Part)
# ============================================================================
class DataHandler:
    """
    TEAMMATE INSTRUCTIONS:
    ------------------------------------------------------------------
    This class is for the Backend Logic. 
    1. Implement 'load_dataset' to read CSV/JSON using Pandas.
    2. Implement 'compute_gpa' for the calculations.
    3. Implement 'export_reports' to save the files.
    
    Do NOT modify the UI code below this class.
    ------------------------------------------------------------------
    """
    def __init__(self):
        self.df = None # Variable to store the Pandas DataFrame
        self.is_ready = False

    def load_dataset(self, file_path):
        """
        TODO: Load the file into self.df using pandas.
        Validate columns and data types here.
        """
        print(f"LOGIC: Loading file from {file_path}...")
        
        # --- TEAMMATE CODE GOES HERE ---
        # try:
        #     if file_path.endswith('.csv'):
        #         self.df = pd.read_csv(file_path)
        #     elif file_path.endswith('.json'):
        #         self.df = pd.read_json(file_path)
        #     self.process_data() # Call cleaning function
        #     self.is_ready = True
        #     return True, "File loaded successfully"
        # except Exception as e:
        #     return False, str(e)
        
        # Mock success for UI testing
        self.is_ready = True
        return True, "Success"

    def compute_stats(self):
        """
        TODO: Calculate GPA, Pass Rate, and other stats required.
        Should update self.df or create new result dataframes.
        """
        print("LOGIC: Computing GPAs and Statistics...")
        # --- TEAMMATE CODE GOES HERE ---
        pass

    def get_dashboard_data(self):
        """
        Returns data formatted for the UI Table.
        Format: List of rows, where each row is a list of strings.
        Example: [['ID', 'Name', 'Major', 'Campus', 'GPA', 'Status'], ...]
        """
        if not self.is_ready:
            return []

        # --- TEAMMATE: REPLACE THIS MOCK DATA WITH REAL DATA FROM SELF.DF ---
        return [
            ["S001", "Alice Johnson", "Computer Science", "Miami", "4.0", "Honor"],
            ["S002", "Brian Lee", "Business Admin", "Orlando", "3.5", "Passed"],
            ["S003", "Carmen Rivera", "Mathematics", "Miami", "2.8", "Risk"],
            ["S004", "David Chen", "Biology", "Tampa", "3.9", "Honor"],
            ["S005", "Eva Green", "Psychology", "Online", "1.5", "Failed"],
        ]

    def export_reports(self):
        """
        TODO: Generate the CSV/JSON output files and Logs.
        """
        print("LOGIC: Exporting reports...")
        # --- TEAMMATE CODE GOES HERE ---
        pass

# ============================================================================
# 🖥️ GUI SECTION (Your Part)
# ============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("University Grade Processor")
        self.resize(1200, 800)
        self.setStyleSheet(APP_STYLES)

        # Connect to Logic Class
        self.logic = DataHandler()

        # Layout Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content()
        self.switch_view(0)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet(f"background-color: {COLORS['sidebar']};")
        self.sidebar.setFixedWidth(250)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(20, 40, 20, 20)
        layout.setSpacing(10)

        # Brand
        layout.addWidget(self.create_label("KU ANALYTICS", 18, True, COLORS['accent']))
        layout.addWidget(self.create_label("Grade Processor", 10, False, COLORS['text_dim']))
        layout.addSpacing(20)

        # Menu
        self.menu_buttons = []
        labels = ["🏠 Home", "📊 Dashboard", "📈 Charts", "⚙️ Settings"]
        for i, text in enumerate(labels):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, x=i: self.switch_view(x))
            self.style_menu_btn(btn, active=False)
            layout.addWidget(btn)
            self.menu_buttons.append(btn)

        layout.addStretch()
        layout.addWidget(self.create_label("v1.0.2 Stable", 9, False, COLORS['text_dim']))
        self.main_layout.addWidget(self.sidebar)

    def setup_content(self):
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # View 0: Home
        self.view_home = self.create_home_view()
        self.stack.addWidget(self.view_home)

        # View 1: Dashboard
        self.view_dash = self.create_dashboard_view()
        self.stack.addWidget(self.view_dash)

        # View 2 & 3: Placeholders
        self.stack.addWidget(self.create_placeholder_view("Charts Module"))
        self.stack.addWidget(self.create_placeholder_view("Settings Module"))

    def create_home_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(450, 300)
        card.setStyleSheet(f"background-color: {COLORS['card']}; border-radius: 15px;")
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(15)

        card_layout.addWidget(self.create_label("Welcome to UGP", 22, True))
        card_layout.addWidget(self.create_label("Please load a student dataset to begin.", 11, False, COLORS['text_dim']))

        self.btn_load = QPushButton("📂 UPLOAD DATASET")
        self.btn_load.setFixedSize(200, 45)
        self.btn_load.setStyleSheet(f"background-color: {COLORS['accent']}; color: #0f172a; font-weight: bold;")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.clicked.connect(self.handle_load_file)
        
        self.loader = QProgressBar()
        self.loader.setFixedWidth(200)
        self.loader.setStyleSheet(f"QProgressBar {{ background: {COLORS['sidebar']}; border: none; height: 4px; }} QProgressBar::chunk {{ background: {COLORS['accent']}; }}")
        self.loader.hide()

        card_layout.addWidget(self.btn_load)
        card_layout.addWidget(self.loader)
        layout.addWidget(card)
        return container

    def create_dashboard_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)

        header = QHBoxLayout()
        header.addWidget(self.create_label("Academic Dashboard", 20, True))
        
        btn_export = QPushButton("📥 Export Reports")
        btn_export.setFixedSize(140, 35)
        btn_export.clicked.connect(self.logic.export_reports)
        header.addWidget(btn_export, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Student ID", "Full Name", "Major", "Campus", "GPA", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        return container

    def create_placeholder_view(self, text):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.create_label(f"{text}\n(To be implemented)", 16, False, COLORS['text_dim']))
        return w

    # --- Actions ---
    def handle_load_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Data Files (*.csv *.json)")
        if fname:
            self.btn_load.setEnabled(False)
            self.btn_load.setText("PROCESSING...")
            self.loader.show()
            self.loader.setRange(0, 0) # Infinite loading
            
            # Simulate delay for UX
            QTimer.singleShot(1500, lambda: self.process_loaded_file(fname))

    def process_loaded_file(self, fname):
        success, msg = self.logic.load_dataset(fname)
        self.loader.hide()
        self.btn_load.setEnabled(True)
        self.btn_load.setText("📂 UPLOAD DATASET")

        if success:
            self.logic.compute_stats() # Trigger teammate's math
            self.populate_table()
            self.switch_view(1) # Go to dashboard
        else:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{msg}")

    def populate_table(self):
        data = self.logic.get_dashboard_data()
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, item)

    def switch_view(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.menu_buttons):
            self.style_menu_btn(btn, active=(i == idx))

    # --- Helpers ---
    def create_label(self, text, size, bold=False, color=COLORS['text']):
        lbl = QLabel(text)
        weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
        lbl.setFont(QFont("Segoe UI", size, weight))
        lbl.setStyleSheet(f"color: {color};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if '\n' in text else Qt.AlignmentFlag.AlignLeft)
        return lbl

    def style_menu_btn(self, btn, active):
        bg = COLORS['card'] if active else "transparent"
        fg = COLORS['accent'] if active else COLORS['text']
        btn.setStyleSheet(f"""
            QPushButton {{ 
                text-align: left; padding-left: 15px; 
                background-color: {bg}; color: {fg}; 
                border-radius: 8px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {COLORS['card']}; color: {COLORS['accent']}; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())